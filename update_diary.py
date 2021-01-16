from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import fractions
import json
import os


# def add_recipe_to_diary(driver, recipe_props):
    # is_favorite = recipe_props['is_favorite']

    # # Click add to diary
    # if is_favorite:
        # print(recipe_props['name'])
        # add_to_diary_button = driver.find_element_by_class_name('GHDCC5OBKN')
        # robust_click(add_to_diary_button, driver)
        # try:
            # # Wait for add modal to show
            # WebDriverWait(driver, WAIT_SECONDS).until(
                # EC.presence_of_element_located((
                    # By.CLASS_NAME,
                    # 'btn-orange-flat'))
            # )
            # # Add recipe
            # add_recipe_button = driver.find_element_by_class_name(
                # 'btn-orange-flat')
            # robust_click(add_recipe_button, driver)
        # except TimeoutException:
            # print('The "add to diary" modal took too long to load.')
    # return 0


# TODO reimplement this
# def add_starred_recipes_to_diary():
    # # Enable headless Firefox
    # os.environ['MOZ_HEADLESS'] = '1'

    # print('Adding favorite/starred recipes to today\'s diary entry...')
    # with webdriver.Firefox(executable_path='./geckodriver') as driver:
        # login(driver)
        # iterate_over_recipes(driver, add_recipe_to_diary)
    # print()
