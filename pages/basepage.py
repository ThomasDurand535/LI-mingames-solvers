from selenium import webdriver


class BasePage:
    def __init__(self, url, cookies):
        self.driver = webdriver.Firefox()
        self.driver.get(url)
        self.driver.implicitly_wait(2)
        self.setCookies(cookies)
        self.driver.refresh()
        self.driver.implicitly_wait(2)

    def setCookies(self, cookies):
        for c in cookies:
            self.driver.add_cookie(c)
