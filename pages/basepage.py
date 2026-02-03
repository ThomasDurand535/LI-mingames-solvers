from selenium.webdriver.firefox.webdriver import WebDriver


class BasePage:
    def __init__(self, driver: WebDriver, url: str, cookies):
        self.driver = driver
        cookieLen = len(self.driver.get_cookies())
        self.driver.get(url)
        if cookieLen == 0:
            self.setCookies(cookies)
            self.driver.refresh()

    def setCookies(self, cookies):
        for c in cookies:
            self.driver.add_cookie(c)
