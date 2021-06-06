import json
import yaml


def create_active_yaml(data_dir):
    with open(f'{data_dir}/recipe_name_to_id.json', 'r') as f:
        name_to_id_json = json.load(f)
        with open('active.yaml', 'w') as f:
            yaml.dump(list(name_to_id_json.keys()), f)
