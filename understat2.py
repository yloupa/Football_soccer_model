
import lxml
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup


def get_matches_data(url: str) -> pd.DataFrame:
    """
    Get matches data of the given championship.

    Args:
        url: URL to the championship understat page
    """
    page_tree = requests.get(url)
    soup_page = BeautifulSoup(page_tree.content, "lxml")  # Use 'html.parser' instead of 'lxml'
    scripts = soup_page.find_all("script")

    matches_data = get_json_data(script=scripts[2])  #see understattest to see how to find it's third script

    return matches_data


def get_json_data(script) -> pd.DataFrame:
    s_string = script.string

    ind_start = s_string.index("('") + 2 #see understat test for beginning of json to see why +2
    ind_end = s_string.index("')")

    j_data = s_string[ind_start:ind_end]
    j_data = j_data.encode("utf-8").decode("unicode_escape")
    js_data = json.loads(j_data)
    if type(js_data) == list:
        data = pd.json_normalize(js_data)
    elif type(js_data) == dict:
        data = pd.json_normalize(js_data.values())

    return data


# Example URL (you can replace with the desired championship page)
url = "https://understat.com/league/EPL"
matches = get_matches_data(url=url)

# Show the first few rows of the matches data
print(matches.head())

# Create a list to hold all expanded records
all_records = []

# Iterate through each team
for _, team_row in matches.iterrows():
    team_id = team_row['id']
    team_title = team_row['title']

    # For each history entry of this team, create a complete record
    for history_entry in team_row['history']:
        # Convert the history entry to a dictionary if it's not already
        if isinstance(history_entry, dict):
            history_dict = history_entry
        else:
            history_dict = json.loads(history_entry) if isinstance(history_entry, str) else {}

        # Create a new record with team info and history data
        complete_record = {
            'id': team_id,
            'title': team_title
        }
        # Add all history fields to the record
        complete_record.update(history_dict)

        # Add to our collection
        all_records.append(complete_record)

# Convert all records to a DataFrame
matches_expanded = pd.DataFrame(all_records)

# Show the first few rows to verify
print(matches_expanded.head())

# Save to CSV
matches_expanded.to_csv('matches_expanded.csv', index=False)