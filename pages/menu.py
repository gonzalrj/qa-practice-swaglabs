import time

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class Menu(BasePage):
    _burger_menu_btn = (By.ID, "react-burger-menu-btn")
    _logout_lnk = (By.ID, "logout_sidebar_link")

    def logout_user(self, base_url):
        super()._click(self._burger_menu_btn)
        super()._click(self._logout_lnk)

