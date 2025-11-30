from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class Cart(BasePage):
    _shopping_cart_badge = (By.CSS_SELECTOR, "span[data-test='shopping-cart-badge']")

    def _is_badge_count_visible(self) -> bool:
        """
        Returns True if there is a product in the bag.
        Badge will not be visible in the DOM if there's no product in the bag.
        :return: bool
        """
        return super()._is_element_visible(self._shopping_cart_badge, 1)

    def _get_cart_badge_count(self) -> int:
        return int(super()._find_element(self._shopping_cart_badge).text)
