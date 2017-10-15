from datetime import date
import re
import logging
from time import sleep, time

from behave import (step, use_step_matcher)
from behave.model import Scenario as scenario
from ngSe import By
from selenium.common import exceptions as SELENIUM_EXCEPTIONS
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement as WE
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.functional.features.environment import browser
from tests.functional.static_definitions import element_ids, element_names
from tests.functional.features.fixture_data import fixtureDict
from zc_test_framework.fixture_manager import FixtureManager


BOTTOM_OF_ASC_TABLE = ['N/A']
SAVE_TEXT_KEYWORD = 'SAVED_TEXT'
SAVED_NUMBER_KEYWORD = 'SAVED_NUMBER'
TOP_OF_ASC_TABLE = ['Artist Unavailable', 'Title Unavailable']

use_step_matcher('re')
logger = logging.getLogger("Test_framework")


def wait_for_table_element(table, row, name, clause=By.XPATH):
    element = browser.wait_for(
        '//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
            element_ids[table], row, element_names[name]),
        by=clause
    )
    return element


def wait_for_element_to_have_at_least_one_row(
        locator, timeout=(time() + 30), interval=2):
    """Returns True if a table/list has more than one row.
    Before interacting with a table/list, we don't just want it
    to be on screen, we also want there to be at least one row.
    Args:
        locator (string): format of u'//*[@id="table"]/tbody/tr'
        timeout (float): should be an int plus time(); format of 1459891846.08
        interval (int): format of 2
    """
    error_instance = None
    while time() < timeout:
        try:
            row_count = len(browser.find_elements_by_xpath(locator))
        except SELENIUM_EXCEPTIONS.NoSuchElementException as e:
            error_instance = e
            sleep(interval)
        else:
            if row_count >= 1:
                return True
    if error_instance:
        raise error_instance
    assert False, 'Number of rows: {}'.format(row_count)


def wait_for_element_to_be_in_DOM(
        locator, timeout=(time() + 30), interval=2):
    """Returns element once it's located on the DOM.
    Before interacting with an element we want to make sure it's in the DOM.
    Args:
        locator (string): format of u'//*[@id="element"]'
        timeout (float): should be an int plus time(); format of 1459891846.08
        interval (int): format of 2
    """
    error_instance = None
    element = None
    while time() < timeout:
        try:
            element = browser.wait_for(locator, By.XPATH)
        except (SELENIUM_EXCEPTIONS.NoSuchElementException,
                SELENIUM_EXCEPTIONS.StaleElementReferenceException,
                SELENIUM_EXCEPTIONS.ElementNotVisibleException) as e:
            error_instance = e
            sleep(interval)
        else:
            return element
    if error_instance:
        raise error_instance
    assert False, 'Element: {} \n XPATH: {}'.format(element, locator)


def wait_for_element_to_be_clickable_then_click(
        element, timeout=(time() + 30), interval=2, locator=None):
    """Returns once element is clicked successfully. Retries for a specified
    time if a common selenium expection occurs and calls
    wait_for_element_to_be_in_DOM function if there's an exception and locator
    is passed into the function.
    Args:
        element (object): Ex: WebElement object
        timeout (float): should be an int plus time(); Ex: 1459891846.08
        interval (int): in seconds Ex: 2
    """
    error_instance = None
    while time() < timeout:
        try:
            # NOTE: sometimes is_enabled() gives a false positive
            element.is_enabled()
            element.click()
        except (SELENIUM_EXCEPTIONS.NoSuchElementException,
                SELENIUM_EXCEPTIONS.StaleElementReferenceException,
                SELENIUM_EXCEPTIONS.ElementNotVisibleException,
                SELENIUM_EXCEPTIONS.WebDriverException) as e:
            error_instance = e
            sleep(interval)
            if locator is not None:
                element = wait_for_element_to_be_in_DOM(
                    locator, timeout, interval)
        else:
            return
    if error_instance:
        raise error_instance
    assert False, 'Element not clickable'


def set_wait_times(total_wait, interval):
    """Returns total wait and interval as a tuple.
    If total wait and/or interval isn't an empty string change it to an int;
    if total wait and/or interval is an empty string change it to default ints
    Args:
        total_wait (string): format of "60"
        interval (string): format of "1"
    """
    if total_wait:
        total_wait = int(total_wait)
    else:
        total_wait = 60
    if interval:
        interval = int(interval)
    else:
        interval = 1
    return (total_wait, interval)


def check_text_in_element(element, text):
    """Returns -1 if text is not in element
    Returns > -1 if text is in element
    Returns elem_text for use in scenario debug statement
    """
    string_text = element.text
    string_value = element.get_attribute('value')
    if not string_value:
        elem_text = string_text
    elif not string_text:
        elem_text = string_value
    else:
        elem_text = string_value + string_text
    return elem_text.find(text.strip()), elem_text


# Test automation framework step for injecting data in amg DB
@step(u'(?:(?:I|the user) set the testing framework with attribute table$)')
def generate_fixture(context):

    if context.fixture_manager:
        manager = context.fixture_manager
    else:
        manager = FixtureManager()
        context.fixture_manager = manager

    for row in context.table:
        zipped_table = {}

        """Creating a list of factory attributes and value"""
        factory_attr = str(row['attribute']).split(',')
        factory_val = str(row['value']).split(',')
        factory_name = str(row['factory'])

        while '' in factory_attr:
            factory_attr.remove('')

        while '' in factory_val:
            factory_val.remove('')

        """Verify # of attributes are same as # of values"""
        if len(factory_attr) != len(factory_val):
            logger.error(
                "AssertionError: Number of attributes {} are not equal to "
                    "equal number of values {} given.".format(len(
                        factory_attr), len(factory_val)))
            raise AssertionError

        for key, val in zip(factory_attr, factory_val):
            zipped_table[key.strip()] = val.strip()

        if factory_name not in fixtureDict.keys():
            logger.error(
                "KeyError: factory name {} does not exist in fixture "
                    "dictionary.".format(factory_name))
            raise KeyError

        logger.info(
           "Factory name '{}' and user given attributes '{}'.".format(
               factory_name, zipped_table))

        """Importing class dynamically through this"""
        fixture_path_lst = fixtureDict[factory_name].split(".")
        fixture_pkg = __import__(fixture_path_lst[0] + "." + fixture_path_lst[1])
        fixture_file = getattr(fixture_pkg, fixture_path_lst[1])
        fixture_cls = getattr(fixture_file, fixture_path_lst[2])
        logger.debug("Fixture class is {}.".format(fixture_cls))

        manager.setup(fixture_cls, zipped_table)


# navigation
@step(u'(?:(?:I|the user) go to "([^"]*)"$)')
def user_goes_to(context, page_name):
    browser.navigate(page_name)


@step(u'(?:(?:I|the user) navigate to "([^"]*)"$)')
def user_goes_to_url(context, page_name):
    browser.goto(page_name)


# fill
@step(
    u'(?:(?:I|the user) fill the: "([^"]*)", with "([^"]*)"(?:(?:, wait'
    '(?:(?: for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def user_fills(context, element_id, text, total_wait, interval):
    if (text == SAVE_TEXT_KEYWORD):
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]'.format(element_ids[element_id])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)
    browser.fill(element_ids[element_id], text, by=By.ID)


@step(
    u'(?:(?:I|the user) fill the: "([^"]*)", with the json (\[.*\])'
    '(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def user_fills_with_json(context, element_id, json, total_wait, interval):
    if (json == SAVE_TEXT_KEYWORD):
        json = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]'.format(element_ids[element_id])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)
    browser.fill(element_ids[element_id], json, by=By.ID)


@step(
    u'(?:(?:I|the user) fill the: "([^"]*)", in row: (\d+), in the: '
    '"([^"]*)", with "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?),'
    ' interval: (\d+) second(?:s?))?)$)')
def fill_element_within_repeated_div(
        context, item, row, name, text, total_wait, interval):
    if (text == SAVE_TEXT_KEYWORD):
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
        element_names[name], row, element_names[item])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)
    browser.fill(locator, text, By.XPATH)


@step(
    u'(?:(?:I|the user) fill the: "([^"]*)", in row: (\d+), in column:'
    ' (\d+), in the table: "([^"]*)", with "([^"]*)"(?:(?:, wait(?:(?: for)?):'
    ' (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def fill_element_in_row_in_column_in_table(
        context, name, row, column, table, text, total_wait, interval):
    if (text == SAVE_TEXT_KEYWORD):
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]/td[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, column, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)
        browser.fill(locator, text, By.XPATH)


@step(
    u'(?:(?:I|the user) fill the: "([^"]*)", in row: (\d+), in the table:'
    ' "([^"]*)", with "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+)'
    ' second(?:s?), interval: (\d+) second(?:s?))?)$)')
def fill_element_within_table(
        context, name, row, table, text, total_wait, interval):
    if (text == SAVE_TEXT_KEYWORD):
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)
        browser.fill(locator, text, By.XPATH)


@step(
    u'(?:(?:I|the user) fill the: "([^"]*)", in row: (\d+), '
    'with "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), '
    'interval: (\d+) second(?:s?))?)$)')
def fill_from_list_of_elements(
        context, item, row, text, total_wait, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    row = int(row)
    if item in element_names:
        locator = u'//*[@data-name="{}"]'.format(element_names[item])
    else:
        locator = u'//*[@id="{}"]'.format(element_ids[item])
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        elem_list = browser.find_elements_by_xpath(locator)
        element = elem_list[row - 1]
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)
    browser._fill(element, text, By.XPATH)


@step(
    u'(?:(?:I|the user) fill the input for the angucomplete: "([^"]*)", in '
    'row: (\d+), with "([^"]*)"(?:(?:, wait(?:(?: for)?):'
    ' (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def fill_element_within_angucomplete(
        context, name, row, text, total_wait, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"]//input'.format(
        element_names[name])
    row = int(row)
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        elem_list = browser.find_elements_by_xpath(locator)
        wait_for_element_to_be_clickable_then_click(
            elem_list[row - 1], timeout, interval, locator)
        browser._fill(elem_list[row - 1], text, By.XPATH)


# send
@step(u'(?:(?:I|the user) send the key(?:s?): "([^"]*)", to the page$)')
def send_keys_to_page(context, keys):
    if (keys == 'LEFT_ARROW'):
        keys = Keys.ARROW_LEFT
    elif (keys == 'RIGHT_ARROW'):
        keys = Keys.ARROW_RIGHT
    elif (keys == 'UP_ARROW'):
        keys = Keys.ARROW_UP
    elif (keys == 'DOWN_ARROW'):
        keys = Keys.ARROW_DOWN
    ActionChains(browser).send_keys(keys).perform()


@step(
    u'(?:(?:I|the user) send the (delete|enter) key to: "([^"]*)", times:'
    ' (\d+)(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def send_special_keys_to_element(
        context, key_type, element, num, total_wait, interval):
    num = int(num)
    if (key_type == 'delete'):
        key = Keys.BACK_SPACE
    elif (key_type == 'enter'):
        key = Keys.ENTER
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]'.format(element_ids[element])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    for i in range(num):
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)
        element.send_keys(key)


@step(
    u'(?:(?:I|the user) send the key(?:s?): "([^"]*)", to the page, times:'
    ' (\d+)(?:(?:, interval (\d+) second(?:s?))?)$)')
def send_keys_to_page_multiple_times(context, keys, num, interval):
    num = int(num)
    if interval:
        interval = int(interval)
    else:
        interval = 0
    if (keys == 'LEFT_ARROW'):
        keys = Keys.ARROW_LEFT
    elif (keys == 'RIGHT_ARROW'):
        keys = Keys.ARROW_RIGHT
    elif (keys == 'UP_ARROW'):
        keys = Keys.ARROW_UP
    elif (keys == 'DOWN_ARROW'):
        keys = Keys.ARROW_DOWN
    elif (keys == 'delete'):
        keys = Keys.BACK_SPACE
    elif (keys == 'enter'):
        keys = Keys.ENTER

    for i in range(num):
        ActionChains(browser).send_keys(keys).perform()
        sleep(interval)


@step(
    u'(?:(?:I|the user) send the (delete|enter) key to: "([^"]*)", in row:'
    ' (\d+), in the: "([^"]*)", times: (\d+)(?:(?:, wait(?:(?: for)?): (\d+)'
    ' second(?:s?), interval: (\d+) second(?:s?))?)$)')
def send_special_keys_to_element_within_repeated_div(
        context, key, item, row, name, num, total_wait, interval):
    num = int(num)
    if (key == 'delete'):
        key = Keys.BACK_SPACE
    elif (key == 'enter'):
        key = Keys.ENTER
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
        element_names[name], row, element_names[item])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    for i in range(num):
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)
        element.send_keys(key)


@step(
    u'(?:(?:I|the user) send the (delete|enter) key to the: "([^"]*)",'
    ' in row: (\d+), in the table: "([^"]*)", times: (\d+)(?:(?:, wait(?:(?:'
    ' for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def send_special_keys_to_element_within_table(
        context, key, name, row, table, num, total_wait, interval):
    num = int(num)
    if (key == 'delete'):
        key = Keys.BACK_SPACE
    elif (key == 'enter'):
        key = Keys.ENTER
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        for i in range(num):
            wait_for_element_to_be_clickable_then_click(
                element, timeout, interval, locator)
            element.send_keys(key)


@step(
    u'(?:(?:I|the user) send the (delete|enter) key to the: "([^"]*)", in row:'
    ' (\d+), in column: (\d+), in the table: "([^"]*)", times: (\d+)(?:(?:, '
    'wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def send_special_keys_to_element_within_repeated_div_in_table(
        context, key, name, row, column, table, num, total_wait, interval):
    num = int(num)
    if (key == 'delete'):
        key = Keys.BACK_SPACE
    elif (key == 'enter'):
        key = Keys.ENTER
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]/td[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, column, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        for i in range(num):
            wait_for_element_to_be_clickable_then_click(
                element, timeout, interval, locator)
            element.send_keys(key)


@step(
    u'(?:(?:I|the user) send the (delete|enter) key to: "([^"]*)", in row:'
    ' (\d+), times: (\d+)(?:(?:, wait(?:(?: for)?): (\d+)'
    ' second(?:s?), interval: (\d+) second(?:s?))?)$)')
def send_special_keys_to_list_of_elements(
        context, key, item, row, num, total_wait, interval):
    num = int(num)
    row = int(row)
    if (key == 'delete'):
        key = Keys.BACK_SPACE
    elif (key == 'enter'):
        key = Keys.ENTER
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    if item in element_names:
        locator = u'//*[@data-name="{}"]'.format(element_names[item])
    else:
        locator = u'//*[@id="{}"]'.format(element_ids[item])
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        elem_list = browser.find_elements_by_xpath(locator)
        element = elem_list[row - 1]
    for i in range(num):
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)
        element.send_keys(key)


@step(
    u'(?:(?:I|the user) send the (delete|enter) key to the angucomplete'
    ' input: "([^"]*)", in row: (\d+), times: (\d+)(?:(?:, '
    'wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def send_special_keys_to_angucomplete(
        context, key, name, row, num, total_wait, interval):
    num = int(num)
    if (key == 'delete'):
        key = Keys.BACK_SPACE
    elif (key == 'enter'):
        key = Keys.ENTER
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"]//input'.format(
        element_names[name])
    row = int(row)
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        elem_list = browser.find_elements_by_xpath(locator)
        for i in range(num):
            wait_for_element_to_be_clickable_then_click(
                elem_list[row - 1], timeout, interval, locator)
            elem_list[row - 1].send_keys(key)


@step(u'(?:(?:I|the user) switch focus to the: (\d+), window$)')
def change_window_focus(context, window):
    window_list = browser.window_handles
    assert len(window_list) >= int(window), \
        "Expected >= {} windows opened, actual: {}".format(
            window, len(window_list))
    browser.switch_to_window(window_list[int(window) - 1])


# Save
@step(
    u'(?:(?:I|the user) save the text from the: "([^"]*)"(?:(?:, wait(?:(?:'
    ' for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def save_text_from_object(context, element, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    if element in element_names:
        locator = u'//*[@data-name="{}"]'.format(element_names[element])
    else:
        locator = u'//*[@id="{}"]'.format(element_ids[element])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    scenario.saved_text = element.text
    if element.get_attribute('value'):
        scenario.saved_text += element.get_attribute('value')


@step(
    u'(?:(?:I|the user) save the text from the: "([^"]*)", in the: '
    '"([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?),'
    ' interval: (\d+) second(?:s?))?)$)')
def save_text_from_named_element(context, name, elem, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]//*[@data-name="{}"]'.format(
        element_ids[elem], element_names[name])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    scenario.saved_text = element.text


@step(
    u'(?:(?:I|the user) save the text from the: "([^"]*)", in row: (\d+),'
    ' in the table: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?),'
    ' interval: (\d+) second(?:s?))?)$)')
def save_text_from_table_element(
        context, name, row, table, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        scenario.saved_text = element.text
        if element.get_attribute('value'):
            scenario.saved_text += element.get_attribute('value')


@step(
    u'(?:(?:I|the user) save the text from the: "([^"]*)", in row: (\d+),'
    ' in the list: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?),'
    ' interval: (\d+) second(?:s?))?)$)')
def save_text_from_list_element(
        context, name, row, list_id, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    list_rows_locator = u'//*[@id="{}"]/li'.format(element_ids[list_id])
    locator = u'//*[@id="{}"]/li[{}]//*[@data-name="{}"]'.format(
        element_ids[list_id], row, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            list_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        string_text = element.text
        string_value = element.get_attribute('value')
        if not string_value:
            elem_text = string_text
        elif not string_text:
            elem_text = string_value
        else:
            elem_text = string_value + string_text

        scenario.saved_text = elem_text


@step(
    u'(?:(?:I|the user) save the text from row: (\d+), in dropdown: '
    '"([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def save_text_from_dropdown(context, row, dropdown, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]/option[{}]'.format(element_ids[dropdown], row)
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    scenario.saved_text = element.text


@step(
    u'(?:(?:I|the user) save the text from the: (\d+), option from the: '
    '"([^"]*)" dropdown, in row: (\d+), in the: "([^"]*)"(?:(?:, wait(?:(?:'
    ' for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def save_text_from_dropdown_within_repeated_div(
        context, option, item, row, name, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"][{}]' \
        '//*[@data-name="{}"]/option[{}]'.format(
            element_names[name], row, element_names[item], option)
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    scenario.saved_text = element.text


@step(
    u'(?:(?:I|the user) save the number of rows in the table: "([^"]*)"'
    '(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def save_number_of_rows_in_table(context, table, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        scenario.saved_number = len(browser.find_elements_by_xpath(
            table_rows_locator))


@step(
    u'(?:(?:I|the user) save the number of rows in the list: "([^"]*)"'
    '(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def save_number_of_rows_in_list(context, element_id, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    list_rows_locator = u'//*[@id="{}"]/li'.format(element_ids[element_id])
    if wait_for_element_to_have_at_least_one_row(
            list_rows_locator, timeout, interval):
        scenario.saved_number = len(browser.find_elements_by_xpath(
            list_rows_locator))


@step(
    u'(?:(?:I|the user) save the text from the: "([^"]*)", in row: (\d+), in'
    ' the: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?),'
    ' interval: (\d+) second(?:s?))?)$)')
def save_text_within_repeated_div(
        context, item, row, name, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
        element_names[name], row, element_names[item])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    scenario.saved_text = element.text
    if element.get_attribute('value'):
        scenario.saved_text += element.get_attribute('value')


@step(
    u'(?:(?:I|the user) save the text from the: "([^"]*)", in row: (\d+), '
    '(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: '
    '(\d+) second(?:s?))?)$)')
def save_text_list_of_elements(
        context, item, row, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    row = int(row)
    if item in element_names:
        locator = u'//*[@data-name="{}"]'.format(element_names[item])
    else:
        locator = u'//*[@id="{}"]'.format(element_ids[item])
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        elem_list = browser.find_elements_by_xpath(locator)
        element = elem_list[row - 1]
    scenario.saved_text = element.text
    if element.get_attribute('value'):
        scenario.saved_text += element.get_attribute('value')


@step(
    u'(?:(?:I|the user) save the text from the angucomplete'
    ' input: "([^"]*)", in row: (\d+)(?:(?:, wait(?:(?: for)?):'
    ' (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def save_text_from_angucomplete(
        context, name, row, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"]//input'.format(
        element_names[name])
    row = int(row)
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        elem_list = browser.find_elements_by_xpath(locator)
        element = elem_list[row - 1]
        scenario.saved_text = element.text
        if element.get_attribute('value'):
            scenario.saved_text += element.get_attribute('value')


@step(
    u'(?:(?:I|the user) save the text from the: "([^"]*)", in row: (\d+),'
    ' in column: (\d+), in the table: "([^"]*)"(?:(?:, wait(?:(?: for)?):'
    ' (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def save_text_from_element_in_row_in_column_in_table(
        context, name, row, column, table, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]/td[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, column, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        scenario.saved_text = element.text
        if element.get_attribute('value'):
            scenario.saved_text += element.get_attribute('value')


# Click
@step(
    u'(?:(?:I|the user) click the: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+)'
    ' second(?:s?), interval: (\d+) second(?:s?))?)$)')
def user_clicks_clickable(context, element_id, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]'.format(element_ids[element_id])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", expecting: "([^"]*)"(?:(?:, wait'
    '(?:(?: for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def user_clicks_clickable_expecting(
        context, element_id, expect, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]'.format(element_ids[element_id])
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    # TODO: add clickable logic
    browser.click(
        element_ids[element_id],
        by=By.ID,
        wait_for=expect,
        wait_for_by=By.ID
    )


@step(
    u'(?:(?:I|the user) click the row: (\d+), in the table: "([^"]*)"(?:(?:, '
    'wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def click_table_row(context, row, table, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]'.format(element_ids[table], row)
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the row: (\d+), in the list: "([^"]*)"(?:(?:, '
    'wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def click_list_item(context, row, list_id, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    list_rows_locator = u'//*[@id="{}"]/li'.format(element_ids[list_id])
    locator = u'//*[@id="{}"]/li[{}]'.format(element_ids[list_id], row)
    if wait_for_element_to_have_at_least_one_row(
            list_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in row: (\d+), in the'
    ' table: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?),'
    ' interval: (\d+) second(?:s?))?)$)')
def wait_then_click_name_in_row_in_table(
        context, name, row, table, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in the table: "([^"]*)", that'
    ' contains the text: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+)'
    ' second(?:s?), interval: (\d+) second(?:s?))?)$)')
def click_name_in_table_by_text(
        context, name, table, text, total_wait, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    contains = None
    assert wait_for_element_to_have_at_least_one_row(
        table_rows_locator, timeout)
    while time() < timeout:
        table_list = browser.find_elements_by_xpath(table_rows_locator)
        for row in range(len(table_list)):
            locator = u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                element_ids[table], row + 1, element_names[name])
            try:
                element = browser.wait_for(locator, By.XPATH)
            # some tables wont have the desired element in all rows
            except (SELENIUM_EXCEPTIONS.NoSuchElementException,
                    SELENIUM_EXCEPTIONS.StaleElementReferenceException,
                    SELENIUM_EXCEPTIONS.ElementNotVisibleException):
                    continue
            contains, elem_text = check_text_in_element(element, text)
            if contains > -1:
                wait_for_element_to_be_clickable_then_click(
                    element, timeout, interval, locator)
                return
        sleep(interval)
    assert False, 'Text in step: {} is not in table'.format(
        text)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in row: (\d+), in column:'
    ' (\d+), in the table: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+)'
    ' second(?:s?), interval: (\d+) second(?:s?))?)$)')
def click_named_table_element_in_row_in_column(
        context, name, row, column, table, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    locator = u'//*[@id="{}"]/tbody/tr[{}]/td[{}]//*[@data-name="{}"]'.format(
        element_ids[table], row, column, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in row: (\d+), in the list: '
    '"([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def click_named_list_item(context, name, row, list_id, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    list_rows_locator = u'//*[@id="{}"]/li'.format(element_ids[list_id])
    # this is a hack to get pagination clicking to work for amg
    if name == "page number":
        locator = u'//*[@id="{}"]/li[{}]/a[@class="ng-binding"]'.format(
            element_ids[list_id], row)
    else:
        locator = u'//*[@id="{}"]/li[{}]//*[@data-name="{}"]'.format(
            element_ids[list_id], row, element_names[name])
    if wait_for_element_to_have_at_least_one_row(
            list_rows_locator, timeout, interval):
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in the last row in the table: '
    '"([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def click_last_named_table_element(context, name, table, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    table_rows_locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    if wait_for_element_to_have_at_least_one_row(
            table_rows_locator, timeout, interval):
        table_length = len(browser.find_elements_by_xpath(table_rows_locator))
        locator = u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
            element_ids[table], table_length, element_names[name])
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in the last row in the list: '
    '"([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def click_last_named_list_item(context, name, list_id, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    list_rows_locator = u'//*[@id="{}"]/li'.format(element_ids[list_id])
    if wait_for_element_to_have_at_least_one_row(
            list_rows_locator, timeout, interval):
        list_length = len(browser.find_elements_by_xpath(list_rows_locator))
        locator = u'//*[@id="{}"]/li[{}]//*[@data-name="{}"]'.format(
            element_ids[list_id], list_length, element_names[name])
        element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
        wait_for_element_to_be_clickable_then_click(
            element, timeout, interval, locator)


@step(
    u'(?:I click the: "([^"]*)", in row: (\d+), in the: "([^"]*)"(?:(?:, '
    'wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def click_element_within_repeated_div(
        context, item, row, menu, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
        element_names[menu], row, element_names[item])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in the: "([^"]*)", that'
    ' contains the text: "([^"]*)"(?:(?:, wait(?:(?: for)?): (\d+)'
    ' second(?:s?), interval: (\d+) second(?:s?))?)$)')
def click_within_repeated_div_by_text(
        context, name, menu, text, total_wait, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    menu_rows_locator = u'//*[@data-name="{}"]//*[@data-name="{}"]'.format(
        element_names[menu], element_names[name])
    contains = None
    assert wait_for_element_to_be_in_DOM(menu_rows_locator, timeout, interval)
    while time() < timeout:
        menu_list = browser.find_elements_by_xpath(menu_rows_locator)
        for row in range(len(menu_list)):
            locator = u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
                element_names[menu], row + 1, element_names[name])
            try:
                element = browser.wait_for(locator, By.XPATH)
            # some tables wont have the desired element in all rows
            except (SELENIUM_EXCEPTIONS.NoSuchElementException,
                    SELENIUM_EXCEPTIONS.StaleElementReferenceException,
                    SELENIUM_EXCEPTIONS.ElementNotVisibleException):
                    continue
            contains, elem_text = check_text_in_element(element, text)
            if contains > -1:
                wait_for_element_to_be_clickable_then_click(
                    element, timeout, interval, locator)
                return
        sleep(interval)
    assert False, 'Text in step: {} is not in element'.format(
        text)


@step(
    u'(?:(?:I|the user) click the: "([^"]*)", in row: (\d+)(?:(?:, wait(?:(?:'
    ' for)?): (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def click_from_list_of_elements(context, element, row, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    if element in element_names:
        locator = u'//*[@data-name="{}"]'.format(element_names[element])
    else:
        locator = u'//*[@id="{}"]'.format(element_ids[element])
    row = int(row)
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        elem_list = browser.find_elements_by_xpath(locator)
        wait_for_element_to_be_clickable_then_click(
            elem_list[row - 1], timeout, interval, locator)


# See
@step(u'(?:(?:I|the user) (?:(do not )?)see: "([^"]*)"$)')
def sees_element_onscreen(context, notIn, item):
    if notIn:
        clause = By.NOT_ID
    else:
        clause = By.ID
    browser.wait_for(element_ids[item], clause)


@step(u'(?:(?:I|the user) see this text appear on the page: "([^"]*)"$)')
def text_is_present_on_page(context, text):
    browser.text_is_present(text)


@step(u'(?:(?:I|the user) see that the: "([^"]*)",(?:( does not)?)'
      ' contain(?:s?) the text: "([^"]*)"$)')
def sees_text_in_element(context, elem, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text

    if elem in element_names:
        web_element = browser.wait_for(
            u'//*[@data-name="{}"]'.format(element_names[elem], text),
            By.XPATH
        )
    else:
        web_element = browser.wait_for(
            u'//*[@id="{}"]'.format(element_ids[elem]),
            By.XPATH
        )
    string_text = web_element.text
    string_value = web_element.get_attribute('value')

    if not string_value:
        elem_text = string_text
    elif not string_text:
        elem_text = string_value
    else:
        elem_text = string_value + string_text

    contains = elem_text.find(text.strip())

    if notIn:
        assert contains == -1, \
            "Either the elements innertext or its value attribute contains the \
            text"
    else:
        assert contains > -1, \
            "Neither the elements innertext or its value attribute contains \
            the text: {}, looking in the text: {}".format(text, elem_text)


@step(u'(?:(?:I|the user) see that the table: "([^"]*)",(?:( does not)?)'
      ' contain(?:s?) the text: "([^"]*)"$)')
def table_contains_text(context, table, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        browser.wait_for(
            u'//table[@id="{}"]/tbody//tr[contains(., "{}")]'.format(
                element_ids[table], text),
            By.NOT_XPATH
        )
    else:
        browser.wait_for(
            u'//table[@id="{}"]/tbody//tr[contains(., "{}")]'.format(
                element_ids[table], text),
            By.XPATH
        )


@step(u'(?:(?:I|the user) see that the list: "([^"]*)",(?:( does not)?)'
      ' contain(?:s?) the text: "([^"]*)"$)')
def list_contains_text(context, mylist, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH
    browser.wait_for(
        u'//*[@id="{}"]//li[contains(., "{}")]'.format(
            element_ids[mylist], text),
        clause
    )


@step(u'(?:(?:I|the user) see that row: (\d+), in the list: "([^"]*)"'
      ',(?:( does not)?) contain(?:s?) the text: "([^"]*)"$)')
def list_item_contains_text(context, row, elem, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH
    browser.wait_for(
        u'//*[@id="{}"]/li[{}]//*[contains(.,"{}")]'.format(
            element_ids[elem], row, text),
        clause
    )


@step(u'(?:(?:I|the user) see that: "([^"]*)", in the list: "([^"]*)"'
      ',(?:( does not)?) contain(?:s?) the text: "([^"]*)"$)')
def named_list_item_contains_text(context, name, elem, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH
    browser.wait_for(
        u'//*[@id="{}"]//*[@data-name="{}" and contains(.,"{}")]'.format(
            element_ids[elem], element_names[name], text),
        clause
    )


@step(u'(?:(?:I|the user) see that the: "([^"]*)", in row: (\d+), in the: '
      '"([^"]*)",(?:( does not)?) contain(?:s?) the text: "([^"]*)"$)')
def repeated_div_item_contains_text(context, item, row, elem, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH
    browser.wait_for(
        u'//*[@data-name="{}"][{}]//*[@data-name="{}"]//*[contains(.,"{}")]'.format(  # noqa
            element_names[elem], row, element_names[item], text),
        clause
    )


@step(u'(?:(?:I|the user) see that the dropdown: "([^"]*)", has'
      ' (?:(not )?)selected the option containing the text: "([^"]*)"$)')
def sees_selected_row_dropdown_contains(context, elem_id, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH

    elem_select = browser.wait_for(u'//*[@id="{}"]'.format(
        element_ids[elem_id]), clause)
    value = elem_select.get_attribute('value')
    elem_opt = browser.wait_for('//*[@id="{}"]/option[@value={}]'.format(
        element_ids[elem_id], value), clause)
    total_text = elem_opt.text + elem_opt.get_attribute('value')
    assert total_text.find(text.strip()) > -1, \
        "Currently selected option does not contain the text: {}".format(text)


@step(u'(?:(?:I|the user) see that: "([^"]*)", in the rows in the table: '
      '"([^"]*)", are in (ascending|descending) order by: '
      '(date|alphabetical|numerical)$)')
def compare_visible_rows_in_table(context, name, table, order, how):
    first_row = browser.wait_for(
        '//*[@id="{}"]/tbody/tr[1]'.format(element_ids[table]),
        By.XPATH
    )
    table_rows_count = len(browser.find_elements_by_xpath(
        '//*[@id="{}"]/tbody/tr'.format(element_ids[table])))
    values_list = []
    for i in range(1, table_rows_count + 1):
        if how == 'date':
            value = wait_for_table_element(table, i, name, clause=By.XPATH) \
                .text.splitlines()
            if value[0].strip() == 'N/A':
                value = value[0].strip()
            else:
                value = value[1].strip()
                (month, day, year) = map(
                    int, value.replace('(', '').replace(')', '').split('/'))
                value = date(year, month, day)
        else:
            try:
                value = wait_for_table_element(
                    table, i, name, clause=By.XPATH).text.splitlines()[0].strip()
            except AttributeError:
                value = wait_for_table_element(
                    table, i, name, clause=By.XPATH)[0].text.splitlines()[0].strip()
            if how == 'numerical':
                value = int(value)
            # Text columns need to have all non-alphanumeric characters removed
            # and to be converted to lowercase to be sorted properly
            elif value not in TOP_OF_ASC_TABLE and value not in BOTTOM_OF_ASC_TABLE:
                value = re.sub(r'[^a-zA-Z\d:]', '', value).lower()
        values_list.append(value)

    if order == 'descending':
        sorted_list = sorted(values_list, key=lambda x: x, reverse=True)
        for value in sorted_list:
            if value in TOP_OF_ASC_TABLE:
                sorted_list.append(sorted_list.pop(sorted_list.index(value)))
            if value in BOTTOM_OF_ASC_TABLE:
                sorted_list.insert(
                    0, sorted_list.pop(sorted_list.index(value)))
        assert values_list == sorted_list, \
            'Error: Rows not in proper descending order. Rows: {}'.format(
                values_list)
    else:
        sorted_list = sorted(values_list, key=lambda x: x)
        # RightsID places values consisting only of non-alphanumeric characters
        # at the top of an asc list whereas Python's sort method places them in
        # the same order but following all alphanumeric characters. This loop
        # moves values in the TOP_OF_ASC_TABLE list to the top and inserts
        # non-alphanumeric values immediately after.
        index_offset = 0
        for value in sorted_list:
            if value in TOP_OF_ASC_TABLE:
                sorted_list.insert(
                    0, sorted_list.pop(sorted_list.index(value)))
                index_offset += 1
            if value in BOTTOM_OF_ASC_TABLE:
                sorted_list.append(sorted_list.pop(sorted_list.index(value)))
            if isinstance(value, basestring) and re.match(r'[\W+]', value):
                sorted_list.insert(
                    index_offset, sorted_list.pop(sorted_list.index(value)))
                index_offset += 1
        assert values_list == sorted_list, \
            'Error: Rows not in proper ascending order. Rows: {}'.format(
                values_list)


@step(u'(?:(?:I|the user) see that the: "([^"]*)", in the table: "([^"]*)",'
      ' are in (ascending|descending) order by: (alphabetical|numerical)$)')
def verify_table_sorts(context, name, table, order, how):
    browser.wait_for(
        '//*[@id="{}"]/tbody/tr[1]'.format(element_ids[table]),
        By.XPATH
    )
    values_list = []
    start = 1
    try:
        # Will fail if more than one row is empty
        wait_for_table_element(table, 1, name, clause=By.XPATH)
    except SELENIUM_EXCEPTIONS.NoSuchElementException:
        start = 2
    table_rows_count = len(browser.find_elements_by_xpath(
        '//*[@id="{}"]/tbody/tr'.format(element_ids[table])))
    for i in range(start, table_rows_count + 1):
        value = wait_for_table_element(table, i, name, clause=By.XPATH)
        if isinstance(value, (list)):
            value = value[0].text.splitlines()[0].strip()
            if how == 'numerical':
                value = value.replace(',', '')
                value = str(value)
                if value not in BOTTOM_OF_ASC_TABLE:
                    value = int(value)
                    values_list.append(value)
            else:
                # AMG strips white space, moves everything to lower case, and
                # removes all non-alphanumeric characters before sorting
                value = value.replace(' ', '')
                value = value.lower()
                if value not in BOTTOM_OF_ASC_TABLE:
                    value = re.sub(r'[^a-zA-Z\d:]', '', value)
                    values_list.append(value)
        else:
            value = value.text.splitlines()[0].strip()
            if how == 'numerical':
                value = value.replace(',', '')
                value = str(value)
                if value not in BOTTOM_OF_ASC_TABLE:
                    value = int(value)
                    values_list.append(value)
            else:
                value = value.replace(' ', '')
                value = value.lower()
                if value not in BOTTOM_OF_ASC_TABLE:
                    value = re.sub(r'[^a-zA-Z\d:]', '', value)
                    values_list.append(value)

    if order == 'descending':
        sorted_list = sorted(values_list, reverse=True)
        for value in sorted_list:
            if value in BOTTOM_OF_ASC_TABLE:
                sorted_list.insert(
                    0, sorted_list.pop(sorted_list.index(value)))
        assert values_list == sorted_list, \
            'Error: Rows not in proper descending order. ' \
            'Correct sorting order: {} Actual sorting order: {}'.format(
                sorted_list, values_list)
    else:
        sorted_list = sorted(values_list)
        for value in sorted_list:
            if value in BOTTOM_OF_ASC_TABLE:
                sorted_list.append(sorted_list.pop(sorted_list.index(value)))
        assert values_list == sorted_list, \
            'Error: Rows not in proper ascending order. ' \
            'Correct sorting order: {} Actual sorting order: {}'.format(
                sorted_list, values_list)


@step(u'(?:(?:I|the user) see that the table: "([^"]*)", has'
      ' (greater than|less than|equal to): (\d+), item(?:s?)$)')
def table_contains_fewer_items(context, name, sign, count):
    if count == SAVED_NUMBER_KEYWORD:
        count = scenario.saved_number
    else:
        assert count.isdigit(), \
            'Either SAVED_NUMBER or a positive integer must be given'
        count = int(count)

    table_list = browser.find_elements_by_xpath(
        '//*[@id="{}"]/tbody/tr'.format(element_ids[name])
    )
    if sign == 'less than':
        assert len(table_list) < int(count)
    elif sign == 'greater than':
        assert len(table_list) > int(count)
    else:
        assert int(count) == len(table_list)


@step(u'(?:(?:I|the user) see that the list: "([^"]*)", has'
      ' (greater than|less than|equal to): (\d+), item(?:s?)$)')
def list_contains_fewer_items(context, name, sign, count):
    if count == SAVED_NUMBER_KEYWORD:
        count = scenario.saved_number
    else:
        assert count.isdigit(), \
            'Either SAVED_NUMBER or a positive integer must be given'
        count = int(count)
    table_list = browser.find_elements_by_xpath(
        '//*[@id="{}"]//li'.format(element_ids[name])
    )
    if sign == 'less than':
        assert len(table_list) < count
    elif sign == 'greater than':
        assert len(table_list) > count
    else:
        assert count == len(table_list)


@step(u'(?:(?:I|the user) see that the: "([^"]*)", is(?:( not)?) clickable'
      ' for: (\d+) second(?:s?)$)')
def see_element_is_clickable(context, elem, isNot, seconds):
    assert seconds.isdigit()
    seconds = int(seconds)
    timeout = time() + seconds
    if isNot:
        while time() < timeout:
            try:
                browser.click(
                    u'//*[@id="{}"]'.format(element_ids[elem]), By.XPATH)
                assert False, 'element was clickable'
            except:
                continue
        return
    else:
        while time() < timeout:
            element = None
            element = browser.wait_for(
                u'//*[@id="{}"]'.format(element_ids[elem]), By.XPATH)
            disabled = element.get_attribute('disabled')
            if disabled:
                assert False, 'element wasn\'t clickable'
        return


@step(u'(?:(?:I|the user) see that the: "([^"]*)", is(?:( not)?) checked$)')
def is_checkbox_checked(context, checkbox_id, isNot):
    check_box = browser.find_element_by_xpath(
        u'//*[@id="{}"]'.format(element_ids[checkbox_id])
    )
    assert isNot ^ check_box.get_attribute('checked')


@step(u'(?:(?:I|the user) see that the: "([^"]*)", is'
      ' (greater than|less than|equal to) the saved text$)')
def compare_values(context, elem, comparison):
    element = browser.wait_for(
        u'//*[@id="{}"]'.format(element_ids[elem]),
        By.XPATH
    )
    if comparison == 'greater than':
        assert int(element.text) > int(scenario.saved_text)
    elif comparison == 'less than':
        assert int(element.text) < int(scenario.saved_text)
    elif comparison == 'equal to':
        assert int(element.text) == int(scenario.saved_text)


# Wait
@step(u'(?:(?:I|the user) wait for (\d+)$)')
def wait_for_this_long(context, time):
    sleep(float(time))
    return


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the:'
      ' "([^"]*)", to(?:( not)?) be on screen(?:(?:, interval (\d+)'
      ' second(?:s?))?)$)')
def user_waits_for(context, seconds, item, notIn, interval):
    opts = {}
    if seconds:
        opts['retry_timeout'] = int(seconds)
    else:
        # TODO: when our apps are faster make this <= 30
        opts['retry_timeout'] = 60
    if interval:
        opts['retry_interval'] = int(interval)
    else:
        opts['retry_interval'] = 2

    if notIn:
        clause = By.NOT_ID
    else:
        clause = By.ID

    browser.wait_for(element_ids[item], clause, **opts)


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", to(?:( not)?) contain the text: "([^"]*)"(?:(?:,'
      ' interval (\d+) second(?:s?))?)$)')
def wait_for_id_contains_text(
        context, total_wait, item, notIn, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    contains = None
    locator = u'//*[@id="{}"]'.format(element_ids[item])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    while time() < timeout:
        try:
            contains, elem_text = check_text_in_element(element, text)
        except SELENIUM_EXCEPTIONS as e:
            continue
        if notIn:
            if contains == -1:
                return
        else:
            if contains > -1:
                return
        sleep(interval)
    assert False, 'Text in step: {}. Text on page: {}\nError: {}'.format(
        text, elem_text, e.args)


@step(
    u'(?:(?:I|the user) wait(?:(?: for (\d+)(?: second(?:s?))?)?) for the: '
    '"([^"]*)", to be (greater than|less than|equal to) saved text(?:(?:,'
    ' interval (\d+)(?: second(?:s?))?)?)$)')
def compare_number_in_id_to_saved_text(
        context, total_wait, element_id, comparison, interval):
    try:
        int(scenario.saved_text)
    except ValueError:
        assert False, \
            'SAVED_TEXT can\'t be converted to integer\n {}'.format(
                scenario.saved_text)
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    while time() < timeout:
        element = browser.wait_for(
            u'//*[@id="{}"]'.format(element_ids[element_id]),
            By.XPATH
        )
        if comparison == 'greater than':
            assert int(element.text) > int(scenario.saved_text)
            return
        elif comparison == 'less than':
            assert int(element.text) < int(scenario.saved_text)
            return
        elif comparison == 'equal to':
            assert int(element.text) == int(scenario.saved_text)
            return
        sleep(interval)
    assert False, \
        'Timed out. Text on page: {}\n Saved Text: {}'.format(
            element.text, scenario.saved_text)


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", in row: (\d+), in the list: "([^"]*)", to(?:( not)?) be on'
      ' screen(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_list_item(context, seconds, item, row, elem, notIn, interval):
    opts = {}
    if seconds:
        opts['retry_timeout'] = int(seconds)
    if interval:
        opts['retry_interval'] = int(interval)

    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH

    browser.wait_for(
        u'//*[@id="{}"]//li[{}]//*[@data-name="{}"]'.format(
            element_ids[elem], row, element_names[item]),
        clause,
        **opts
    )


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", in row: (\d+), in the table: "([^"]*)", to(?:( not)?)'
      ' be on screen(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_name_in_table(
        context, seconds, name, row, table, notIn, interval):
    opts = {}
    if seconds:
        opts['retry_timeout'] = int(seconds)
    if interval:
        opts['retry_interval'] = int(interval)

    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH

    browser.wait_for(
        u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
            element_ids[table], row, element_names[name]),
        clause,
        **opts
    )


@step(
    u'(?:(?:I|the user) wait(?:(?: for (\d+)(?: second(?:s?))?)?) for the'
    ' table at: "([^"]*)", to have at least one row(?:(?:, interval (\d+)(?:'
    ' second(?:s?))?)?)$)')
def wait_for_table_have_row(context, total_wait, table, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):
        return
    assert False, 'Table didn\'t have at least one row {}'.format(locator)


@step(
    u'(?:(?:I|the user) wait for the table at: "([^"]*)", to have (greater'
    ' than|less than|equal to): (\d+|SAVED_NUMBER),'
    ' item(?:s?)(?:(?: for: (\d+))?)$)')
def table_waits_diff_items(context, name, sign, count, wait_time):
    if count == SAVED_NUMBER_KEYWORD:
        count = scenario.saved_number
    else:
        assert count.isdigit(), \
            'Either SAVED_NUMBER or a positive integer must be given'
        count = int(count)

    if not wait_time:
        wait_time = 60

    wait_time = int(wait_time)
    timeout = time() + wait_time
    xpath = u'//*[@id="{}"]/tbody/tr'.format(element_ids[name])
    if count != 0:
        assert wait_for_element_to_have_at_least_one_row(xpath, timeout)
    while time() < timeout:
        table_list = browser.find_elements_by_xpath(xpath)
        length_of_table = len(table_list)
        if sign == 'less than' and length_of_table < count:
            return
        elif sign == 'greater than' and length_of_table > count:
            return
        elif sign == 'equal to' and length_of_table == count:
            return
    assert False, \
        'Timed out. Number of rows: {} \n Expected count to be {}: {}'.format(
            length_of_table, sign, count)


@step(
    u'(?:(?:I|the user) wait(?:(?: for (\d+)(?: second(?:s?))?)?) for the list'
    ' at: "([^"]*)", to have (greater than|less than|equal to): (\d+),'
    ' item(?:s?)(?:(?:, interval (\d+)(?: second(?:s?))?)?)$)')
def list_waits_diff_items(
        context, total_wait, element_id, comparison, count, interval):
    if count == SAVED_NUMBER_KEYWORD:
        count = scenario.saved_number
    else:
        assert count.isdigit(), \
            'Either SAVED_NUMBER or a positive integer must be given'
        count = int(count)

    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    xpath = u'//*[@id="{}"]//li'.format(element_ids[element_id])
    if count != 0:
        assert wait_for_element_to_have_at_least_one_row(xpath, timeout)
    while time() < timeout:
        list_rows = browser.find_elements_by_xpath(xpath)
        length_of_list = len(list_rows)
        if comparison == 'less than' and length_of_list < count:
            return
        elif comparison == 'greater than' and length_of_list > count:
            return
        elif comparison == 'equal to' and length_of_list == count:
            return
        sleep(interval)
    assert False, \
        'Timed out. Number of rows: {} \n Expected count to be {} {}'.format(
            length_of_list, comparison, count)


@step(
    u'(?:(?:I|the user) wait for the: "([^"]*)", in row: (\d+), in the'
    ' list: "([^"]*)", to(?:( not)?) contain the text: "([^"]*)"(?:(?: for:'
    ' (\d+)(?: second(?:s?))?)?)$)')
def name_list_row_contains_text(
        context, name, row, element_id, notIn, text, wait_time):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if not wait_time:
        wait_time = 60
    wait_time = int(wait_time)
    timeout = time() + wait_time
    contains = None
    while time() < timeout:
        element = browser.wait_for(
            u'//*[@id="{}"]//li[{}]//*[@data-name="{}"]'.format(
                element_ids[element_id], row, element_names[name]),
            By.XPATH
        )
        try:
            string_text = element.text
            string_value = element.get_attribute('value')
        # if the element is still loading this exception might occur
        except SELENIUM_EXCEPTIONS.StaleElementReferenceException:
            continue
        else:
            if not string_value:
                elem_text = string_text
            elif not string_text:
                elem_text = string_value
            else:
                elem_text = string_value + string_text
            contains = elem_text.find(text.strip())
            if notIn:
                if contains == -1:
                    return
            else:
                if contains > -1:
                    return
    assert False, 'Text in step: {}\n Text on page: {}'.format(
        text, elem_text)


@step(u'(?:(?:I|the user) wait for the: "([^"]*)", in row: (\d+), in the'
      ' table: "([^"]*)", to(?:( not)?) contain the text: "([^"]*)"$)')
def name_table_row_contains_text(context, name, row, table, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    wait_time = 60
    timeout = time() + wait_time
    contains = None
    while time() < timeout:
        element = browser.wait_for(
            u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                element_ids[table], row, element_names[name]),
            By.XPATH
        )
        try:
            contains, elem_text = check_text_in_element(element, text)
        # if the element is still loading this exception might occur
        except SELENIUM_EXCEPTIONS.StaleElementReferenceException:
            continue
        if notIn:
            if contains == -1:
                return
        else:
            if contains > -1:
                return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, elem_text)


@step(u'(?:(?:I|the user) wait(?:(?: for (\d+)(?: second(?:s?))?)?) for'
      ' a(?:n?): "([^"]*)", in a column in the table: "([^"]*)",'
      ' to(?:( not)?) contain the text: "([^"]*)"(?:(?:, interval (\d+)(?:'
      ' second(?:s?))?)?)$)')
def unknown_table_column_contains_text(
        context, total_wait, name, table, notIn, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    contains = None
    xpath = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    assert wait_for_element_to_have_at_least_one_row(xpath, timeout)
    while time() < timeout:
        table_list = browser.find_elements_by_xpath(xpath)
        # get the columns in each row
        all_columns = []
        for row in range(len(table_list)):
            column_path = u'//*[@id="{}"]/tbody/tr[{}]/td'.format(
                element_ids[table], row)
            row_columns = browser.find_elements_by_xpath(column_path)
            all_columns.append(row_columns)
        for row in range(len(table_list)):
            for column in range(len(all_columns[row])):
                try:
                    element = browser.wait_for(
                        u'//*[@id="{}"]/tbody/tr[{}]/td[{}]//*'
                        '[@data-name="{}"]'.format(
                            element_ids[table], row + 1, column + 1,
                            element_names[name]), By.XPATH)
                # some tables wont have the desired element in all columns
                except (SELENIUM_EXCEPTIONS.NoSuchElementException,
                        SELENIUM_EXCEPTIONS.StaleElementReferenceException,
                        SELENIUM_EXCEPTIONS.ElementNotVisibleException):
                        continue
                contains, elem_text = check_text_in_element(element, text)
                if notIn:
                    if contains == -1:
                        return
                else:
                    if contains > -1:
                        return
        sleep(interval)
    assert False, 'Text in step: {} is not in table'.format(
        text)


@step(u'(?:(?:I|the user) wait(?:(?: for (\d+)(?: second(?:s?))?)?) for'
      ' a(?:n?): "([^"]*)", in the table: "([^"]*)", to(?:( not)?)'
      ' contain the text: "([^"]*)"(?:(?:, interval (\d+)(?:'
      ' second(?:s?))?)?)$)')
def unknown_table_row_contains_text(
        context, total_wait, name, table, notIn, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    contains = None
    xpath = u'//*[@id="{}"]/tbody/tr'.format(element_ids[table])
    assert wait_for_element_to_have_at_least_one_row(xpath, timeout)
    while time() < timeout:
        table_list = browser.find_elements_by_xpath(xpath)
        for row in range(len(table_list)):
            try:
                element = browser.wait_for(
                    u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                        element_ids[table], row + 1, element_names[name]),
                    By.XPATH)
            # some tables wont have the desired element in all rows
            except (SELENIUM_EXCEPTIONS.NoSuchElementException,
                    SELENIUM_EXCEPTIONS.StaleElementReferenceException,
                    SELENIUM_EXCEPTIONS.ElementNotVisibleException):
                    continue
            contains, elem_text = check_text_in_element(element, text)
            if notIn:
                if contains == -1:
                    return
            else:
                if contains > -1:
                    return
        sleep(interval)
    assert False, 'Text in step: {} is not in table'.format(
        text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", to(?:( not)?) be clickable(?:(?:, interval (\d+)'
    ' second(?:s?))?)$)')
def wait_for_is_clickable(context, seconds, elem, notIn, interval):
    if seconds:
        wait_time = int(seconds)
    else:
        wait_time = 60
    if interval:
        interval = int(interval)
    else:
        interval = 3
    timeout = time() + wait_time
    element = None
    if notIn:
        while time() < timeout:
            element = browser.wait_for(
                u'//*[@id="{}"]'.format(element_ids[elem]), By.XPATH)
            disabled = element.get_attribute('disabled')
            if disabled:
                return
            if not disabled:
                sleep(interval)
        assert False, 'element was clickable'
    else:
        while time() < timeout:
            element = browser.wait_for(
                u'//*[@id="{}"]'.format(element_ids[elem]), By.XPATH)
            disabled = element.get_attribute('disabled')
            if disabled:
                sleep(interval)
            if not disabled:
                return
        assert False, 'element wasn\'t clickable'


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in the table: "([^"]*)", to(?:( not)?) be'
    ' clickable(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_name_in_table_clickable(
        context, seconds, name, row, table, notIn, interval):
    if seconds:
        wait_time = int(seconds)
    else:
        wait_time = 60
    if interval:
        interval = int(interval)
    else:
        interval = 3
    timeout = time() + wait_time
    element = None
    if notIn:
        while time() < timeout:
            element = browser.wait_for(
                u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                    element_ids[table], row, element_names[name]),
                By.XPATH)
            disabled = element.get_attribute('disabled')
            if disabled:
                return
            if not disabled:
                sleep(interval)
        assert False, 'element was clickable'
    else:
        while time() < timeout:
            element = browser.wait_for(
                u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                    element_ids[table], row, element_names[name]),
                By.XPATH)
            disabled = element.get_attribute('disabled')
            if disabled:
                sleep(interval)
            if not disabled:
                return
        assert False, 'element wasn\'t clickable'


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in the: "([^"]*)", to(?:( not)?) be'
    ' clickable(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_element_in_repeated_div_clickable(
        context, total_wait, name, row, menu, notIn, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    element = None
    if notIn:
        while time() < timeout:
            element = browser.wait_for(
                u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
                    element_names[menu], row, element_names[name]),
                By.XPATH)
            disabled = element.get_attribute('disabled')
            if disabled:
                return
            if not disabled:
                sleep(interval)
        assert False, 'element was clickable'
    else:
        while time() < timeout:
            element = browser.wait_for(
                u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
                    element_names[menu], row, element_names[name]),
                By.XPATH)
            disabled = element.get_attribute('disabled')
            if disabled:
                sleep(interval)
            if not disabled:
                return
        assert False, 'element wasn\'t clickable'


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", to(?:( not)?) be visible(?:(?:, interval (\d+)'
    ' second(?:s?))?)$)')
def wait_for_id_visible(context, seconds, elem, notIn, interval):
    if seconds:
        wait_time = int(seconds)
    else:
        wait_time = 10
    if interval:
        interval = int(interval)
    else:
        interval = 2
    element = None
    # web driver wait can incorrectly return true if ajax has a slight delay
    sleep(1)
    if notIn:
        try:
            element = browser.wait_for(
                u'//*[@id="{}"]'.format(
                    element_ids[elem]),
                By.XPATH)
            WebDriverWait(browser, wait_time, interval).until_not(
                EC.visibility_of((
                    element)))
        except SELENIUM_EXCEPTIONS.TimeoutException:
            assert False, 'element was visible {}'.format(element)
        else:
            return
    else:
        try:
            element = browser.wait_for(
                u'//*[@id="{}"]'.format(
                    element_ids[elem]),
                By.XPATH)
            WebDriverWait(browser, wait_time, interval).until(
                EC.visibility_of((
                    element)))
        except SELENIUM_EXCEPTIONS.TimeoutException:
            assert False, 'element wasn\'t visible {}'.format(element)
        else:
            return


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in the table: "([^"]*)", to(?:( not)?) be'
    ' visible(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_name_in_table_visible(
        context, seconds, name, row, table, notIn, interval):
    if seconds:
        wait_time = int(seconds)
    else:
        wait_time = 10
    if interval:
        interval = int(interval)
    else:
        interval = 2
    element = None
    # web driver wait can incorrectly return true if ajax has a slight delay
    sleep(1)
    if notIn:
        try:
            element = browser.wait_for(
                u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                    element_ids[table], row, element_names[name]),
                By.XPATH)
            WebDriverWait(browser, wait_time, interval).until_not(
                EC.visibility_of((
                    element)))
        except SELENIUM_EXCEPTIONS.TimeoutException:
            assert False, 'element was visible {}'.format(element)
        else:
            return
    else:
        try:
            element = browser.wait_for(
                u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                    element_ids[table], row, element_names[name]),
                By.XPATH)
            WebDriverWait(browser, wait_time, interval).until(
                EC.visibility_of((
                    element)))
        except SELENIUM_EXCEPTIONS.TimeoutException:
            assert False, 'element wasn\'t visible {}'.format(element)
        else:
            return


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in the: "([^"]*)", to(?:( not)?) be'
    ' visible(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_element_in_repeated_div_visible(
        context, total_wait, name, row, menu, notIn, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    # web driver wait can incorrectly return true if ajax has a slight delay
    sleep(1)
    locator = u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
        element_names[menu], row, element_names[name])
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    if notIn:
        try:
            WebDriverWait(browser, total_wait, interval).until_not(
                EC.visibility_of((
                    element)))
        except SELENIUM_EXCEPTIONS.TimeoutException:
            assert False, 'element was visible {}'.format(element)
        else:
            return
    else:
        try:
            WebDriverWait(browser, total_wait, interval).until(
                EC.visibility_of((
                    element)))
        except SELENIUM_EXCEPTIONS.TimeoutException:
            assert False, 'element wasn\'t visible {}'.format(element)
        else:
            return


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", to(?:( not)?) be checked(?:(?:, interval (\d+)'
      ' second(?:s?))?)$)')
def wait_for_is_checked(context, seconds, elem, notIn, interval):
    if seconds:
        wait_time = int(seconds)
    else:
        wait_time = 60
    if interval:
        interval = int(interval)
    else:
        interval = 3
    # couldn't get this step to work with opts, so I did this method instead
    timeout = time() + wait_time
    check_box = None
    if notIn:
        while time() < timeout:
            check_box = browser.wait_for(
                u'//*[@id="{}"]'.format(element_ids[elem]),
                By.XPATH
            )
            if not check_box.is_selected():
                return
            sleep(interval)
        assert not check_box.is_selected(), check_box.is_selected()
    else:
        while time() < timeout:
            check_box = browser.wait_for(
                u'//*[@id="{}"]'.format(element_ids[elem]),
                By.XPATH
            )
            if check_box.is_selected():
                return
            sleep(interval)
        assert check_box.is_selected(), check_box.is_selected()


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", in row: (\d+), in the table: "([^"]*)", to(?:( not)?)'
      ' be checked(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_name_is_checked(
        context, total_wait, name, row, table, notIn, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    check_box = None
    if notIn:
        while time() < timeout:
            check_box = browser.wait_for(
                u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                    element_ids[table], row, element_names[name]),
                By.XPATH
            )
            if not check_box.is_selected():
                return
            sleep(interval)
        assert not check_box.is_selected(), check_box.is_selected()
    else:
        while time() < timeout:
            check_box = browser.wait_for(
                u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                    element_ids[table], row, element_names[name]),
                By.XPATH
            )
            if check_box.is_selected():
                return
            sleep(interval)
        assert check_box.is_selected(), check_box.is_selected()


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", in row: (\d+), in the list: "([^"]*)", to(?:( not)?)'
      ' be checked(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_name_in_list_is_checked(
        context, total_wait, name, row, list_element, notIn, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    check_box = None
    if notIn:
        while time() < timeout:
            check_box = browser.wait_for(
                u'//*[@id="{}"]//li[{}]//*[@data-name="{}"]'.format(
                    element_ids[list_element], row, element_names[name]),
                By.XPATH
            )
            if not check_box.is_selected():
                return
            sleep(interval)
        assert not check_box.is_selected(), check_box.is_selected()
    else:
        while time() < timeout:
            check_box = browser.wait_for(
                u'//*[@id="{}"]//li[{}]//*[@data-name="{}"]'.format(
                    element_ids[list_element], row, element_names[name]),
                By.XPATH
            )
            if check_box.is_selected():
                return
            sleep(interval)
        assert check_box.is_selected(), check_box.is_selected()


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the'
      ' dropdown: "([^"]*)", to(?:( not)?) have selected the option containing'
      ' the text: "([^"]*)"(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_row_dropdown_contains(
        context, seconds, elem_id, notIn, text, interval):
    opts = {}
    if seconds:
        opts['retry_timeout'] = int(seconds)
    else:
        opts['retry_timeout'] = 60
    if interval:
        opts['retry_interval'] = int(interval)
    else:
        opts['retry_interval'] = 3
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH

    elem_select = browser.wait_for(u'//*[@id="{}"]'.format(
        element_ids[elem_id]), clause)
    value = elem_select.get_attribute('value')
    elem_opt = browser.wait_for(
        u'//*[@id="{}"]/option[@value="{}"]'.format(
            element_ids[elem_id], value),
        clause, **opts
    )
    total_text = elem_opt.text + elem_opt.get_attribute('value')
    assert total_text.find(text.strip()) > -1, "FAIL: Text found {}".format(
        total_text)


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the'
      ' dropdown: "([^"]*)", to(?:( not)?) have selected the option containing'
      ' the text: "([^"]*)", in row: (\d+), in the: "([^"]*)"(?:(?:,'
      ' interval (\d+) second(?:s?))?)$)')
def wait_for_row_dropdown_contains_within_repeated_div(
        context, seconds, item, notIn, text, row, menu, interval):
    opts = {}
    if seconds:
        opts['retry_timeout'] = int(seconds)
    else:
        opts['retry_timeout'] = 60
    if interval:
        opts['retry_interval'] = int(interval)
    else:
        opts['retry_interval'] = 3
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH

    elem_select = browser.wait_for(
        u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
            element_names[menu], row, element_names[item]), clause)
    value = elem_select.get_attribute('value')
    elem_opt = browser.wait_for(
        u'//*[@data-name="{}"][{}]'
        '//*[@data-name="{}"]/option[@value="{}"]'.format(
            element_names[menu], row, element_names[item], value),
        clause, **opts
    )
    total_text = elem_opt.text + elem_opt.get_attribute('value')
    assert total_text.find(text.strip()) > -1, "FAIL: Text found {}".format(
        total_text)


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", in row: (\d+), in the: "([^"]*)", to(?:( not)?) be on'
      ' screen(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_element_within_repeated_div(
        context, seconds, item, row, menu, notIn, interval):
    opts = {}
    if seconds:
        opts['retry_timeout'] = int(seconds)
    else:
        opts['retry_timeout'] = 60
    if interval:
        opts['retry_interval'] = int(interval)
    else:
        opts['retry_interval'] = 3

    if notIn:
        clause = By.NOT_XPATH
    else:
        clause = By.XPATH
    browser.wait_for(
        u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
            element_names[menu], row, element_names[item]),
        clause, **opts
    )


@step(u'(?:(?:I|the user) wait for the: "([^"]*)", in row: (\d+), in the: '
      '"([^"]*)", to(?:( not)?) contain the text: "([^"]*)"$)')
def element_within_repeated_div_contains_text(
        context, item, row, menu, notIn, text):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    wait_time = 60
    timeout = time() + wait_time
    contains = None
    while time() < timeout:
        element = browser.wait_for(
            u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
                element_names[menu], row, element_names[item]),
            By.XPATH
        )
        try:
            contains, elem_text = check_text_in_element(element, text)
        # if the element is still loading this exception might occur
        except SELENIUM_EXCEPTIONS.StaleElementReferenceException:
            continue
        if notIn:
            if contains == -1:
                return
        else:
            if contains > -1:
                return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, elem_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in column: (\d+), in the table: "([^"]*)",'
    ' to(?:( not)?) contain the text: "([^"]*)"(?:(?:, interval (\d+)'
    ' second(?:s?))?)$)')
def wait_element_in_row_in_column_in_table_to_contain_text(
        context, seconds, name, row, column, table, notIn, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    if seconds:
        wait_time = int(seconds)
    else:
        wait_time = 60
    if interval:
        interval = int(interval)
    else:
        interval = 3
    timeout = time() + wait_time
    while time() < timeout:
        element = browser.wait_for(
            u'//*[@id="{}"]/tbody/tr[{}]/td[{}]//*[@data-name="{}"]'.format(
                element_ids[table], row, column, element_names[name]),
            By.XPATH
        )
        try:
            contains, elem_text = check_text_in_element(element, text)
        except SELENIUM_EXCEPTIONS.StaleElementReferenceException:
            continue
        if notIn:
            if contains == -1:
                return
        else:
            if contains > -1:
                return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, elem_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), to(?:( not)?) contain the text: '
    '"([^"]*)"(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_list_elements_to_contain_text(
        context, total_wait, item, row, notIn, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    row = int(row)
    if item in element_names:
        locator = u'//*[@data-name="{}"]'.format(element_names[item])
    else:
        locator = u'//*[@id="{}"]'.format(element_ids[item])
    wait_for_element_to_be_in_DOM(locator, timeout, interval)
    while time() < timeout:
        if wait_for_element_to_have_at_least_one_row(locator, timeout, interval):  # nopep8
                elem_list = browser.find_elements_by_xpath(locator)
                element = elem_list[row - 1]
        try:
            contains, elem_text = check_text_in_element(element, text)
        except SELENIUM_EXCEPTIONS.StaleElementReferenceException:
            continue
        if notIn:
            if contains == -1:
                return
        else:
            if contains > -1:
                return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, elem_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", to(?:( not)?) have the attribute: "([^"]*)", which '
    'contains the text: "([^"]*)"(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_id_to_contain_attribute(
        context, total_wait, elem, notIn, attribute, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    while time() < timeout:
        web_element = browser.wait_for(
            u'//*[@id="{}"]'.format(element_ids[elem]),
            By.XPATH
        )
        attribute_text = web_element.get_attribute(attribute)
        if notIn:
            assert text not in attribute_text, attribute_text
            return
        else:
            assert text in attribute_text, attribute_text
            return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, attribute_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in the table: "([^"]*)", to(?:( not)?) have '
    'the attribute: "([^"]*)", which contains the text: "([^"]*)"(?:(?:, '
    'interval (\d+) second(?:s?))?)$)')
def wait_for_attribute_within_a_table(
        context, total_wait, item, row, table, notIn,
        attribute, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    while time() < timeout:
        web_element = browser.wait_for(
            u'//*[@id="{}"]/tbody/tr[{}]//*[@data-name="{}"]'.format(
                element_ids[table], row, element_names[item]),
            By.XPATH
        )
        attribute_text = web_element.get_attribute(attribute)
        if notIn:
            assert text not in attribute_text, attribute_text
            return
        else:
            assert text in attribute_text, attribute_text
            return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, attribute_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in column: (\d+), in the table: "([^"]*)", '
    'to(?:( not)?) have the attribute: "([^"]*)", which contains the '
    'text: "([^"]*)"(?:(?:, interval (\d+) second(?:s?))?)$)')
def wait_for_attribute_in_column_within_a_table(
        context, total_wait, item, row, column, table, notIn,
        attribute, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    while time() < timeout:
        web_element = browser.wait_for(
            u'//*[@id="{}"]/tbody/tr[{}]/td[{}]//*[@data-name="{}"]'.format(
                element_ids[table], row, column, element_names[item]),
            By.XPATH
        )
        attribute_text = web_element.get_attribute(attribute)
        if notIn:
            assert text not in attribute_text, attribute_text
            return
        else:
            assert text in attribute_text, attribute_text
            return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, attribute_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), in the: "([^"]*)", to(?:( not)?) have '
    'the attribute: "([^"]*)", which contains the text: "([^"]*)"(?:(?:, '
    'interval (\d+) second(?:s?))?)$)')
def wait_for_attribute_within_repeated_div(
        context, total_wait, item, row, menu, notIn,
        attribute, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    while time() < timeout:
        web_element = browser.wait_for(
            u'//*[@data-name="{}"][{}]//*[@data-name="{}"]'.format(
                element_names[menu], row, element_names[item]),
            By.XPATH
        )
        attribute_text = web_element.get_attribute(attribute)
        if notIn:
            assert text not in attribute_text, attribute_text
            return
        else:
            assert text in attribute_text, attribute_text
            return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, attribute_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
    '"([^"]*)", in row: (\d+), to(?:( not)?) have the attribute: '
    '"([^"]*)", which contains the text: "([^"]*)"(?:(?:,  interval (\d+) '
    'second(?:s?))?)$)')
def wait_for_attribute_within_list_of_elements(
        context, total_wait, name, row, notIn, attribute, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    while time() < timeout:
        elem_list = browser.find_elements_by_xpath(
            u'//*[@data-name="{}"]'.format(element_names[name]))
        attribute_text = elem_list[int(row) - 1].get_attribute(attribute)
        if notIn:
            assert text not in attribute_text, attribute_text
            return
        else:
            assert text in attribute_text, attribute_text
            return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, attribute_text)


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the '
      'angucomplete: "([^"]*)", in row: (\d+), to(?:( not)?) contain the '
      'text: "([^"]*)"(?:(?:,  interval (\d+) second(?:s?))?)$)')
def wait_for_angucomplete_contains_text(
        context, total_wait, item, row, notIn, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    contains = None
    # first two rows appear to always be blank
    row = int(row) + 2
    while time() < timeout:
        element = browser.wait_for(
            u'//*[@data-name="{}"]/div[1]/div[1]/div[{}]'.format(
                element_names[item], row),
            By.XPATH
        )
        try:
            contains, elem_text = check_text_in_element(element, text)
        # if the element is still loading this exception might occur
        except SELENIUM_EXCEPTIONS.StaleElementReferenceException:
            continue
        if notIn:
            if contains == -1:
                return
        else:
            if contains > -1:
                return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, elem_text)


@step(
    u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the'
    ' angucomplete input: "([^"]*)", in row: (\d+), to(?:( not)?) contain the'
    ' text: "([^"]*)"(?:(?:,  interval (\d+) second(?:s?))?)$)')
def wait_for_angucomplete_input_contains_text(
        context, total_wait, name, row, notIn, text, interval):
    if text == SAVE_TEXT_KEYWORD:
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    contains = None
    row = int(row)
    while time() < timeout:
        locator = u'//*[@data-name="{}"]//input'.format(element_names[name])
        wait_for_element_to_be_in_DOM(locator, timeout, interval)
        if wait_for_element_to_have_at_least_one_row(
                locator, timeout, interval):
            elem_list = browser.find_elements_by_xpath(locator)
            element = elem_list[row - 1]
        try:
            contains, elem_text = check_text_in_element(element, text)
        # if the element is still loading this exception might occur
        except SELENIUM_EXCEPTIONS.StaleElementReferenceException:
            continue
        if notIn:
            if contains == -1:
                return
        else:
            if contains > -1:
                return
    assert False, 'Text in step: {}. Text on page: {}'.format(
        text, elem_text)


@step(u'(?:(?:I|the user) wait (?:(?:for (\d+) second(?:s?) )?)for the: '
      '"([^"]*)", in the table: "([^"]*)", to be in (ascending|descending)'
      ' order by: (alphabetical|numerical)(?:(?:,  interval (\d+) '
      'second(?:s?))?)$)')
def wait_for_verify_table_sorts(
        context, total_wait, name, table, order, how, interval):
    browser.wait_for(
        '//*[@id="{}"]/tbody/tr[1]'.format(element_ids[table]),
        By.XPATH
    )
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    while time() < timeout:
        values_list = []
        start = 1
        try:
            # Will fail if more than one row is empty
            wait_for_table_element(table, 1, name, clause=By.XPATH)
        except SELENIUM_EXCEPTIONS.NoSuchElementException:
            start = 2
        table_rows_count = len(browser.find_elements_by_xpath(
            '//*[@id="{}"]/tbody/tr'.format(element_ids[table])))
        for i in range(start, table_rows_count + 1):
            value = wait_for_table_element(table, i, name, clause=By.XPATH)
            if isinstance(value, (list)):
                value = value[0].text.splitlines()[0].strip()
                if how == 'numerical':
                    value = value.replace(',', '')
                    value = str(value)
                    if value not in BOTTOM_OF_ASC_TABLE:
                        value = int(value)
                        values_list.append(value)
                else:
                    # AMG strips white space, changes to lower case, and
                    # removes all non-alphanumeric characters before sorting
                    value = value.replace(' ', '')
                    value = value.lower()
                    if value not in BOTTOM_OF_ASC_TABLE:
                        value = re.sub(r'[^a-zA-Z\d:]', '', value)
                        values_list.append(value)
            else:
                value = value.text.splitlines()[0].strip()
                if how == 'numerical':
                    value = value.replace(',', '')
                    value = str(value)
                    if value not in BOTTOM_OF_ASC_TABLE:
                        value = int(value)
                        values_list.append(value)
                else:
                    value = value.replace(' ', '')
                    value = value.lower()
                    if value not in BOTTOM_OF_ASC_TABLE:
                        value = re.sub(r'[^a-zA-Z\d:]', '', value)
                        values_list.append(value)

        if order == 'descending':
            sorted_list = sorted(values_list, reverse=True)
            for value in sorted_list:
                if value in BOTTOM_OF_ASC_TABLE:
                    sorted_list.insert(
                        0, sorted_list.pop(sorted_list.index(value)))
            assert values_list == sorted_list, \
                'Error: Rows not in proper descending order. ' \
                'Correct sorting order: {} Actual sorting order: {}'.format(
                    sorted_list, values_list)
            return
        else:
            sorted_list = sorted(values_list)
            for value in sorted_list:
                if value in BOTTOM_OF_ASC_TABLE:
                    sorted_list.append(sorted_list.pop(
                        sorted_list.index(value)))
            assert values_list == sorted_list, \
                'Error: Rows not in proper ascending order. ' \
                'Correct sorting order: {} Actual sorting order: {}'.format(
                    sorted_list, values_list)
            return
        sleep(interval)
    assert False, "Timed out."


# Hover
@step(u'(?:(?:I|the user) hover over the: "([^"]*)", in row: (\d+), in the'
      ' table: "([^"]*)"(?:(?: for (\d+) second(?:s?))?)$)')
def hover_over_table_elements(context, name, row, table, secs):
    if not secs:
        secs = 5
    elem = wait_for_table_element(table, row, name, clause=By.XPATH)
    browser.hover_on(elem, hover_time=secs)


@step(u'(?:(?:I|the user) hover over the: "([^"]*)", in row: (\d+), in the'
      ' list: "([^"]*)"(?:(?: for (\d+) second(?:s?))?)$)')
def hover_over_list_elements(context, name, row, list, secs):
    if not secs:
        secs = 5
    elem = browser.wait_for(
        '//*[@id="{}"]/li[{}]//*[@data-name="{}"]'.format(
            element_ids[list], row, element_names[name]),
        by=By.XPATH
    )
    browser.hover_on(elem, hover_time=secs)


# Dropdown interaction
@step(
    u'(?:(?:I|the user) select the: (\d+), option from the: "([^"]*)" dropdown'
    '(?:(?:, wait(?:(?: for)?): (\d+) second(?:s?), interval: (\d+)'
    ' second(?:s?))?)$)')
def select_option_from_dropdown(context, row, dropdown, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@id="{}"]/option[{}]'.format(element_ids[dropdown], row)
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) select the: (\d+), option from the: "([^"]*)"'
    ' dropdown, in row: (\d+), in the: "([^"]*)"(?:(?:, wait(?:(?: for)?):'
    ' (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def select_option_from_dropdown_within_repeated_div(
        context, option_row, item, row, menu, total_wait, interval):
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    locator = u'//*[@data-name="{}"][{}]' \
        '//*[@data-name="{}"]/option[{}]'.format(
            element_names[menu], row, element_names[item], option_row)
    element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
    wait_for_element_to_be_clickable_then_click(
        element, timeout, interval, locator)


@step(
    u'(?:(?:I|the user) select the option from the: "([^"]*)" dropdown,'
    ' that contains the text: "([^"]*)"(?:(?:, wait(?:(?: for)?):'
    ' (\d+) second(?:s?), interval: (\d+) second(?:s?))?)$)')
def select_text_option_dropdown(context, dropdown, text, total_wait, interval):
    if (text == SAVE_TEXT_KEYWORD):
        text = scenario.saved_text
    total_wait, interval = set_wait_times(total_wait, interval)
    timeout = time() + total_wait
    xpath = u'//*[@id="{}"]/option'.format(element_ids[dropdown])
    assert wait_for_element_to_be_in_DOM(xpath, timeout, interval)
    while time() < timeout:
        option_list = browser.find_elements_by_xpath(xpath)
        for option in range(len(option_list)):
            locator = u'//*[@id="{}"]/option[{}]'.format(
                element_ids[dropdown], option + 1)
            element = wait_for_element_to_be_in_DOM(locator, timeout, interval)
            contains, elem_text = check_text_in_element(element, text)
            if contains > -1:
                wait_for_element_to_be_clickable_then_click(
                    element, timeout, interval, locator)
                return
    assert False, 'Text in step: {} is not in dropdown'.format(
        text)


# Debug Steps
@step(u'(?:(?:I|the user) print the saved values$)')
def print_saved_values(context):
    if not hasattr(scenario, 'saved_number'):
        scenario.saved_number = 0
    if not hasattr(scenario, 'saved_text'):
        scenario.saved_text = ''
    assert False, "SAVED_TEXT: {}\nSAVED_NUMER: {}".format(
        scenario.saved_text, scenario.saved_number)
