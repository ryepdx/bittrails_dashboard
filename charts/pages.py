import random
from page import Page

class ChartPage(Page):
    url = '/charts'
    
    def random_option_from(self, select):
        options = select.find_elements_by_tag_name("option")
        return options[random.randint(0, len(options)-1)]
        
    @property
    def datastream(self):
        return self.browser.find_element_by_name('datastream')
        
    @property
    def group_by(self):
        return self.browser.find_element_by_name('group_by')
        
    @property
    def chart_type(self):
        return self.browser.find_element_by_name('chart_type')
        
    @property
    def create_button(self):
        return self.browser.find_element_by_xpath('//input[@type="submit"]')
        
    @property
    def has_chart(self):
        return bool(self.browser.find_element_by_xpath(
            '//div[@id="chart"]/svg'))

    @property
    def has_no_data(self):
        return bool(self.browser.find_element_by_xpath(
            '//div[@id="no_data_warning"]'))
