import subprocess
import os
import fnmatch
import datetime
import argparse


def get_newest_file(directory):
    try:
        files = os.listdir(directory)
        if not files:
            return None  # No files in the directory
        full_paths = [os.path.join(directory, file) for file in files]
        newest_file = max(full_paths, key=os.path.getctime)
        return newest_file
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


current_year = str(datetime.datetime.now().year)
current_week = str(datetime.date.today().isocalendar()[1])

# Define script paths

subprocess.run(["python", "pp_get_props_json.py"])
subprocess.run(["python", "props.py", "--year", current_year, "--week", current_week, "--pp_file", get_newest_file('pp_data')])
subprocess.run(["python", "streak_finder.py", "--year", current_year, "--week", current_week])

print("deleting",get_newest_file('pp_data'));
os.remove(get_newest_file('pp_data'))