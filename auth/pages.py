import page

class ThirdPartyAuthPage(page.Page):
    def __init__(self, browser, username, password = 'b1ttr41ls!!1!'):
        super(ThirdPartyAuthPage, self).__init__(browser)
        self.username = username
        self.password = password


class TwitterPage(ThirdPartyAuthPage):
    def fill_out_auth_form(self):
        self.browser.find_element_by_id(
            "username_or_email").send_keys(self.username)
        self.browser.find_element_by_id("password").send_keys(self.password)
        return self
        
    def submit(self):
        self.browser.find_element_by_id("allow").click()
        

class FoursquarePage(ThirdPartyAuthPage):
    def fill_out_auth_form(self):
        self.browser.find_element_by_xpath(
            '//a[contains(text(), "Log in")]').click()
        self.browser.find_element_by_id('username').send_keys(self.username)
        self.browser.find_element_by_id('password').send_keys(self.password)
        return self
            
    def submit(self):
        self.browser.find_element_by_xpath(
            '//input[@type="submit" and @value="Log in"]').click()
        self.browser.find_element_by_xpath(
            '//input[@type="submit" and @value="Allow"]').click()
            

class LastfmPage(ThirdPartyAuthPage):
    def fill_out_auth_form(self):
        self.browser.find_element_by_id('username').send_keys(self.username)
        self.browser.find_element_by_id('password').send_keys(self.password)
        return self
    
    def submit(self):
        self.browser.find_element_by_xpath(
            '//input[@type="submit" and @value="Come on in"]').click()
        self.browser.find_element_by_xpath(
            '//input[contains(@class, "confirmButton")]').click()
        

class GooglePage(ThirdPartyAuthPage):
    def fill_out_auth_form(self):
        email = self.browser.find_element_by_id('Email')
        password = self.browser.find_element_by_id('Passwd')
        
        email.click()
        email.send_keys(self.username)
        password.click()
        password.send_keys(self.password)
        
        return self
        
    def submit(self):
        self.browser.find_element_by_id('signIn').click()
        self.browser.find_element_by_xpath(
            '//button[@id="submit_approve_access" and not(@disabled)]').click()
        
