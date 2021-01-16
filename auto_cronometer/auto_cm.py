from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
)
import os


class AutoCronometer():
    def __init__(self):
        self.driver = webdriver.Firefox(
            executable_path=os.environ.get('geckodriver_path'),
            log_path=os.environ.get('geckodriver_log_path'))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def login(self):
        self.driver.get('https://cronometer.com/login/')
        user_ele = self.driver.find_element_by_name('username')
        pass_ele = self.driver.find_element_by_name('password')
        user_ele.send_keys(os.environ.get('cronometer_user'))
        pass_ele.send_keys(os.environ.get('cronometer_pass'))

        submit_button = self.driver.find_element_by_id('login-button')
        submit_button.click()

    def wait_on_ele_id(self, id_name):
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((
                By.ID,
                id_name)))

    def wait_on_ele_class(self, class_name):
        WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located((
                By.CLASS_NAME,
                class_name)))

    def robust_click(self, element):
        """
        Sometimes the "Subscribe to Cronometer Gold" dialog pops up, which can
        block a Selenium mouse click. This will close that dialog before trying
        to click the given element.
        """
        try:
            element.click()
        except ElementClickInterceptedException:
            # Close the dialog
            dialog = self.driver.find_element_by_class_name('popupContent')
            cancel_button = dialog.find_element_by_tag_name('button')
            cancel_button.click()
            print('Closed subscription popup dialog!')

            # Retry
            element.click()
