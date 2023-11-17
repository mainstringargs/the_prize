import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import csv
import fnmatch
import datetime
import time
import random
import pytz
import argparse
import json
import mapped_pp_stats
import os
import json
import datetime
import base64

import os
import datetime
import json

league = "NFL"

# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")

parser.add_argument("--league", type=str, default=league, help="league")

args = parser.parse_args()

# Access argument values
league = str(args.league)

print("LEAGUE IS",league);

def load_newest_json_file_from_date(directory_path, target_date):
    def is_target_date_file(file_path, target_date):
        file_stat = os.stat(file_path)
        file_modified_date = datetime.date.fromtimestamp(file_stat.st_mtime)
        return file_modified_date == target_date

    # List all files in the directory
    all_files = os.listdir(directory_path)

    # Filter JSON files for the target date
    target_date_files = [file for file in all_files if is_target_date_file(os.path.join(directory_path, file), target_date) and file.endswith('.json')]

    if target_date_files:
        # Sort the files by modification time to get the newest one
        newest_file = max(target_date_files, key=lambda f: os.path.getmtime(os.path.join(directory_path, f)))
        full_path_to_newest_file = os.path.join(directory_path, newest_file)
        
        # Load the JSON data from the file into a variable
        with open(full_path_to_newest_file, 'rb') as json_file:
            print("Loading",json_file)
            json_data = json.loads(json_file.read().decode('utf-8'))

        return json_data
    else:
        return None

def load_oldest_json_file_from_date(directory_path, target_date):
    def is_target_date_file(file_path, target_date):
        file_stat = os.stat(file_path)
        file_modified_date = datetime.date.fromtimestamp(file_stat.st_mtime)
        return file_modified_date == target_date

    # List all files in the directory
    all_files = os.listdir(directory_path)

    # Filter JSON files for the target date
    target_date_files = [file for file in all_files if is_target_date_file(os.path.join(directory_path, file), target_date) and file.endswith('.json')]

    if target_date_files:
        # Sort the files by modification time to get the newest one
        newest_file = min(target_date_files, key=lambda f: os.path.getmtime(os.path.join(directory_path, f)))
        full_path_to_newest_file = os.path.join(directory_path, newest_file)
        
        # Load the JSON data from the file into a variable
        with open(full_path_to_newest_file, 'rb') as json_file:
            print("Loading",json_file)
            json_data = json.loads(json_file.read().decode('utf-8'))

        return json_data
    else:
        return None

def load_middle_json_file_from_date(directory_path, target_date):
    def is_target_date_file(file_path, target_date):
        file_stat = os.stat(file_path)
        file_modified_date = datetime.date.fromtimestamp(file_stat.st_mtime)
        return file_modified_date == target_date

    # List all files in the directory
    all_files = os.listdir(directory_path)

    # Filter JSON files for the target date
    target_date_files = [file for file in all_files if is_target_date_file(os.path.join(directory_path, file), target_date) and file.endswith('.json')]

    if target_date_files:
        # Sort the files by modification time
        sorted_files = sorted(target_date_files, key=lambda f: os.path.getmtime(os.path.join(directory_path, f)))

        # Find the middle file
        middle_index = len(sorted_files) // 2
        middle_file = sorted_files[middle_index]

        full_path_to_middle_file = os.path.join(directory_path, middle_file)

        # Load the JSON data from the middle file into a variable
        with open(full_path_to_middle_file, 'rb') as json_file:
            print("Loading", json_file)
            json_data = json.loads(json_file.read().decode('utf-8'))

        return json_data
    else:
        return None


driver = webdriver.Chrome()

# Define the directory where your CSV files are located
directory = 'ftn_prop_predictions'

# List all files in the directory with the .csv extension
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and league in f and "_results" not in f]

# Find the latest CSV file in the directory
latest_csv_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join(directory, f)))

print("latest_csv_file",latest_csv_file)

# Construct the full file path
file_path = os.path.join(directory, latest_csv_file)

# Load the latest CSV file into a DataFrame
df = pd.read_csv(file_path)

last_five_data = {}

date_format = "%Y-%m-%dT%H:%M:%S%z"


def get_event(start_time, last_five):
    # Parse the string to create a datetime object
    prop_start_time_dt = start_time

    for event in last_five:
        print(event)
        event_start_time_dt = datetime.datetime.strptime(event["GameStartTime"], date_format)

        # Normalize time zones using pytz
        event_start_time_dt = event_start_time_dt.astimezone(pytz.timezone('US/Central'))

        # Compare only the date part
        if prop_start_time_dt == event_start_time_dt.date():
            return event
    return None

def get_actual_result(stat_type,event):

    if "Totals" not in event:
        return None
    totals = event["Totals"]
    mapped_stat = mapped_pp_stats.get_mapped_stat(stat_type)
    
    if mapped_stat is None:
        return None;
    
    stat_list = mapped_stat.split(",")
    total = 0.0
    prop_total = 0.0
    for stat in stat_list:
        if stat not in totals:
            print("Setting", stat, "to 0")
            totals[stat] = 0.0
        total += totals[stat]
    
    prop_total = prop_total + total;
    return prop_total;

def update_last_five(player_id,last_five_url):
    driver.get(last_five_url)

    # Wait for at least one <pre> element to load (adjust the timeout as needed)
    wait = WebDriverWait(driver, 10)
    elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'pre')))

    # Initialize an empty list to store the text content of all <pre> elements
    json_data_list = []

    # Extract the text content of all <pre> elements
    for element in elements:
        json_data_list.append(element.text)
        

    # Generate a random sleep duration between 3 and 30 seconds
    sleep_duration = random.uniform(0, 3)
    print("sleeping for",sleep_duration, flush=True)

    # Sleep for the generated duration
    time.sleep(sleep_duration)

    # Attempt to parse the extracted text as JSON
    try:
        # Combine the text content of all <pre> elements into a single JSON string
        combined_json_data = ''.join(json_data_list)
        
        data = json.loads(combined_json_data)

        #print(data, flush=True)
        last_five_data[player_id] = data
        
    except json.JSONDecodeError:
        print("The extracted text is not valid JSON.")
        

player_ids = {}

# Example usage:
directory_path = 'pp_data'
target_date = datetime.date.today() - datetime.timedelta(days=1)  # Yesterday
json_info = load_oldest_json_file_from_date(directory_path, target_date)

players = {}
for d in json_info["included"]:
    players[d["id"]] = d["attributes"]

data = []
for d in json_info['data']:
    data.append({
        'player_id': d['relationships']['new_player']['data']['id'], 
        **players[d['relationships']['new_player']['data']['id']],
        **d['attributes']
    })


pp_data = pd.DataFrame(data)
pp_data = pp_data.applymap(lambda x: x.strip().replace('\t','') if isinstance(x, str) else x)
filter_combo = pp_data['combo'] == True  # Use True for combo = True
filter_league = pp_data['league'] == league  # Use "NBA" for league = "NBA"

# Combine the filters to filter the DataFrame
pp_data = pp_data[~(filter_combo)]
pp_data = pp_data[(filter_league)]

print(pp_data.columns)

pp_data.to_csv("test2.csv")

url = "aHR0cHM6Ly9hcGkucHJpemVwaWNrcy5jb20vcGxheWVycy8="
decoded_url = base64.b64decode(url).decode()

def find_player_id(league,team,name):
    if league not in player_ids:
        player_ids[league]={}
        
    if team not in player_ids[league]:
        player_ids[league][team]={}
        
    if name in player_ids[league][team]:
        return player_ids[league][team][name]    

    matching_row = pp_data.loc[pp_data['display_name'] == name.strip()]

    if not matching_row.empty:
        # Print the values from the first matching row
        print("Found matching row", matching_row.iloc[0]['display_name'], matching_row.iloc[0]['player_id'])
        return matching_row.iloc[0]['player_id']
    else:
        print("No matching row found for", name)
        return None
    

                
# Define a function to process each row
def process_row(row):
    # Store existing row headers in variables
    team = row['Team']
    name = row['Player']
    stat = row['Stat']
    line = row['Line']
    bet = row['Bet']
    win_percent = row['Win%']
    player_id = find_player_id(league,team,name)
    
    if player_id is not None:
        last_five_url = decoded_url+str(player_id)+"/last_five_games?league_name="+str(league)

        if player_id not in last_five_data:
            update_last_five(player_id, last_five_url)

        actuals = last_five_data[player_id]
        
        event = get_event(target_date, actuals)
        print("Event on",target_date,"is",event,last_five_url)
        if event is not None:
            actual_prop_result = get_actual_result(stat, event)
            result = "Push"
            if actual_prop_result > float(line):
                result = "Over"
            elif actual_prop_result < float(line):
                result = "Under"
            
            row['Prop Actual'] = str(actual_prop_result)
            row['Prop Result'] = result
            row['Hit'] = str(result.lower() == bet.lower())  # Populate the 'Hit' column
        else:
            row['Prop Actual'] = ""
            row['Prop Result'] = ""
            row['Hit'] = ""

        # Create a single string with all row headers and values
        row_info = f"team: {team}, name: {name}, stat: {stat}, line: {line}, bet: {bet}, win_percent: {win_percent}"

        # Print the combined row information
        print(row_info, flush=True)

    return row



# Apply the processing function to each row
df = df.apply(process_row, axis=1)

df = df.rename(columns={'Next Start Time': 'Event Start Time'})
# Sort the DataFrame
custom_order = ['Over', 'Under', 'Push', ""]
df['Prop Result'] = df['Prop Result'].astype('category')
df['Prop Result'].cat.set_categories(custom_order, inplace=True)
df = df.sort_values('Prop Result')

custom_order = ['True', 'False', ""]
df['Hit'] = df['Hit'].astype('category')
df['Hit'].cat.set_categories(custom_order, inplace=True)
df = df.sort_values('Hit')

#columns_to_remove = ['Player Id', 'Next Event Id', 'Last Five URL','Unnamed: 0']
#df = df.drop(columns=columns_to_remove)

# Calculate the percentage of Hit == True and Hit == False values
hit_true_count = len(df[df['Hit'] == 'True'])
hit_false_count = len(df[df['Hit'] == 'False'])
total_count = len(df[df['Hit'] != ''])
if total_count > 0:
    hit_true_percentage = round((hit_true_count / total_count) * 100, 2)
    hit_false_percentage = round((hit_false_count / total_count) * 100, 2)
else:
    hit_true_percentage = 0
    hit_false_percentage = 0

# Sort the DataFrame by "Percent Avg Distance" within "Hit == True"
df_true = df[df['Hit'] == 'True']
df_true = df_true.sort_values(by='Win%', ascending=False)

# Sort the DataFrame by "Percent Avg Distance" within "Hit == False"
df_false = df[df['Hit'] == 'False']
df_false = df_false.sort_values(by='Win%', ascending=False)

# Combine the sorted DataFrames back
sorted_df = pd.concat([df_true, df_false])

# Include the percentages in the CSV as the first two rows
percentages_df = pd.DataFrame({'Percentage of Hit == True': [hit_true_percentage], 'Percentage of Hit == False': [hit_false_percentage]})
result_df = pd.concat([percentages_df, sorted_df], ignore_index=True)

# Display the results
print(f'Percentage of Hit == True: {hit_true_percentage:.2f}%')
print(f'Percentage of Hit == False: {hit_false_percentage:.2f}%')

# Save the sorted DataFrame, including percentages, to the CSV file with the new name
new_file_name = latest_csv_file.replace('.csv', '_results.csv')
new_file_path = os.path.join(directory, new_file_name)
result_df.to_csv(new_file_path, index=False)