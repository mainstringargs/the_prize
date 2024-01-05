import subprocess
import os
import fnmatch
import datetime
import argparse
import time
import random


def sleep_random_time():
    # Generate a random sleep time between 0 and 5 minutes
    sleep_time = random.uniform(0, 60)  # 300 seconds = 5 minutes

    print("Sleeping for", sleep_time, "seconds", flush=True)
    # Sleep for the randomly generated time
    time.sleep(sleep_time)


pp_result_data_path = 'normalized_props'

# Check if the directory already exists
if not os.path.exists(pp_result_data_path):
    # If it doesn't exist, create the directory
    os.makedirs(pp_result_data_path)
    print(f"Directory '{pp_result_data_path}' created.")
else:
    print(f"Directory '{pp_result_data_path}' already exists.")

# Call the function to sleep for a random time
sleep_random_time()

today_date = datetime.datetime.now().strftime('%Y%m%d')
json_file_path = f'normalized_props/same_prop_correlation_scorecard_{today_date}.json'
if not os.path.exists(json_file_path):
    print(f"The file '{json_file_path}' does not exist.  Lets create it.", flush=True)
    # Call the function to generate the scorecard
    subprocess.run(["python", "correlation_scorecard_same_prop.py"])
else:
    print(f"The file '{json_file_path}' already exists. Skipping the function call.", flush=True)

subprocess.run(["python", "pp_get_props_json.py"])
subprocess.run(["python", "ud_get_props_json.py"])
subprocess.run(["python", "dkp6_get_props_json.py"])
subprocess.run(["python", "sleeper_get_props_json.py"])

subprocess.run(["python", "pp_prop_normalizer.py"])
subprocess.run(["python", "ud_prop_normalizer.py"])
subprocess.run(["python", "dkp6_prop_normalizer.py"])
subprocess.run(["python", "sleeper_prop_normalizer.py"])

subprocess.run(["python", "prop_comp_combined.py"])
