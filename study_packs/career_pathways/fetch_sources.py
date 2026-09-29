"""Download pinned official source files into raw/ and verify their sha256 against raw/SOURCES.md."""
import hashlib, pathlib, re, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / "raw"
URLS = {
    "Education_CIP_to_ONET_SOC.xlsx": "https://www.onetcenter.org/crosswalks/cip/Education_CIP_to_ONET_SOC.xlsx",
    "occupation_data.csv": "https://www.onetcenter.org/dl_files/database/db_31_0_csv/occupation_data.csv",
    "knowledge.csv": "https://www.onetcenter.org/dl_files/database/db_31_0_csv/knowledge.csv",
    "essential_skills.csv": "https://www.onetcenter.org/dl_files/database/db_31_0_csv/essential_skills.csv",
}
def main():
    pins = dict((n, h) for h, n in re.findall(r"^([0-9a-f]{64})\s+(\S+)$", (RAW / "SOURCES.md").read_text(), re.M))
    for name, url in URLS.items():
        dest = RAW / name
        if not dest.exists():
            urllib.request.urlretrieve(url, dest)
        got = hashlib.sha256(dest.read_bytes()).hexdigest()
        status = "ok" if got == pins.get(name) else f"HASH MISMATCH (pinned {pins.get(name)})"
        print(f"{name}: {status}")
if __name__ == "__main__":
    main()
