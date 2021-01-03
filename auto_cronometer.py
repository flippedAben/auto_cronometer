from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)
import os
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


def iterate_over_recipes(driver, function):
    """
    Applies "function" to all recipe DOM elements.
    """
    recipe_data = {}
    try:
        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.ID, "navArea"))
        )
        driver.get('https://cronometer.com/#foods')

        WebDriverWait(driver, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.CLASS_NAME, "gwt-DecoratedTabPanel"))
        )
        tabs = driver.find_elements_by_class_name('gwt-TabBarItem-wrapper')
        for tab in tabs:
            tab_label = tab.find_element_by_class_name('gwt-Label')
            if tab_label.text.endswith('Recipes'):
                robust_click(tab_label, driver)
                break

        recipe_div = driver.find_element_by_class_name('GHDCC5OBJRB')
        recipes = recipe_div.find_elements_by_tag_name('a')
        for i, recipe in enumerate(recipes):
            # Hack: the recipe element goes stale quickly, so get it again
            recipe = recipe_div.find_elements_by_tag_name('a')[i]
            props = {
                'name': recipe.text
            }
            robust_click(recipe, driver)
            WebDriverWait(driver, WAIT_SECONDS).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'admin-food-name'))
            )

            # Is the recipe favorited/starred?
            props['is_favorite'] = True
            star_div = driver.find_element_by_class_name('GHDCC5OBEO')
            star_img = star_div.find_element_by_tag_name('img')
            star_src = star_img.get_attribute('src')
            if 'fav_star_unselected' in star_src:
                props['is_favorite'] = False

            recipe_data[props['name']] = function(driver, props)
    except TimeoutException:
        print('An element took too long to load. Re run the script.')

    return recipe_data


def scrape_recipe_ingredients(driver, recipe_props):
    print(recipe_props['name'])
    is_favorite = recipe_props['is_favorite']

    grocery_list_data = []
    headers = []

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
        grocery_list_data.append(headers)
    for raw_row in ingredients_table[1:]:
        row = [td.text for td in raw_row.find_elements_by_tag_name('td')]
        row.append(recipe_props['name'])
        row.append(int(is_favorite))
        grocery_list_data.append(row)

    return grocery_list_data


def scrape_to_csv():
    # Enable headless Firefox
    os.environ['MOZ_HEADLESS'] = '1'

    print('Scraping recipe ingredient info from Cronometer...')
    data = []
    headers = []
    with webdriver.Firefox(executable_path='./geckodriver') as driver:
        login(driver)
        recipe_data = iterate_over_recipes(driver, scrape_recipe_ingredients)
        for recipe, grocery_table in recipe_data.items():
            if not headers:
                headers = grocery_table[0]
            data.extend(grocery_table[1:])
    print()

    all_ing_pd = pd.DataFrame(data, columns=headers)
    all_ing_pd.to_csv('data/ingredients.csv')


def add_recipe_to_diary(driver, recipe_props):
    is_favorite = props['is_favorite']

    # Click add to diary
    if is_favorite:
        print(recipe_props['name'])
        add_to_diary_button = driver.find_element_by_class_name('GHDCC5OBKN')
        robust_click(add_to_diary_button, driver)
        try:
            # Wait for add modal to show
            WebDriverWait(driver, WAIT_SECONDS).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'btn-orange-flat'))
            )
            # Add recipe
            add_recipe_button = driver.find_element_by_class_name('btn-orange-flat')
            robust_click(add_recipe_button, driver)
        except TimeoutException:
            print('The "add to diary" modal took too long to load. Re run the script.')
    return 0


def add_starred_recipes_to_diary():
    # Enable headless Firefox
    os.environ['MOZ_HEADLESS'] = '1'

    print('Adding favorite/starred recipes to today\'s diary entry...')
    with webdriver.Firefox(executable_path='./geckodriver') as driver:
        login(driver)
        iterate_over_recipes(driver, add_recipe_to_diary)
    print()

