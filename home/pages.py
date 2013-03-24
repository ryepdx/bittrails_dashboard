from page import Page

class LoginPage(Page):
    def get_login_button(self):
        return self.browser.find_element_by_id('loginButton')

            
class CustomDatastreamPage(Page):
    CUSTOM_DATASTREAM_URL = '/custom_datastream'
    
    def fill_url(self, url):
        self.browser.find_element_by_id("datastream_url").send_keys(url)
        return self
        
    def fill_name(self, name):
        self.browser.find_element_by_id("datastream_name").send_keys(name)
        return self
        
    def click_submit(self):
        return self.browser.find_element_by_xpath(
            '//form//input[@type="submit" and @class="button"]').click()

class HomePage(Page):
    def find_on_list_of_connected_datastreams(self, datastream):
        return self.browser.find_element_by_xpath(
            '//ul[@id="connectedServices"]/li[contains(text(), "%s")]' % (
            datastream.title()))
            
    def find_on_list_of_available_datastreams(self, datastream):
        return self.browser.find_element_by_xpath(
            '//ul[@id="availableServices"]/li/a[contains(text(), "%s")]' % (
            datastream.title()))
            
    def get_custom_datastream_link(self):
        return self.browser.find_element_by_xpath(
            '//a[@href="%s"]' % CustomDatastreamPage.CUSTOM_DATASTREAM_URL)
            
