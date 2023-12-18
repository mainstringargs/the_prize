import datetime
import os 
import json
import base64
import csv
import pandas as pd
import argparse
import base64
import pandas as pd

import csv
import fnmatch
import datetime
import time
import random
import pytz
import argparse
import mapped_pp_stats
import sheets

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
            if "results_prop_info" in filename and "full" not in filename:
                file_time = filename.replace("results_prop_info_","").replace(".json","")
                file_time = datetime.datetime.strptime(file_time, "%Y-%m-%d").timestamp()
            

            file_date = str(datetime.datetime.fromtimestamp(file_time).date())
            print(filename, file_date, flush=True)
            # Check if the file's date matches the specific day
            if file_date == specific_day:
                # If it's the first file matching the specific day or newer than the previous newest file
                if newest_file is None or file_time > newest_file_time:
                    newest_file = file_path
                    newest_file_time = file_time

    return newest_file
    
# Get today's date
event_date = args.event_date


print("event_date is",event_date)

formatted_date = event_date
newest_file = find_newest_file_from_day(pp_result_data_path, formatted_date)

print("found",newest_file)

date_format = "%Y-%m-%dT%H:%M:%S%z"

def get_prop_for_event(prop, player):
    # Parse the string to create a datetime object
    prop_start_time_dt = datetime.datetime.strptime(prop['start_time'], date_format)

    for event in player["last_five_results"]:
        event_start_time_dt = datetime.datetime.strptime(event["GameStartTime"], date_format)

        # Normalize time zones using pytz
        prop_start_time_dt = prop_start_time_dt.astimezone(pytz.UTC)
        event_start_time_dt = event_start_time_dt.astimezone(pytz.UTC)

        # Compare only the date part
        if prop_start_time_dt.date() == event_start_time_dt.date():
            return event
    return None

def get_actual_result(prop,event):
    stat_type = prop['stat_type']
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
        
        

url = "aHR0cHM6Ly9hcGkucHJpemVwaWNrcy5jb20vcGxheWVycy8="
decoded_url = base64.b64decode(url).decode()


with open(str(newest_file), 'rb') as f:
    f_data = f.read()
    
json_info = json.loads(f_data.decode('utf-8'))

prop_results_list=[]
no_handlers_list = []

for league_data in json_info:
    print(league_data,":",len(json_info[league_data]),"entries")
    for key in json_info[league_data]:
        player = json_info[league_data][key];
        
        for prop_key in player["props"]:
            prop = player["props"][prop_key];
            event = get_prop_for_event(prop, player)
            if event is not None:
                prop_name = prop_key;

                league = prop['league']
                name = (prop['display_name'])
                position = prop['position']
                market = prop['market']
                team_abbr = prop['team']
                opp_team_abbr = prop['description']
                player_id = prop['player_id']
                combo = prop['combo']
                is_promo = prop['is_promo']
                line_score = prop['line_score']
                stat_type = prop['stat_type']
                start_time = prop['start_time']
                game_id = prop['game_id']
                last_five_url = decoded_url+str(player_id)+"/last_five_games?league_name="+str(league)
                
                if not combo:
                    print(player_id,league,name,position,market,combo,is_promo,line_score,stat_type,start_time,last_five_url, game_id);
                    actual_result = get_actual_result(prop,event)
                    
                    if actual_result is None:
                        no_handlers_list.append(stat_type+" "+league+" "+name);
                        continue
                        
                    result_string = "Push"
                    if line_score < actual_result:
                        result_string = "Over"
                    if line_score > actual_result:
                        result_string = "Under"
                    
                    prop_results_list.append([league,name,position,market,team_abbr,opp_team_abbr,game_id,start_time,is_promo,stat_type,line_score,actual_result,result_string])
                    
                    
with open('processing/prop_report_'+formatted_date+'.csv', 'w', newline='') as file:
    writer = csv.writer(file)
     
    writer.writerow(["league","name","position","team","team_abbr","opp_team_abbr","game_id","start_time","promo","prop","line","actual","result"])
    
    for result in prop_results_list:
        writer.writerow(result)


print("NO HANDLER REPORT")
for no_handler in no_handlers_list:
    if "in first" not in no_handler.lower() and "kicking points" not in no_handler.lower():
        print(no_handler)
print("END NO HANDLER REPORT")


processed = pd.read_csv('processing/prop_report_'+formatted_date+'.csv', encoding='unicode_escape')

#sheets.write_to_spreadsheet('processing/prop_report_'+formatted_date+'.csv',"PP Results",formatted_date,6)

sheets.write_to_spreadsheet('processing/prop_report_'+formatted_date+'.csv',"PP Results",'Individual Props',add_column_name="Event Date",add_column_data=formatted_date,index=0,overwrite=False,append=True)

#print(processed)

df = processed.sort_values(by=['prop','result','team','name'])

df.to_csv("results/all-data-raw_"+formatted_date+".csv",index=False)

for sport in json_info:
    print("SPORT",sport)
    sorted_data = df[df['league'].isin([sport])]
    print(sorted_data)
    

    if sorted_data.shape[0] == 0:
        print("SPORT",sport,"is empty")
        continue;
        
    sorted_data.to_csv("results/"+sport+"_all-data-raw_"+formatted_date+".csv",index=False)

    # After you've processed the data and calculated results
    grouped_data = sorted_data.groupby(['prop', 'result']).size().unstack(fill_value=0)

    # Calculate total counts for each 'prop'
    grouped_data['Total'] = grouped_data.sum(axis=1)

    # Calculate percentages for 'Over' and 'Under' and round to 2 decimal places
    if 'Over' in grouped_data:
        grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
    else:
        grouped_data['Over %'] = 0
        
    if 'Under' in grouped_data:
        grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100
    else:
        grouped_data['Under %'] = 0
        
    # Round the percentages to 2 decimal places
    grouped_data['Over %'] = grouped_data['Over %'].round(1)
    grouped_data['Under %'] = grouped_data['Under %'].round(1)

    # Check if 'Push' is present and calculate 'Push %' if it is
    if 'Push' in grouped_data.columns:
        grouped_data['Push %'] = (grouped_data['Push'] / grouped_data['Total']) * 100
        grouped_data['Push %'] = grouped_data['Push %'].round(1)

    # Print the percentages
    grouped_data.to_csv("results/"+sport+"_all-data-grouped-by-prop_"+formatted_date+".csv")


    # After you've processed the data and calculated results
    grouped_data = sorted_data.groupby(['name', 'position', 'team', 'result']).size().unstack(fill_value=0)

    # Calculate total counts for each player
    grouped_data['Total'] = grouped_data.sum(axis=1)

    # Calculate percentages for 'Over' and 'Under' and round to 2 decimal places
    if 'Over' in grouped_data:
        grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
    else:
        grouped_data['Over %'] = 0
    
    if 'Under' in grouped_data:
        grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100
    else:
        grouped_data['Under %'] = 0
        
    # Round the percentages to 2 decimal places
    grouped_data['Over %'] = grouped_data['Over %'].round(1)
    grouped_data['Under %'] = grouped_data['Under %'].round(1)

    # Check if 'Push' is present and calculate 'Push %' if it is
    if 'Push' in grouped_data.columns:
        grouped_data['Push %'] = (grouped_data['Push'] / grouped_data['Total']) * 100
        grouped_data['Push %'] = grouped_data['Push %'].round(1)

    # Print the percentages
    grouped_data.to_csv("results/"+sport+"_all-data-grouped-by-player_"+formatted_date+".csv")


    # Existing code...

    # After you've processed the data and calculated results
    grouped_data = sorted_data.groupby(['name', 'position', 'team', 'prop', 'result']).size().unstack(fill_value=0)

    # Calculate total counts for each player
    grouped_data['Total'] = grouped_data.sum(axis=1)

    # Calculate percentages for 'Over' and 'Under' and round to 2 decimal places
    if 'Over' in grouped_data:
        grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
    else:
        grouped_data['Over %'] = 0
    
    if 'Under' in grouped_data:
        grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100
    else:
        grouped_data['Under %'] = 0

    # Round the percentages to 2 decimal places
    grouped_data['Over %'] = grouped_data['Over %'].round(1)
    grouped_data['Under %'] = grouped_data['Under %'].round(1)

    # Check if 'Push' is present and calculate 'Push %' if it is
    if 'Push' in grouped_data.columns:
        grouped_data['Push %'] = (grouped_data['Push'] / grouped_data['Total']) * 100
        grouped_data['Push %'] = grouped_data['Push %'].round(1)

    # Print the percentages
    grouped_data.to_csv("results/"+sport+"_all-data-grouped-by-player-prop_"+formatted_date+".csv")

