import pytest
import allure

from pages.login_page import LoginPage
from pages.menu import Menu


@allure.parent_suite("Swag Labs Website")
@allure.suite("Authentication")
@allure.sub_suite("Login")
class TestLogin:
    # region User login credentials
    success_login = ("standard_user", "secret_sauce")
    invalid_login = ("invalid", "login")
    locked_out_user = ("locked_out_user", "secret_sauce")

    @pytest.fixture(autouse=True)
    def set_up_pages(self, driver):
        self.login_page = LoginPage(driver)
        self.menu = Menu(driver)

    @pytest.fixture(autouse=True)
    def setup_teardown(self, base_url):
        with allure.step("Go to homepage and clear all cookies."):
            self.login_page._go_to(base_url, "clear_cookies")

    @pytest.mark.xdist_loadgroup(name="checkout_users")
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.login
    @allure.title("Verify successful login using valid credentials")
    def test_success_login(self, driver, base_url):
        with allure.step("Login user using valid credentials."):
            self.login_page._execute_login(*self.success_login)

        with allure.step("Verify that user was successfully logged in."):
            assert not self.login_page._is_error_header_displayed(), "User was not logged in."

        with allure.step("Logout user."):
            self.menu.logout_user(base_url)

    @pytest.mark.xdist_loadgroup(name="checkout_users")
    @pytest.mark.regression
    @pytest.mark.login
    @allure.title("Verify failed login using invalid credentials")
    def test_invalid_login(self, driver, base_url):
        with allure.step("Login using invalid credentials."):
            self.login_page._execute_login(*self.invalid_login)

        with allure.step("Verify that user was not logged in."):
            assert "do not match" in self.login_page._get_error_message(), ("Username and Password mismatch error "
                                                                            "should be returned.")

    @pytest.mark.xdist_loadgroup(name="checkout_users")
    @pytest.mark.regression
    @pytest.mark.login
    @allure.title("Verify locked out user")
    def test_lockedout_login(self, driver, base_url):
        with allure.step("Login user using locked out credentials."):
            self.login_page._execute_login(*self.locked_out_user)

        with allure.step("Verify that the lock out error is displayed."):
            assert "locked out" in self.login_page._get_error_message(), "User not prompted with lock out error."
