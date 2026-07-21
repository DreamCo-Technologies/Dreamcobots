"""
application_submitter.py

Automates the process of finding job listings and submitting applications
via Selenium.  Each supported site has its own handler method; add a new
method (and register it in SITE_HANDLERS) to extend support for additional
platforms.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurable timing constants (seconds)
PAGE_LOAD_WAIT = 3
ACTION_WAIT = 2
POST_SUBMIT_WAIT = 1


class ApplicationSubmitter:
    """Submits job applications on supported sites using a shared Selenium driver."""

    def __init__(self, driver: webdriver.Chrome, resume_parser=None):
        """
        :param driver: A logged-in Selenium WebDriver instance.
        :param resume_parser: Optional ResumeParser used to gate applications on
                              qualification checks.
        """
        self.driver = driver
        self.resume_parser = resume_parser
        self.submitted: list[dict] = []

        # Extend this mapping to add support for additional sites.
        self.SITE_HANDLERS = {
            "linkedin": self._apply_linkedin,
            "indeed": self._apply_indeed,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_for_site(self, site_config: dict) -> int:
        """
        Navigate to a job search URL and apply to listings.

        :param site_config: One entry from config['applications'].
        :returns: Number of applications submitted.
        """
        site = site_config["site"]
        handler = self.SITE_HANDLERS.get(site)
        if handler is None:
            print(
                f"[ApplicationSubmitter] No handler for '{site}'. "
                "Add a method to ApplicationSubmitter.SITE_HANDLERS to enable it."
            )
            return 0

        if self.resume_parser and not self.resume_parser.is_qualified():
            print(
                f"[ApplicationSubmitter] Resume does not meet minimum qualifications "
                f"for '{site}'. Skipping."
            )
            return 0

        print(f"[ApplicationSubmitter] Starting applications on '{site}'…")
        return handler(site_config)

    def run_all(self, applications: list[dict]) -> dict[str, int]:
        """
        Run the submitter for every site in *applications*.

        :returns: Mapping of site name → number of applications submitted.
        """
        results: dict[str, int] = {}
        for app_config in applications:
            results[app_config["site"]] = self.run_for_site(app_config)
        return results

    # ------------------------------------------------------------------
    # Site-specific handlers
    # ------------------------------------------------------------------

    def _apply_linkedin(self, site_config: dict) -> int:
        """Handle Easy Apply listings on LinkedIn."""
        search_url = site_config["search_url"]
        max_applications = site_config.get("max_applications", 5)
        submitted = 0

        try:
            self.driver.get(search_url)
            wait = WebDriverWait(self.driver, 15)
            time.sleep(PAGE_LOAD_WAIT)

            job_cards = self.driver.find_elements(
                By.CSS_SELECTOR, ".job-card-container"
            )

            for card in job_cards[:max_applications]:
                try:
                    card.click()
                    time.sleep(ACTION_WAIT)

                    apply_button = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(@class,'jobs-apply-button')]")
                        )
                    )
                    # Only proceed for Easy Apply buttons (identified by CSS class).
                    if "jobs-apply-button--top-card" not in apply_button.get_attribute("class"):
                        continue

                    apply_button.click()
                    time.sleep(ACTION_WAIT)

                    # Submit the first step of the Easy Apply modal.
                    submit_btn = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[@aria-label='Submit application']")
                        )
                    )
                    submit_btn.click()
                    time.sleep(POST_SUBMIT_WAIT)

                    job_title = self._safe_text(card, By.CSS_SELECTOR, ".job-card-list__title")
                    self.submitted.append({"site": "linkedin", "job": job_title})
                    submitted += 1
                    print(f"[ApplicationSubmitter] Applied to LinkedIn job: {job_title}")

                except (TimeoutException, NoSuchElementException):
                    # Move on if an individual card fails.
                    continue

        except Exception as exc:  # pylint: disable=broad-except
            print(f"[ApplicationSubmitter] Error during LinkedIn applications: {exc}")

        print(f"[ApplicationSubmitter] LinkedIn: submitted {submitted} application(s).")
        return submitted

    def _apply_indeed(self, site_config: dict) -> int:
        """Handle Easily Apply listings on Indeed."""
        search_url = site_config["search_url"]
        max_applications = site_config.get("max_applications", 5)
        submitted = 0

        try:
            self.driver.get(search_url)
            time.sleep(PAGE_LOAD_WAIT)

            job_cards = self.driver.find_elements(
                By.CSS_SELECTOR, ".jobsearch-ResultsList .result"
            )

            for card in job_cards[:max_applications]:
                try:
                    card.click()
                    time.sleep(ACTION_WAIT)

                    apply_button = self.driver.find_element(
                        By.ID, "indeedApplyButton"
                    )
                    apply_button.click()
                    time.sleep(ACTION_WAIT)

                    # Switch to the Indeed apply iframe if present.
                    iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                    if iframes:
                        self.driver.switch_to.frame(iframes[0])

                    submit_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[@type='submit']")
                        )
                    )
                    submit_btn.click()
                    time.sleep(POST_SUBMIT_WAIT)
                    self.driver.switch_to.default_content()

                    job_title = self._safe_text(card, By.CSS_SELECTOR, ".jobTitle")
                    self.submitted.append({"site": "indeed", "job": job_title})
                    submitted += 1
                    print(f"[ApplicationSubmitter] Applied to Indeed job: {job_title}")

                except (TimeoutException, NoSuchElementException):
                    self.driver.switch_to.default_content()
                    continue

        except Exception as exc:  # pylint: disable=broad-except
            print(f"[ApplicationSubmitter] Error during Indeed applications: {exc}")

        print(f"[ApplicationSubmitter] Indeed: submitted {submitted} application(s).")
        return submitted

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_text(parent, by, selector: str, default: str = "Unknown") -> str:
        """Return the text of a child element, or *default* if not found."""
        try:
            return parent.find_element(by, selector).text.strip()
        except NoSuchElementException:
            return default
