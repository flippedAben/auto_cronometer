import os
import json
import yaml


def create_active_yaml(data_dir):
    doc = []
    for json_file in os.listdir(data_dir):
        with open(f'{data_dir}/{json_file}', 'r') as f:
            recipe_json = json.load(f)
            item = {
                'id': recipe_json['cronometer_id'],
                'name': recipe_json['name'],
            }
            doc.append(item)

    with open('active.yaml', 'w') as f:
        yaml.dump(doc, f)
