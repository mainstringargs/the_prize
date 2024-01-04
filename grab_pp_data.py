import schedule
import time
import subprocess
import datetime


def run_get_props_json():
    current_time = datetime.datetime.now()
    print(f"Running run_get_props_json at {current_time}", flush=True)
    subprocess.run(["python", "pp_get_props_json.py"])
    print(f"Completed run_get_props_json at {datetime.datetime.now()}", flush=True)


def run_pp_results_grabber_json():
    current_time = datetime.datetime.now()
    print(f"Running run_pp_results_grabber_json at {current_time}", flush=True)
    subprocess.run(["python", "pp_results_report.py"])
    print(f"Completed run_pp_results_grabber_json at {datetime.datetime.now()}", flush=True)


def run_streak_driver():
    current_time = datetime.datetime.now()
    print(f"Running run_streak_driver at {current_time}", flush=True)
    subprocess.run(["python", "streak_driver.py"])
    print(f"Completed run_streak_driver at {datetime.datetime.now()}", flush=True)


def run_ftn_scraper():
    current_time = datetime.datetime.now()
    print(f"Running run_ftn_scraper at {current_time}", flush=True)
    subprocess.run(["python", "ftn_scraper.py"])
    print(f"Completed run_ftn_scraper at {datetime.datetime.now()}", flush=True)


def run_streak_resulter():
    current_time = datetime.datetime.now()
    print(f"Running run_streak_resulter at {current_time}", flush=True)
    subprocess.run(["python", "streak_resulter.py"])
    print(f"Completed run_streak_resulter at {datetime.datetime.now()}", flush=True)


def run_ftn_resulter_nfl():
    current_time = datetime.datetime.now()
    print(f"Running run_ftn_resulter_nfl at {current_time}")
    subprocess.run(["python", "ftn_resulter.py", "--league", "NFL"], flush=True)
    print(f"Completed run_ftn_resulter_nfl at {datetime.datetime.now()}", flush=True)


def run_ftn_resulter_nba():
    current_time = datetime.datetime.now()
    print(f"Running run_ftn_resulter_nba at {current_time}", flush=True)
    subprocess.run(["python", "ftn_resulter.py", "--league", "NBA"])
    print(f"Completed run_ftn_resulter_nba at {datetime.datetime.now()}", flush=True)


def prop_comp_driver():
    current_time = datetime.datetime.now()
    print(f"Running prop_comp_driver at {current_time}", flush=True)
    subprocess.run(["python", "prop_comp_combined_driver.py"])
    print(f"Completed prop_comp_driver at {datetime.datetime.now()}", flush=True)


# Schedule the script to run at 7:00 am, 12:55 pm, and 11:00 pm
# schedule.every().day.at("07:00").do(run_get_props_json)
schedule.every().day.at("09:30"
                        ).do(run_streak_driver)
schedule.every().day.at("06:45").do(run_pp_results_grabber_json)
schedule.every().day.at("07:30").do(run_streak_resulter)
# schedule.every().day.at("10:30").do(run_ftn_scraper)
schedule.every().day.at("11:00").do(run_streak_driver)
schedule.every().day.at("14:30").do(run_streak_driver)
schedule.every().day.at("17:30").do(run_streak_driver)

# schedule.every().day.at("09:45").do(run_ftn_resulter_nba)
schedule.every().day.at("06:00").do(run_get_props_json)
schedule.every().day.at("08:00").do(run_get_props_json)
schedule.every().day.at("10:00").do(run_get_props_json)
schedule.every().day.at("12:00").do(run_get_props_json)
schedule.every().day.at("14:00").do(run_get_props_json)
schedule.every().day.at("16:00").do(run_get_props_json)
schedule.every().day.at("18:00").do(run_get_props_json)
schedule.every().day.at("20:00").do(run_get_props_json)

schedule.every().day.at("07:15").do(prop_comp_driver)
schedule.every().day.at("07:45").do(prop_comp_driver)
schedule.every().day.at("08:15").do(prop_comp_driver)
schedule.every().day.at("08:45").do(prop_comp_driver)
schedule.every().day.at("09:15").do(prop_comp_driver)
schedule.every().day.at("09:45").do(prop_comp_driver)
schedule.every().day.at("10:15").do(prop_comp_driver)
schedule.every().day.at("10:45").do(prop_comp_driver)
schedule.every().day.at("11:15").do(prop_comp_driver)
schedule.every().day.at("11:45").do(prop_comp_driver)
schedule.every().day.at("12:15").do(prop_comp_driver)
schedule.every().day.at("12:45").do(prop_comp_driver)
schedule.every().day.at("13:15").do(prop_comp_driver)
schedule.every().day.at("13:45").do(prop_comp_driver)
schedule.every().day.at("14:15").do(prop_comp_driver)
schedule.every().day.at("14:45").do(prop_comp_driver)
schedule.every().day.at("15:15").do(prop_comp_driver)
schedule.every().day.at("15:45").do(prop_comp_driver)
schedule.every().day.at("16:15").do(prop_comp_driver)
schedule.every().day.at("16:45").do(prop_comp_driver)
schedule.every().day.at("17:15").do(prop_comp_driver)
schedule.every().day.at("17:45").do(prop_comp_driver)
schedule.every().day.at("18:15").do(prop_comp_driver)
schedule.every().day.at("18:45").do(prop_comp_driver)
schedule.every().day.at("19:15").do(prop_comp_driver)
schedule.every().day.at("19:45").do(prop_comp_driver)
schedule.every().day.at("20:15").do(prop_comp_driver)
schedule.every().day.at("20:45").do(prop_comp_driver)
schedule.every().day.at("21:15").do(prop_comp_driver)
schedule.every().day.at("22:15").do(prop_comp_driver)
schedule.every().day.at("23:15").do(prop_comp_driver)


def checker():
    current_time = datetime.datetime.now()
    today = current_time.weekday()
    hour = current_time.hour
    minute = current_time.minute
    second = current_time.second
    # print("Checking", hour, minute, second, flush=True)

    # Check if today is Monday (0), Tuesday (1), or Friday (4) and it's 10:01 AM
    # if today in [0, 1, 4] and hour == 10 and minute == 1 and second<1.0:
    #    run_ftn_resulter_nfl()


# if today in [5, 6] and hour == 9 and minute == 30 and second<1.0:
#   run_get_props_json()

while True:
    # checker()
    schedule.run_pending()
    time.sleep(60)
