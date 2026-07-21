"""
cli.py

Command-line interface for the Job Application Bot.
Provides a menu-driven interaction so users can control the bot without
writing any code.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import argparse
import json
import sys
from pathlib import Path


def _load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        print(f"[CLI] Config file not found: {config_path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-application-bot",
        description=(
            "Automate job logins, resume parsing, and application submissions "
            "across multiple job sites."
        ),
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the configuration file (default: config.json).",
    )
    parser.add_argument(
        "--resume",
        default=None,
        help="Path to resume file (.pdf or .docx). Overrides config['resume_path'].",
    )

    subparsers = parser.add_subparsers(dest="command", title="commands")

    # --- parse-resume ---
    subparsers.add_parser(
        "parse-resume",
        help="Parse a resume and display the qualification summary.",
    )

    # --- login ---
    login_parser = subparsers.add_parser(
        "login",
        help="Test login credentials for all configured sites.",
    )
    login_parser.add_argument(
        "--site",
        default=None,
        help="Limit login test to a specific site name.",
    )

    # --- apply ---
    apply_parser = subparsers.add_parser(
        "apply",
        help="Submit job applications on all configured sites.",
    )
    apply_parser.add_argument(
        "--site",
        default=None,
        help="Limit applications to a specific site name.",
    )
    apply_parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser in headless mode (no visible window).",
    )

    # --- run ---
    run_parser = subparsers.add_parser(
        "run",
        help="Full pipeline: login → parse resume → submit applications.",
    )
    run_parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser in headless mode (no visible window).",
    )

    return parser


def cmd_parse_resume(config: dict, resume_path: str) -> None:
    from resume_parser import ResumeParser

    required_skills = config.get("required_skills", [])
    parser = ResumeParser(required_skills)
    parser.load(resume_path)
    summary = parser.qualification_summary()

    print("\n=== Resume Qualification Summary ===")
    print(f"  Found skills  : {summary['found_skills']}")
    print(f"  Missing skills: {summary['missing_skills']}")
    print(f"  Qualified     : {summary['qualified']}")


def cmd_login(config: dict, site_filter: str | None, headless: bool = False) -> None:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from login_handler import LoginHandler

    credentials = config.get("credentials", [])
    if site_filter:
        credentials = [c for c in credentials if c["site"] == site_filter]

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        handler = LoginHandler(driver)
        results = handler.login_all(credentials)
        print("\n=== Login Results ===")
        for site, success in results.items():
            status = "✓ Success" if success else "✗ Failed"
            print(f"  {site}: {status}")
    finally:
        driver.quit()


def cmd_apply(
    config: dict,
    site_filter: str | None,
    resume_path: str,
    headless: bool,
) -> None:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from login_handler import LoginHandler
    from resume_parser import ResumeParser
    from application_submitter import ApplicationSubmitter

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    required_skills = config.get("required_skills", [])
    resume_parser = ResumeParser(required_skills)
    if resume_path:
        resume_parser.load(resume_path)

    credentials = config.get("credentials", [])
    applications = config.get("applications", [])
    if site_filter:
        credentials = [c for c in credentials if c["site"] == site_filter]
        applications = [a for a in applications if a["site"] == site_filter]

    driver = webdriver.Chrome(options=options)
    try:
        handler = LoginHandler(driver)
        handler.login_all(credentials)

        submitter = ApplicationSubmitter(driver, resume_parser)
        results = submitter.run_all(applications)

        print("\n=== Application Results ===")
        for site, count in results.items():
            print(f"  {site}: {count} application(s) submitted")
    finally:
        driver.quit()


def cmd_run(config: dict, resume_path: str, headless: bool) -> None:
    """Full pipeline convenience command."""
    print("=== Step 1: Parsing Resume ===")
    cmd_parse_resume(config, resume_path)

    print("\n=== Step 2: Logging In & Submitting Applications ===")
    cmd_apply(config, site_filter=None, resume_path=resume_path, headless=headless)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    config = _load_config(args.config)
    resume_path = args.resume or config.get("resume_path", "resume.pdf")

    if args.command == "parse-resume":
        cmd_parse_resume(config, resume_path)

    elif args.command == "login":
        headless = getattr(args, "headless", False)
        cmd_login(config, site_filter=args.site, headless=headless)

    elif args.command == "apply":
        cmd_apply(
            config,
            site_filter=args.site,
            resume_path=resume_path,
            headless=args.headless,
        )

    elif args.command == "run":
        cmd_run(config, resume_path=resume_path, headless=args.headless)


if __name__ == "__main__":
    main()
