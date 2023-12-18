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



# Define the CSV file name with the current date
csv_file_name = f"normalized_props/pp_props_{formatted_date}.csv"

# Example usage:
directory_path = "pp_data"
newest_file = find_newest_file_from_day(directory_path, formatted_date)

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
df = df[df['odds_type'].isin(['standard'])]
df.to_csv(csv_file_name)


# Print a message indicating the CSV file has been created
print(f"CSV file '{csv_file_name}' created.")

print("Cleaning up",newest_file)
os.remove(newest_file)