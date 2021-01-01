from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)
import pandas as pd


WAIT_SECONDS = 3


def login(driver):
    import secrets
    driver.get('https://cronometer.com/login/')
    user_ele = driver.find_element_by_name('username')
    pass_ele = driver.find_element_by_name('password')
    user_ele.send_keys(secrets.u)
    pass_ele.send_keys(secrets.p)

    submit_button = driver.find_element_by_id('login-button')
    submit_button.click()


def robust_click(element, driver):
    """
    Sometimes the "Subscribe to Cronometer Gold" dialog pops up, which can
    block a Selenium mouse click. If this will close that dialog before trying
    to click the given element.
    """
    try:
        element.click()
    except ElementClickInterceptedException:
        # close dialog
        cancel_button = driver.find_element_by_class_name('GHDCC5OBEIC')
        cancel_button.click()
        print('Closed subscription popup dialog!')

        # retry clicking the element
        element.click()


def scrape_recipe_ingredients(driver):
    grocery_list_data = []
    headers = []

    try:
        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.ID, "navArea"))
        )
        print('Top level navigator loaded')
        driver.get('https://cronometer.com/#foods')

        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.CLASS_NAME, "gwt-DecoratedTabPanel"))
        )
        print('Food tab navigator loaded')
        tabs = driver.find_elements_by_class_name('gwt-TabBarItem-wrapper')
        for tab in tabs:
            tab_label = tab.find_element_by_class_name('gwt-Label')
            if tab_label.text.endswith('Recipes'):
                robust_click(tab_label, driver)
                break

        recipe_div = driver.find_element_by_class_name('GHDCC5OBJRB')
        recipes = recipe_div.find_elements_by_class_name('gwt-Anchor')
        for recipe in recipes:
            robust_click(recipe, driver)
            WebDriverWait(driver, WAIT_SECONDS).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'admin-food-name'))
            )
            recipe_title = driver.find_element_by_class_name('admin-food-name')
            print(f'{recipe_title.text} pane loaded')

            is_favorite = True
            # Is the recipe favorited/starred?
            star_div = driver.find_element_by_class_name('GHDCC5OBEO')
            star_img = star_div.find_element_by_tag_name('img')
            star_src = star_img.get_attribute('src')
            if 'fav_star_unselected' in star_src:
                is_favorite = False

            # Add ingredients
            ingredients = driver.find_element_by_class_name('GHDCC5OBPO')
            ingredients_table_div = ingredients.find_element_by_class_name('GHDCC5OBKO')
            ingredients_table = ingredients_table_div.find_elements_by_tag_name('tr')
            if not headers:
                headers = [
                    td.text
                    for td
                    in ingredients_table[0].find_elements_by_tag_name('td')]
                headers.append('Recipe')
                headers.append('Favorite')
            for raw_row in ingredients_table[1:]:
                row = [td.text for td in raw_row.find_elements_by_tag_name('td')]
                row.append(recipe_title.text)
                row.append(int(is_favorite))
                grocery_list_data.append(row)
    except TimeoutException:
        print('An element took too long to load. Re run the script.')

    return grocery_list_data, headers

# Enable headless Firefox
import os
os.environ['MOZ_HEADLESS'] = '1'

print('Scraping ingredient information off Cronometer...')
data = []
headers = []
with webdriver.Firefox(executable_path='./geckodriver') as driver:
    login(driver)
    data, headers = scrape_recipe_ingredients(driver)
print()

all_ing_pd = pd.DataFrame(data, columns=headers)
all_ing_pd.to_csv('data/ingredients.csv')
