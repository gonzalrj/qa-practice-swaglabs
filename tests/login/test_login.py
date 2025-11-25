import pytest
import allure

from pages.login_page import LoginPage
from pages.menu import Menu


@allure.parent_suite("Cambridge Drupal Website")
@allure.suite("Authentication")
@allure.sub_suite("Login")
class TestLogin:
    # region User login credentials
    success_login = ("standard_user", "secret_sauce")
    locked_out_user = ("locked_out_user", "secret_sauce")

    @pytest.fixture(autouse=True)
    def objects_set_up(self, driver):
        self.loginpage = LoginPage(driver)
        self.menu = Menu(driver)

    @pytest.fixture(autouse=True)
    def setup_teardown(self, base_url):
        with allure.step("Go to homepage and clear all cookies."):
            self.loginpage._go_to(base_url, "clear_cookies")

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title("Verify that user was logged in using valid credentials.")
    def test_success_login(self, driver, base_url):
        with allure.step("Login user using valid credentials."):
            self.loginpage._login_user(*self.success_login)

        with allure.step("Verify that user was successfully logged in."):
            assert not self.loginpage._is_error_header_displayed(time=2), "User was not logged in."

        with allure.step("Logout usr."):
            self.menu.logout_user(base_url)

    @pytest.mark.regression
    @allure.title("Verify that user was not logged in using locked out credentials.")
    def test_lockedout_login(self, driver, base_url):
        with allure.step("Login user using locked out credentials."):
            self.loginpage._login_user(*self.locked_out_user)

        with allure.step("Verify that the lock out error is displayed."):
            assert self.loginpage._is_lockout_error_displayed(time=2), "User not prompted with lock out error."
