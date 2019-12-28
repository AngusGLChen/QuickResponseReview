'''
Created on 23 Mar 2019

@author: gche0022
'''

import time

def click_action(driver, xpath):
    element = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(3)