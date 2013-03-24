'''
Runs Selenium tests.
'''
import home.pages
from . import pages
from selenium_test import SeleniumTest

class AuthTests(SeleniumTest):
    def __init__(self, *args, **kwargs):
        super(AuthTests, self).__init__(*args, **kwargs)
        self.home = home.pages.HomePage(self.browser)
        
        # Twitter is absent here because home.selenium_tests takes care of it.
        self.pages = {
            'foursquare': pages.FoursquarePage(self.browser, self.wait,
                'testuser@bittrails.com', password='b1ttr41ls'),
            'lastfm': pages.LastfmPage(self.browser, self.wait, 'bt_testuser'),
            'google': pages.GooglePage(self.browser, self.wait,
                'bittrails.testuser')
        }
            
    def post_auth(self):
        # Alright, let's authorize all the services!
        self.browser.get(self.app_url)
        
        for service in ["google", "foursquare", "lastfm"]:
            self.home.find_on_list_of_available_datastreams(service).click()
            self.pages[service].fill_out_auth_form().submit()
            assert self.home.find_on_list_of_connected_datastreams(service)
