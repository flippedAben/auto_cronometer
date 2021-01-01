import pandas as pd
import fractions
from collections import defaultdict


def info_multiple_versions(group_ing_df):
    multiple_versions_exists = False
    for key, df in group_ing_df:
        df = df[['Unit', 'Recipe']]
        if df.shape[0] > 1:
            if df.index.nunique() > 1:
                print('[Info] Multiple types of version per ingredient found.')
                print()
                multiple_versions_exists = True

    if multiple_versions_exists:
        for key, df in group_ing_df:
            df = df[['Recipe']]
            if df.shape[0] > 1:
                if df.index.nunique() > 1:
                    print(f'"[Info] {key}" has multiple versions:')
                    print(df)
                    print()


def error_multiple_units(group_ing_df):
    multiple_units_exists = False
    for key, df in group_ing_df:
        df = df[['Unit', 'Recipe']]
        if df.shape[0] > 1:
            if df['Unit'].nunique() > 1:
                print('[Error] Multiple types of unit per ingredient found.')
                print('[Error] Until I implement unit conversion, this will be an error.')
                print()
                multiple_units_exists = True
                break

    if multiple_units_exists:
        for key, df in group_ing_df:
            df = df[['Unit', 'Recipe']]
            if df.shape[0] > 1:
                if df.Unit.nunique() > 1:
                    print(f'"[Error] {key}" has multiple units:')
                    print(df)
                    print()
        print('[Error] Exiting...')
        exit(1)


def clean_data(all_ing_pd):
    # Some amounts are in fractions (e.g. 1/2)
    all_ing_pd[['Amount']] = all_ing_pd[['Amount']].applymap(lambda x:
            float(fractions.Fraction(x)))
    # Weight has the unit in it, so take it out...
    all_ing_pd[['Weight']] = all_ing_pd[['Weight']].applymap(lambda x:
            float(x.split(' ')[0]))
    # ... and put it in the column name
    all_ing_pd.rename(columns={'Weight': 'Weight (g)'}, inplace=True)


def get_grocery_list():
    all_ing_pd = pd.read_csv('data/ingredients.csv')

    # Only look at favorited recipes
    # "Favorite" encodes the information: "I'm making the recipe this week"
    all_ing_pd = all_ing_pd.loc[all_ing_pd['Favorite'] == 1]

    clean_data(all_ing_pd)

    # Categorize ingredients (Description) by string up to the first comma
    all_ing_pd = all_ing_pd.set_index('Description')
    group_ing_df = all_ing_pd.groupby(lambda index: index.split(',')[0])

    # Ask user to use a single type of ingredient if possible
    info_multiple_versions(group_ing_df)

    # Ask user to only use one kind of unit per ingredient
    error_multiple_units(group_ing_df)

    # Create aggregated grocery list
    group_desc_df = all_ing_pd.groupby('Description')
    grocery_list = []
    grocery_list.append(['Item', 'Amount', 'Unit', 'Order'])
    for key, df in group_desc_df:
        amount = round(pd.to_numeric(df['Amount']).sum(), 2)
        unit = df['Unit'].unique()[0]
        grocery_list.append([key, amount, unit])

    return grocery_list
