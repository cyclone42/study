#file tet_unittest.py
import unittest
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging


logging.basicConfig(filename="log_selenium.txt", level=logging.INFO)
logger = logging.getLogger("Drag-Drop")


class TestExamples(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        #binary = FirefoxBinary('/Applications/Firefox.app/Contents/MacOS/firefox-bin')
        #self.driver = webdriver.Firefox(firefox_binary=binary, timeout=2)
        self.driver.implicitly_wait(1)
        self.driver.maximize_window()

    def test_drag_element(self):
        driver = self.driver
        driver.get("http://html5demos.com/drag")
        # hover on an element using action chain
        source_elem = driver.find_element_by_id("two")
        elem2_to_hover = ActionChains(driver).move_to_element(source_elem)
        elem2_to_hover.perform()

        #target_elem = driver.find_element_by_id("bin")
        target_elem = driver.find_element_by_css_selector("div#bin")
        elem_to_hover = ActionChains(driver).move_to_element(target_elem)
        elem_to_hover.perform()
        time.sleep(10)

        logger.info("source = {}, target = {} \n".format(source_elem.text, target_elem))
        elem1_to_hover = ActionChains(driver).drag_and_drop(source_elem, target_elem).perform()
        time.sleep(25)
        driver.refresh()
        #driver.refresh()
 

    def tearDown(self):
        self.driver.quit()
        logger.info("Tearing down the browser")
		   
if __name__ == "__main__":
    unittest.main()
