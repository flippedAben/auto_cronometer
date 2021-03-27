#!/usr/bin/env python3
"""Usage:
    auto_cm scrape [--all]
    auto_cm diary
    auto_cm cloud

Automate food/nutrition bookkeeping tasks.

Commands:
    scrape    Scrape Cronometer's website for ingredient information. By
              default, scrapes the ingredients only.
    diary     Add current set of favorite recipes to today's diary
    cloud     Put the grocery list on the cloud

"""
from docopt import docopt
import auto_cronometer.scrape as scrape
import auto_cronometer.update_diary as update_diary
import auto_cronometer.cloudify as cloudify


def main():
    args = docopt(__doc__)
    if args['scrape']:
        scrape.scrape_recipes(args['--all'])
    elif args['diary']:
        update_diary.add_starred_recipes_to_diary()
    elif args['cloud']:
        cloudify.upload_grocery_list()


if __name__ == '__main__':
    main()
