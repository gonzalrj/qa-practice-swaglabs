import logging
from typing import Tuple, Optional

from selenium.common import NoSuchElementException
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)
Locator = Tuple[By, str]


class BasePage:
    def __init__(self, driver: WebDriver, default_wait: int = 10):
        self.driver = driver
        self.default_wait = default_wait
        self.wait = WebDriverWait(self.driver, self.default_wait)

    def _go_to(self, url: str, clear_cookies=None):
        self.driver.get(url)
        if clear_cookies == "clear_cookies":
            self.driver.delete_all_cookies()

    def _find_element(self, locator: tuple) -> WebElement:
        """
        Expects a locator e.g. (By.ID, "id") and the unpacks it thus *locator
        as find_element expects 2 separate values and not a single tuple.
        :param locator:
        :return: WebElement:
        """
        return self.driver.find_element(*locator)

    def _find_elements(self, locator: tuple) -> list[WebElement]:
        """
        Expects a locator e.g. (By.ID, "id") and the unpacks it thus *locator
        as find_elements expects 2 separate values and not a single tuple.
        Finds and returns all elements with the same locator passed as an argument.
        :param locator:
        :return: list[WebElement]
        """
        return self.driver.find_elements(*locator)

    def _wait_until_element_is_visible(self, locator, wait_time: Optional[int] = None) -> WebElement:
        """Wait until visible and return the element (raises AssertionError on timeout)."""
        timeout = wait_time or self.default_wait
        try:
            elem = WebDriverWait(self.driver, timeout).until(ec.visibility_of_element_located(locator))
            return elem
        except TimeoutException as exc:
            msg = f"Element {locator} was not visible after {timeout} seconds."
            logger.error(msg)
            raise AssertionError(msg) from exc

    def _wait_until_element_is_clickable(self, locator, wait_time: Optional[int] = None) -> WebElement:
        timeout = wait_time or self.default_wait
        try:
            elem = WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(locator))
            return elem
        except TimeoutException as exc:
            msg = f"Element {locator} was not clickable after {timeout} seconds."
            logger.error(msg)
            raise AssertionError(msg) from exc

    def _wait_until_redirected_to(self, url: str, wait_time: Optional[int] = None):
        timeout = wait_time or self.default_wait
        WebDriverWait(self.driver, timeout).until(ec.url_to_be(url))

    def _click(self, locator, wait_time: Optional[int] = None, retries: int = 2) -> None:
        """Wait for clickable and attempt click with a small retry for transient errors."""
        for attempt in range(1, retries + 1):
            try:
                elem = self._wait_until_element_is_clickable(locator, wait_time)
                elem.click()
                return
            except (StaleElementReferenceException, ElementClickInterceptedException) as exc:
                logger.warning("Click attempt %s for %s failed: %s", attempt, locator, exc)
                if attempt == retries:
                    raise
            except AssertionError:
                # Re-raise to keep clear failure messages from wait helper
                raise

    def _type_text(self, locator, text: str, wait_time: Optional[int] = None) -> None:
        """Wait for visibility, clear, and send keys."""
        elem = self._wait_until_element_is_visible(locator, wait_time)
        elem.clear()
        elem.send_keys(text)

    def _is_element_visible(self, locator: tuple, time=5) -> bool:
        try:
            elem = self._wait_until_element_is_visible(locator, time)
            return elem.is_displayed()
        except (NoSuchElementException, TimeoutException, AssertionError, StaleElementReferenceException):
            return False

    def _hit_esc_key(self):
        a = ActionChains(self.driver)
        a.send_keys(Keys.ESCAPE).perform()

    def _hit_enter_key(self):
        a = ActionChains(self.driver)
        a.send_keys(Keys.ENTER).perform()

    def _get_current_url(self) -> str:
        return self.driver.current_url

