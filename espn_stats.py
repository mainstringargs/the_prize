import requests
import pandas as pd
import csv
from collections.abc import Mapping, Iterable
import json
import os
from datetime import datetime
import pytz
import argparse
import base64

# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")

parser.add_argument("--sport", type=str, default="nfl", help="Sport")
parser.add_argument("--year", type=int, default=2023, help="Year")
parser.add_argument("--week", type=int, default=1, help="Week")

# Parse arguments
args = parser.parse_args()

# Access argument values
year = str(args.year).strip()
week = str(args.week).strip()
sport = str(args.sport).strip().lower()

print("Grabbing....",year,week)

# Specify the directory path you want to create
directory_path = 'processing'

# Check if the directory already exists
if not os.path.exists(directory_path):
    # If it doesn't exist, create the directory
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")
else:
    print(f"Directory '{directory_path}' already exists.")


def is_float(string):
    if string.replace(".", "").isnumeric():
        return True
    else:
        return False
        
def get_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request fails
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {str(e)}")
    except ValueError as e:
        print(f"JSON parsing failed: {str(e)}")
    return None
    
    
url = "aHR0cHM6Ly9jZG4uZXNwbi5jb20vY29yZS8="
decoded_url = base64.b64decode(url).decode()

print("decoded_url",decoded_url, flush=True)

def get_schedule(year, week):
    url = f"{decoded_url}{sport}/schedule?xhr=1&year={year}&week={week}"
    json_data = get_json_data(url)
    return json_data

def get_game_stats(game_id):
    url = f"{decoded_url}{sport}/boxscore?xhr=1&gameId={game_id}"
    json_data = get_json_data(url)
    
    if json_data:
        game_athletes = []
        home_team_stats = json_data.get("gamepackageJSON", {}).get("boxscore", {}).get("players", [])[1]
        away_team_stats = json_data.get("gamepackageJSON", {}).get("boxscore", {}).get("players", [])[0]
        
        def process_team_stats(team_stats, home_flag):
            team_name = team_stats.get("team", {}).get("displayName", "")
            stat_categories = team_stats.get("statistics", [])
            for stat_cat in stat_categories:
                stat_fields = (stat_cat.get("keys", ""))
                stat_name = stat_cat.get("name", "")
                for athlete in stat_cat.get("athletes", []):
                    athlete_name = athlete.get("athlete", {}).get("displayName", "")
                    stats = athlete.get("stats")
                    athlete_stats = {
                        "name": athlete_name,
                        "team": home_team_name if home_flag else away_team_name,
                        "opp": home_team_name if not home_flag else away_team_name,
                        "home": home_flag,
                    }
                    for field in stat_fields:
                        if is_float(stats[stat_fields.index(field)]):
                            athlete_stats[field]=float(stats[stat_fields.index(field)])
                        else:
                            athlete_stats[field]=stats[stat_fields.index(field)]
                    stat_tuple = athlete_stats
                    #print(stat_tuple);
                    #athlete_stats[f"{stat_name}_stats"] = [stat_tuple]
                    game_athletes.append(athlete_stats)
                    #print(athlete_stats)
        
        home_team_name = home_team_stats.get("team", {}).get("displayName", "")
        away_team_name = away_team_stats.get("team", {}).get("displayName", "")
        
        process_team_stats(home_team_stats, home_flag=True)
        process_team_stats(away_team_stats, home_flag=False)
        
        return game_athletes

    return []
    

# Call the function to retrieve and parse the JSON data
json_data = get_schedule(year, week)

date_format = "%Y-%m-%dT%H:%MZ"
        
if json_data:
    schedule_data = json_data.get("content", {}).get("schedule", {})
    all_scheduled_games = []

    for day in schedule_data:
        games = schedule_data[day]
        for game in games.get("games", []):
            all_scheduled_games.append((game.get("date", ""), game.get("name", ""), game.get("id", "")))

    all_games_stats = []
    
    for game in all_scheduled_games:
        print("processing",game,(game[2]))
        # Call the function to retrieve and merge the stats into a single DataFrame

        date = datetime.strptime(game[0], date_format)
        
        date = pytz.utc.localize(date)

        # Get the current time in UTC
        current_time = datetime.now(pytz.utc)

        # Compare the two datetime objects
        if date < current_time:
            all_games_stats.extend(get_game_stats(game[2]))
        else:
            print(game,"hasn't happened yet")

    # Print the combined DataFrame
    #print(all_games_stats, flush=True)    
    with open("processing/espn_"+sport+"_actuals_"+str(year)+"_week_"+str(week)+".json", 'w', encoding='utf-8') as f:
        json.dump(all_games_stats, f, ensure_ascii=False, indent=4)
