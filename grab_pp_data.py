import schedule
import time
import subprocess
import datetime 

def run_get_props_json():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "get_props_json.py"])

def run_pp_results_grabber_json():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "pp_results_report.py"])
    
def run_streak_driver():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "streak_driver.py"])    

    
def run_ftn_scraper():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "ftn_scraper.py"])    

def run_streak_resulter():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "streak_resulter.py"])    

def run_ftn_resulter_nfl():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "ftn_resulter.py","--league","NFL"])    
    
def run_ftn_resulter_nba():
    # Run the "get_props_json.py" script using subprocess
    subprocess.run(["python", "ftn_resulter.py","--league","NBA"])    

# Schedule the script to run at 7:00 am, 2:00 pm, and 11:00 pm
schedule.every().day.at("07:00").do(run_get_props_json)
schedule.every().day.at("08:00").do(run_pp_results_grabber_json)
schedule.every().day.at("09:00").do(run_streak_resulter)
schedule.every().day.at("10:45").do(run_ftn_scraper)
schedule.every().day.at("12:00").do(run_streak_driver)
schedule.every().day.at("14:00").do(run_get_props_json)
schedule.every().day.at("09:45").do(run_ftn_resulter_nba)
schedule.every().day.at("23:00").do(run_get_props_json)


def checker():
    current_time = datetime.datetime.now()
    today = current_time.weekday()
    hour = current_time.hour
    minute = current_time.minute
    second = current_time.second
    #print("Checking", hour, minute, second, flush=True)
    
    # Check if today is Monday (0), Tuesday (1), or Friday (4) and it's 10:01 AM
    if today in [0, 1, 4] and hour == 10 and minute == 1 and second<1.0:
        run_ftn_resulter_nfl()

    
while True:
    checker()
    schedule.run_pending()
    time.sleep(1)
