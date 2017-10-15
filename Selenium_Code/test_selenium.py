#file test_unittest.py
#
# To execute : change to python 3.0 , python <filename> 
#
#
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logging.basicConfig(filename="log.txt", level=logging.INFO)



class TestExamples(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.url = "https://campaign-manager.qa.zefr.com/iob/view-io/126/1748"



    def test_iframe(self):
        try:
           driver = self.driver
           driver.get(self.url)
           print("swati title = {}".format(driver.title))
           self.assertIn("Zefr Accounts | Login", driver.title)
           elem = driver.find_element(By.CSS_SELECTOR, "input#session_email")
           elem.send_keys("qa.0@zefr.com")
           #elem.send_keys(Keys.RETURN)
           driver.implicitly_wait(10)
           elem = driver.find_element_by_css_selector("input#session_password")
           elem.send_keys("T3stT3amR0cks0")
           elem = driver.find_element_by_css_selector("button#sign-in-button")
           elem.click()

           # Start new element for CM page
           newelem = driver.find_element_by_css_selector("div#iob-io-details-io-name")
           driver.implicitly_wait(10)
           newelem = driver.find_elements_by_css_selector("div.plan-tab.ng-scope") #TITLE MENU
           print("swati newelem = {} \n".format(newelem))
           driver.implicitly_wait(20)

           #CLICK ON TED(1)
           second_elem = newelem[1]  #ted(1)
           second_elem.click()

           #ACCESS THE TED(1) MODAL - IFRAME
           action_driver = ActionChains(driver)
           loc_elem = driver.find_elements_by_css_selector("div.col-small select#iob-line-item-select-kpi-type")
           loc_elem[1].click()
         
           # Access the location pencil button
           pencil_elem = driver.find_elements_by_xpath(u'//*[@ng-show="visibility.location"]//*[@data-name="geo-customizer"]')
           print("Location pencil element = {}".format(pencil_elem))
           time.sleep(2)
           pencil_elem
        
           # Move to iframe 
           time.sleep(3)
           iframe_elem = pencil_elem[1]
           print("iframe element = {}".format(iframe_elem))
           iframe_elem.click()

           """
           driver.switch_to_frame(iframe_elem) 

           time.sleep(2)
           # CLICK ON SEARCH FOR GEO TARGETS
           in_iframe = driver.find_element_by_css_selector("input#geo-tgt-search.search")
           in_iframe.send_keys("90230") 
           time.sleep(2)
           driver.implicitly_wait(30)
#           driver.switch_to.defaultContent();
           """
        finally:
           logging.info("Test One Video: " ) 




    def atest_kpi(self):
        try:
           driver = self.driver
           driver.get(self.url)
           print("swati title = {}".format(driver.title))
           self.assertIn("Zefr Accounts | Login", driver.title)
           elem = driver.find_element(By.CSS_SELECTOR, "input#session_email")
           elem.send_keys("qa.0@zefr.com")
           #elem.send_keys(Keys.RETURN)
           driver.implicitly_wait(10)
           elem = driver.find_element_by_css_selector("input#session_password")
           elem.send_keys("T3stT3amR0cks0")
           elem = driver.find_element_by_css_selector("button#sign-in-button")
           elem.click()

           # Start new element for CM page
           newelem = driver.find_element_by_css_selector("div#iob-io-details-io-name") 
           driver.implicitly_wait(10)
           newelem = driver.find_elements_by_css_selector("div.plan-tab.ng-scope") #TITLE MENU 
           print("swati newelem = {} \n".format(newelem))
           driver.implicitly_wait(20)
  
           #CLICK ON TED(1)
           second_elem = newelem[1]  #ted(1)
           second_elem.click()

           #ACCESS THE TED(1) MODAL - IFRAME
           action_driver = ActionChains(driver)

           # First column ; KPI TYPE 
           loc_elem = driver.find_elements_by_css_selector("div.col-small select#iob-line-item-select-kpi-type")
           print("package pencil element -packages {}".format(loc_elem))

#           wait = WebDriverWait(driver, 10) 
#           loc_elem = driver.find_elements(By.CSS_SELECTOR, "i[@data-name='geo-customizer']")
#           loc_elem = driver.find_elements_by_css_selector("div.fake-tbody div.col-small i.fa.fa-pencil.ng-scope")
           print("Location pencil element = {}".format(loc_elem))

           loc_elem[0].click() # second ROW : CLICK ON LINE ITEM NAME - ted 
           driver.implicitly_wait(30)
        finally:
           logging.info("Test One Video: " )
			 

    def tearDown(self):
        time.sleep(3)
        self.driver.quit()
#        self.driver.close()
        logging.info("IQUIT")


if __name__ == "__main__":
    unittest.main()



"""
    def test_one(self):
        try:
           driver = self.driver
           driver.get(self.url)
           print("swati title = {}".format(driver.title))
           self.assertIn("Zefr Accounts | Login", driver.title)
           elem = driver.find_element(By.CSS_SELECTOR, "input#session_email")
           elem.send_keys("qa.0@zefr.com")
           #elem.send_keys(Keys.RETURN)
           driver.implicitly_wait(10)
           elem = driver.find_element_by_css_selector("input#session_password")
           elem.send_keys("T3stT3amR0cks0")
           elem = driver.find_element_by_css_selector("button#sign-in-button")
           elem.click()

           # Start new element for CM page
           newelem = driver.find_element_by_css_selector("div#iob-io-details-io-name")
           driver.implicitly_wait(10)
           newelem = driver.find_elements_by_css_selector("div.plan-tab.ng-scope") #TITLE MENU
           print("swati newelem = {} \n".format(newelem))
           driver.implicitly_wait(20)
           second_elem = newelem[1]  #ted(1)
           second_elem.click()
           action_driver = ActionChains(driver)
           #loc_elem = driver.find_element_by_css_selector("div.col-small i.fa-pencil.ng-scope") # location pencil
           loc_elem = driver.find_element_by_css_selector("div.col-small i.fa-pencil.ng-scope") # location pencil
#           loc_elem.location_once_scrolled_into_view

#           loc_elem = driver.find_element_by_id("test_swati")
           print("dir LOC ELEM {}".format(dir(loc_elem)))

           action_driver.move_to_element(loc_elem).perform()


#           elemlist = driver.find_elements(By.CSS_SELECTOR, "div.package-adder.ng-pristine div.ng-binding.ng-scope")
#           third_elem = elemlist[2]
#           pencil_elem = driver.find_element(By.CSS_SELECTOR,"i.fa.fa-pencil.ng-scope")
#           loc_elem = driver.find_element_by_css_selector("div.col-small i.fa-pencil.ng-scope") # location pencil
#           print("SWATI loc elem {}".format(loc_elem))
#           loc_elem.click()

           driver.implicitly_wait(30)
        finally:
           logging.info("Test One Video: " )



"""
