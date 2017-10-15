#
# To execute : change to python +3.0 
#               python <filename>


import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class TestExamples(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        print("set up")
        self.url = "https://campaign-manager.stage.zefr.com/iob/view-io/293/633"

    # How to scroll to a hidden element
    def test_scroll_horizontally(self):
        print("Signed in sucessfully")
        try:
            driver = self.driver
            driver.get(self.url)
            print("Title: {}".format(driver.title))
            elem = driver.find_element(By.CSS_SELECTOR, "input#session_email")
            elem.send_keys("qa.0@zefr.com")
            elem = driver.find_element_by_css_selector("input#session_password")
            elem.send_keys("T3stT3amR0cks0")
            elem = driver.find_element_by_css_selector("button#sign-in-button")
            elem.click()
 
            print("Signed in sucessfully")
            time.sleep(2)
            # Click on plus 'Bumpers+PR ' element
            newele = driver.find_elements(By.XPATH, "//*[@data-name='iob-io-details-plan-tab']")[1]
            newele.click()
            age_elem = driver.find_element(By.XPATH, "//*[@ng-show='visibility.age']")
            age_elem.click()
            age_val = driver.find_element(By.XPATH, "//*[@data-name='iob-line-item-age-selected']") 
            print("age value is = {}".format(age_val.text))
 
            # Another way for making hidden value visible. Just look for that element 
            driver.execute_script("return arguments[0].scrollIntoView();", age_elem)

            # Trying to scroll vertical up 
            print("Trying to scroll vertical up") 
            driver.execute_script("window.scrollBy(0, -300);")

            time.sleep(5)

            # Trying to scroll Veritical Down
            print("Trying to scroll Vertical Down") 
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(5)

        except:
            print("Unknown error") 

    def tearDown(self):
        print("teardown") 
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
