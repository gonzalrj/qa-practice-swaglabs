from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    # region Element locators
    _username_fld = (By.ID, "user-name")
    _pwd_fld = (By.ID, "password")
    _login_btn = (By.ID, "login-button")
    _err_msg = (By.CSS_SELECTOR, "h3[data-test='error']")
    # _lockout_err_msg = (By.XPATH, "//h3[contains(text(),'locked out')]")
    # endregion

    # region Page methods
    def _execute_login(self, username: str, pwd: str):
        super()._type_text(self._username_fld, username)
        super()._type_text(self._pwd_fld, pwd)
        super()._click(self._login_btn)

    def _is_error_header_displayed(self, time=2) -> bool:
        return super()._is_element_visible(self._err_msg, time)

    def _get_error_message(self):
        return super()._find_element(self._err_msg).text
    # endregion


