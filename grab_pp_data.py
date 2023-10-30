import schedule
import time
import subprocess

def run_get_props_json():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "get_props_json.py"])

def run_pp_results_grabber_json():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "pp_results_grabber.py"])


# Schedule the script to run at 8:00 am, 2:00 pm, and 8:00 pm
schedule.every().day.at("07:00").do(run_pp_results_grabber_json)
schedule.every().day.at("08:00").do(run_get_props_json)
schedule.every().day.at("14:00").do(run_get_props_json)
schedule.every().day.at("23:00").do(run_get_props_json)


while True:
    schedule.run_pending()
    time.sleep(1)
