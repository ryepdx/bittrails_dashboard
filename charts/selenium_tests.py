'''
Runs Selenium tests.
'''
from . import pages
from selenium_test import SeleniumTest

class ChartTests(SeleniumTest):
    def __init__(self, *args, **kwargs):
        super(ChartTests, self).__init__(*args, **kwargs)
        self.chart_page = pages.ChartPage(self.browser)
        
    def pre_auth(self):
        self.browser.get(self.app_url + self.chart_page.url)
        self.wait.until(lambda b: '/login?next=' in b.current_url, 
            self.browser.current_url)
            
    def post_auth(self):
        self.browser.get(self.app_url + self.chart_page.url)
        self.chart_page.random_option_from(self.chart_page.datastream).click()
        self.chart_page.random_option_from(self.chart_page.group_by).click()
        self.chart_page.random_option_from(self.chart_page.chart_type).click()
        self.chart_page.create_button.click()
        
        # And now we should see a chart!
        try:
            assert self.chart_page.has_chart
            
        # Or at least a "your data is being loaded" message.
        except Exception as e:
            assert self.chart_page.has_no_data
