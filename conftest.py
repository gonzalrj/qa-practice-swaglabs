import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", help="Base URL for tests")
    parser.addoption("--browser", action="store", default="chrome",
                     help="Browser: chrome, firefox, or edge")
    parser.addoption("--headless", action="store_true", default=False,
                     help="Run browser in headless mode")


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    selenium_remote_url = os.environ.get("SELENIUM_REMOTE_URL")

    # Common Chrome prefs (disable password manager / credential service)
    chrome_prefs = {
        "profile.password_manager_leak_detection": False,
        "credentials_enable_service": False,
    }

    # -------------
    # REMOTE DRIVER
    # -------------
    if selenium_remote_url:
        print(f"Using Remote WebDriver: {selenium_remote_url}")

        if browser == "chrome":
            options = ChromeOptions()
            options.add_experimental_option("prefs", chrome_prefs)
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

        elif browser == "firefox":
            options = FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

        elif browser == "edge":
            options = EdgeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

        else:
            raise Exception(f"Browser {browser} is not supported!")

        driver = webdriver.Remote(command_executor=selenium_remote_url, options=options)
        yield driver
        driver.quit()
        return

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
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Read explicit binaries from env (set in Dockerfile) or use sensible defaults
        chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        # Point Chrome options at the browser binary
        options.binary_location = chrome_bin

        # Use Service with executable_path to bypass Selenium Manager
        service = ChromeService(executable_path=chromedriver_path)

        driver = webdriver.Chrome(service=service, options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # If you installed geckodriver somewhere, you can provide a Service similarly (optional)
        driver = webdriver.Firefox(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # If you installed msedgedriver, provide a Service similarly (optional)
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
