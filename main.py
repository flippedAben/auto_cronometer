import argparse

import auto_cronometer
import cloudify
import secrets


description_help ="""
Automate food/nutrition bookkeeping tasks.

Supported commands

    scrape: scrape Cronometer's recipe ingredients into a CSV
    diary:  add current set of favorite recipes to today's diary
    cloud:  put the grocery list on the cloud
"""


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description_help
    )
    parser.add_argument(
        'command',
    )
    args = parser.parse_args()
    if args.command == 'scrape':
        auto_cronometer.scrape_to_csv()
    elif args.command == 'diary':
        auto_cronometer.add_starred_recipes_to_diary()
    elif args.command == 'cloud':
        cloudify.upload_grocery_list()
    else:
        print(f'[Error] The command "{args.command}" is not supported.')


if __name__ == '__main__':
    main()
