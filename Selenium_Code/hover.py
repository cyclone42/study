#file test_unittest.py
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging


logging.basicConfig(filename="log_selenium.txt", level=logging.INFO)
logger = logging.getLogger("Drag-Drop")


class TestExamples(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
#        self.driver.implicitly_wait(5)
        self.driver.maximize_window()

    def test_hover_on_element(self):
        driver = self.driver
        driver.get("http://html5demos.com/drag")
        logger.info("Here is the driver title = {}".format(driver.title))
#        self.assertIn("Python", driver.title)
        elem = driver.find_element_by_css_selector("header h1")
        self.assertIn(elem.text, "Drag and drop")
        # hover on an element using action chain
        drag_elem = driver.find_element_by_id("two")
        elem1_to_hover = ActionChains(driver).move_to_element(drag_elem)
        elem1_to_hover.perform()
        time.sleep(2)

        drag_elem2 = driver.find_element_by_id("four")
        elem2_to_hover = ActionChains(driver).move_to_element(drag_elem2)
        elem2_to_hover.perform()
        time.sleep(2)
#       assert "No results found." not in driver.page_source
        #logging.info("Test One Video: " )

    def test_drag_element(self):
        driver = self.driver
        driver.get("http://html5demos.com/drag")
        # hover on an element using action chain
        source_elem = driver.find_element_by_id("two")
        target_elem = driver.find_element_by_id("bin")
        logger.info("source = {}, targe = {} \n".format(source_elem, target_elem))
        elem1_to_hover = ActionChains(driver).drag_and_drop(source_elem, target_elem).perform()
        time.sleep(35)


    def tearDown(self):
        self.driver.quit()
        logging.info("IQUIT")
		   
if __name__ == "__main__":
    unittest.main()
