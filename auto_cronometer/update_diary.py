import os
import yaml
import auto_cronometer.auto_cm as auto_cm


def add_active_recipes_to_diary():
    # Get the active recipes list
    with open('active.yaml', 'r') as f:
        active_names = yaml.load(f, Loader=yaml.Loader)

    # Enable headless Firefox
    os.environ['MOZ_HEADLESS'] = '1'

    with auto_cm.AutoCronometer() as ac:
        ac.login()
        ac.go_to_recipes_tab()

        print("Adding active recipes to today's diary entry...")
        recipes = ac.get_recipes_list_items()
        for _, recipe in enumerate(recipes):
            details = ac.get_recipe_details_pane(recipe)
            name = ac.get_recipe_title(details).text
            if name in active_names:
                print(name)
                # Should be the first button found in the details pane
                add_to_diary_button = details.find_element_by_tag_name(
                    'button')
                ac.robust_click(add_to_diary_button)

                # Add recipe
                ac.wait_on_ele_class('btn-orange-flat')
                add_recipe_button = ac.driver.find_element_by_class_name(
                    'btn-orange-flat')
                ac.robust_click(add_recipe_button)
