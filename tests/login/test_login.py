import pytest

from pages.login_page import LoginPage
from pages.menu import Menu


class TestLogin:
    # region User login credentials
    success_login = ("standard_user", "secret_sauce")
    locked_out_user = ("locked_out_user", "secret_sauce")

    @pytest.fixture(autouse=True)
    def objects_set_up(self, driver):
        self.loginpage = LoginPage(driver)
        self.menu = Menu(driver)

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_success_login(self, driver, base_url):
        # Go to homepage and clear all cookies.
        self.loginpage._go_to(base_url, "clear_cookies")

        # Login user using valid credentials.
        self.loginpage._login_user(*self.success_login)

        # Verify that user was successfully logged in.
        assert not self.loginpage._is_error_header_displayed(time=2), "User was not logged in."

        # Logout user.
        self.menu.logout_user(base_url)

    @pytest.mark.regression
    def test_lockedout_login(self, driver, base_url):
        # Go to homepage and clear all cookies.
        self.loginpage._go_to(base_url, "clear_cookies")

        # Login user using locked out credentials.
        self.loginpage._login_user(*self.locked_out_user)

        # Verify that the lock out error is displayed.
        assert self.loginpage._is_lockout_error_displayed(time=2), "User not prompted with lock out error."
