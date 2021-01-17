#!/usr/bin/env python3
import argparse

import auto_cronometer.scrape as scrape
import auto_cronometer.update_diary as update_diary
import auto_cronometer.cloudify as cloudify


class AutoCMParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()


description_help = """
Automate food/nutrition bookkeeping tasks

Supported commands

    scrape: scrape Cronometer's recipe ingredients into a CSV
    diary:  add current set of favorite recipes to today's diary
    cloud:  put the grocery list on the cloud

"""


def main():
    parser = AutoCMParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description_help
    )
    parser.add_argument(
        'command',
    )
    args = parser.parse_args()
    if args.command == 'scrape':
        scrape.scrape_recipes()
    elif args.command == 'diary':
        update_diary.add_starred_recipes_to_diary()
    elif args.command == 'cloud':
        cloudify.upload_grocery_list()


if __name__ == '__main__':
    main()
