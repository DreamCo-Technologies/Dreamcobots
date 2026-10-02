"""Download pinned official source files into raw/ and verify their sha256 against raw/SOURCES.md.
All O*NET files are pinned to the O*NET 31.0 Database (db_31_0_csv)."""
import hashlib, pathlib, re, sys, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / "raw"
DB = "https://www.onetcenter.org/dl_files/database/db_31_0_csv/"
URLS = {
    "Education_CIP_to_ONET_SOC.xlsx": "https://www.onetcenter.org/crosswalks/cip/Education_CIP_to_ONET_SOC.xlsx",
    "occupation_data.csv": DB + "occupation_data.csv",
    "knowledge.csv": DB + "knowledge.csv",
    "essential_skills.csv": DB + "essential_skills.csv",
    "job_zones.csv": DB + "job_zones.csv",
    "job_zone_reference.csv": DB + "job_zone_reference.csv",
    "task_statements.csv": DB + "task_statements.csv",
}
def main():
    pins = dict((n, h) for h, n in re.findall(r"^([0-9a-f]{64})\s+(\S+)$", (RAW / "SOURCES.md").read_text(), re.M))
    bad = 0
    for name, url in URLS.items():
        dest = RAW / name
        if not dest.exists():
            urllib.request.urlretrieve(url, dest)
        got = hashlib.sha256(dest.read_bytes()).hexdigest()
        ok = got == pins.get(name)
        bad += not ok
        print(f"{name}: {'ok' if ok else f'HASH MISMATCH (pinned {pins.get(name)}, got {got})'}")
    return 1 if bad else 0
if __name__ == "__main__":
    sys.exit(main())
