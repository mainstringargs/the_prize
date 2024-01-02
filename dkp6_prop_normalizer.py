import json
import datetime
import json
import csv
import os

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

def find_newest_file_from_day(directory_path, specific_day, league):
    # Initialize variables to store information about the newest file
    newest_file = None
    newest_file_time = None

    # Iterate over the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        print(file_path,league)
        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path) and league in file_path:
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
csv_file_name = f"normalized_props/dkp6_props_{formatted_date}.csv"

leagues = ["NBA","NFL"]

# Example usage:
directory_path = "dkp6_data"


nfl_prop_types = ['RecYds', 'REC', 'TD', 'KPTS', 'PaTD', 'PaYds', 'RuYds', 'COMP', 'ATT', 'Ru+Rec']
nba_prop_types = ['3PM','AST','PTS','P+A+R','REB','STL','BLK']

prop_types = {"NFL":nfl_prop_types,"NBA":nba_prop_types}

# Create a list to store rows for the CSV file
csv_rows = []


for league in leagues:

    newest_file = find_newest_file_from_day(directory_path, formatted_date, league)

    print("newest_file", newest_file)

    with open(str(newest_file), 'rb') as f:
        f_data = f.read()

    json_info = json.loads(f_data.decode('utf-8'))

    print("Cleaning up", newest_file)
    os.remove(newest_file)

    comp_map = {}
    competitions = json_info.get('competitions')

    for comp in competitions:
        if "competitionId" in comp:
            comp_map[comp.get("competitionId")] = comp;

    print(comp_map)
    if 'unfilteredPicksMap' in json_info:
        unfiltered_picks_map = json_info.get('unfilteredPicksMap')

            
        existing_props = set()

        for prop in prop_types[league]:
            if prop in unfiltered_picks_map:
                prop_lines = unfiltered_picks_map.get(prop).get(prop)

                for entry in prop_lines:
                    player_detail = entry.get("playerDetail")
                    competitions = entry.get("competitions")[0]
                    stat_lines = entry.get("statLines")
                    player_dk_id = player_detail.get("playerDkId")
                    first_name = player_detail.get("firstName")
                    last_name = player_detail.get("lastName")
                    display_name = player_detail.get("displayName")
                    position_name = player_detail.get("positionName")
                    has_injury_status = player_detail.get("hasInjuryStatus")
                    team_name = player_detail.get("team").get("name")
                    team_city = player_detail.get("team").get("city")
                    team_abbr = player_detail.get("team").get("abbreviation")
                    competition_id = competitions.get("competitionId")
                    competition_name = competitions.get("name")
                    competition_start_time = competitions.get("startTime")
                    competition_state = competitions.get("competitionState")
                    competition_sport = comp_map.get(competition_id).get("sport")
                    away_team_abbr = competitions.get("awayTeam").get("abbreviation")
                    home_team_abbr = competitions.get("homeTeam").get("abbreviation")

                    
                    for stat_line in stat_lines:
                        
                        prop_name = stat_lines.get(stat_line).get("statCategory").get("name")
                        prop_abbr = stat_lines.get(stat_line).get("statCategory").get("abbreviation")
                        prop_line = stat_lines.get(stat_line).get("targetValue")
                        key = (display_name + " " + prop_name);
                        
                        if key not in existing_props:
                            existing_props.add(key)
                            # Append a new row to the list
                            csv_row = [
                                player_dk_id, first_name, last_name, display_name, position_name, has_injury_status,
                                team_name, team_city, team_abbr, competition_id, competition_name, competition_start_time,
                                competition_state, competition_sport, away_team_abbr, home_team_abbr, prop_name, prop_abbr, prop_line
                            ]

                            # Print the row
                            print("Parsed Row:", csv_row,flush=True)

                            # Append the row to the list
                            csv_rows.append(csv_row)
                    

# Writing the CSV file
with open(csv_file_name, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Write header
    csv_writer.writerow([
        'player_dk_id', 'first_name', 'last_name', 'display_name', 'position_name', 'has_injury_status',
        'team_name', 'team_city', 'team_abbr', 'competition_id', 'competition_name',
        'competition_start_time', 'competition_state', 'competition_sport', 'away_team_abbr', 'home_team_abbr',
        'prop_name', 'prop_abbr', 'prop_line'
    ])
    
    # Write rows
    csv_writer.writerows(csv_rows)

