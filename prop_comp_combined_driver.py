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

    print("Sleeping for",sleep_time,"seconds",flush=True)
    # Sleep for the randomly generated time
    time.sleep(sleep_time)

# Call the function to sleep for a random time
sleep_random_time()


subprocess.run(["python", "pp_get_props_json.py"])
subprocess.run(["python", "ud_get_props_json.py"])
subprocess.run(["python", "dkp6_get_props_json.py"])
subprocess.run(["python", "sleeper_get_props_json.py"])

subprocess.run(["python", "pp_prop_normalizer.py"])
subprocess.run(["python", "ud_prop_normalizer.py"])
subprocess.run(["python", "dkp6_prop_normalizer.py"])
subprocess.run(["python", "sleeper_prop_normalizer.py"])


subprocess.run(["python", "prop_comp_combined.py"])
