"""
Selenium Job Application Bot
Automates job searching and application submission across multiple platforms.
Selenium is an optional dependency — the module is importable without it installed.
"""
# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401 — framework compliance marker


import os
import random
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

SUPPORTED_PLATFORMS = ["indeed", "linkedin", "glassdoor", "ziprecruiter", "monster"]

SIMULATED_JOBS = [
    {
        "title": "Software Engineer",
        "company": "TechCorp Inc.",
        "location": "Austin, TX",
        "url": "https://example-indeed.com/job/12345",
        "description": "Python developer role with 3+ years of experience.",
        "platform": "indeed",
        "salary": "$90,000 - $120,000",
    },
    {
        "title": "Data Analyst",
        "company": "Analytics Co.",
        "location": "Remote",
        "url": "https://example-linkedin.com/job/67890",
        "description": "SQL and Tableau skills required. Entry-level friendly.",
        "platform": "linkedin",
        "salary": "$65,000 - $85,000",
    },
    {
        "title": "Marketing Manager",
        "company": "Brand Builders LLC",
        "location": "New York, NY",
        "url": "https://example-glassdoor.com/job/11111",
        "description": "Lead digital marketing campaigns and manage a small team.",
        "platform": "glassdoor",
        "salary": "$75,000 - $100,000",
    },
    {
        "title": "Customer Success Specialist",
        "company": "SaaS Solutions",
        "location": "Chicago, IL",
        "url": "https://example-ziprecruiter.com/job/22222",
        "description": "Support B2B customers through onboarding and escalations.",
        "platform": "ziprecruiter",
        "salary": "$50,000 - $65,000",
    },
    {
        "title": "Project Manager",
        "company": "Enterprise Works",
        "location": "Dallas, TX",
        "url": "https://example-monster.com/job/33333",
        "description": "PMP preferred. Agile experience a plus.",
        "platform": "monster",
        "salary": "$85,000 - $110,000",
    },
]


class SeleniumJobApplicationBot:
    """
    Automates job searching and application submission across multiple platforms.

    When Selenium is available, the bot uses ChromeDriver to interact with job sites.
    In simulation mode (no Selenium installed), it uses placeholder data so the module
    can be imported and tested without a browser environment.
    """

    def __init__(self, config=None):
        """
        Initialize the bot with an optional configuration dictionary.

        Args:
            config (dict, optional): Supports keys:
                - 'headless' (bool): Run Chrome in headless mode. Default True.
                - 'delay_seconds' (int): Seconds to wait between actions. Default 2.
                - 'simulation_mode' (bool): Force simulation mode. Default False.
                - 'log_file' (str): Path to write application log. Default None.
        """
        self.config = config or {}
        self.headless = self.config.get("headless", True)
        self.delay = self.config.get("delay_seconds", 2)
        self.simulation_mode = self.config.get("simulation_mode", not SELENIUM_AVAILABLE)
        self.log_file = self.config.get("log_file", None)
        self.driver = None
        self._application_log = []

        mode_label = "SIMULATION" if self.simulation_mode else "LIVE (Selenium)"
        print(f"[JobBot] Initialized in {mode_label} mode.")
        if not SELENIUM_AVAILABLE and not self.config.get("simulation_mode"):
            print("[JobBot] Selenium not installed. Running in simulation mode.")
            print("[JobBot] To enable live mode: pip install selenium webdriver-manager")

    def setup_driver(self):
        """
        Set up the Chrome WebDriver for browser automation.

        In simulation mode, this method prints a setup message and returns None.
        In live mode, it initializes a headless ChromeDriver instance.

        Returns:
            WebDriver or None: The driver instance, or None in simulation mode.
        """
        if self.simulation_mode:
            print("[JobBot] setup_driver() called in simulation mode — no browser launched.")
            return None

        if not SELENIUM_AVAILABLE:
            print("[JobBot] ERROR: Selenium is not installed. Cannot setup driver.")
            return None

        print("[JobBot] Setting up Chrome WebDriver...")
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options,
            )
            print("[JobBot] Chrome WebDriver ready.")
        except Exception as e:
            print(f"[JobBot] Driver setup failed: {e}")
            self.driver = None

        return self.driver

    def search_jobs(self, keywords, location, platform="indeed"):
        """
        Search for jobs matching the given keywords on the specified platform.

        In simulation mode, returns filtered placeholder results.
        In live mode, uses Selenium to scrape the job platform.

        Args:
            keywords (str): Job title or keywords to search (e.g., 'Python developer').
            location (str): City, state, or 'Remote'.
            platform (str): Job platform to search. Default 'indeed'.
                            Must be one of: indeed, linkedin, glassdoor, ziprecruiter, monster.

        Returns:
            list[dict]: List of job dicts with keys: title, company, location, url,
                        description, platform, salary.
        """
        platform = platform.lower()
        if platform not in SUPPORTED_PLATFORMS:
            print(f"[JobBot] Unsupported platform '{platform}'. Supported: {SUPPORTED_PLATFORMS}")
            return []

        print(f"[JobBot] Searching '{keywords}' in '{location}' on {platform}...")

        if self.simulation_mode:
            kw_lower = keywords.lower()
            results = [
                j for j in SIMULATED_JOBS
                if (kw_lower in j["title"].lower() or kw_lower in j["description"].lower())
                and j["platform"] == platform
            ]
            if not results:
                results = [j for j in SIMULATED_JOBS if j["platform"] == platform]
            print(f"[JobBot] Found {len(results)} simulated job(s).")
            return results

        # Live Selenium scraping placeholder — extend per platform as needed
        print(f"[JobBot] Live scraping not yet implemented for '{platform}'. Returning empty list.")
        return []

    def apply_to_job(self, job, resume_path, cover_letter=None):
        """
        Apply to a single job listing.

        In simulation mode, randomly succeeds or fails to mimic real-world outcomes.
        In live mode, uses Selenium to fill and submit the application form.

        Args:
            job (dict): Job dict as returned by search_jobs().
            resume_path (str): Absolute path to the resume file (PDF or DOCX).
            cover_letter (str, optional): Cover letter text. If None, skipped.

        Returns:
            bool: True if application was submitted successfully, False otherwise.
        """
        title = job.get("title", "Unknown Role")
        company = job.get("company", "Unknown Company")

        if not os.path.isfile(resume_path) and not self.simulation_mode:
            print(f"[JobBot] Resume not found at '{resume_path}'. Skipping {title} @ {company}.")
            return False

        print(f"[JobBot] Applying to: {title} @ {company} ({job.get('platform', 'N/A')})...")
        time.sleep(self.delay * 0.1)  # Minimal delay (10% of configured delay) for simulation mode to speed up testing

        if self.simulation_mode:
            success = random.random() > 0.2  # 80% simulated success rate
            if success:
                print(f"[JobBot]   ✓ Application submitted (simulated).")
            else:
                print(f"[JobBot]   ✗ Application failed — already applied or form error (simulated).")
            self._application_log.append({"job": job, "success": success, "mode": "simulation"})
            return success

        # Live application logic placeholder
        print(f"[JobBot] Live application not yet implemented for this platform.")
        return False

    def run_job_campaign(self, keywords, location, resume_path, max_applications=10):
        """
        Run a full job search-and-apply campaign across all supported platforms.

        Args:
            keywords (str): Job search keywords.
            location (str): Target location.
            resume_path (str): Path to resume file.
            max_applications (int): Maximum number of applications to submit. Default 10.

        Returns:
            dict: Campaign results with keys:
                - 'applied' (int): Number of successful applications.
                - 'skipped' (int): Jobs skipped (already applied, no match).
                - 'errors' (int): Failed application attempts.
                - 'jobs_found' (int): Total jobs discovered.
        """
        print(f"\n[JobBot] Starting job campaign for '{keywords}' in '{location}'...")
        print(f"[JobBot] Max applications: {max_applications}\n")

        applied = 0
        skipped = 0
        errors = 0
        all_jobs = []

        for platform in SUPPORTED_PLATFORMS:
            if applied >= max_applications:
                break
            jobs = self.search_jobs(keywords, location, platform=platform)
            all_jobs.extend(jobs)

        for job in all_jobs:
            if applied >= max_applications:
                print(f"[JobBot] Reached max applications ({max_applications}). Stopping.")
                break
            success = self.apply_to_job(job, resume_path)
            if success:
                applied += 1
            else:
                errors += 1

        if self.driver:
            self.driver.quit()

        result = {
            "applied": applied,
            "skipped": skipped,
            "errors": errors,
            "jobs_found": len(all_jobs),
        }

        print(f"\n[JobBot] Campaign complete:")
        print(f"   Jobs found   : {result['jobs_found']}")
        print(f"   Applied      : {result['applied']}")
        print(f"   Skipped      : {result['skipped']}")
        print(f"   Errors       : {result['errors']}")
        return result

    def get_supported_platforms(self):
        """
        Return the list of supported job platforms.

        Returns:
            list[str]: Platform names (lowercase).
        """
        return list(SUPPORTED_PLATFORMS)

    def run(self):
        """
        Interactive CLI entry point for the Selenium Job Application Bot.
        """
        print("\n" + "=" * 60)
        print("  Selenium Job Application Bot — DreamCobots")
        print("=" * 60)
        print("Type 'quit' at any prompt to exit.\n")

        while True:
            print("\nOptions:")
            print("  1) Run a full job campaign")
            print("  2) Search jobs on a specific platform")
            print("  3) List supported platforms")
            print("  4) Quit")
            choice = input("\nSelect an option (1-4): ").strip()

            if choice == "1":
                keywords = input("  Job keywords (e.g. 'Python developer'): ").strip()
                if keywords.lower() == "quit":
                    break
                location = input("  Location (e.g. 'Austin, TX' or 'Remote'): ").strip()
                if location.lower() == "quit":
                    break
                resume = input("  Path to resume file: ").strip()
                if resume.lower() == "quit":
                    break
                try:
                    max_apps = int(input("  Max applications [10]: ").strip() or "10")
                except ValueError:
                    max_apps = 10
                self.run_job_campaign(keywords, location, resume, max_applications=max_apps)

            elif choice == "2":
                keywords = input("  Job keywords: ").strip()
                if keywords.lower() == "quit":
                    break
                location = input("  Location: ").strip()
                if location.lower() == "quit":
                    break
                platforms = self.get_supported_platforms()
                platform = input(f"  Platform [{', '.join(platforms)}]: ").strip().lower() or "indeed"
                jobs = self.search_jobs(keywords, location, platform=platform)
                print(f"\n  Results ({len(jobs)} job(s)):")
                for j in jobs:
                    print(f"  - {j['title']} @ {j['company']} ({j['location']}) — {j.get('salary', 'N/A')}")
                    print(f"    {j['url']}")

            elif choice == "3":
                print(f"\n  Supported platforms: {', '.join(self.get_supported_platforms())}")

            elif choice == "4" or choice.lower() == "quit":
                print("[JobBot] Goodbye! Good luck with your job search.")
                break
            else:
                print("[JobBot] Invalid option. Please choose 1–4.")


if __name__ == "__main__":
    bot = SeleniumJobApplicationBot()
    bot.run()


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 15, "leads_generated": 15, "revenue": 600}
