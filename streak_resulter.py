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
import sheets

driver = webdriver.Chrome()

# Define the directory where your CSV files are located
directory = 'streak_data'

# List all files in the directory with the .csv extension
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and "_results" not in f and "combined" not in f]

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
    prop_start_time_dt = datetime.datetime.strptime(start_time, date_format)

    for event in last_five:
        event_start_time_dt = datetime.datetime.strptime(event["GameStartTime"], date_format)

        # Normalize time zones using pytz
        prop_start_time_dt = prop_start_time_dt.astimezone(pytz.UTC)
        event_start_time_dt = event_start_time_dt.astimezone(pytz.UTC)

        # Compare only the date part
        if prop_start_time_dt.date() == event_start_time_dt.date():
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
                
# Define a function to process each row
def process_row(row):
    # Store existing row headers in variables
    streak = row['Streak']
    league = row['League']
    team = row['Team']
    next_opp = row['Next Opp']
    next_event_id = row['Next Event Id']
    next_start_time = row['Next Start Time']
    name = row['Name']
    player_id = row['Player Id']
    position = row['Position']
    prop = row['Prop']
    line = row['Line']
    average = row['Average']
    raw_avg_distance = row['Raw Avg Distance']
    percent_avg_distance = row['Percent Avg Distance']
    last_five_url = row['Last Five URL']
    
    if player_id not in last_five_data:
        update_last_five(player_id, last_five_url)

    actuals = last_five_data[player_id]
    
    event = get_event(next_start_time, actuals)
    
    if event is not None:
        actual_prop_result = get_actual_result(prop, event)
        result = "Push"
        if actual_prop_result > float(line):
            result = "Over"
        elif actual_prop_result < float(line):
            result = "Under"
        
        row['Prop Actual'] = str(actual_prop_result)
        row['Prop Result'] = result
        row['Hit'] = str(result == streak)  # Populate the 'Hit' column
    else:
        row['Prop Actual'] = ""
        row['Prop Result'] = ""
        row['Hit'] = ""

    # Create a single string with all row headers and values
    row_info = f"Streak: {streak}, League: {league}, Team: {team}, Next Opp: {next_opp}, Next Event Id: {next_event_id}, Next Start Time: {next_start_time}, Name: {name}, Player_Id: {player_id}, Position: {position}, Prop: {prop}, Line: {line}, Average: {average}, Raw Avg Distance: {raw_avg_distance}, Percent Avg Distance: {percent_avg_distance}, Last Five URL: {last_five_url}, Hit {row['Hit']}"

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

columns_to_remove = ['Player Id', 'Next Event Id', 'Last Five URL','Unnamed: 0']
df = df.drop(columns=columns_to_remove)

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
df_true = df_true.sort_values(by='Percent Avg Distance', ascending=False)

# Sort the DataFrame by "Percent Avg Distance" within "Hit == False"
df_false = df[df['Hit'] == 'False']
df_false = df_false.sort_values(by='Percent Avg Distance', ascending=False)

# Combine the sorted DataFrames back
sorted_df = pd.concat([df_true, df_false])

sorted_df = sorted_df = df.pop('Hit') 
  
# insert column using insert(position,column_name, 
# first_column) function 
sorted_df = sorted_df.insert(0, 'Hit', first_column) 

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

sheets.write_to_spreadsheet(new_file_path,"Last Five Streaker",new_file_name.replace("pp_streaks_","").replace('_results.csv',''),1)

import subprocess
subprocess.run(["python", "streak_combined_resulter.py"])