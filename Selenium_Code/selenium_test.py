#file test_unittest.py
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import logging
logging.basicConfig(filename="log.txt", level=logging.INFO)


class TestExamples(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
#        self.driver.implicitly_wait(30)
        self.driver.maximize_window()

    def test_one(self):
        try:
           driver = self.driver
           driver.get("http://www.python.org")
           self.assertIn("Python", driver.title)
           elem = driver.find_element_by_name("q")
           elem.send_keys("documentation")
           elem.send_keys(Keys.RETURN)
#           assert "No results found." not in driver.page_source
        finally:
           logging.info("Test One Video: " )
		   
    def test_two(self):
        try:
           driver = self.driver
           driver.get("http://www.google.com")
           elem = driver.find_element_by_name("q")
           elem.send_keys("webdriver")
           elem.send_keys(Keys.RETURN)
        finally:
           	logging.info("Test Two Video: " )
#           	logging.info("Test Two Video: " + VIDEO_URL + driver.session_id)

#    def test_google_menu(self):
#        self.menu=self.driver.find_element_by_css_selector("a.gb_b[title$='apps']")
#        logging.info("HREF of google apps: ", self.menu.get_attribute("href"))
#        self.menu.click()
			
    def tearDown(self):
        self.driver.quit()
        logging.info("IQUIT")


if __name__ == "__main__":
    unittest.main()
