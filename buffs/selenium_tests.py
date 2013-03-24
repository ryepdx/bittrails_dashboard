'''
Runs Selenium tests.
'''
from . import pages
from selenium_test import SeleniumTest

class BuffTests(SeleniumTest):
    def __init__(self, *args, **kwargs):
        super(BuffTests, self).__init__(*args, **kwargs)
        self.buff_page = pages.BuffPage(self.browser)
        
    def pre_auth(self):
        self.browser.get(self.app_url + self.buff_page.url)
        self.wait.until(lambda b: '/login?next=' in b.current_url, 
            self.browser.current_url)
            
    def post_auth(self):
        self.browser.get(self.app_url + self.buff_page.url)
        assert self.buff_page.has_active
        assert self.buff_page.has_history
