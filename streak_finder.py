from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import subprocess
import os
import fnmatch
import datetime
import time
import random

import argparse
import base64
import pandas as pd

# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")

parser.add_argument("--year", type=int, default=2023, help="Year")
parser.add_argument("--week", type=int, default=1, help="Week")

# Parse arguments
args = parser.parse_args()

# Access argument values
year_value = str(args.year)
week_value = str(args.week)

print("Generating results for",year_value,week_value);

prop_lines = pd.read_csv("processing/prop_lines_"+year_value+"_week_"+week_value+".csv")

print(prop_lines)

driver = webdriver.Chrome()

# Specify the directory path you want to create
directory_path = 'pp_data'

# Check if the directory already exists
if not os.path.exists(directory_path):
    # If it doesn't exist, create the directory
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")
else:
    print(f"Directory '{directory_path}' already exists.")

# Navigate to the desired URL (base 64 encoded)
url = "aHR0cHM6Ly9hcGkucHJpemVwaWNrcy5jb20vcGxheWVycy8="
decoded_url = base64.b64decode(url).decode()

print("decoded_url",decoded_url, flush=True)

props = ["NFL","MLB","NHL","NBA"]

filter = prop_lines['league'].isin(props)
prop_lines = prop_lines[filter]
    
no_handlers = []

print("There are ",len(prop_lines),"to parse");

prop_nums = len(prop_lines);
val = 0;
        
def get_mapped_stat(stat_type):
    stat_mapping = {
        "Pass Completions": "PassingCompletions",
        "Pass Yards": "PassingYards",
        "Pass TDs": "PassingTouchdowns",
        "Pass Attempts": "PassingAttempts",
        "Fumbles Lost": "FumblesLost",
        "INT": "Interceptions",
        "Receptions": "Receptions",
        "Receiving Yards": "ReceivingYards",
        "Rec TDs": "ReceivingTouchdowns",
        "Rec Targets": "ReceivingTargets",
        "Rush Yards": "RushingYards",
        "Rush Attempts": "RushingAttempts",
        "Rush TDs": "RushingTouchdowns",
        "Fantasy Score": "FantasyScore",
        "Touchdowns": "Touchdowns",
        "Pass+Rush+Rec TDs": "PassRushRecTD",
        "Rush+Rec TDs": "RushRecTD",
        "Pass+Rush Yds": "PassPlusRushYards",
        "Rec+Rush Yds": "RecPlusRushYards",
        "Rush+Rec Yds": "RecPlusRushYards",
        "Sacks": "Sacks",
        "Tackles+Ast": "TackleAssists,Tackles",
        "FG Made": "FieldGoalsMade",
        "Kicking Points": "KickingPoints",
        "Punts": "Punts",
        "Pitcher Strikeouts": "PitcherStrikeouts", 
        "Total Bases": "TotalBases",        
        "Walks Allowed": "WalksAllowed", 
        "Hits Allowed": "HitsAllowed", 
        "Pitcher Fantasy Score": "PitcherFantasyScore", 
        "Hits+Runs+RBIS": "HitsAndRunsAndRBIs",
        "Hits+Runs+RBIs": "HitsAndRunsAndRBIs",
        "Pitching Outs": "PitchingOuts",        
        "Pitcher Fantasy Score": "PitcherFantasyScore", 
        "Hitter Fantasy Score": "HitterFantasyScore", 
        "RBIs": "RBIs", 
        "Runs": "Runs",         
        "Hitter Strikeouts": "HitterStrikeouts",   
        "Goalie Saves": "GoalieSaves",        
        #"Time On Ice": "TimeOnIce", 
        "Points": "Points", 
        "Shots On Goal": "ShotsOnGoal", 
        "Assists": "Assists", 
        "Faceoffs Won": "FaceoffsWon", 
        "Hits": "Hits", 
        "Points": "Points",  
        "Rebounds": "Rebounds",        
        "Assists": "Assists",       
        "Turnovers": "Turnovers",  
        "Steals": "Steals",      
        "Blocked Shots": "BlockedShots",        
        "3-PT Made": "ThreePointersMade",      
        "Free Throws Made": "FreeThrowsMade",  
        "Pts+Rebs+Asts": "PtsRebsAsts",               
        "Blks+Stls": "BlksStls",  
        "Pts+Asts": "PtsAsts",   
        "Pts+Rebs": "PtsRebs",   
        "Rebs+Asts": "RebsAsts",  
    }
    return stat_mapping.get(stat_type, "")

def streak_check(line, mapped_stat, json_data, comparator):
    if len(json_data) < 5:
        return False
    
    for stat in json_data:
        totals = stat["Totals"]
        stat_list = mapped_stat.split(",")
        total = 0.0
        
        for stat in stat_list:
            if stat not in totals:
                print("Setting", stat, "to 0")
                totals[stat] = 0.0
            total += totals[stat]
        
        print(f"{comparator} checking {total} with {line} for {mapped_stat}")
        if comparator(total, line):
            return False
    
    return True

def find_streak(name, stat_type, line_score, json_data, comparator):
    line = float(line_score)
    mapped_stat = get_mapped_stat(stat_type)
    
    if mapped_stat:
        return streak_check(line, mapped_stat, json_data, comparator)
    else:
        print("!!!!!!!!!$$$$Can't handle", stat_type)
        no_handlers.append(name+" "+stat_type+" "+str(line_score))


prop_info = {}

streaks = []

for ind in prop_lines.index:
    league = prop_lines['league'][ind]
    name = (prop_lines['display_name'][ind])
    position = prop_lines['position'][ind]
    market = prop_lines['market'][ind]
    player_id = prop_lines['player_id'][ind]
    combo = prop_lines['combo'][ind]
    is_promo = prop_lines['is_promo'][ind]
    line_score = prop_lines['line_score'][ind]
    stat_type = prop_lines['stat_type'][ind]
    start_time = prop_lines['start_time'][ind]
    last_five_url = decoded_url+str(player_id)+"/last_five_games?league_name="+str(league)
    print(player_id,league,name,position,market,combo,is_promo,line_score,stat_type,start_time,last_five_url);
    
    if player_id not in prop_info:
    
        if not combo and not is_promo:
            print("On",val,"/",prop_nums, flush=True)
            print("Grabbing",player_id,league,name,last_five_url, flush=True)
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
            sleep_duration = random.uniform(1, 5)
            print("sleeping for",sleep_duration, flush=True)

            # Sleep for the generated duration
            time.sleep(sleep_duration)

            # Attempt to parse the extracted text as JSON
            try:
                # Combine the text content of all <pre> elements into a single JSON string
                combined_json_data = ''.join(json_data_list)
                
                data = json.loads(combined_json_data)

                #print(data, flush=True)
                prop_info[player_id] = data
                
            except json.JSONDecodeError:
                print("The extracted text is not valid JSON.")
    else:
        print("Skipping over",player_id,name,flush=True)
    val = val + 1
    
    if player_id in prop_info:
        json_data = prop_info[player_id]
        

        if "in first" not in stat_type.lower():
            up_streak = find_streak(name, stat_type, line_score, json_data, lambda x, y: x < y)
            down_streak = find_streak(name, stat_type, line_score, json_data, lambda x, y: x > y)
            
            if up_streak:
                streaks.append("Up Streak "+league+" "+name+ " "+stat_type+" "+str(line_score))
            if down_streak:
                streaks.append("Down Streak "+league+" "+name+ " "+stat_type+" "+str(line_score))
        
print("Now we have ",len(prop_info),flush=True)
#print("Dump ",(prop_info),flush=True)

print("No Handler Report",flush=True)

for no_handle in no_handlers:
    print(no_handle,flush=True);

print("Report Dumped",flush=True)

streaks.sort()

print("Report",flush=True)

for streak in streaks:
    print(streak,flush=True);
    
print("Report Dumped",flush=True)

# Close the browser window
driver.quit()

        
        

