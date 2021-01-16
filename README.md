# Automatic Cronometer

`auto-cm` is a CLI tools for working with Cronometer.

## Grocery list creation with nutrition info

The command: `auto-cm`

1. Scrapes Cronometer for your recipes.
2. Adds all starred recipes to today's diary
3. Uploads the grocery list to a Google Sheet on the cloud.

## Assumptions

- Recipe names are unique (after converting to lower case and removing symbols
  and converting white space to underscore)

## Setup

The setup takes quite a bit of effort.

### Create configuration files

#### `secrets.py`

This file should look like this:

```python3
u = <Cronometer username>
p = <Cronometer password>
sheet_id = <Existing Google Sheet that will contain the grocery list>
```

Don't share it with anyone. Apply your own security measures.

#### `client_id.json`

Basically follow the instructions in the Quickstart of the Google Sheets API v4 page.
