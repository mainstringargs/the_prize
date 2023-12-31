import os
import csv
from datetime import datetime
import sheets
import json
import argparse
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

parser = argparse.ArgumentParser(description="Script with command-line arguments")

parser.add_argument("--qb_prop", type=str, default="Pass Yards", help="QB Prop")
parser.add_argument("--other_prop", type=str, default="Receiving Yards", help="Other Prop")
parser.add_argument("--num_other", type=int, default=1, help="Num Other")
parser.add_argument("--reverse_other", type=bool, default=True, help="Reverse Other Ordering")
parser.add_argument("--push_as_match", type=bool, default=True, help="Treat push as a match")
parser.add_argument("--league", type=str, default="NFL", help="League")

args = parser.parse_args()
qb_prop = args.qb_prop
other_prop = args.other_prop
num_other = args.num_other
reverse_other = args.reverse_other
push_as_match = args.push_as_match
league = args.league
relevant_props = {qb_prop, other_prop}

print("qb_prop",qb_prop)
print("other_prop",other_prop)
print("num_other",num_other)
print("reverse_other",reverse_other)
print("push_as_match",push_as_match)
print("league",league)

directory_path = 'processing'
filename_format = 'prop_lines_'
combined_dataframe = find_team_abbr.combine_csv_files(directory_path, filename_format)
print(combined_dataframe)


# Loop through CSV files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv") and   (league+"_all-data-raw_") in filename:
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
                
                if league == 'NFL':
                    team_abbr = find_team_abbr.city_to_abbreviation(team)
                    
                    if (team == "Los Angeles" or team == "New York"):
                        team_abbr = find_team_abbr.find_team_abbr(combined_dataframe, name, "NFL")
                        if not team_abbr:
                            print("No abbr for",team,prop,name,flush=True)
                            team_abbr = team
                            
                    team = team_abbr
                
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
                    event[team][prop] = dict(sorted(event[team][prop].items(), key=lambda x: x[1]['line'], reverse=reverse_other))


            
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


def all_values_match(results, result_to_match, allow_push, max_results):
    #print('all_values_match','max_results',max_results,'result_to_match',result_to_match,'results',results)
    for val in range(max_results):
        #print('results[val][0]',results[val][0],'result_to_match',result_to_match)
        if results[val][0] != result_to_match or (allow_push and not results[val][0]!="Push"):
            return False
    
    return True

for team in team_data:

    tally = {}
    team_raw_match = 0
    team_raw_over = 0
    team_raw_under = 0
    team_raw_total = 0
    team_matches = []

  #  print(team,len(team_data[team]))
    for event in team_data[team]:
        #if team == 'NO':
       #     print('event',event)
        if qb_prop in event and other_prop in event and len(event[qb_prop]) >= 1 and len(event[other_prop]) >= num_other:      
            pass_yards = event[qb_prop]
            receiving_yards = event[other_prop]
          #  print('pass_yards',pass_yards)
           # print('receiving_yards',receiving_yards)
            pass_event = next(iter(pass_yards.values()))
            pass_result = pass_event['result']
            pass_name = pass_event['name']
         #   print('pass_result',pass_result)
            rriter = iter(receiving_yards.values())
           # result = next(rriter)
          #  receiving_result1 = result['result']
          #  receiving_name1 = result['name']
         #   receiving_result2 = next(rriter)['result']
         
            results = []
            others = []
            for i in range(num_other):
                result = next(rriter)
                result_val = result['result']
                result_name = result['name']
                results.append((result_val,result_name))
                others.append(result_name)
         
            all_over_match = all_values_match(results, 'Over', push_as_match, num_other) 
            all_under_match = all_values_match(results, 'Under', push_as_match, num_other)
          #  print('all_over_match',all_over_match,'all_under_match',all_under_match)
            
            raw_total_events = raw_total_events + 1
            team_raw_total = team_raw_total + 1
            
            if (all_over_match and pass_result == 'Over') or (all_under_match and pass_result=='Under') or (pass_result == "Push" and push_as_match):
                raw_match_count = raw_match_count + 1
                team_raw_match = team_raw_match + 1
                direction = None
                if all_under_match or (pass_result == 'Push' and push_as_match):
                    raw_under_match_count = raw_under_match_count + 1
                    team_raw_under = team_raw_under + 1
                    direction = 'Under'
                elif all_over_match or (pass_result == 'Push' and push_as_match):
                    raw_over_match_count = raw_over_match_count + 1 
                    team_raw_over = team_raw_over + 1
                    direction = 'Over'
                if direction != None:
                    tuple_match = (pass_name, tuple(others),  direction)
                    team_matches.append(tuple_match)
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

