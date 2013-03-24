import random
from page import Page

class BuffPage(Page):
    url = '/buffs'
    
    @property
    def has_history(self):
        return bool(self.browser.find_element_by_xpath(
            '//h1[contains(text(), "History")]'))
            
    @property
    def has_active(self):
        return bool(self.browser.find_element_by_xpath(
            '//h1[contains(text(), "Active")]'))
