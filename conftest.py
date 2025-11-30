import os
import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

# Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Edge
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", help="Base URL")
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store_true", default=False)


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    # Force headless in CI
    if os.environ.get("GITHUB_ACTIONS") == "true":
        headless = True

    chrome_prefs = {
        "profile.password_manager_leak_detection": False,
        "credentials_enable_service": False,
    }

    print(f"WebDriver: browser={browser}, headless={headless}")

    chromedriver_log = os.environ.get("CHROMEDRIVER_LOG", "/tmp/chromedriver.log")
    geckodriver_log = os.environ.get("GECKODRIVER_LOG", "/tmp/geckodriver.log")
    edgedriver_log = os.environ.get("EDGEDRIVER_LOG", "/tmp/edgedriver.log")

    # ============ CHROME ============
    if browser == "chrome":
        options = ChromeOptions()
        options.add_experimental_option("prefs", chrome_prefs)

        if headless:
            try:
                options.add_argument("--headless=new")
            except Exception:
                options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-first-run")

        service = ChromeService(
            executable_path=ChromeDriverManager().install(),
            log_path=chromedriver_log,
        )
        driver = webdriver.Chrome(service=service, options=options)

    # ============ FIREFOX ============
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = FirefoxService(
            executable_path=GeckoDriverManager().install(),
            log_path=geckodriver_log,
        )
        driver = webdriver.Firefox(service=service, options=options)

    # ============ EDGE ============
    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            try:
                options.add_argument("--headless=new")
            except Exception:
                options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = EdgeService(
            executable_path=EdgeChromiumDriverManager().install(),
            log_path=edgedriver_log,
        )
        driver = webdriver.Edge(service=service, options=options)

    else:
        raise Exception(f"Unsupported browser: {browser}")

    try:
        driver.maximize_window()
    except WebDriverException:
        pass

    yield driver
    driver.quit()
