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
import pytz
import argparse
import base64
import mapped_pp_stats
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
    
# Specify the directory path you want to create
directory_path = 'streak_data'

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

props = ["NFL","MLB","NHL","NBA","CFB","CBB","NBA1H","NFL1H"]

filter = prop_lines['league'].isin(props)
prop_lines = prop_lines[filter]
    
no_handlers = []

print("There are ",len(prop_lines),"to parse");

prop_nums = len(prop_lines);
val = 0;
    
today = datetime.datetime.now()
# Create a Central Time Zone (CT) object
ct_timezone = pytz.timezone('US/Central')
# Convert the local time to the Central Time Zone
ct_time = today.astimezone(ct_timezone)

# Calculate the date two days before today
six_months_ago = ct_time - datetime.timedelta(days=180)

date_format = "%Y-%m-%dT%H:%M:%S%z"  

def streak_check(line, mapped_stat, json_data, comparator):
    if len(json_data) < 5:
        return (False, -4321)
    
    prop_total = 0.0
    
    for stat in json_data:
        if 'Totals' not in stat:
            return (False, -1234)
        
        totals = stat["Totals"]
        stat_list = mapped_stat.split(",")
        total = 0.0
        
        startTime = datetime.datetime.strptime(stat["GameStartTime"], date_format)
        
        if startTime < six_months_ago:
            print("Game is too old... ignoring")
            return (False, -987654321)
        
        for stat in stat_list:
            if stat not in totals:
                print("Setting", stat, "to 0")
                totals[stat] = 0.0
            total += totals[stat]
        
        prop_total = prop_total + total;
        
        print(f"{comparator} checking {total} with {line} for {mapped_stat}")
        if comparator(total, line):
            return (False, -999)
    
    
    
    return (True, (prop_total/5))

def find_streak(name, stat_type, line_score, json_data, last_five_url, comparator):
    line = float(line_score)
    mapped_stat = mapped_pp_stats.get_mapped_stat(stat_type)
    
    if mapped_stat:
        return streak_check(line, mapped_stat, json_data, comparator)
    else:
        print("!!!!!!!!!$$$$Can't handle", stat_type, last_five_url)
        no_handlers.append(name+" "+stat_type+" "+str(line_score)+" "+str(last_five_url))
        return (False, -12345)

prop_info = {}

streaks = []

for ind in prop_lines.index:
    league = prop_lines['league'][ind]
    name = (prop_lines['display_name'][ind])
    position = prop_lines['position'][ind]
    team = prop_lines['team'][ind]  
    opp = prop_lines['description'][ind]      
    market = prop_lines['market'][ind]
    game_id = prop_lines['game_id'][ind]    
    player_id = prop_lines['player_id'][ind]
    combo = prop_lines['combo'][ind]
    is_promo = prop_lines['is_promo'][ind]
    line_score = prop_lines['line_score'][ind]
    stat_type = prop_lines['stat_type'][ind]
    start_time = prop_lines['start_time'][ind]
    last_five_url = decoded_url+str(player_id)+"/last_five_games?league_name="+str(league)
    print(player_id,league,team,opp,game_id,name,player_id,position,market,combo,is_promo,line_score,stat_type,start_time,last_five_url);
    
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
                prop_info[player_id] = data
                
            except json.JSONDecodeError:
                print("The extracted text is not valid JSON.")
    else:
        print("Skipping over",player_id,name,flush=True)
    val = val + 1
    
    if player_id in prop_info:
        json_data = prop_info[player_id]
        

        if "in first" not in stat_type.lower():
            up_streak = find_streak(name, stat_type, line_score, json_data, last_five_url, lambda x, y: x < y)
            down_streak = find_streak(name, stat_type, line_score, json_data, last_five_url, lambda x, y: x > y)
            
            if up_streak[0]:
                avg_diff = float(up_streak[1]) - float(line_score)
                percent_diff = 100.0 * ((avg_diff) / ((float(up_streak[1]) + float(line_score))/2.0))
                streaks.append(["Over",league,team,opp,game_id,start_time,name,player_id,position,stat_type,(line_score),round(float(up_streak[1]),2),round(avg_diff,1),round(percent_diff,1),last_five_url])
            if down_streak[0]:
                avg_diff = float(line_score) - float(down_streak[1])
                percent_diff = 100.0 * ((avg_diff) / ((float(down_streak[1]) + float(line_score))/2.0))
                streaks.append(["Under",league,team,opp,game_id,start_time,name,player_id,position,stat_type,(line_score),round(float(down_streak[1]),2),round(avg_diff,1),round(percent_diff,1),last_five_url])
        
print("Now we have ",len(prop_info),flush=True)
#print("Dump ",(prop_info),flush=True)



print("Report",flush=True)

# Create a Pandas DataFrame from the streaks list
streaks_df = pd.DataFrame(streaks, columns=["Streak", "League", "Team", "Next Opp", "Next Event Id", "Next Start Time", "Name", "Player Id", "Position", "Prop", "Line", "Average", "Raw Avg Distance", "Percent Avg Distance", "Last Five URL"])

# Sort the DataFrame based on your criteria
sorted_streaks_df = streaks_df.sort_values(by=['Streak', 'Percent Avg Distance'], ascending=[True, False])

# Convert the sorted DataFrame back to a list
sorted_streaks = sorted_streaks_df.values.tolist()

# Generate a timestamp
timestamp = time.strftime("%Y-%m-%d-%H%M%S")

csv_filename = f"streak_data/pp_streaks_{timestamp}.csv"

with open(csv_filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Streak","League","Team","Next Opp","Next Event Id","Next Start Time","Name","Player Id","Position","Prop","Line","Average","Raw Avg Distance","Percent Avg Distance","Last Five URL"])

    for streak in streaks:
        print(streak,flush=True);
        writer.writerow(streak)
    
df = pd.read_csv(csv_filename)

df = df.sort_values(by=['Streak','Percent Avg Distance'], ascending=[True, False])

df.to_csv(csv_filename)

print("CSV Report Dumped",flush=True)


print("No Handler Report",flush=True)

for no_handle in no_handlers:
    print(no_handle,flush=True);

print("No Handler Report Dumped",flush=True)

# Close the browser window
driver.quit()

        
        

