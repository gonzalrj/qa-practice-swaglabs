from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class InventoryPage(BasePage):
    _add_to_crt_btn_path = "(//button[contains(text(),'Add to cart')])[{}]"
    _remove_btn_path = "(//button[contains(text(),'Remove')])[{}]"

    def _click_add_to_cart_btn(self, position):
        target_btn = self._add_to_crt_btn_path.format(position)
        btn_locator = (By.XPATH, target_btn)
        super()._click(btn_locator)

    def _click_remove_btn(self, position):
        target_btn = self._remove_btn_path.format(position)
        btn_locator = (By.XPATH, target_btn)
        super()._click(btn_locator)
