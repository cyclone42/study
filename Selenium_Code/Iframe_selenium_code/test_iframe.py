#
# To execute : change to python 3.0 , python <filename> 
#
#


import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestExamples(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.url = "https://campaign-manager.qa.zefr.com/iob/view-io/126/1780"
        self.email = "qa.0@zefr.com"
        self.password = "T3stT3amR0cks0"


    def test_iframe(self):
        try:
           driver = self.driver
           driver.get(self.url)
           self.assertIn("ZEFR Accounts | Login", driver.title)
           elem = driver.find_element(By.CSS_SELECTOR, "input#session_email")
           elem.send_keys(self.email)
           elem = driver.find_element_by_css_selector("input#session_password")
           elem.send_keys(self.password)
           elem = driver.find_element_by_css_selector("button#sign-in-button")
           elem.click()

           # Start new element for CM page
           newelem = driver.find_elements_by_css_selector("div.plan-tab.ng-scope") #TITLE MENU

           #CLICK ON menu TestPlan 
           newelem[0].click() 

           # Move the focus to the element/pencil which has iframe
           loc_elem = driver.find_element_by_css_selector("div.col-small select#iob-line-item-select-kpi-type")
           loc_elem.click()

           pencil_elem = driver.find_elements_by_xpath(u'//*[@ng-show="visibility.location"]//*[@data-name="geo-customizer"]')
           frame_elem = pencil_elem[1]
           print("iframe element = {}".format(frame_elem))
           frame_elem.click()
           time.sleep(2)

           # SWITCH TO IFRAME MODAL       
           driver.switch_to.frame(driver.find_element_by_xpath('//*[@class="geo-iframe"]'))

           # ======================================== # 

           some_elem = driver.find_element_by_css_selector('input#geo-tgt-search')
           some_elem.send_keys("Austin")
           some_elem.send_keys(Keys.ENTER)
            
           search_result_elem = driver.find_element_by_xpath('//*[@id="search-results-panel"]')
           search_result_elem.click()
           list_elem = driver.find_elements_by_xpath('//*[@id="search-results-panel"]//*[@class="tgt-option"]') 
           first_elem = list_elem[1]
           first_elem.click()
           print("Clicked on 2nd element")
           time.sleep(2)
           list_incl_elem = driver.find_elements_by_xpath('//*[@class="btn incl-btn"]') 
           first_include_elem = list_incl_elem[1] 
           first_include_elem.click()
           print("Include 2nd element")

           # UNSELECT GEO TARGETS ELEMENTS
           selected_list = driver.find_elements_by_css_selector('div.tgt-option >span.tgt-included')
           excl_elem = driver.find_element_by_xpath("//*[contains(text(), 'United States')]")
           print("here is the exclued item text = {} ".format(excl_elem))
           time.sleep(2)
           excl_elem.click() 
           time.sleep(3)
           cancel_elem = driver.find_elements_by_xpath('//*[@class="btn remove-btn"]') 
           cancel_elem[0].click()
           time.sleep(4)

           # SAVE THE MODAL AT THE END AS SAVING CLOSES THE MODAL
           save_elem = driver.find_element_by_css_selector('button.btn-save')
           save_elem.click()
           print("===THE END =====")

        except:
           print("Unknown error ") 



    def tearDown(self):
        time.sleep(5)
        self.driver.close()
        print("Closing the browser")


if __name__ == "__main__":
    unittest.main()
