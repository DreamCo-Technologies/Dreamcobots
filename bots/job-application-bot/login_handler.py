"""
login_handler.py

Handles authentication for multiple job application sites.
Credentials are loaded from environment variables (preferred) or from
the config.json file as a fallback.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class LoginHandler:
    """Manages Selenium-based login sessions for multiple sites."""

    # Field selectors per site – extend this dict to add new platforms.
    SITE_SELECTORS = {
        "linkedin": {
            "username_field": (By.ID, "username"),
            "password_field": (By.ID, "password"),
            "submit_button": (By.XPATH, "//button[@type='submit']"),
        },
        "indeed": {
            "username_field": (By.ID, "ifl-InputFormField-3"),
            "password_field": (By.ID, "ifl-InputFormField-7"),
            "submit_button": (By.XPATH, "//button[@type='submit']"),
        },
    }

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.logged_in_sites: list[str] = []

    def _get_credentials(self, site_config: dict) -> tuple[str, str]:
        """
        Return (username, password) for a site.

        Environment variables take priority over values stored in config.json
        so that secrets are never hard-coded in the repository.

        Expected env-var names:  <SITE>_USERNAME  /  <SITE>_PASSWORD
        where <SITE> is the site name uppercased (e.g. LINKEDIN_USERNAME).
        """
        site_upper = site_config["site"].upper()
        username = os.environ.get(
            f"{site_upper}_USERNAME", site_config.get("username", "")
        )
        password = os.environ.get(
            f"{site_upper}_PASSWORD", site_config.get("password", "")
        )
        return username, password

    def login(self, site_config: dict) -> bool:
        """
        Log in to a single site.

        :param site_config: One entry from config['credentials'].
        :returns: True on success, False on failure.
        """
        site = site_config["site"]
        url = site_config["url"]
        username, password = self._get_credentials(site_config)

        if not username or not password:
            print(f"[LoginHandler] Credentials missing for '{site}'. Skipping.")
            return False

        selectors = self.SITE_SELECTORS.get(site)
        if selectors is None:
            print(
                f"[LoginHandler] No selectors configured for '{site}'. "
                "Add an entry to LoginHandler.SITE_SELECTORS to enable this site."
            )
            return False

        try:
            print(f"[LoginHandler] Navigating to login page for '{site}'…")
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 15)

            user_el = wait.until(EC.presence_of_element_located(selectors["username_field"]))
            user_el.clear()
            user_el.send_keys(username)

            pass_el = self.driver.find_element(*selectors["password_field"])
            pass_el.clear()
            pass_el.send_keys(password)

            submit_el = self.driver.find_element(*selectors["submit_button"])
            submit_el.click()

            time.sleep(2)
            self.logged_in_sites.append(site)
            print(f"[LoginHandler] Successfully logged in to '{site}'.")
            return True

        except TimeoutException:
            print(f"[LoginHandler] Timed out waiting for login page elements on '{site}'.")
        except NoSuchElementException as exc:
            print(f"[LoginHandler] Login form element not found on '{site}': {exc}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[LoginHandler] Unexpected error logging in to '{site}': {exc}")

        return False

    def login_all(self, credentials: list[dict]) -> dict[str, bool]:
        """
        Attempt to log in to every site listed in *credentials*.

        :returns: Mapping of site name → success flag.
        """
        results: dict[str, bool] = {}
        for cred in credentials:
            results[cred["site"]] = self.login(cred)
        return results
