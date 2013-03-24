import page

class TwitterLogin(page.Page):
    def fill_username(self, username = "bt_testuser"):
        self.browser.find_element_by_id("username_or_email").send_keys(username)
        return self
        
    def fill_password(self, password = "b1ttr41ls!!1!"):
        self.browser.find_element_by_id("password").send_keys(password)
        return self
        
    def click_allow(self):
        self.browser.find_element_by_id("allow").click()
        return self
