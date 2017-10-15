#file test_unittest.py
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
#        self.driver.maximize_window()
        #self.url = "https://campaign-manager.qa.zefr.com/iob/view-io/126/1748"
        self.url = "https://campaign-manager.qa.zefr.com/iob/view-io/126/1750"


    def moveiframe(self, mydriver, xpath=None, id=None):

       print("INSIDE MOVE IN IFRAME")
       driver = mydriver 

       if xpath:
          xpath = "//*[@class='package-tree-iframe']"
          driver.switch_to.frame(driver.find_element_by_xpath(xpath))
       print("Switched the frame")

       # IT OPENED THAT BUGGY MODAL
       some_elem = driver.find_element_by_css_selector('div#proposed-tab')
       print("some element on buggy modal")
       time.sleep(2)
       if some_elem:
          some_elem.click()
          print("clicked some element")
          driver.refresh()
          time.sleep(2)    


    def atest_2nd_iframe(self):
 
        try:
           driver = self.driver
           driver.get(self.url)
           self.assertIn("Zefr Accounts | Login", driver.title)
           elem = driver.find_element(By.CSS_SELECTOR, "input#session_email")
           elem.send_keys("qa.0@zefr.com")
           elem = driver.find_element_by_css_selector("input#session_password")
           elem.send_keys("T3stT3amR0cks0")
           elem = driver.find_element_by_css_selector("button#sign-in-button")
           elem.click()

           # Click on plus '+' element
           myele = driver.find_element_by_css_selector("button#iob-io-details-add-plan > i")
           myele.click()
           time.sleep(2)
           print("HERE IS PRINTING 1")
           new_plan_elem = driver.find_elements_by_xpath('//*[@data-name="iob-io-details-plan-tab"]')
           print("Name of new plan = {}".format(new_plan_elem))

           for item in new_plan_elem:
               print("Here is the plan text = {}".format(item.text))
               if item.text == "Untitled Plan 3":
                  item.click() # Go to New plan page
                  time.sleep(2)

           # Adding line item BUTTON
           lineitem = driver.find_element_by_xpath('//*[@ng-click="addLineItem()"]')
           lineitem.click()
           time.sleep(2)
           print("Here is lineitem")
           # Click on search packages BOX

           # Search Packages BUTTON
           new_modal = driver.find_element_by_xpath("//*[@data-name='iob-package-adder-modal-open']")
           new_modal.click()

           # NEW MODAL FOR PACKAGE SEARCH 
           name_ele = driver.find_element_by_xpath("//*[@id='iob-package-adder-modal-available-name-sort']")
           print("\n NAME ELEM = {}".format(name_ele.text))
           search_ava_elem = driver.find_element_by_xpath("//*[@id='iob-package-adder-modal-search']")
           search_ava_elem.send_keys("Animal Lover")
           click_ele = driver.find_element_by_xpath("//*[@data-name='iob-package-adder-modal-select']")
           click_ele.click()
           close_elem = driver.find_element_by_css_selector("div#iob-package-adder-modal-close i.fa-times")
           print("CLOSING THE MODAL")
           close_elem.click() 
           print("CLICKED CLOSING THE MODAL")


          # Click on pencil element to open an iframe
           pencil_modal = driver.find_element_by_xpath("//*[@data-name='iob-package-adder-customizer']")
           time.sleep(2)
           pencil_modal.click()
           print("Clicked on new frame")

           time.sleep(2)
           # SWITCH THE FRAME ======> 
  
           myxpath = "//*[@class='package-tree-iframe']"
           print("before new frame")
           
           result =  self.moveiframe(mydriver=driver, xpath=myxpath)
           print("After new frame = {}".format(result))

           """
           search_pkg_elem = driver.find_element_by_xpath('//*[@class="col-large"]//*[@class="edit-mode"]//*[@ng-model="searchStr"]')
           print("HERE is search pkg ")
           search_pkg_elem.send_keys("Animal Lovers")
           search_pkg_elem.send_keys(Keys.ENTER)
           """

           # click outside

           """
           # Click on pencil element 
           pencil_elem = driver.find_element_by_xpath('//*[@data-name="iob-package-adder-customizer"]')
           pencil_elem.click()

           driver.switch_to.frame(driver.find_element_by_xpath('//*[@placeholder="Filter Packages"]'))
           time.sleep(2)
           """

#           frame_ele = driver.find_element_by_xpath('//*[@placeholder="Filter Packages"]')
#           frame_ele.send_keys("SWATI")
#           time.sleep(3)
           

        finally:
           print("1 swati newelem")


    def test_iframe(self):
        try:
           driver = self.driver
           driver.get(self.url)
           #self.assertIn("Zefr Accounts | Login", driver.title)
           elem = driver.find_element(By.CSS_SELECTOR, "input#session_email")
           elem.send_keys("qa.0@zefr.com")
           elem = driver.find_element_by_css_selector("input#session_password")
           elem.send_keys("T3stT3amR0cks0")
           elem = driver.find_element_by_css_selector("button#sign-in-button")
           elem.click()

           # Start new element for CM page
           #newelem = driver.find_element_by_css_selector("div#iob-io-details-io-name")
           newelem = driver.find_elements_by_css_selector("div.plan-tab.ng-scope") #TITLE MENU
           print("swati newelem = {} \n".format(newelem))

           #CLICK ON menu TED(1)
           newelem[1].click()  # Ted(1)

           #ACCESS THE TED(1) MODAL - IFRAME
           loc_elem = driver.find_elements_by_css_selector("div.col-small select#iob-line-item-select-kpi-type")
           loc_elem[1].click()

           pencil_elem = driver.find_elements_by_xpath(u'//*[@ng-show="visibility.location"]//*[@data-name="geo-customizer"]')
           frame_elem = pencil_elem[1]
           print("iframe element = {}".format(frame_elem))
           frame_elem.click()
           time.sleep(2)

           # SWITCH TO IFRAME MODAL       
           driver.switch_to.frame(driver.find_element_by_xpath('//*[@class="geo-iframe"]'))

           # Making sure this is wrong page
           some_elem = driver.find_element_by_css_selector('div#completed-tab')
           print("some element = {}".format(some_elem))
           some_elem.click()
           print("clicked some element")
           driver.refresh() 
           time.sleep(2)



           #REPEATED CODE 
           #CLICK ON menu TED(1)
           # ======================================== # 
           newelem = driver.find_elements_by_css_selector("div.plan-tab.ng-scope") #TITLE MENU
           newelem[1].click()  # Ted(1)

           #ACCESS THE TED(1) MODAL - IFRAME
           loc_elem = driver.find_elements_by_css_selector("div.col-small select#iob-line-item-select-kpi-type")
           loc_elem[1].click() # KPI CLICK
           print("clicked on KPI")
           pencil_elem = driver.find_elements_by_xpath(u'//*[@ng-show="visibility.location"]//*[@data-name="geo-customizer"]')
           frame_elem = pencil_elem[1]
           print("2nd iframe element = {}".format(frame_elem))
           frame_elem.click() # PENCIL EDIT CLICK
           print("2nd pencil element = {}".format(frame_elem))
           time.sleep(2)
           driver.switch_to.frame(driver.find_element_by_xpath('//*[@class="geo-iframe"]'))

           # ======================================== # 

           some_elem = driver.find_element_by_css_selector('input#geo-tgt-search')
           some_elem.send_keys("Austin")
           some_elem.send_keys(Keys.ENTER)
            
           result_count = driver.find_element_by_css_selector(".result-count").text
           print("result = {}".format(result_count))
           search_result_elem = driver.find_element_by_xpath('//*[@id="search-results-panel"]')
           search_result_elem.click()
           list_elem = driver.find_elements_by_xpath('//*[@id="search-results-panel"]//*[@class="tgt-option"]') 
           first_elem = list_elem[1]
           first_elem.click()
           print("CLICKED 2ND SEARCH ELEMENT ")
           time.sleep(2)
           list_incl_elem = driver.find_elements_by_xpath('//*[@class="btn incl-btn"]') 
           first_include_elem = list_incl_elem[1] 
           first_include_elem.click()
           print("CLICKED 2ND INCLUDE ELEMENT ")

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

        finally:
           print("Test One" ) 


    def tearDown(self):
#        time.sleep(5)
#        self.driver.close()
        print("Closing the browser")


if __name__ == "__main__":
    unittest.main()
