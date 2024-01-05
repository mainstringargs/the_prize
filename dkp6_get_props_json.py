from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import base64
from selenium.webdriver.chrome.options import Options
import os
import glob
import time
import random


def sleep_random_time():
    # Generate a random sleep time between 30 seconds and 1 minutes
    sleep_time = random.uniform(10, 30)  # seconds

    print(f"Sleeping for {sleep_time} seconds...", flush=True)
    time.sleep(sleep_time)
    print("Awake now!", flush=True)


chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

# Specify the directory path you want to create
directory_path = 'dkp6_data'

#files = glob.glob(directory_path + '/*')
#for f in files:
#    os.remove(f)

# Check if the directory already exists
if not os.path.exists(directory_path):
    # If it doesn't exist, create the directory
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")
else:
    print(f"Directory '{directory_path}' already exists.")

# Navigate to the desired URL (base 64 encoded)
urls = {"NBA": "aHR0cHM6Ly9waWNrNi5kcmFmdGtpbmdzLmNvbS8/c3BvcnQ9TkJBJl9kYXRhPXJvdXRlcyUyRl9pbmRleA==",
        "NFL": "aHR0cHM6Ly9waWNrNi5kcmFmdGtpbmdzLmNvbS8/c3BvcnQ9TkZMJl9kYXRhPXJvdXRlcyUyRl9pbmRleA=="}

draft_groups = {"NBA": set(), "NFL": set()}


def grab_url_data(league, url, dgid=None):
    if dgid:
        updatedUrl = url + "&pickGroup=" + str(dgid)
        print("Loading..." + updatedUrl, flush=True);
        driver.get(updatedUrl)
    else:
        driver.get(url)

    sleep_random_time()
    # Wait for at least one <pre> element to load (adjust the timeout as needed)
    wait = WebDriverWait(driver, 60)
    elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'pre')))
    # Initialize an empty list to store the text content of all <pre> elements
    json_data_list = []
    # Extract the text content of all <pre> elements
    for element in elements:
        json_data_list.append(element.text)
    # Attempt to parse the extracted text as JSON
    try:
        # Combine the text content of all <pre> elements into a single JSON string
        combined_json_data = ''.join(json_data_list)

        data = json.loads(combined_json_data)

        # Generate a timestamp
        timestamp = time.strftime("%Y-%m-%d")

        if 'draftGroupId' in data:
            draft_group_id = int(data['draftGroupId'])

            # Define the JSON filename with the timestamp
            json_filename = f"{directory_path}/dkp6_projections_{league}_{draft_group_id}_{timestamp}.json"

            if (draft_group_id in draft_groups[league]):
                return None;

            # Save the JSON data to a file with pretty printing and without escaping characters
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            print(f"Webpage data saved to {json_filename}")

            return draft_group_id

    except json.JSONDecodeError:
        print("The extracted text is not valid JSON.")
    return None


for league, url in urls.items():
    decoded_url = base64.b64decode(url).decode()
    print("decoded_url", decoded_url, flush=True)
    dg_id = grab_url_data(league, decoded_url)
    draft_groups[league].add(dg_id)
    while (dg_id):
        dg_id = dg_id + 1
        dg_id = grab_url_data(league, decoded_url, dg_id)
        draft_groups[league].add(dg_id)

# Close the browser window
driver.quit()
