import datetime
import os 
import json
import base64
import csv
import pandas as pd

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
            file_date = str(datetime.datetime.fromtimestamp(file_time).date())

            # Check if the file's date matches the specific day
            if file_date == specific_day:
                # If it's the first file matching the specific day or newer than the previous newest file
                if newest_file is None or file_time > newest_file_time:
                    newest_file = file_path
                    newest_file_time = file_time

    return newest_file
    
# Get today's date
today = datetime.datetime.now()

formatted_date = today.strftime("%Y-%m-%d")
newest_file = find_newest_file_from_day(pp_result_data_path, formatted_date)

print("found",newest_file)

date_format = "%Y-%m-%dT%H:%M:%S%z"

def get_mapped_stat(stat_type):
    stat_mapping = {
        "Pass Completions": "PassingCompletions",
        "Pass Yards": "PassingYards",
        "Pass TDs": "PassingTouchdowns",
        "Pass Attempts": "PassingAttempts",
        "Fumbles Lost": "FumblesLost",
        "INT": "Interceptions",
        "Pass INTs": "Interceptions",
        "Receptions": "Receptions",
        "Receiving Yards": "ReceivingYards",
        "Rec TDs": "ReceivingTouchdowns",
        "Rec Targets": "ReceivingTargets",
        "Rush Yards": "RushingYards",
        "Rush Attempts": "RushingAttempts",
        "Rush TDs": "RushingTouchdowns",
        "Fantasy Score": "FantasyScore",
        "Touchdowns": "Touchdowns",
        "Pass+Rush+Rec TDs": "PassingTouchdowns,RushingTouchdowns,ReceivingTouchdowns",
        "Rush+Rec TDs": "RushingTouchdowns,ReceivingTouchdowns",
        "Pass+Rush Yds": "PassingYards,RushingYards",
        "Rec+Rush Yds": "RushingYards,ReceivingYards",
        "Rush+Rec Yds": "RushingYards,ReceivingYards",
        "Sacks": "Sacks",
        "Tackles+Ast": "TackleAssists,Tackles",
        "FG Made": "FieldGoalsMade",
        #"Kicking Points": "KickingPoints",
        "Punts": "Punts",
        "Pitcher Strikeouts": "PitcherStrikeouts", 
        "Total Bases": "TotalBases",        
        "Walks Allowed": "WalksAllowed", 
        "Hits Allowed": "HitsAllowed", 
        "Pitcher Fantasy Score": "PitcherFantasyScore", 
        "Hits+Runs+RBIS": "HitsAndRunsAndRBIs",
        "Pitching Outs": "PitchingOuts",        
        "Pitcher Fantasy Score": "PitcherFantasyScore", 
        "Hitter Fantasy Score": "HitterFantasyScore", 
        "RBIs": "RBIs", 
        "Runs": "Runs",         
        "Hitter Strikeouts": "HitterStrikeouts",   
        "Earned Runs Allowed": "EarnedRunsAllowed",
        "Goalie Saves": "GoalieSaves",        
        #"Time On Ice": "TimeOnIce", 
        "Points": "Points", 
        "Goals": "Goals", 
        "Shots On Goal": "ShotsOnGoal", 
        "SOG + BS": "ShotsOnGoal,BlockedShots",
        "Assists": "Assists", 
        "Faceoffs Won": "FaceoffsWon", 
        "Hits": "Hits", 
        "Points": "Points",  
        "Rebounds": "Rebounds",        
        "Offensive Rebounds": "OffensiveRebounds",   
        "Defensive Rebounds": "DefensiveRebounds",   
        "Assists": "Assists",       
        "Turnovers": "Turnovers",  
        "Steals": "Steals",      
        "Blocked Shots": "BlockedShots",        
        "FG Attempted": "FieldGoalsAttempted",  
        "FG Made": "FieldGoalsMade",  
        "FG Missed": "FieldGoalsMissed",  
        "3-PT Made": "ThreePointersMade",    
        "3-PT Attempted": "ThreePointersAttempted",         
        "Free Throws Made": "FreeThrowsMade",  
        "Pts+Rebs+Asts": "PtsRebsAsts",               
        "Blks+Stls": "BlksStls",  
        "Pts+Asts": "PtsAsts",   
        "Pts+Rebs": "PtsRebs",   
        "Rebs+Asts": "RebsAsts",  
    }
    return stat_mapping.get(stat_type, None)


def get_prop_for_event(prop, player):
    #print(prop)

    # Parse the string to create a datetime object
    prop_start_time_dt = datetime.datetime.strptime(prop['start_time'], date_format)

    for event in player["last_five_results"]:
        event_start_time_dt =  datetime.datetime.strptime(event["GameStartTime"], date_format)
        if (prop_start_time_dt==event_start_time_dt):
            return event
    return None

def get_actual_result(prop,event):
    stat_type = prop['stat_type']
    if "Totals" not in event:
        return None
    totals = event["Totals"]
    mapped_stat = get_mapped_stat(stat_type)
    
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
                player_id = prop['player_id']
                combo = prop['combo']
                is_promo = prop['is_promo']
                line_score = prop['line_score']
                stat_type = prop['stat_type']
                start_time = prop['start_time']
                last_five_url = decoded_url+str(player_id)+"/last_five_games?league_name="+str(league)
                
                if not combo:
                    print(player_id,league,name,position,market,combo,is_promo,line_score,stat_type,start_time,last_five_url);
                    actual_result = get_actual_result(prop,event)
                    
                    if actual_result is None:
                        no_handlers_list.append(stat_type+" "+league+" "+name);
                        continue
                        
                    result_string = "Push"
                    if line_score < actual_result:
                        result_string = "Over"
                    if line_score > actual_result:
                        result_string = "Under"
                    
                    prop_results_list.append([league,name,position,market,is_promo,stat_type,line_score,actual_result,result_string])
                    
                    
with open('processing/prop_report_'+formatted_date+'.csv', 'w', newline='') as file:
    writer = csv.writer(file)
     
    writer.writerow(["league","name","position","team","promo","prop","line","actual","result"])
    
    for result in prop_results_list:
        writer.writerow(result)


print("NO HANDLER REPORT")
for no_handler in no_handlers_list:
    if "in first" not in no_handler.lower() and "kicking points" not in no_handler.lower():
        print(no_handler)
print("END NO HANDLER REPORT")


processed = pd.read_csv('processing/prop_report_'+formatted_date+'.csv')

#print(processed)

df = processed.sort_values(by=['prop','result','team','name'])

df.to_csv("results/all-data-raw_"+formatted_date+".csv",index=False)

for sport in json_info:
    sorted_data = df[df['league'].isin([sport])]
    print(sorted_data)


    # After you've processed the data and calculated results
    grouped_data = sorted_data.groupby(['prop', 'result']).size().unstack(fill_value=0)

    # Calculate total counts for each 'prop'
    grouped_data['Total'] = grouped_data.sum(axis=1)

    # Calculate percentages for 'Over' and 'Under' and round to 2 decimal places
    grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
    grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100

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
    grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
    grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100

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
    grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
    grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100

    # Round the percentages to 2 decimal places
    grouped_data['Over %'] = grouped_data['Over %'].round(1)
    grouped_data['Under %'] = grouped_data['Under %'].round(1)

    # Check if 'Push' is present and calculate 'Push %' if it is
    if 'Push' in grouped_data.columns:
        grouped_data['Push %'] = (grouped_data['Push'] / grouped_data['Total']) * 100
        grouped_data['Push %'] = grouped_data['Push %'].round(1)

    # Print the percentages
    grouped_data.to_csv("results/"+sport+"_all-data-grouped-by-player-prop_"+formatted_date+".csv")

