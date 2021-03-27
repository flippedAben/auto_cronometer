import json
import yaml
from collections import defaultdict


def get_grocery_list(data_dir):
    # Get the active recipes list
    with open('active.yaml', 'r') as f:
        active_recipes = yaml.load(f, Loader=yaml.Loader)

    header_row = []
    recipe_data = []
    # Get ingredients data
    for active_recipe in active_recipes:
        recipe_id = active_recipe['id']
        with open(f'{data_dir}/recipe_{recipe_id}.json', 'r') as f:
            json_data = json.load(f)

            ingredients = json_data['ingredients']
            rows = [row for row in ingredients]
            if not header_row:
                header_row = rows[0]

            # Ignore the header row (i.e. first row)
            recipe_data.extend(rows[1:])

    # Group by 'Description'
    description_i = header_row.index('Description')
    # Only keep 'Amount' and 'Unit' data
    amount_i = header_row.index('Amount')
    unit_i = header_row.index('Unit')
    ingredients = defaultdict(list)
    for row in recipe_data:
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
    for row in get_grocery_list('data'):
        print(row)
