import csv
import fractions
import json
import os

import auto_cronometer.auto_cm as auto_cm


def parse_table(table):
    data = []
    rows = table.find_elements_by_tag_name('tr')
    for raw_row in rows:
        row = [td.text for td in raw_row.find_elements_by_tag_name('td')]
        data.append(row)
    return data


def clean_ingredients_data(data):
    """
    Destructively cleans data.
    """
    data[0].append('Weight Unit')
    for i in range(1, len(data)):
        # Amount should be a float, not a fraction
        data[i][1] = float(fractions.Fraction(data[i][1]))

        # Take the unit out of weight, and put it in its own column
        number, unit = data[i][-1].split(' ')
        data[i][-1] = number
        data[i].append(unit)


def clean_nutrition_data(data):
    """
    Destructively cleans data coming from one of the nutrition tables.
    """
    data[0][2] = 'Unit'
    for i in range(1, len(data)):
        # Removing leading white space
        data[i][0] = data[i][0].strip()


def ingredients_table_to_csv(table, clean_data_func, out_dir):
    data = parse_table(table)
    clean_data_func(data)
    with open(f'{out_dir}/ingredients.csv', 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)


def nutrition_table_to_csv(table, clean_data_func, out_dir):
    data = parse_table(table)
    clean_data_func(data)
    with open(f'{out_dir}/{data[0][0].lower()}.csv', 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)


def normalize_recipe_name(raw_recipe_name):
    # Only take alphanumerics and white space
    normalized_name = [
        c
        for c in raw_recipe_name.lower()
        if c.isalnum() or c.isspace()
    ]

    # Convert white space to underscore
    normalized_name = ''.join(map(
        lambda c: '_' if c.isspace() else c,
        normalized_name))
    return normalized_name


def scrape_recipes():
    # Enable headless Firefox
    os.environ['MOZ_HEADLESS'] = '1'

    # TODO this is kind of slow. See if you can make it faster.
    with auto_cm.AutoCronometer() as ac:
        ac.login()
        ac.go_to_recipes_tab()

        print('Scraping recipes and storing data...')
        recipes = ac.get_recipes_list_items()
        for _, recipe in enumerate(recipes):
            # Hack: the recipe element goes stale quickly, so get it again
            # Maybe we don't need the hack anymore?
            # recipe = recipe_div.find_elements_by_tag_name('a')[i]
            recipe_details = ac.get_recipe_details_pane(recipe)
            recipe_name = ac.get_recipe_title(recipe_details).text
            normalized_name = normalize_recipe_name(recipe_name)

            recipe_data_dir = f'data/{normalized_name}'
            # This directory will store CSV files for this recipe
            os.makedirs(recipe_data_dir, exist_ok=True)

            # Write some metadata about the recipe
            metadata = {
                'original_name': recipe_name,
                'is_favorite': ac.is_recipe_favorite(recipe_details)
            }
            print(metadata)

            with open(f'{recipe_data_dir}/metadata.json', 'w') as f:
                json.dump(metadata, f)

            tables = recipe_details.find_elements_by_class_name('prettyTable')
            ingredients_table = tables[1]
            ingredients_table_to_csv(
                ingredients_table,
                clean_ingredients_data,
                recipe_data_dir
            )

            # The nutrition tables have similar structure
            for nutrition_table in tables[2:]:
                # Assume the top left entry is the table name
                nutrition_table_to_csv(
                    nutrition_table,
                    clean_nutrition_data,
                    recipe_data_dir
                )
