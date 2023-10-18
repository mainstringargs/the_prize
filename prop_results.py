import pandas as pd
import requests
from pandas import json_normalize
import json
import csv
from datetime import datetime
import dateutil
import os
import argparse

nfl_teams = {
    'Cardinals': 'Arizona Cardinals',
    'Falcons': 'Atlanta Falcons',
    'Ravens': 'Baltimore Ravens',
    'Bills': 'Buffalo Bills',
    'Panthers': 'Carolina Panthers',
    'Bears': 'Chicago Bears',
    'Bengals': 'Cincinnati Bengals',
    'Browns': 'Cleveland Browns',
    'Cowboys': 'Dallas Cowboys',
    'Broncos': 'Denver Broncos',
    'Lions': 'Detroit Lions',
    'Packers': 'Green Bay Packers',
    'Texans': 'Houston Texans',
    'Colts': 'Indianapolis Colts',
    'Jaguars': 'Jacksonville Jaguars',
    'Chiefs': 'Kansas City Chiefs',
    'Chargers': 'Los Angeles Chargers',
    'Rams': 'Los Angeles Rams',
    'Raiders': 'Las Vegas Raiders',
    'Dolphins': 'Miami Dolphins',
    'Vikings': 'Minnesota Vikings',
    'Patriots': 'New England Patriots',
    'Saints': 'New Orleans Saints',
    'Giants': 'New York Giants',
    'Jets': 'New York Jets',
    'Eagles': 'Philadelphia Eagles',
    'Steelers': 'Pittsburgh Steelers',
    '49ers': 'San Francisco 49ers',
    'Seahawks': 'Seattle Seahawks',
    'Buccaneers': 'Tampa Bay Buccaneers',
    'Titans': 'Tennessee Titans',
    'Commanders': 'Washington Commanders'
}

# Specify the directory path you want to create
directory_path = 'results'

# Check if the directory already exists
if not os.path.exists(directory_path):
    # If it doesn't exist, create the directory
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")
else:
    print(f"Directory '{directory_path}' already exists.")

# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")

default_game_day = "sunday"
default_pp_day = "saturday"

parser.add_argument("--game_day", type=str, default=default_game_day, help="Day of Game data")
parser.add_argument("--year", type=int, default=2023, help="Year")
parser.add_argument("--week", type=int, default=1, help="Week")
parser.add_argument("--pp_day", type=str, default=default_pp_day, help="Day of PP data")
parser.add_argument("--sport", type=str, default="nfl", help="Sport")

# Parse arguments
args = parser.parse_args()

# Access argument values
year_value = str(args.year)
week_value = str(args.week)
game_day = str(args.game_day).lower().strip()
pp_day = str(args.pp_day).lower().strip()
sport = str(args.sport).lower().strip()

print("Generating results for",year_value,week_value);

prop_lines = pd.read_csv("processing/prop_lines_"+year_value+"_week_"+week_value+".csv")

f = open("processing/espn_"+sport+"_actuals_"+year_value+"_week_"+week_value+".json")
espn_results = json.load(f)

# Function to clean player names
def clean_name(name):
    return str(name).replace("'", "").replace(".", "").replace("Jr", "").replace("II", "").replace("III", "").replace("Moehrig-Woodard", "Moehrig").replace("Joshua Palmer","Josh Palmer").replace("D/ST","DST").strip()

# Read the CSV file
df = pd.read_csv("processing/fantasy_actuals_"+year_value+"_week_"+week_value+".csv")

# Create a dictionary of fantasy results with cleaned player names
fantasy_results = df.to_dict(orient='records')
fantasy_nfl_results = {clean_name(result["name"]): result for result in fantasy_results}

passing_stats = {}
rushing_stats = {}
receiving_stats = {}
tackling_stats = {}
fumble_stats = {}
interception_stats = {}
punt_return_stats = {}
kick_return_stats = {}
punting_stats = {}
kicking_stats = {}

for stat_entry in espn_results:
    key = clean_name(stat_entry['name']) + " - "+ stat_entry['team']
    #print("key",key);
    if "rushingYards" in stat_entry:
        rushing_stats[key] = stat_entry;
    elif "passingYards" in stat_entry:
        passing_stats[key] = stat_entry;
    elif "receivingYards" in stat_entry:
        receiving_stats[key] = stat_entry;        
    elif "totalTackles" in stat_entry:
        tackling_stats[key] = stat_entry;   
    elif "interceptions" in stat_entry:
        interception_stats[key] = stat_entry;   
    elif "fumbles" in stat_entry:
        fumble_stats[key] = stat_entry        
    elif "fieldGoalPct" in stat_entry:
        kicking_stats[key] = stat_entry;    
    elif "punts" in stat_entry:
        punting_stats[key] = stat_entry;         
    elif "puntReturns" in stat_entry:
        punt_return_stats[key] = stat_entry;       
    elif "kickReturns" in stat_entry:
        kick_return_stats[key] = stat_entry;           
    else:
        print("No Handler for",stat_entry);

prop_filter = "NFL"
if sport == "nfl":
    prop_filter = "NFL"
elif sport == "college-football":
    prop_filter = "CFB"    

filter = (prop_lines['league']==prop_filter)
prop_lines = prop_lines[filter]
#filter = (prop_lines['position']!='DST')
#prop_lines = prop_lines[filter]

def find_team_name(team_name, market):
    for result in espn_results:
        team = result['team']

        clean_team_name = team_name.replace("North Carolina State","NC State").replace("(FL)","").replace("(OH)","").replace("St.","").replace("State","").strip().lower();
        clean_market = market.replace("North Carolina State","NC State").replace("(FL)","").replace("(FL)","").replace("(OH)","").replace("St.","").replace("State","").lower().strip();
        #if 'Bearkats'.lower() in team_name.lower():
         #   print(clean_team_name,"<<<>>>",clean_market,"<<<>>>",team.lower())
        if clean_team_name in team.lower() and clean_market in team.lower():
            print("FOUND",team,"for",team_name,"market",market);
            return team
    print("NO TEAM FOUND for",team_name,"market",market);
    return "NO_TEAM";
    

with open('processing/prop_report_'+year_value+'_week_'+week_value+'_game_day_'+game_day+'_pp_day_'+pp_day+'.csv', 'w', newline='') as file:
    writer = csv.writer(file)
     
    writer.writerow(["league","name","position","team","prop","line","actual","result"])
     
    for ind in prop_lines.index:
        league = prop_lines['league'][ind]
        name = clean_name(prop_lines['display_name'][ind])
        position = prop_lines['position'][ind]
        market = prop_lines['market'][ind]
        
        if sport == "college-football":
            team_name = find_team_name(prop_lines['team_name'][ind], market);
        else:
            team_name = prop_lines['team_name'][ind]
            
        if team_name == "NO_TEAM":
            print("!!!----> Skipping",name,position,market,"as there are no espn stats");
            continue;
        
        stat_type = prop_lines['stat_type'][ind]
        line_score = prop_lines['line_score'][ind]
        start_time = prop_lines['start_time'][ind]
        
        # Parse the timestamp string using dateutil.parser
        timestamp = dateutil.parser.parse(start_time)

        # Determine the day of the week (0=Monday, 1=Tuesday, ..., 6=Sunday)
        day_of_week = timestamp.weekday()

        # Convert the day of the week to a string
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = days[day_of_week].strip().lower()


        if position == "DST":
            key = name     
            team_name = nfl_teams[name.replace("DST","").strip()];
        else:
            key = name + " - "+ team_name
        
        #print("Loop Key",key)
        if game_day != day_name and game_day != "all":        
            print(name,team_name,game_day,"Prop is for",day_name,"ignoring")
            continue;
                    
        propStat = -10000
        if stat_type == "Receiving Yards":
            if key in receiving_stats:
                stat = receiving_stats[key]
                propStat = float(stat['receivingYards'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)
        elif stat_type == "Rec Targets":
            if key in receiving_stats:
                stat = receiving_stats[key]
                propStat = float(stat['receivingTargets'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)
        elif stat_type == "Receptions":
            if key in receiving_stats:
                stat = receiving_stats[key]
                propStat = float(stat['receptions'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)        
        elif stat_type == "Pass Yards":
            if key in passing_stats:
                stat = passing_stats[key]
                propStat = float(stat['passingYards'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)      
        elif stat_type == "Pass Completions":
            if key in passing_stats:
                stat = passing_stats[key]
                propStat = float(stat["completions/passingAttempts"].split('/')[0])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)        
        elif stat_type == "Pass Attempts":
            if key in passing_stats:
                stat = passing_stats[key]
                propStat = float(stat["completions/passingAttempts"].split('/')[1])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)     
        elif stat_type == "INT" or stat_type == "Pass INTs":
            if key in passing_stats:
                stat = passing_stats[key]
                propStat = float(stat['interceptions'])
            else:
                propStat = 0.0      
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)     
        elif stat_type == "Pass TDs":
            if key in passing_stats:
                stat = passing_stats[key]
                propStat = float(stat['passingTouchdowns'])
            else:
                propStat = 0.0      
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)                   
        elif stat_type == "Pass+Rush+Rec TDs":
            total = 0.0
            if key in receiving_stats:
                stat = receiving_stats[key]
                propPassingStat = float(stat['receivingTouchdowns'])
                total = total + propPassingStat
            if key in rushing_stats:
                stat = rushing_stats[key]
                propRushingStat = float(stat['rushingTouchdowns'])
                total = total + propRushingStat
            if key in passing_stats:
                stat = passing_stats[key]
                propRushingStat = float(stat['passingTouchdowns'])
                total = total + propRushingStat
            propStat = total    
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)         
        elif stat_type == "Rush+Rec TDs":
            total = 0.0
            if key in receiving_stats:
                stat = receiving_stats[key]
                propPassingStat = float(stat['receivingTouchdowns'])
                total = total + propPassingStat
            if key in rushing_stats:
                stat = rushing_stats[key]
                propRushingStat = float(stat['rushingTouchdowns'])
                total = total + propRushingStat
            propStat = total    
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)   
        elif stat_type == "Rec TDs":
            propStat = 0.0
            if key in receiving_stats:
                stat = receiving_stats[key]
                propStat = float(stat['receivingTouchdowns']) 
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)   
        elif stat_type == "Rush TDs":
            propStat = 0.0
            if key in rushing_stats:
                stat = rushing_stats[key]
                propStat = float(stat['rushingTouchdowns']) 
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)   
        elif stat_type == "Pass+Rush Yds":
            total = 0.0
            if key in passing_stats:
                stat = passing_stats[key]
                propPassingStat = float(stat['passingYards'])
                total = total + propPassingStat
            if key in rushing_stats:
                stat = rushing_stats[key]
                propRushingStat = float(stat['rushingYards'])
                total = total + propRushingStat
            propStat = total    
            print(name,position,team_name,stat_type,line_score)
            print(stat_type, propStat)                     
        elif stat_type == "Rush Yards":
            if key in rushing_stats:
                stat = rushing_stats[key]
                propStat = float(stat['rushingYards'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)    
        elif stat_type == "Rush Attempts":
            if key in rushing_stats:
                stat = rushing_stats[key]
                propStat = float(stat['rushingAttempts'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)       
        elif stat_type == "Rush+Rec Yds":
            total = 0.0;
            if key in receiving_stats:
                stat = receiving_stats[key]
                propReceivingStat = float(stat['receivingYards'])
                total = total + propReceivingStat
            if key in rushing_stats:
                stat = rushing_stats[key]
                propRushingStat = float(stat['rushingYards'])
                total = total + propRushingStat
            propStat = total
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)      
        elif stat_type == "Sacks":
            if key in tackling_stats:
                stat = tackling_stats[key]
                propStat = float(stat['sacks'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)        
        elif stat_type == "FG Made":
            if key in kicking_stats:
                stat = kicking_stats[key]
                propStat = float(stat["fieldGoalsMade/fieldGoalAttempts"].split('/')[0])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)            
        elif stat_type == "Punts":
            if key in punting_stats:
                stat = punting_stats[key]
                propStat = float(stat["punts"])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)            
        elif stat_type == "Tackles+Ast":
            if key in tackling_stats:
                stat = tackling_stats[key]
                propStat = float(stat['totalTackles'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)               
        elif stat_type == "Kicking Points":
            if key in kicking_stats:
                stat = kicking_stats[key]
                propStat = float(stat['totalKickingPoints'])
            else:
                propStat = 0.0
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)            
        elif stat_type == "Fantasy Score" and name in fantasy_nfl_results:
            propStat = float(fantasy_nfl_results[name]['fantasyScore'])
            print(name,position,team_name,stat_type,line_score)
            print(stat_type,propStat)            
        elif "in First" not in stat_type:
            print("!!!!No handler for:")
            print("!!!!",name,position,team_name,stat_type,line_score)      
        
        if propStat > -9999:
            result = "Tie"
            if line_score < propStat:
                result = "Over"
            if line_score > propStat:
                result = "Under"
                
            writer.writerow([league, name, position, team_name, stat_type, line_score, propStat, result])
            
            
processed = pd.read_csv('processing/prop_report_'+year_value+'_week_'+week_value+'_game_day_'+game_day+'_pp_day_'+pp_day+'.csv')

print(processed)

sorted_data = processed.sort_values(by=['prop','result','team','name'])

sorted_data.to_csv("results/"+sport+"_all-data-raw_"+year_value+"_week_"+week_value+"_game_day_"+game_day+'_pp_day_'+pp_day+".csv",index=False)


# Existing code...

# After you've processed the data and calculated results
grouped_data = sorted_data.groupby(['prop', 'result']).size().unstack(fill_value=0)

# Calculate total counts for each 'prop'
grouped_data['Total'] = grouped_data.sum(axis=1)

# Calculate percentages for 'Over' and 'Under' and round to 2 decimal places
grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100

# Round the percentages to 2 decimal places
grouped_data['Over %'] = grouped_data['Over %'].round(2)
grouped_data['Under %'] = grouped_data['Under %'].round(2)

# Check if 'Tie' is present and calculate 'Tie %' if it is
if 'Tie' in grouped_data.columns:
    grouped_data['Tie %'] = (grouped_data['Tie'] / grouped_data['Total']) * 100
    grouped_data['Tie %'] = grouped_data['Tie %'].round(2)

# Print the percentages
grouped_data.to_csv("results/"+sport+"_all-data-grouped-by-prop_"+year_value+"_week_"+week_value+"_game_day_"+game_day+'_pp_day_'+pp_day+".csv")


# After you've processed the data and calculated results
grouped_data = sorted_data.groupby(['name', 'position', 'team', 'result']).size().unstack(fill_value=0)

# Calculate total counts for each player
grouped_data['Total'] = grouped_data.sum(axis=1)

# Calculate percentages for 'Over' and 'Under' and round to 2 decimal places
grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100

# Round the percentages to 2 decimal places
grouped_data['Over %'] = grouped_data['Over %'].round(2)
grouped_data['Under %'] = grouped_data['Under %'].round(2)

# Check if 'Tie' is present and calculate 'Tie %' if it is
if 'Tie' in grouped_data.columns:
    grouped_data['Tie %'] = (grouped_data['Tie'] / grouped_data['Total']) * 100
    grouped_data['Tie %'] = grouped_data['Tie %'].round(2)

# Print the percentages
grouped_data.to_csv("results/"+sport+"_all-data-grouped-by-player_"+year_value+"_week_"+week_value+"_game_day_"+game_day+'_pp_day_'+pp_day+".csv")


# Existing code...

# After you've processed the data and calculated results
grouped_data = sorted_data.groupby(['name', 'position', 'team', 'prop', 'result']).size().unstack(fill_value=0)

# Calculate total counts for each player
grouped_data['Total'] = grouped_data.sum(axis=1)

# Calculate percentages for 'Over' and 'Under' and round to 2 decimal places
grouped_data['Over %'] = (grouped_data['Over'] / grouped_data['Total']) * 100
grouped_data['Under %'] = (grouped_data['Under'] / grouped_data['Total']) * 100

# Round the percentages to 2 decimal places
grouped_data['Over %'] = grouped_data['Over %'].round(2)
grouped_data['Under %'] = grouped_data['Under %'].round(2)

# Check if 'Tie' is present and calculate 'Tie %' if it is
if 'Tie' in grouped_data.columns:
    grouped_data['Tie %'] = (grouped_data['Tie'] / grouped_data['Total']) * 100
    grouped_data['Tie %'] = grouped_data['Tie %'].round(2)

# Print the percentages
grouped_data.to_csv("results/"+sport+"_all-data-grouped-by-player-prop_"+year_value+"_week_"+week_value+"_game_day_"+game_day+'_pp_day_'+pp_day+".csv")

