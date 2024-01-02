import json
import datetime
import json
import os
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

def find_newest_file_from_day(directory_path, specific_day, data_type):
    # Initialize variables to store information about the newest file
    newest_file = None
    newest_file_time = None

    # Iterate over the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path) and data_type in file_path:
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
csv_file_name = f"normalized_props/sleeper_props_{formatted_date}.csv"


# Example usage:
directory_path = "sleeper_data"


player_data_file = find_newest_file_from_day(directory_path, formatted_date, "players")
lines_data_file = find_newest_file_from_day(directory_path, formatted_date, "lines")
print("loading","player_data_file",player_data_file,"lines_data_file",lines_data_file)

with open(str(player_data_file), 'rb') as f:
    f_data = f.read()
    
json_info = json.loads(f_data.decode('utf-8'))

players_map = {}

for pd in json_info:
    players_map[pd["sport"].upper()+"-"+pd["player_id"]] = pd;


with open(str(lines_data_file), 'rb') as f:
    f_data = f.read()
       
json_info = json.loads(f_data.decode('utf-8'))
   
# Define the CSV file name with the current date
csv_file_name = f"normalized_props/sleeper_props_{formatted_date}.csv"

# Define the CSV headers
csv_headers = ["sport","game_id","game_status","line_type","outcome_type","wager_type","season_type","subject_type","subject_id","popularity","first_name","last_name","full_name","position","team","line","prop","over_multiplier","under_multiplier"]

sports = set()

with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer object
    csvwriter = csv.writer(csvfile)

    # Write the headers to the CSV file
    csvwriter.writerow(csv_headers)

    rows_to_sort = []
    for line_data in json_info:
        sport = line_data["sport"].upper()
        game_id = line_data["game_id"]
        game_status = line_data["game_status"]
        line_type = line_data["line_type"]
        outcome_type = line_data["outcome_type"]
        wager_type = line_data["wager_type"]
        season_type = line_data["season_type"]
        subject_type = line_data["subject_type"]
        subject_id = line_data["subject_id"]
        popularity = None;
        if "pick_stats" in line_data:
            popularity = line_data['pick_stats']['popularity']
            
        if sport+"-"+subject_id in players_map:
            player_info = players_map[sport+"-"+subject_id]
            #print(player_info)

            first_name = player_info['first_name']
            last_name = player_info['last_name']
            position = player_info['position']
            team = player_info['team']
            
            over_mult = None;
            under_mult = None;
            line = None;
            prop = None;
            for option in line_data['options']:
                payout_multiplier = option['payout_multiplier']
                line = option['outcome_value']
                prop = option['market_type']
                outcome = option['outcome']
                if outcome == "over":
                    over_mult = payout_multiplier
                elif outcome == "under":
                    under_mult = payout_multiplier
            
            rows_to_sort.append([sport,game_id,game_status,line_type,outcome_type,wager_type,season_type,subject_type,subject_id,popularity,first_name,last_name,(first_name+" "+last_name),position,team,line, prop, over_mult, under_mult])
              
    # Sort the rows by 'sport', 'first_name', and 'last_name'
    sorted_rows = sorted(rows_to_sort, key=lambda x: (x[0], x[10], x[11]))

    for row in sorted_rows:
        csvwriter.writerow(row)               
                
# Print a message indicating the CSV file has been created
print(f"CSV file '{csv_file_name}' created.")

print("Cleaning up",player_data_file)
print("Cleaning up",lines_data_file)
os.remove(player_data_file)
os.remove(lines_data_file)

