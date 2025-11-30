import allure
import pytest

from pages.cart_page import Cart
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@allure.parent_suite("Swag Labs Website")
@allure.suite("Checkout")
@allure.sub_suite("Cart")
class TestCartFunc:
    success_login = ("standard_user", "secret_sauce")

    @pytest.fixture(autouse=True)
    def set_up_pages(self, driver):
        self.login_page = LoginPage(driver)
        self.inventory_page = InventoryPage(driver)
        self.cart = Cart(driver)

    @pytest.mark.checkout
    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title("Verify adding products to cart")
    def test_adding_badge_count(self, driver, base_url):
        with allure.step("Login user"):
            self.login_page._go_to(base_url)
            self.login_page._execute_login(*self.success_login)

        with allure.step("Add first product to cart."):
            self.inventory_page._click_add_to_cart_btn(1)

        with allure.step("Verify that cart badge count is correct."):
            badge_count = self.cart._get_cart_badge_count()
            assert badge_count == 1, f"Expected badge count is 1, but got {badge_count}"

        with allure.step("Add second product to cart."):
            self.inventory_page._click_add_to_cart_btn(3)

        with allure.step("Verify that cart badge count is correct."):
            badge_count = self.cart._get_cart_badge_count()
            assert badge_count == 2, f"Expected badge count is 2, but got {badge_count}"

    @pytest.mark.checkout
    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title("Verify removing products from cart")
    def test_decreasing_badge_count(self, driver, base_url):
        with allure.step("Login user"):
            self.login_page._go_to(base_url)
            self.login_page._execute_login(*self.success_login)

        with allure.step("Add first product to cart."):
            self.inventory_page._click_add_to_cart_btn(1)

        with allure.step("Verify that cart badge count is correct."):
            badge_count = self.cart._get_cart_badge_count()
            assert badge_count == 1, f"Expected badge count is 1, but got {badge_count}"

        with allure.step("Remove the same product from cart."):
            self.inventory_page._click_remove_btn(1)

        with allure.step("Verify that cart badge count is correct."):
            assert not self.cart._is_badge_count_visible(), f"Badge count should not visible."
