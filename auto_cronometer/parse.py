import fractions
import json
import os
import re
from bs4 import BeautifulSoup


def parse_table(table):
    data = []
    rows = table.find_all('tr')
    for raw_row in rows:
        row = [td.text for td in raw_row.find_all('td')]
        data.append(row)
    return data


def clean_ingredients_data(data):
    """
    Destructively cleans data.
    """
    # Discard empty last column
    for i in range(len(data)):
        data[i] = data[i][:-1]

    header_row = data[0]
    header_row.append('Weight Unit')
    amount_i = header_row.index('Amount')
    weight_i = header_row.index('Weight')
    calories_i = header_row.index('Calories')
    for i in range(1, len(data)):
        # Amount should be a float, not a fraction
        data[i][amount_i] = float(fractions.Fraction(data[i][amount_i]))

        data[i][calories_i] = float(data[i][calories_i])

        # Take the unit out of weight, and put it in its own column
        number, unit = data[i][weight_i].split(' ')
        data[i][weight_i] = float(number)
        data[i].append(unit)


def clean_nutrition_data(data):
    """
    Destructively cleans data coming from one of the nutrition tables.
    """
    # This header column is blank, but it should be Unit
    data[0][2] = 'Unit'
    for i in range(1, len(data)):
        # Removing leading white space
        data[i][0] = data[i][0].strip()


def parse_recipe_htmls(html_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    cronometer_id_re = re.compile(r'Recipe #(\d+),.*')

    htmls = os.listdir(html_dir)
    for html in htmls:
        recipe_json = {}
        recipe_html_id = int(os.path.splitext(html)[0].split('_')[1])
        recipe_json['html_id'] = recipe_html_id

        with open(f'{html_dir}/{html}', 'r') as f:
            html = f.read()
            soup = BeautifulSoup(html, 'lxml')
            main_div = soup.find(
                'div',
                {'class': 'admin-food-editor-content-area'}
            )

            recipe_name = main_div.find(
                'div',
                {'class': 'admin-food-name'})
            recipe_json['name'] = recipe_name.text

            star_img = main_div.find(
                'img',
                {'title': 'Add to favorites'})
            recipe_json['favorite'] = 'star_unselected' not in star_img['src']

            recipe_number = main_div.find(lambda x: 'Recipe #' in x.text)
            match = cronometer_id_re.match(recipe_number.text)
            if match:
                cronometer_id = match.group(1)
                recipe_json['cronometer_id'] = cronometer_id

            tables = main_div.find_all(
                'table',
                {'class': 'prettyTable'})
            ingredients_table = tables[1]
            ingredients = parse_table(ingredients_table)
            clean_ingredients_data(ingredients)
            recipe_json['ingredients'] = ingredients

            nutrition_tables = tables[2:]
            for nutrition_table in nutrition_tables:
                nutrition = parse_table(nutrition_table)
                clean_nutrition_data(nutrition)
                # Type of nutrition is stored here
                nutrition_type = nutrition[0][0]
                recipe_json[nutrition_type.lower()] = nutrition

        with open(f'{out_dir}/recipe_{cronometer_id}.json', 'w') as f:
            json.dump(recipe_json, f)
