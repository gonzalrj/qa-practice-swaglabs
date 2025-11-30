import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", help="Base URL for tests")
    parser.addoption("--browser", action="store", default="chrome", help="Browser: chrome, firefox, or edge")
    parser.addoption("--headless", action="store_true", default=False, help="Run browser in headless mode")


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    # Common Chrome prefs (disable password manager / credential service)
    chrome_prefs = {
        "profile.password_manager_leak_detection": False,
        "credentials_enable_service": False
    }

    # -------------
    # LOCAL DRIVER (explicit Service -> bypass Selenium Manager)
    # -------------
    print("Using Local WebDriver")

    if browser == "chrome":
        options = ChromeOptions()
        options.add_experimental_option("prefs", chrome_prefs)
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        # CI flags
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-first-run")

        driver = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Firefox(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Edge(options=options)

    else:
        raise Exception(f"Browser {browser} is not supported!")

    # try to maximize but only catch WebDriver-related errors
    try:
        driver.maximize_window()
    except WebDriverException:
        pass

    yield driver
    driver.quit()
