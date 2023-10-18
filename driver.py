import subprocess
import os
import fnmatch
from datetime import datetime, timedelta
import argparse

# Default values
default_year = 2023
default_week = 6
default_pp_day = "saturday"
default_game_day = "sunday"

# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")
parser.add_argument("--game_day", type=str, default=default_game_day, help="Day of Game data")
parser.add_argument("--pp_day", type=str, default=default_pp_day, help="Day of PP data")
parser.add_argument("--year", type=int, default=default_year, help="Year")
parser.add_argument("--week", type=int, default=default_week, help="Week")
args = parser.parse_args()

# Access argument values
year_value = str(args.year)
week_value = str(args.week)
pp_data_day_of_week_value = str(args.pp_day).lower()
game_day_of_week_value = str(args.game_day).lower()

# Function to find the last created file on a specific day of the week
def find_last_created_on_day_of_week(pattern, path, day_of_week):
    day_mapping = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }

    if day_of_week not in day_mapping:
        return None  # Invalid day_of_week

    result = []
    today = datetime.now()
    last_week = today - timedelta(days=7)
    target_day = day_mapping[day_of_week]

    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                file_path = os.path.join(root, name)
                file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_creation_time >= last_week and file_creation_time.weekday() == target_day:
                    result.append((file_path, file_creation_time))

    if result:
        result.sort(key=lambda x: x[1], reverse=True)
        return result[0][0]  # Return the path of the last created file
    else:
        return None

# Find the last created file in 'pp_data' folder
last_created_file = find_last_created_on_day_of_week('*.json', 'pp_data', pp_data_day_of_week_value)

print("Found pp_file:", last_created_file, flush=True)

# Define script paths
script_paths = [
    ("espn_stats.py", ["--year", year_value, "--week", week_value, "--sport", "nfl"]),
    ("get_fantasy_data.py", ["--year", year_value, "--week", week_value]),
    ("props.py", ["--year", year_value, "--week", week_value, "--pp_file", last_created_file]),
    ("prop_results.py", ["--year", year_value, "--week", week_value, "--game_day", game_day_of_week_value, "--pp_day", pp_data_day_of_week_value,"--sport", "nfl"])
]

# Run subprocesses for each script
for script_path, script_args in script_paths:
    subprocess.run(["python", script_path] + script_args)
