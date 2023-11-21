from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import subprocess
import csv
import fnmatch
import datetime
import time
import random
import csv
import pandas as pd
import argparse
import base64
import pandas as pd
import csv


today = datetime.datetime.now()
formatted_date = today.strftime("%Y-%m-%d")

# Specify the directory path you want to create
pp_result_data_path = 'normalized_props'

# Check if the directory already exists
if not os.path.exists(pp_result_data_path):
    # If it doesn't exist, create the directory
    os.makedirs(pp_result_data_path)
    print(f"Directory '{pp_result_data_path}' created.")
else:
    print(f"Directory '{pp_result_data_path}' already exists.")

def find_newest_file_from_day(directory_path, specific_day):
    # Initialize variables to store information about the newest file
    newest_file = None
    newest_file_time = None

    # Iterate over the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path):
            file_time = os.path.getctime(file_path)
            file_date = str(datetime.datetime.fromtimestamp(file_time).date())

            # Check if the file's date matches the specific day
            if file_date == specific_day:
                # If it's the first file matching the specific day or newer than the previous newest file
                if newest_file is None or file_time > newest_file_time:
                    newest_file = file_path
                    newest_file_time = file_time

    return newest_file



print(f"Running for date {formatted_date}.")


# Navigate to the desired URL (base 64 encoded)
url = "aHR0cHM6Ly9zdGF0cy51bmRlcmRvZ2ZhbnRhc3kuY29tL3YxL3RlYW1z="
decoded_url = base64.b64decode(url).decode()

print("decoded_url",decoded_url, flush=True)
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

driver.get(decoded_url)

# Wait for at least one <pre> element to load (adjust the timeout as needed)
wait = WebDriverWait(driver, 10)
elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'pre')))

# Initialize an empty list to store the text content of all <pre> elements
json_data_list = []

# Extract the text content of all <pre> elements
for element in elements:
    json_data_list.append(element.text)

# Attempt to parse the extracted text as JSON
try:
    # Combine the text content of all <pre> elements into a single JSON string
    combined_json_data = ''.join(json_data_list)
    
    teams = json.loads(combined_json_data)
except json.JSONDecodeError:
    print("The extracted text is not valid JSON.")

# Close the browser window
driver.quit()

ud_teams = {}

for val in teams['teams']:
    ud_teams[val['id']] = val

# Example usage:
directory_path = "ud_data"
newest_file = find_newest_file_from_day(directory_path, formatted_date)

print("newest_file",newest_file)

with open(str(newest_file), 'rb') as f:
    f_data = f.read()
    
json_info = json.loads(f_data.decode('utf-8'))

ud_appearances = {};
for val in json_info["appearances"]:
    ud_appearances[val["id"]] = val

ud_games = {}
for val in json_info["games"]:
    ud_games[val["id"]] = val


ud_players = {}
for val in json_info["players"]:
    ud_players[val["id"]] = val

ud_solo_games = {}
for val in json_info["solo_games"]:
    ud_solo_games[val["id"]] = val

#print("ud_appearances",ud_appearances);
#print("ud_games",ud_games);
#print("ud_over_under_lines",ud_over_under_lines);
#print("ud_players",ud_players);
#print("ud_solo_games",ud_solo_games);


# Define the CSV file name with the current date
csv_file_name = f"normalized_props/ud_props_{formatted_date}.csv"

# Define the CSV headers
csv_headers = ["Title", "Prop Name", "Prop Display Name", "First Name", "Last Name", "Full Name", "Sport", "Stat Value",
               "Scheduled Time", "Match Title", "Team Name", "Team Abbr", "Boosted", "Boosted Multiplier", "Boosted Choice"]


with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer object
    csvwriter = csv.writer(csvfile)

    # Write the headers to the CSV file
    csvwriter.writerow(csv_headers)
    
    for val in json_info["over_under_lines"]:
        #print(val)
        title = val['over_under']['title']
        prop_name = val['over_under']['appearance_stat']['stat']
        prop_display_name = val['over_under']['appearance_stat']['display_stat']
        appearance_id = val["over_under"]["appearance_stat"]['appearance_id']
        stat_value = val['stat_value']
        appearance = ud_appearances[appearance_id]
        team_id = appearance["team_id"]
        match_id = appearance["match_id"]
        match_type = appearance["match_type"]
        position_id = appearance["position_id"]
        player_id = appearance["player_id"]
        player = ud_players[player_id]
        first_name = player["first_name"]
        last_name = player["last_name"]
        full_name = ""
        if first_name and last_name:
            full_name = first_name+ " "+last_name
        elif first_name:
            full_name = first_name
        elif last_name:
            full_name = last_name            
        
        sport = player["sport_id"]
        team_name = ""
        team_abbr = ""
        if team_id is not None and team_id in ud_teams:
            team_name = ud_teams[team_id]['name']
            team_abbr = ud_teams[team_id]['abbr']
        
        boosted = False
        boosted_multiplier = ""
        boosted_choice = ""
        
        if len(val['options']) == 1:
           # print(option)
            option = val['options'][0]
            if option['payout_multiplier'] != "1.0":
                boosted = True
                boosted_multiplier = option['payout_multiplier']
                boosted_choice = option['choice']

        game = ""
        scheduled_time = ""
        title = ""
        if "SoloGame" == match_type:
            game = ud_solo_games[match_id]
            scheduled_time = game['scheduled_at']
            title = game['title']   
        else:
            game = ud_games[match_id]
            scheduled_time = game['scheduled_at']
            title = game['title']  
        

        
        csvwriter.writerow([title, prop_name, prop_display_name, first_name, last_name, full_name, sport, stat_value,
                            scheduled_time, title, team_name, team_abbr, boosted, boosted_multiplier, boosted_choice])

# Print a message indicating the CSV file has been created
print(f"CSV file '{csv_file_name}' created.")

print("Cleaning up",newest_file)
os.remove(newest_file)