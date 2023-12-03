import os
import csv
from datetime import datetime
import sheets
import json
from collections import Counter
import find_team_abbr

# Directory containing the CSV files
directory = "results"

# Directory to store the condensed CSVs
output_directory = "correlated"

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Get the current date in YYYY-MM-DD format
current_date = datetime.now().strftime('%Y-%m-%d')

# Initialize a dictionary to store combined data for each league and prop
team_data = {}

relevant_props = {"Pass Yards","Receiving Yards"}

directory_path = 'processing'
filename_format = 'prop_lines_'
combined_dataframe = find_team_abbr.combine_csv_files(directory_path, filename_format)
print(combined_dataframe)


# Loop through CSV files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv") and   "NFL_all-data-raw_" in filename:
        file_path = os.path.join(directory, filename)
        league = filename.split("_")[0]  # Extract the league name from the filename
        print(filename)
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            event = {}
            for row in reader:
                #print(row)
                prop = row['prop']
                team = row['team']
                name = row['name'] 
                team_abbr = find_team_abbr.find_team_abbr(combined_dataframe, name, "NFL")
                
                if team_abbr and (team == "Los Angeles" or team == "New York"):
                    team = team_abbr
                elif not team_abbr and (team == "Los Angeles" or team == "New York"):
                    print("No abbr for ",prop,team,name)
                
                line = row['line']                        
                actual = row['actual']  
                result = row['result']  
                
                if prop in relevant_props:
                
                    if team not in team_data:
                        team_data[team] = []
                        
                    if team not in event:
                        event[team] ={}
                    
                    if prop not in event[team]:
                        event[team][prop] = {}
                        
                    if name not in event[team][prop]:
                        event[team][prop][name] = {}
                        
                    event[team][prop][name]['prop'] = prop                    
                    event[team][prop][name]['line'] = float(line)
                    event[team][prop][name]['actual'] = float(actual)
                    event[team][prop][name]['result'] = (result) 
                    event[team][prop][name]['name'] = name
                    event[team][prop] = dict(sorted(event[team][prop].items(), key=lambda x: x[1]['line'], reverse=True))


            
            for team in event:
                team_data[team].append(event[team])        
                    

# Serializing json
json_object = json.dumps(team_data, indent=4)
 
# Writing to sample.json
with open("out.json", "w") as outfile:
    outfile.write(json_object)
    
raw_match_count = 0
raw_over_match_count = 0
raw_under_match_count = 0
raw_total_events = 0

team_correlations = {}



for team in team_data:

    tally = {}
    team_raw_match = 0
    team_raw_over = 0
    team_raw_under = 0
    team_raw_total = 0
    team_matches = []

    for event in team_data[team]:
        #print('event',event)
        if 'Pass Yards' in event and 'Receiving Yards' in event and len(event['Pass Yards']) == 1 and len(event['Receiving Yards']) > 1:      
            pass_yards = event['Pass Yards']
            receiving_yards = event['Receiving Yards']
          #  print('pass_yards',pass_yards)
           # print('receiving_yards',receiving_yards)
            pass_event = next(iter(pass_yards.values()))
            pass_result = pass_event['result']
            pass_name = pass_event['name']
         #   print('pass_result',pass_result)
            rriter = iter(receiving_yards.values())
            receiving_result1 = next(rriter)['result']
            receiving_name1 = next(rriter)['name']
         #   receiving_result2 = next(rriter)['result']
            
            raw_total_events = raw_total_events + 1
            team_raw_total = team_raw_total + 1
            
            if pass_result == receiving_result1: # and pass_result == receiving_result2:
                raw_match_count = raw_match_count + 1
                team_raw_match = team_raw_match + 1
            
                if pass_result == 'Under':
                    raw_under_match_count = raw_under_match_count + 1
                    team_raw_under = team_raw_under + 1
                    team_matches.append((pass_name, receiving_name1, 'Under'))
                elif pass_result == 'Over':
                    raw_over_match_count = raw_over_match_count + 1 
                    team_raw_over = team_raw_over + 1
                    team_matches.append((pass_name, receiving_name1, 'Over'))
    tally['raw_match_count'] = team_raw_match;
    tally['raw_over_match_count'] = team_raw_over;
    tally['raw_under_match_count'] = team_raw_under;
    tally['raw_total_events'] = team_raw_total;
    tally['team_matches'] = Counter(team_matches)
    if(team_raw_total > 0):
        tally['percent'] = round(team_raw_match/team_raw_total,2)
    else:
        tally['percent']= 0
    
    team_correlations[team] = tally

    
team_correlations = dict(sorted(team_correlations.items(), key=lambda x: x[1]['percent'], reverse=True))

for team in team_correlations:
    print(team, team_correlations[team], "\n")

print('raw_match_count',raw_match_count)
print('raw_over_match_count',raw_over_match_count)
print('raw_under_match_count',raw_under_match_count)
print('raw_total_events',raw_total_events)
print('percent',round(raw_match_count/raw_total_events,2))

