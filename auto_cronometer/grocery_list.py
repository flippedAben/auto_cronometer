import json
import glob
import csv
from collections import defaultdict


def get_grocery_list():
    # Get ingredients data
    header_row = []
    favorite_recipe_data = []
    for recipe_dir in glob.glob('./data/*'):
        with open(f'{recipe_dir}/metadata.json', 'r') as f:
            json_data = json.load(f)
        if json_data['is_favorite']:
            with open(f'{recipe_dir}/ingredients.csv') as f:
                reader = csv.reader(f)
                rows = [row for row in reader]
                if not header_row:
                    header_row = rows[0]

                # Ignore the header row (i.e. first row)
                favorite_recipe_data.extend(rows[1:])

    # Group by 'Description'
    description_i = header_row.index('Description')
    # Only keep 'Amount' and 'Unit' data
    amount_i = header_row.index('Amount')
    unit_i = header_row.index('Unit')
    ingredients = defaultdict(list)
    for row in favorite_recipe_data:
        amount_unit_data = [row[amount_i], row[unit_i]]
        ingredients[row[description_i]].append(amount_unit_data)

    grocery_list = []
    grocery_list.append(['Item', 'Amount', 'Unit', 'Order'])
    # Aggregate similar units
    for name, rows in ingredients.items():
        amounts_per_unit = defaultdict(int)
        for amount, unit in rows:
            amounts_per_unit[unit] += float(amount)

        for unit, amount in amounts_per_unit.items():
            grocery_list.append([name, amount, unit])

    return grocery_list


if __name__ == '__main__':
    get_grocery_list()
