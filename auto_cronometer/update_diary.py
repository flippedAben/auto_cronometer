import os

import auto_cronometer.auto_cm as auto_cm


def add_starred_recipes_to_diary():
    # Enable headless Firefox
    os.environ['MOZ_HEADLESS'] = '1'

    with auto_cm.AutoCronometer() as ac:
        ac.login()
        ac.go_to_recipes_tab()

        print('Adding favorite/starred recipes to today\'s diary entry...')
        recipes = ac.get_recipes_list_items()
        for _, recipe in enumerate(recipes):
            details = ac.get_recipe_details_pane(recipe)
            if ac.is_recipe_favorite(details):
                print(ac.get_recipe_title(details).text)

                # Should be the first button found in the details pane
                add_to_diary_button = details.find_element_by_tag_name(
                    'button')
                ac.robust_click(add_to_diary_button)

                # Add recipe
                ac.wait_on_ele_class('btn-orange-flat')
                add_recipe_button = ac.driver.find_element_by_class_name(
                    'btn-orange-flat')
                ac.robust_click(add_recipe_button)
    print()
