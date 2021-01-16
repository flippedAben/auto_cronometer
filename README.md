# Automatic Cronometer

A CLI tool for working with Cronometer.

## Assumptions

- Recipe names are unique (after converting to lower case and removing symbols
  and converting white space to underscore)

## Setup

The setup takes quite a bit of effort.

### Download `geckodriver`

- Get the latest release from [the GitHub page](https://github.com/mozilla/geckodriver/releases).
- `tar xzf <the geckodriver tar.gz>`

### Generate `client_id.json`

Basically follow the instructions in the Quickstart of the Google Sheets API v4 page.

### Create `config.sh`

This file should look like this:

```python3
geckodriver_path=<path to geckodriver>
cronometer_user=<cronometer username>
cronometer_pass=<cronometer password>
google_sheets_api_sheet_id=<existing google sheet that will contain the grocery list>
google_sheets_api_client_id_path=<path to client_id.json>
google_sheets_api_token_pickle_path=<path to token.pickle>
```

Don't share it with anyone. Apply your own security measures.
