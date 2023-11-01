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

driver = webdriver.Chrome()


# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
formatted_date = yesterday.strftime("%Y-%m-%d")

parser.add_argument("--event_date", type=str, default=formatted_date, help="event_date")


# Parse arguments
args = parser.parse_args()

# Specify the directory path you want to create
pp_result_data_path = 'pp_result_data'

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

def find_oldest_file_from_day(directory_path, specific_day):
    # Initialize variables to store information about the oldest file
    oldest_file = None
    oldest_file_time = None

    # Iterate over the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path):
            file_time = os.path.getctime(file_path)
            file_date = str(datetime.datetime.fromtimestamp(file_time).date())

            # Check if the file's date matches the specific day
            if file_date == specific_day:
                # If it's the first file matching the specific day or older than the previous oldest file
                if oldest_file is None or file_time < oldest_file_time:
                    oldest_file = file_path
                    oldest_file_time = file_time

    return oldest_file


event_date = args.event_date
# Get today's date
formatted_date = event_date

print(f"Running for date {formatted_date}.")


# Example usage:
directory_path = "pp_data"
newest_file = find_oldest_file_from_day(directory_path, formatted_date)

print("newest_file",newest_file)

with open(str(newest_file), 'rb') as f:
    f_data = f.read()
    
json_info = json.loads(f_data.decode('utf-8'))

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


df = pd.DataFrame(data)
df = df.applymap(lambda x: x.strip().replace('\t','') if isinstance(x, str) else x)


filter = df['combo']==True
filtered_df = df[~filter]
filtered_df = filtered_df[df['league'].isin(['NFL', 'NBA', 'MLB','NHL', 'CFB'])]


data_dict = filtered_df.to_dict(orient='records')

# Navigate to the desired URL (base 64 encoded)
url = "aHR0cHM6Ly9hcGkucHJpemVwaWNrcy5jb20vcGxheWVycy8="
decoded_url = base64.b64decode(url).decode()

def are_same_day(datetime1, datetime2):
    return datetime1.year == datetime2.year and datetime1.month == datetime2.month and datetime1.day == datetime2.day

prop_info = {}

val = 0;

event_date_dt = datetime.datetime.strptime(event_date, "%Y-%m-%d")

for data in data_dict:
    val = val + 1;
    print("At "+str(val)+"/"+str(len(data_dict)));
    player_id = data['player_id']
    name = data['name']
    league = data['league']

    last_five_url = decoded_url+str(player_id)+"/last_five_games?league_name="+str(league)

    #print("last_five_url",last_five_url)
    #print("start_time",data['start_time'])
    
    date_format = "%Y-%m-%dT%H:%M:%S%z"

    # Parse the string to create a datetime object
    start_time_dt = datetime.datetime.strptime(data['start_time'], date_format)
    print("Analyzing",player_id,name,league, last_five_url,start_time_dt)
    if are_same_day(start_time_dt, event_date_dt) and not data['combo'] and not data['is_promo']:
        #print("Found match",data)
        if league not in prop_info or player_id not in prop_info[league]:
         
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
                
                json_data = json.loads(combined_json_data)
                
                if league not in prop_info:
                    prop_info[league]={}

                print("Creating new",player_id,name,flush=True)   
                #print(data, flush=True)
                prop_info[league][player_id]={}
                prop_info[league][player_id]["last_five_results"] = json_data
                prop_info[league][player_id]["props"] = {}
                prop_info[league][player_id]["props"][data['stat_type']] = data
                
            except json.JSONDecodeError:
                print("The extracted text is not valid JSON.")
        else:
            print("Appending existing to",player_id,name,flush=True)   
            prop_info[league][player_id]["props"][data['stat_type']] = data           
       
       
print("We have",len(prop_info),"data")

# Convert the dictionary to a JSON string
json_string = json.dumps(prop_info, indent=4)

file_loc = pp_result_data_path+"/results_prop_info_"+event_date+".json";
# Alternatively, you can write the JSON to a file
with open(file_loc, "w") as json_file:
    json_file.write(json_string)
    
print("Wrote",file_loc);