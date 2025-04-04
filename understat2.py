
import lxml
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from typing import Sequence
import time




def get_matches_data(url: str) -> pd.DataFrame:
    """
    Get matches data of the given championship.

    Args:
        url: URL to the championship understat page
    """
    page_tree = requests.get(url)
    soup_page = BeautifulSoup(page_tree.content, "lxml")
    scripts = soup_page.find_all("script")

    matches_data = get_json_data(script=scripts[2])  #see understattest to see how to find it's third script

    league, season = url.split("/")[-2:]
    matches_data["league"] = league
    matches_data["season"] = f"{int(season)}-{int(season)+1}"

    return matches_data

def get_matches_data_multi_seasons(
    url: str, seasons: Sequence[int]=list(range(2014, 2025, 1)) #make sure range is only to 2025, 2024 and 2025 url return the same data creating duplicates
) -> pd.DataFrame:
    all_data = []
    for season in seasons:
        season_url = f"{url}/{season}"
        season_matches_data = get_matches_data(url=season_url)

        all_data.append(season_matches_data)

        time.sleep(1) #in case of limiting

    all_data = pd.concat(all_data, axis=0)

    return all_data.reset_index(drop=True)


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
matches = get_matches_data_multi_seasons(url=url)

# if you only want to get the current season use below
# matches=get_matches_data(url=url)


# Show the first few rows of the matches data
pd.set_option('display.max_columns', None)
print(matches.head())

pd.reset_option('display.max_columns')

# Create a list to hold all expanded records
all_records = []

# Iterate through each team
for _, team_row in matches.iterrows():
    team_id = team_row['id']
    team_title = team_row['title']
    team_league = team_row['league']
    team_season = team_row['season']

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
            'title': team_title,
            'league': team_league,
            'season': team_season
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