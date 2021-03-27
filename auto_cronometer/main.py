#!/usr/bin/env python3
"""Usage:
    auto_cm scrape [--html_dir DIR]
    auto_cm parse <html_dir> [--json_dir DIR]
    auto_cm diary
    auto_cm cloud

Automate food/nutrition bookkeeping tasks.

Commands:
    scrape    Scrape Cronometer's website for recipe HTMLs.
    parse     Parse scraped HTMLs in <html_dir> into JSON files.
    diary     Add current set of favorite recipes to today's diary.
    cloud     Put the grocery list on the cloud.

Options:
    --html_dir DIR    Store the HTMLs in DIR [default: raw_htmls]
    --json_dir DIR    Store the JSONs in DIR [default: data]

"""
from docopt import docopt
import auto_cronometer.scrape as scrape
import auto_cronometer.parse as parse
import auto_cronometer.update_diary as update_diary
import auto_cronometer.cloudify as cloudify


def main():
    args = docopt(__doc__)
    if args['scrape']:
        scrape.scrape_recipes(args['--html_dir'])
    elif args['parse']:
        parse.parse_recipe_htmls(args['<html_dir>'], args['--json_dir'])
    elif args['diary']:
        update_diary.add_starred_recipes_to_diary()
    elif args['cloud']:
        cloudify.upload_grocery_list()


if __name__ == '__main__':
    main()
