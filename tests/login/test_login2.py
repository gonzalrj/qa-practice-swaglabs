import pytest

from pages.login_page import LoginPage
from pages.menu import Menu


class TestAuthentication:
    valid_cred = ("standard_user", "secret_sauce")

    @pytest.mark.login
    def test_valid_login(self, driver, base_url):
        # Go to https://www.saucedemo.com/
        login_page = LoginPage(driver)
        login_page._go_to(base_url)

        # Execute login
        login_page._execute_login(*self.valid_cred)

        # Verify that I am redirected to Inventory page
        current_url = login_page._get_current_url()
        assert base_url + "/inventory.html" == current_url, f"User was redirected to {current_url} instead."

        # Execute logout
        menu = Menu(driver)
        menu.logout_user(base_url)
