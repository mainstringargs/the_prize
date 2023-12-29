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

def find_newest_file_from_day(directory_path, specific_day, sport, book):
    # Initialize variables to store information about the newest file
    files = set()

    # Iterate over the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        #print(file_path,flush=True)
        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path) and sport in file_path and book in file_path:
            file_time = os.path.getctime(file_path)
            file_date = str(datetime.datetime.fromtimestamp(file_time).date())
            if file_date == specific_day:
                # If it's the first file matching the specific day or newer than the previous newest file
                files.add(file_path)

    return files

books = ["fanduel", "bet365","betmgm","caesars","draftkings"]
sports = ["nba","nfl","mlb"]

for book in books:
    for sport in sports:
        relevant_files = find_newest_file_from_day('scores_and_odds_data',formatted_date, sport.upper(), book.lower())
        for relevant_file in relevant_files:
            print("reading...",relevant_file,flush=True)
            f_data = None;
            with open(str(relevant_file), 'rb') as f:
                f_data = f.read()
                
            json_info = json.loads(f_data.decode('utf-8'))
            #print(json_info,flush=True)
            if "markets" in json_info:
                if "player props" in json_info["markets"]:
                    player_props = json_info["markets"]["player props"]
                    
                    for player in player_props:
                        name = player['player']['first_name']+" "+['player']['last_name'];
                        team = player['team']['key'];
                        print(team,name,player['stat'],player['value'],player['projection'],player['over'],player['under'],flush=True)
                    