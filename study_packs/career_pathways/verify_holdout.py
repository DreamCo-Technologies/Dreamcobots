"""Independent verifier for blind-holdout evidence records (standard library only).

The scorer (score_holdout.py --finalize) runs on a shared box, so it cannot prove its own push or its own arithmetic:
anyone with write access to the box could shim git or edit the scorer. This verifier is meant to be run by SOMEONE
OTHER THAN THE SCORER (for example the merchant's gate) on their own machine. Given an evidence record it:

  1. runs `git ls-remote` against the canonical repository https://github.com/DreamCo-Technologies/Dreamcobots.git
     (by absolute path /usr/bin/git, sanitized environment) and fetches the allowed branches
     (edu-career-pathways/majors-onet-study-plans and main) into a fresh temporary repository;
  2. requires the record's grading_commit (and remote_tip_sha) to be reachable from an allowed branch tip;
  3. reads grading_sheet.csv, GRADING_FINAL.txt, items.json and KEY_COMMITMENT.txt at grading_commit, and
     REVEALED_KEY.json, the results file and the record at the reveal commit (default: the allowed tip), via git show;
  4. checks sheet_sha256, the key commitment (sha256 of REVEALED_KEY.json), the items hash and the results file's
     integrity_hash;
  5. recomputes every score, baseline and pass check with its own implementation of the documented pass rule and
     requires the record and results file to match exactly.

CLI:
    python verify_holdout.py RECORD.json [--repo-url URL] [--reveal-commit SHA] [--results RESULTS.json] [--json]
  exit 0 = accepted (consistent, not test-only); 1 = rejected; 2 = usage error.

API:
    import verify_holdout
    r = verify_holdout.verify(record)          # record: dict, or path to the record JSON
    r["accepted"], r["ok"], r["errors"], r["checks"], r["recomputed"]

`accepted` is true only when every check passes and neither the record nor the verification is test-only.
"""
import argparse, csv, hashlib, io, json, os, pathlib, re, shutil, stat, subprocess, sys, tempfile, urllib.parse

CANONICAL_REPO = "github.com/dreamco-technologies/dreamcobots"
CANONICAL_REMOTE_URL = "https://github.com/DreamCo-Technologies/Dreamcobots"
CANONICAL_FETCH_URL = CANONICAL_REMOTE_URL + ".git"
ALLOWED_BRANCHES = ("edu-career-pathways/majors-onet-study-plans", "main")
PACK_PATH = "study_packs/career_pathways"
KIT_REL = f"{PACK_PATH}/evidence/holdout_kit"
OUT_REL = f"{PACK_PATH}/data/dreamco_knowledge/evidence/holdout"
GIT = "/usr/bin/git"
TIMEOUT_S = 180
# repository-local settings that could run commands or weaken transport are overridden on every git call
SAFE_CONFIG = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", "-c", "http.sslVerify=true",
               "-c", "protocol.ext.allow=never", "-c", "core.askPass=/bin/false", "-c", "credential.helper="]
DETECTION_MIN, FALSE_ALARM_MAX, GAP_MIN, AGREEMENT_MIN, MIN_ITEMS = 0.8, 0.2, 1.0, 0.8, 4
FINAL_RX = re.compile(r"^FINAL: grader=(?P<grader>[^;]+); declared_at=(?P<at>[^;\s]+); sheet_sha256=(?P<sheet>[0-9a-f]{64})\s*$",
                      re.M)
_NAME = r"[A-Za-z0-9_.-]+"
_PATH_RX = re.compile(rf"^/(?P<owner>{_NAME})/(?P<repo>{_NAME}?)(?:\.git)?/?$")
_SCP_RX = re.compile(rf"^git@(?P<host>[A-Za-z0-9.-]+):(?P<owner>{_NAME})/(?P<repo>{_NAME}?)(?:\.git)?/?$")
_SHA_RX = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")


class VerifyError(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---------- remote URL ----------
def normalize_remote(url):
    """'github.com/<owner>/<repo>' (lower case) for a strict GitHub URL, else None.

    Accepted: https://github.com/<owner>/<repo>[.git][/] with no userinfo, port, query or fragment; ssh://git@github.com/
    <owner>/<repo>[.git] (user exactly 'git', no password or port); git@github.com:<owner>/<repo>[.git]. The host must be
    exactly github.com (any case); owner and repo may contain only letters, digits, '-', '_' and '.'."""
    if not isinstance(url, str) or any(c in url for c in "#?\\%\x00 \t\r\n"):
        return None  # no fragments, queries, escapes or whitespace anywhere (e.g. 'https://evil.example#@github.com/...')
    m = _SCP_RX.match(url)
    if m:
        return f"github.com/{m['owner']}/{m['repo']}".lower() if m["host"].lower() == "github.com" else None
    try:
        u = urllib.parse.urlsplit(url)
        port = u.port
    except ValueError:
        return None
    scheme, netloc = u.scheme.lower(), u.netloc
    if u.query or u.fragment or port is not None or u.password is not None or ":" in netloc:
        return None
    if scheme == "https":
        if "@" in netloc or u.username is not None:
            return None  # no userinfo
        host = netloc
    elif scheme == "ssh":
        user, at, host = netloc.partition("@")
        if not at or user != "git" or "@" in host:
            return None
    else:
        return None
    if host.lower() != "github.com" or (u.hostname or "") != host.lower():
        return None
    m = _PATH_RX.match(u.path)
    return f"github.com/{m['owner']}/{m['repo']}".lower() if m else None


# ---------- git: absolute path, sanitized environment, fresh repository ----------
def git_binary():
    """/usr/bin/git, after checking it is a root-owned regular executable that only root can modify."""
    try:
        st, dst = os.stat(GIT), os.stat(os.path.dirname(GIT))
    except OSError:
        raise VerifyError(f"{GIT} not found; refusing (git is never looked up on PATH)")
    if not stat.S_ISREG(st.st_mode) or not os.access(GIT, os.X_OK):
        raise VerifyError(f"{GIT} is not an executable file")
    for s_, what in ((st, GIT), (dst, os.path.dirname(GIT))):
        if s_.st_uid != 0 or s_.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise VerifyError(f"{what} is not root-owned or is writable by others; refusing to trust it")
    return GIT


class GitSession:
    """Runs /usr/bin/git with a minimal environment: no inherited variables at all (so no GIT_*, proxy or PATH
    overrides), HOME and XDG_* in an empty temporary directory, GIT_CONFIG_NOSYSTEM=1 and GIT_CONFIG_GLOBAL=/dev/null.
    `mirror` is a fresh bare repository that receives the real remote's branches (blobless) and is deleted on exit."""

    def __init__(self, fetch_url):
        self.url = fetch_url

    def __enter__(self):
        self.git = git_binary()
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="holdout-git-"))
        home = self.tmp / "home"
        home.mkdir()
        self.env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "XDG_CONFIG_HOME": str(home / "xdg-config"),
                    "XDG_CACHE_HOME": str(home / "xdg-cache"), "XDG_DATA_HOME": str(home / "xdg-data"),
                    "XDG_STATE_HOME": str(home / "xdg-state"), "XDG_RUNTIME_DIR": str(home / "xdg-runtime"),
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
                    "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}
        self.mirror = self.tmp / "mirror.git"
        self.tips = {}
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run(self, cwd, *args, text=True, timeout=TIMEOUT_S, extra_env=None):
        try:
            return subprocess.run([self.git, "-C", str(cwd), *SAFE_CONFIG, *args], capture_output=True, text=text,
                                  env={**self.env, **(extra_env or {})}, timeout=timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as e:
            return subprocess.CompletedProcess(e.cmd, 124, "" if text else b"", f"timeout after {timeout}s")

    def m(self, *args, text=True):
        return self.run(self.mirror, *args, text=text)

    def ls_remote(self, branches):
        """{branch: tip} on the real remote for the branches that exist there. Refuses if the remote is unreachable."""
        refs = [f"refs/heads/{b}" for b in branches]
        r = self.run(self.tmp, "ls-remote", self.url, *refs)
        if r.returncode:
            raise VerifyError(f"cannot reach the remote with git ls-remote (exit {r.returncode}: {r.stderr.strip()[:300]}); "
                              "local refs are never used instead")
        tips = {}
        for line in r.stdout.splitlines():
            s_, _, ref = line.partition("\t")
            if ref in refs and _SHA_RX.match(s_):
                tips[ref[len("refs/heads/"):]] = s_
        return tips

    def fetch(self, tips):
        """Fetch the given branches (blobless; blobs are fetched lazily) into the fresh mirror and check that each tip
        equals what ls-remote reported."""
        if not tips:
            raise VerifyError("none of the allowed branches exists on the remote")
        for args in (("init", "-q", "--bare", str(self.mirror)),):
            r = self.run(self.tmp, *args)
            if r.returncode:
                raise VerifyError(f"git init failed: {r.stderr.strip()}")
        for k, v in (("remote.origin.url", self.url), ("remote.origin.promisor", "true"),
                     ("remote.origin.partialclonefilter", "blob:none"), ("core.repositoryformatversion", "1"),
                     ("extensions.partialClone", "origin")):
            self.m("config", k, v)
        specs = [f"+refs/heads/{b}:refs/heads/{b}" for b in tips]
        r = self.m("fetch", "-q", "--no-tags", "--filter=blob:none", "origin", *specs)
        if r.returncode:
            raise VerifyError(f"git fetch from the remote failed: {r.stderr.strip()[:300]}")
        for b, t in tips.items():
            got = self.m("rev-parse", "--verify", "-q", f"refs/heads/{b}^{{commit}}").stdout.strip()
            if got != t:
                raise VerifyError(f"the remote branch {b} moved while it was being checked ({t[:12]} -> {got[:12]}); retry")
        self.tips = dict(tips)

    def is_ancestor(self, a, b):
        return bool(_SHA_RX.match(a or "")) and self.m("merge-base", "--is-ancestor", a, b).returncode == 0

    def branches_containing(self, commit):
        return [b for b, t in self.tips.items() if self.is_ancestor(commit, t)]

    def show(self, commit, path):
        r = self.m("show", f"{commit}:{path}", text=False)
        return r.stdout if r.returncode == 0 else None

    def finalizations(self, key_sha, tips=None):
        """Commits reachable from the tips that already contain FINALIZED.txt, REVEALED_KEY.json or a holdout results
        file for this key commitment."""
        tips = list((tips or self.tips).values())
        fin, rev = f"{KIT_REL}/FINALIZED.txt", f"{KIT_REL}/REVEALED_KEY.json"
        r = self.m("log", "--full-history", "--format=%H", *tips, "--", fin, rev, OUT_REL)
        if r.returncode:
            raise VerifyError(f"git log failed: {r.stderr.strip()[:300]}")
        hits = []
        for c in r.stdout.split():
            b = self.show(c, fin)
            if b and f"key_sha256: {key_sha}" in b.decode("utf-8", "replace"):
                hits.append(f"{c[:12]}:{fin}")
            b = self.show(c, rev)
            if b and sha(b) == key_sha:
                hits.append(f"{c[:12]}:{rev}")
            for p in self.m("ls-tree", "-r", "--name-only", c, "--", OUT_REL).stdout.split("\n"):
                if p.endswith(".results.json"):
                    b = self.show(c, p)
                    try:
                        if b and json.loads(b).get("key_sha256") == key_sha:
                            hits.append(f"{c[:12]}:{p}")
                    except ValueError:
                        pass
        return sorted(set(hits))


    def blob_id(self, commit, path):
        """Blob id of path at commit (None if absent); needs no blob download."""
        r = self.m("rev-parse", "--verify", "-q", f"{commit}:{path}")
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None

    def rev_list(self, *args):
        r = self.m("rev-list", *args)
        if r.returncode:
            raise VerifyError(f"git rev-list failed: {r.stderr.strip()[:300]}")
        return r.stdout.split()

    def cat_blob(self, blob):
        r = self.m("cat-file", "blob", blob, text=False)
        return r.stdout if r.returncode == 0 else None

    def evidence_grading_commits(self, key_sha, kit_tag, tips=None):
        """{grading_commit named: [where]} over every results file, evidence record and FINALIZED.txt for this key
        commitment in any commit reachable from the tips. A record counts when its results file (same commit) has this
        key_sha256 or its content_version names this kit draw."""
        tips = list((tips or self.tips).values())
        fin = f"{KIT_REL}/FINALIZED.txt"
        named, cache = {}, {}

        def blob_json(b):
            if b not in cache:
                raw = self.cat_blob(b)
                try:
                    cache[b] = json.loads(raw) if raw else None
                except ValueError:
                    cache[b] = None
            return cache[b]

        for c in self.rev_list("--full-history", *tips, "--", OUT_REL, fin):
            entries = {}
            for line in self.m("ls-tree", "-r", c, "--", OUT_REL, fin).stdout.splitlines():
                meta, _, p = line.partition("\t")
                if meta.split()[1:2] == ["blob"]:
                    entries[p] = meta.split()[2]
            for p, b in entries.items():
                if p == fin:
                    t = (self.cat_blob(b) or b"").decode("utf-8", "replace")
                    if f"key_sha256: {key_sha}" in t:
                        m_ = re.search(r"^grading_commit: (\S+)", t, re.M)
                        named.setdefault(m_[1] if m_ else None, []).append(f"{c[:12]}:{p}")
                elif p.endswith(".results.json"):
                    d = blob_json(b)
                    if isinstance(d, dict) and d.get("key_sha256") == key_sha:
                        named.setdefault(d.get("grading_commit"), []).append(f"{c[:12]}:{p}")
                elif p.endswith(".json"):
                    d = blob_json(b)
                    if not isinstance(d, dict):
                        continue
                    rp = d.get("results_path")
                    res = blob_json(entries[rp]) if rp in entries else None
                    if (isinstance(res, dict) and res.get("key_sha256") == key_sha) or \
                            str(d.get("content_version", "")).endswith(kit_tag):
                        named.setdefault(d.get("grading_commit"), []).append(f"{c[:12]}:{p}")
        return named

    def check_signer(self, commit, require_signer):
        """(ok, detail): commit carries a valid signature from the registered key. require_signer is an SSH key
        fingerprint 'SHA256:...', an SSH allowed_signers file, or an armored GPG public key file."""
        kind, spec = parse_signer(require_signer)
        raw = self.m("cat-file", "commit", commit, text=False).stdout.decode("utf-8", "replace")
        sig = _commit_signature(raw)
        if not sig:
            return False, "grading_commit is not signed"
        work = self.tmp / f"signer-{commit[:12]}"
        work.mkdir(exist_ok=True)
        if kind in ("ssh-fingerprint", "ssh-allowed-signers"):
            if "BEGIN SSH SIGNATURE" not in sig:
                return False, "grading_commit is not SSH-signed"
            if kind == "ssh-fingerprint":
                key_type, key_b64, fpr = _ssh_signature_key(sig)
                if fpr != spec:
                    return False, f"signed by {fpr}, not the registered {spec}"
                allowed = work / "allowed_signers"
                allowed.write_text(f'registered-signer namespaces="git" {key_type} {key_b64}\n')
            else:
                allowed = pathlib.Path(spec).resolve()
            r = self.m("-c", f"gpg.ssh.allowedSignersFile={allowed}", "-c", f"gpg.ssh.program={SSH_KEYGEN}",
                       "verify-commit", "--raw", commit)
            ok = r.returncode == 0 and "Good \"git\" signature" in (r.stdout + r.stderr)
            return ok, (r.stdout + r.stderr).strip()[:300]
        if "BEGIN PGP SIGNATURE" not in sig:
            return False, "grading_commit is not GPG-signed"
        home = work / "gnupg"
        home.mkdir(mode=0o700)
        env = {"GNUPGHOME": str(home)}
        imp = subprocess.run([GPG, "--batch", "--quiet", "--import", str(spec)], capture_output=True, text=True,
                             env={**self.env, **env}, stdin=subprocess.DEVNULL, timeout=TIMEOUT_S)
        lst = subprocess.run([GPG, "--batch", "--with-colons", "--fingerprint", "--list-keys"], capture_output=True,
                             text=True, env={**self.env, **env}, stdin=subprocess.DEVNULL, timeout=TIMEOUT_S)
        fprs = {l.split(":")[9] for l in lst.stdout.splitlines() if l.startswith("fpr:")}
        if imp.returncode or not fprs:
            return False, "could not import the registered GPG key"
        r = self.run(self.mirror, "-c", f"gpg.program={GPG}", "verify-commit", "--raw", commit, extra_env=env)
        subprocess.run(["/usr/bin/gpgconf", "--homedir", str(home), "--kill", "all"], capture_output=True,
                       env={**self.env, **env}, stdin=subprocess.DEVNULL, timeout=60) if os.path.exists("/usr/bin/gpgconf") else None
        valid = [l.split() for l in r.stderr.splitlines() if l.startswith("[GNUPG:] VALIDSIG ")]
        ok = r.returncode == 0 and any(set(v[2:]) & fprs for v in valid)
        return ok, ("good signature from the registered GPG key" if ok else r.stderr.strip()[:300])


# ---------- the pass rule, implemented independently of score_holdout.py ----------
def parse_sheet(sheet_b, items):
    """Grades from the exact sheet bytes. Returns (grades, errors) with the same validation as the scorer."""
    crit = {i["item_id"]: [c["criterion"] for c in i["rubric"]] for i in items}
    grades, errs = {}, []
    for row in csv.DictReader(io.StringIO(sheet_b.decode("utf-8"), newline="")):
        h = (row.get("item_id") or "").strip()
        if h not in crit or h in grades:
            errs.append(f"bad or duplicate item_id {h!r}")
            continue
        if any((row.get(f"criterion_{n}") or "").strip() != crit[h][n - 1] for n in (1, 2, 3)):
            errs.append(f"{h}: criterion edited")
        vals = [(row.get(f"score_{n}") or "").strip() for n in (1, 2, 3)]
        if any(v not in ("0", "1", "2") for v in vals):
            errs.append(f"{h}: score not 0/1/2")
        fc = (row.get("factually_correct") or "").strip().lower()
        if fc not in ("yes", "no", "unsure"):
            errs.append(f"{h}: factually_correct")
        grader = " ".join((row.get("grader") or "").split())
        if not grader:
            errs.append(f"{h}: grader empty")
        grades[h] = {"scores": [int(v) for v in vals if v in ("0", "1", "2")], "factually_correct": fc, "grader": grader}
    missing = [i["item_id"] for i in items if i["item_id"] not in grades]
    if missing:
        errs.append(f"rows missing: {missing}")
    return grades, errs


def _down(s, c):
    rest = [x for n, x in enumerate(s) if n != c]
    return s[c] <= 1 and s[c] < sum(rest) / 2


def _counts(pairs, grades):
    weak = [(h, k) for h, k in pairs if k["candidate_type"] == "weakened"]
    full = [(h, k) for h, k in pairs if k["candidate_type"] == "full_strength"]
    det = [h for h, k in weak if _down(grades[h]["scores"], k["weakened_criterion"] - 1)]
    fa = [h for h, _ in full if _down(grades[h]["scores"], grades[h]["scores"].index(min(grades[h]["scores"])))]
    return weak, full, det, fa


def _agreement(s, bands):
    return sum(x in b for x, b in zip(s, bands)) / 3


def _baselines(kis):
    rnd = sum(sum(len(set(b) & {0, 1, 2}) / 3 for b in k["accepted_scores"]) / 3 for k in kis) / len(kis)
    all2 = sum(_agreement([2, 2, 2], k["accepted_scores"]) for k in kis) / len(kis)
    sc = 0.0
    for k in kis:
        if k["candidate_type"] == "weakened":
            sc += _agreement([0 if n == k["weakened_criterion"] - 1 else 2 for n in range(3)], k["accepted_scores"])
        else:
            sc += sum(_agreement([0 if n == c else 2 for n in range(3)], k["accepted_scores"]) for c in range(3)) / 3
    return {"uniform_random": rnd, "all_2s": all2, "shortcut_one_criterion_0": sc / len(kis)}


def recompute(key, grades):
    """(kit-level summary, {asset_id: {score, baseline_score, baselines, n_items, checks, rule_passed, ...}})."""
    pairs = list(key["items"].items())
    weak, full, det, fa = _counts(pairs, grades)
    fm = sum(sum(grades[h]["scores"]) for h, _ in full) / (3 * len(full))
    wm = sum(grades[h]["scores"][k["weakened_criterion"] - 1] for h, k in weak) / len(weak)
    rate, fa_rate, gap = len(det) / len(weak), len(fa) / len(full), fm - wm
    kit = {"n_weakened": len(weak), "n_full_strength": len(full), "detected": len(det), "detection_rate": round(rate, 4),
           "false_alarms": len(fa), "false_alarm_rate": round(fa_rate, 4), "full_strength_mean": round(fm, 4),
           "weakened_criterion_mean": round(wm, 4), "mean_gap": round(gap, 4),
           "passed": rate >= DETECTION_MIN and fa_rate <= FALSE_ALARM_MAX and gap >= GAP_MIN}
    groups = {}
    for h, k in pairs:
        groups.setdefault(k["asset_id"], []).append((h, k))
    out = {}
    for aid, ps in groups.items():
        kis = [k for _, k in ps]
        agree = sum(x in b for h, k in ps for x, b in zip(grades[h]["scores"], k["accepted_scores"])) / (3 * len(ps))
        b = _baselines(kis)
        w, f, d, a = _counts(ps, grades)
        n_full = len(f)
        dr = len(d) / len(w) if w else None
        fr = len(a) / len(f) if f else None
        checks = {"kit_discrimination": bool(kit["passed"]),
                  "eligible": len(ps) >= MIN_ITEMS and n_full >= 1 and len(w) >= 1,
                  "asset_detection_rate": dr is not None and dr >= DETECTION_MIN,
                  "asset_false_alarm_rate": fr is not None and fr <= FALSE_ALARM_MAX,
                  "agreement_min": agree >= AGREEMENT_MIN,
                  "agreement_above_baseline": agree > max(b.values()) + 1e-12,
                  "no_full_strength_judged_incorrect": not [h for h, _ in f if grades[h].get("factually_correct") == "no"]}
        out[aid] = {"score": round(agree, 4), "baseline_score": round(max(b.values()), 4),
                    "baselines": {k_: round(v, 4) for k_, v in b.items()}, "n_items": len(ps),
                    "asset_discrimination": {"n_weakened": len(w), "detected": len(d),
                                             "detection_rate": None if dr is None else round(dr, 4),
                                             "n_full_strength": n_full, "false_alarms": len(a),
                                             "false_alarm_rate": None if fr is None else round(fr, 4),
                                             "detection_min": DETECTION_MIN, "false_alarm_max": FALSE_ALARM_MAX},
                    "checks": checks, "rule_passed": all(checks.values())}
    return kit, out


# ---------- verification ----------
def _load(x):
    if isinstance(x, dict):
        return x
    return json.loads(pathlib.Path(x).read_bytes())


# ---------- signatures ----------
SSH_KEYGEN = "/usr/bin/ssh-keygen"
GPG = "/usr/bin/gpg"


def parse_signer(spec):
    """('ssh-fingerprint', 'SHA256:...') | ('ssh-allowed-signers', path) | ('gpg-key', path)."""
    s_ = str(spec)
    if re.fullmatch(r"SHA256:[A-Za-z0-9+/]{43}", s_):
        return "ssh-fingerprint", s_
    p = pathlib.Path(s_)
    if p.is_file():
        head = p.read_text("utf-8", "replace")
        return ("gpg-key", str(p.resolve())) if "BEGIN PGP PUBLIC KEY BLOCK" in head else ("ssh-allowed-signers", str(p.resolve()))
    if re.fullmatch(r"(0x)?[0-9A-Fa-f]{40}", s_):
        raise VerifyError("a GPG fingerprint alone cannot be checked: pass the exported public key file "
                          "(gpg --export --armor <fingerprint> > owner.asc)")
    raise VerifyError("require_signer must be an SSH key fingerprint (SHA256:...), an SSH allowed_signers file, or an "
                      "armored GPG public key file")


def _commit_signature(raw_commit):
    """The gpgsig header (armored signature) of a raw commit object, or None."""
    lines, sig, inside = raw_commit.split("\n"), [], False
    for line in lines:
        if line == "":
            break
        if line.startswith("gpgsig ") or line.startswith("gpgsig-sha256 "):
            inside = True
            sig.append(line.split(" ", 1)[1])
        elif inside and line.startswith(" "):
            sig.append(line[1:])
        else:
            inside = False
    return "\n".join(sig) or None


def _ssh_signature_key(armored):
    """(key type, base64 public key, 'SHA256:...' fingerprint) of the public key embedded in an SSHSIG signature."""
    import base64, struct
    body = "".join(l for l in armored.splitlines() if l and not l.startswith("-----"))
    blob = base64.b64decode(body)
    if blob[:6] != b"SSHSIG":
        raise VerifyError("not an SSH signature")
    (n,) = struct.unpack(">I", blob[10:14])
    pub = blob[14:14 + n]
    (t,) = struct.unpack(">I", pub[:4])
    fpr = "SHA256:" + base64.b64encode(hashlib.sha256(pub).digest()).decode().rstrip("=")
    return pub[4:4 + t].decode(), base64.b64encode(pub).decode(), fpr


def parse_expected_shas(spec):
    """Expected SHAs from a dict, a JSON file (VERIFIED_SHAS.json or a saved verify() result with a 'shas' key), or a
    'grading_commit=<sha>,reveal_commit=<sha>[,remote_tip_sha=<sha>]' string."""
    if isinstance(spec, dict):
        d = spec
    elif pathlib.Path(str(spec)).is_file():
        d = json.loads(pathlib.Path(str(spec)).read_bytes())
    else:
        d = dict(kv.split("=", 1) for kv in str(spec).split(",") if "=" in kv)
    d = d.get("shas", d)
    out = {k: d[k] for k in ("grading_commit", "reveal_commit", "remote_tip_sha") if d.get(k)}
    if not out or not all(_SHA_RX.match(v) for v in out.values()):
        raise VerifyError("expect_shas needs grading_commit, reveal_commit and/or remote_tip_sha as full SHAs")
    return out


# ---------- verification ----------
def verify(record, repo_url=CANONICAL_FETCH_URL, *, reveal_commit=None, results=None, allowed_branches=ALLOWED_BRANCHES,
           expect_shas=None, require_signer=None, _test_remote=None):
    """Verify one holdout evidence record against the real remote. Returns a dict with ok, accepted, test_only, errors,
    checks, shas (grading_commit, reveal_commit, remote_branch, remote_tip_sha) and recomputed. `_test_remote` (a local
    repository path) is for this pack's test suite only: it marks the verification test_only, so it is never accepted.

    expect_shas: SHAs recorded earlier (see parse_expected_shas); grading_commit and reveal_commit must be identical and
    a recorded remote_tip_sha must still be reachable from the remote tip, so a force-push that rewrote history fails.
    require_signer: grading_commit must carry a valid signature from this registered key (see parse_signer)."""
    errors, checks = [], {}

    def need(name, cond, msg):
        checks[name] = bool(cond)
        if not cond:
            errors.append(f"{name}: {msg}")
        return bool(cond)

    out = {"ok": False, "accepted": False, "test_only": _test_remote is not None, "errors": errors, "checks": checks,
           "shas": {}, "recomputed": None}
    try:
        rec = _load(record)
        expected = parse_expected_shas(expect_shas) if expect_shas is not None else None
        if require_signer is not None:
            parse_signer(require_signer)
        rec_test_only = bool(rec.get("test_only")) or rec.get("grading_commit") is None
        out["record_test_only"] = rec_test_only
        if not need("repo_url_canonical", normalize_remote(repo_url) == CANONICAL_REPO, f"{repo_url!r} is not {CANONICAL_REMOTE_URL}"):
            return out
        branches = tuple(b for b in allowed_branches if b in ALLOWED_BRANCHES)
        gc, tip_rec = rec.get("grading_commit") or "", rec.get("remote_tip_sha") or ""
        m = re.fullmatch(r"holdout:(?P<aid>[^:]+):(?P<run>\d{8}-\d{2})", rec.get("evidence_id", ""))
        if not need("record_shape", m and _SHA_RX.match(gc), "evidence_id or grading_commit malformed"):
            return out
        aid, run = m["aid"], m["run"]
        rec_path, res_path = f"{OUT_REL}/{aid}/{run}.json", rec.get("results_path", "")
        sheet_p, final_p, rev_p = f"{KIT_REL}/grading_sheet.csv", f"{KIT_REL}/GRADING_FINAL.txt", f"{KIT_REL}/REVEALED_KEY.json"
        need("remote_branch_allowed", rec.get("remote_branch") in ALLOWED_BRANCHES, f"remote_branch {rec.get('remote_branch')!r}")
        if not rec_test_only:
            need("remote_url_recorded", rec.get("remote_url") == CANONICAL_REMOTE_URL, f"remote_url {rec.get('remote_url')!r}")
        with GitSession(_test_remote or CANONICAL_FETCH_URL) as g:
            tips = g.ls_remote(branches)
            g.fetch(tips)
            on = g.branches_containing(gc)
            if not need("grading_commit_on_allowed_branch", on, f"{gc[:12]} is not reachable from {list(tips)} on the remote"):
                return out
            branch = rec.get("remote_branch") if rec.get("remote_branch") in on else on[0]
            tip = tips[branch]
            out["shas"] = {"grading_commit": gc, "remote_branch": branch, "remote_tip_sha": tip}
            need("remote_tip_sha_on_remote", g.branches_containing(tip_rec) and g.is_ancestor(gc, tip_rec),
                 "remote_tip_sha is not on an allowed branch or does not contain grading_commit")
            # 1. the reveal: absent at grading_commit and before it; added exactly once, later; never changed after
            need("reveal_absent_at_and_before_grading", g.blob_id(gc, rev_p) is None and not g.rev_list("--full-history", gc, "--", rev_p),
                 "REVEALED_KEY.json exists at grading_commit or in one of its ancestors (key revealed before grading)")
            touches = g.rev_list("--full-history", "--no-merges", tip, "--", rev_p)
            reveal = touches[0] if len(touches) == 1 else None
            need("reveal_added_exactly_once", reveal and g.blob_id(reveal, rev_p) and not any(
                g.blob_id(p, rev_p) for p in g.rev_list("--parents", "-n1", reveal)[1:]),
                f"REVEALED_KEY.json must be added in exactly one commit and never modified, removed or re-added "
                f"({len(touches)} commits touch it)")
            if reveal:
                need("reveal_after_grading", reveal != gc and g.is_ancestor(gc, reveal),
                     "the reveal commit is grading_commit itself or does not descend from it")
                need("reveal_unchanged_at_tip", g.blob_id(tip, rev_p) == g.blob_id(reveal, rev_p),
                     "REVEALED_KEY.json at the remote tip differs from the reveal commit")
                if reveal_commit is not None:
                    given = g.m("rev-parse", "--verify", "-q", f"{reveal_commit}^{{commit}}").stdout.strip()
                    need("reveal_commit_matches", given == reveal, f"--reveal-commit {str(reveal_commit)[:12]} is not the "
                         f"commit that added REVEALED_KEY.json ({reveal[:12]})")
                out["shas"]["reveal_commit"] = reveal
            if errors:
                return out
            # 2. the sheet and GRADING_FINAL.txt are identical at grading_commit, at reveal and at every commit between
            want = (g.blob_id(gc, sheet_p), g.blob_id(gc, final_p))
            path = g.rev_list("--ancestry-path", f"{gc}..{reveal}")
            changed = [c[:12] for c in path if (g.blob_id(c, sheet_p), g.blob_id(c, final_p)) != want]
            need("sheet_unchanged_from_grading_to_reveal", all(want) and not changed,
                 f"grading_sheet.csv or GRADING_FINAL.txt differs between grading_commit and the reveal (at {changed[:5]})")
            # evidence is frozen once revealed
            frozen = [p for p in (rec_path, res_path) if g.blob_id(tip, p) != g.blob_id(reveal, p)
                      or g.rev_list("--full-history", "--no-merges", f"{reveal}..{tip}", "--", p)]
            need("evidence_unchanged_after_reveal", not frozen, f"changed or missing after the reveal commit: {frozen}")
            # 4. recorded SHAs
            if expected:
                for k in ("grading_commit", "reveal_commit"):
                    if k in expected:
                        need(f"expected_{k}", expected[k] == out["shas"].get(k), f"{k} {out['shas'].get(k)} != expected {expected[k]}")
                if "remote_tip_sha" in expected:
                    need("expected_remote_tip_still_reachable", g.is_ancestor(expected["remote_tip_sha"], tip),
                         "the recorded remote tip is no longer reachable from the branch (history was rewritten)")
            # 5. signature
            if require_signer is not None:
                ok_sig, detail = g.check_signer(gc, require_signer)
                need("grading_commit_signed_by_registered_key", ok_sig, detail)
            sheet_b = g.show(gc, sheet_p)
            final_b = g.show(gc, final_p)
            items_b = g.show(gc, f"{KIT_REL}/items.json")
            commit_b = g.show(gc, f"{KIT_REL}/KEY_COMMITMENT.txt")
            key_b = g.show(reveal, rev_p)
            results_b = g.show(reveal, res_path)
            rec_b = g.show(reveal, rec_path)
            files = {"grading_sheet.csv": sheet_b, "GRADING_FINAL.txt": final_b, "items.json": items_b,
                     "KEY_COMMITMENT.txt": commit_b, "REVEALED_KEY.json": key_b, "results file": results_b, "record file": rec_b}
            if not need("committed_files_present", all(v is not None for v in files.values()),
                        "missing at the committed SHAs: " + ", ".join(k for k, v in files.items() if v is None)):
                return out
            commitment = dict(l.split(": ", 1) for l in commit_b.decode().splitlines() if ": " in l)
            # 3. every results file, record and FINALIZED.txt for this key commitment names the same grading_commit
            try:
                kj = json.loads(key_b)
                kit_tag = f"{kj.get('kit')} drawn {kj.get('created_at')}"
            except ValueError:
                kit_tag = "\x00"
            named = g.evidence_grading_commits(commitment.get("key_sha256", "?"), kit_tag)
            need("all_evidence_names_this_grading_commit", set(named) <= {gc},
                 "evidence for this key commitment names other grading commits: "
                 + "; ".join(f"{str(k)[:12]} in {v[:3]}" for k, v in named.items() if k != gc))
        need("record_matches_committed_record", json.loads(rec_b) == rec, "the record differs from the committed record")
        need("results_integrity_hash", rec.get("integrity_hash") == "sha256:" + sha(results_b), "integrity_hash != sha256(results file)")
        if results is not None:
            need("results_matches_committed", _load(results) == json.loads(results_b), "given results differ from the committed results")
        res = json.loads(results_b)
        fm = FINAL_RX.search(final_b.decode("utf-8", "replace"))
        if not need("grading_final_parses", fm, "GRADING_FINAL.txt has no FINAL line with sheet_sha256"):
            return out
        need("sheet_sha256", sha(sheet_b) == fm["sheet"], "sha256(grading_sheet.csv) != sheet_sha256 in GRADING_FINAL.txt")
        need("key_commitment", sha(key_b) == commitment.get("key_sha256"), "sha256(REVEALED_KEY.json) != KEY_COMMITMENT key_sha256")
        need("items_commitment", sha(items_b) == commitment.get("items_json_sha256"), "sha256(items.json) != KEY_COMMITMENT")
        if errors:
            return out
        key, items = json.loads(key_b), json.loads(items_b)["items"]
        by_id = {i["item_id"]: i for i in items}
        need("key_matches_items", set(key["items"]) == set(by_id) and all(
            sha(by_id[h]["candidate_answer"].encode()) == k["candidate_answer_sha256"] for h, k in key["items"].items()),
            "key and items.json disagree")
        grades, perrs = parse_sheet(sheet_b, items)
        if not need("sheet_valid", not perrs and not errors, "; ".join(perrs[:5])):
            return out
        grader = " ".join(fm["grader"].split())
        need("single_declared_grader", {g_["grader"] for g_ in grades.values()} == {grader} and rec.get("grader") == grader,
             "sheet graders, GRADING_FINAL grader and record grader differ")
        kit, assets = recompute(key, grades)
        if not need("asset_in_kit", aid in assets, f"{aid} has no kit items"):
            return out
        a = assets[aid]
        expected_passed = a["rule_passed"] and not rec_test_only
        out["recomputed"] = {"asset_id": aid, **a, "passed": expected_passed, "kit_discrimination": kit}
        need("score", rec.get("score") == a["score"] == res.get("score"), f"score {rec.get('score')} != recomputed {a['score']}")
        need("baseline_score", rec.get("baseline_score") == a["baseline_score"] == res.get("baseline_score"), "baseline_score differs")
        need("baselines", res.get("baselines") == a["baselines"], "baselines differ")
        need("n_items", rec.get("n_items") == a["n_items"] == res.get("n_items"), "n_items differs")
        need("pass_checks", res.get("pass_checks") == a["checks"], "pass_checks differ")
        need("asset_discrimination", res.get("asset_discrimination") == a["asset_discrimination"], "asset_discrimination differs")
        rk = res.get("kit_discrimination") or {}
        need("kit_discrimination", {k: rk.get(k) for k in kit} == kit, "kit_discrimination differs")
        need("rule_passed", res.get("rule_passed") == a["rule_passed"], "rule_passed differs")
        need("passed", rec.get("passed") is expected_passed and res.get("passed") is expected_passed,
             f"passed {rec.get('passed')} != recomputed {expected_passed}")
        need("results_hashes", res.get("key_sha256") == sha(key_b) and res.get("grading_sheet_sha256") == sha(sheet_b)
             and res.get("items_json_sha256") == sha(items_b), "results file hashes differ")
        need("results_git_fields", all(res.get(f) == rec.get(f) for f in ("grading_commit", "remote_url", "remote_branch", "remote_tip_sha")),
             "results and record git fields differ")
    except VerifyError as e:
        errors.append(str(e))
    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as e:
        errors.append(f"malformed input: {type(e).__name__}: {e}")
    out["ok"] = not errors
    out["accepted"] = out["ok"] and not out["test_only"] and not out.get("record_test_only", True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify a holdout evidence record against the canonical remote.")
    ap.add_argument("record", help="path to data/dreamco_knowledge/evidence/holdout/<asset_id>/<run>.json")
    ap.add_argument("--repo-url", default=CANONICAL_FETCH_URL, help="must normalize to github.com/DreamCo-Technologies/Dreamcobots")
    ap.add_argument("--reveal-commit", default=None, help="optional: must equal the commit that added REVEALED_KEY.json")
    ap.add_argument("--results", default=None, help="optional results file to compare with the committed one")
    ap.add_argument("--expect-shas", default=None, help="VERIFIED_SHAS.json, a saved --json result, or "
                    "grading_commit=<sha>,reveal_commit=<sha>[,remote_tip_sha=<sha>]")
    ap.add_argument("--require-signer", default=None, help="SSH key fingerprint (SHA256:...), SSH allowed_signers file, or "
                    "armored GPG public key file; grading_commit must be signed by it")
    ap.add_argument("--json", action="store_true", help="print the full result as JSON")
    a = ap.parse_args(argv)
    r = verify(a.record, a.repo_url, reveal_commit=a.reveal_commit, results=a.results, expect_shas=a.expect_shas,
               require_signer=a.require_signer)
    if a.json:
        print(json.dumps(r, indent=2, default=str))
    else:
        print(("ACCEPTED" if r["accepted"] else "REJECTED") + f": {a.record}")
        for k, v in r.get("shas", {}).items():
            print(f"  {k}: {v}")
        for e in r["errors"]:
            print("  -", e)
        if r["ok"] and not r["accepted"]:
            print("  - consistent, but test-only: not evidence")
    return 0 if r["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
