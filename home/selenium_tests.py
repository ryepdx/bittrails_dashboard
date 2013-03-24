'''
Runs Selenium tests.
'''
from . import pages
from auth import pages as auth_pages
from selenium_test import SeleniumTest

class LoginTests(SeleniumTest):
    def __init__(self, *args, **kwargs):
        super(LoginTests, self).__init__(*args, **kwargs)
        self.home_page = pages.HomePage(self.browser)
        self.login_page = pages.LoginPage(self.browser)
        self.twitter_page = auth_pages.TwitterPage(self.browser, self.wait,
            'bt_testuser', 'b1ttr41ls!!1!')
        
    def pre_auth(self):
        self.browser.get(self.app_url)
        self.wait.until(lambda b: b.current_url.endswith('/login'), 
            self.browser.current_url)
        
    def login(self):
        self.browser.get(self.app_url)
        self.wait.until(lambda b: b.title.startswith('Bit Trails'),
            self.browser.title)

        self.login_page.get_login_button().click()
        self.wait.until(lambda b: b.title.startswith('Twitter'),
            self.browser.title)
            
        assert self.browser.current_url.startswith(
            'https://api.twitter.com/oauth/')
        
        self.twitter_page.fill_out_auth_form().submit()
        self.wait.until(lambda b: b.title.startswith('Bit Trails'),
            self.browser.title)
        
    def auth(self):
        pass
        
    def post_auth(self):
        # Should redirect to /home now that we are authenticated.
        self.browser.get(self.app_url)
        self.wait.until(lambda b: b.current_url.endswith('/home'), 
            self.browser.current_url)

        # Should also show Twitter as connected now.
        self.home_page.find_on_list_of_connected_datastreams("Twitter")

class CustomDatastreamTests(SeleniumTest):
    DATASTREAM_URL = 'ryepdx.com/test.csv'
    DATASTREAM_NAME = 'number of widgets in a widget factory'
    
    def __init__(self, *args, **kwargs):
        super(CustomDatastreamTests, self).__init__(*args, **kwargs)
        self.home_page = pages.HomePage(self.browser)
        self.custom_page = pages.CustomDatastreamPage(self.browser)
    
    def pre_auth(self):
        # Should redirect us to /login.
        self.browser.get(self.app_url + '/custom_datastream')
        self.wait.until(lambda b: '/login?next=' in b.current_url, 
            self.browser.current_url)

    def post_auth(self):
        # Go to the homepage and wait for the custom datastream link to appear.
        self.browser.get(self.app_url)
        self.wait.until(lambda b: self.home_page.get_custom_datastream_link())
        
        # Click the custom datastream link.
        self.home_page.get_custom_datastream_link().click()
        self.wait.until(lambda b: b.current_url.endswith(
            self.custom_page.CUSTOM_DATASTREAM_URL), self.browser.current_url)
        
        # Fill out the custom datastream form.
        self.custom_page.fill_url(self.DATASTREAM_URL).fill_name(
            self.DATASTREAM_NAME).click_submit()
        self.wait.until(lambda b: b.current_url.endswith('/home'),
            self.browser.current_url)
        
        # Check for our custom datastream on the list of connected datastreams.
        self.home_page.find_on_list_of_connected_datastreams(
            self.DATASTREAM_NAME)
