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
import re
import time
import random

def sleep_random_time():
    # Generate a random sleep time between 30 seconds and 1 minutes
    sleep_time = random.uniform(0, 15)  # seconds

    print(f"Sleeping for {sleep_time} seconds...", flush=True)
    time.sleep(sleep_time)
    print("Awake now!", flush=True)

chrome_options = Options()
#chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

# Specify the directory path you want to create
directory_path = 'scores_and_odds_data'

# Check if the directory already exists
if not os.path.exists(directory_path):
    # If it doesn't exist, create the directory
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")
else:
    print(f"Directory '{directory_path}' already exists.")

# Navigate to the desired URL (base 64 encoded)
urls = {"NBA":"aHR0cHM6Ly93d3cuc2NvcmVzYW5kb2Rkcy5jb20vbmJhL3BhcmxheQ==", "NFL":"aHR0cHM6Ly93d3cuc2NvcmVzYW5kb2Rkcy5jb20vbmZsL3BhcmxheQ==", "MLB":"aHR0cHM6Ly93d3cuc2NvcmVzYW5kb2Rkcy5jb20vbWxiL3BhcmxheQ=="}

urlprefix = base64.b64decode('aHR0cHM6Ly9vcnA3NGkwcXk4LmV4ZWN1dGUtYXBpLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tL3Byb2Qvc2ltaXEtcXVlcnk/dj0xLjAmc3BvcnQ9')

books = ["fanduel","bet365","betmgm","caesars","draftkings"]

def base64ToString(b):
    return str(b)
    
for league, url in urls.items():
    decoded_url = base64.b64decode(url).decode()

    print("decoded_url",decoded_url, flush=True)
    
    driver.get(decoded_url)
    sleep_random_time()

    # Wait for at least one <pre> element to load (adjust the timeout as needed)
    wait = WebDriverWait(driver, 60)
    elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'section')))
    
    # Use WebDriverWait to wait for the element to be present
    selector = '//*[@id="simiq-game-select"]'
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, selector))
    )
    
    # Get all children of the selected element
    children = element.find_elements(By.XPATH, "./*")

    # Extract the integer value between /events/ and /parlay in each URL
    event_ids = [re.search(r'/events/(\d+)/parlay', a.get_attribute('href')).group(1) for child in children for a in child.find_elements(By.TAG_NAME, 'a') if re.search(r'/events/(\d+)/parlay', a.get_attribute('href'))]

    key = "0bb17ad1e5d7a763521233aa3c7a54f0"
    # Print or process the extracted event IDs
    for event_id in event_ids:
        for book in books:
            urlmiddle = f"{league.lower()}&event={event_id}&book={book}"
            urlpostfix = f"&key={key}&conditions="
            fullurl = (base64ToString(urlprefix)+urlmiddle+(urlpostfix)).replace("b'","").replace("'","")
            print('full url',fullurl,flush=True)
        

    # # Initialize an empty list to store the text content of all <pre> elements
    # json_data_list = []

    # # Extract the text content of all <pre> elements
    # for element in elements:
        # json_data_list.append(element.text)

    # # Attempt to parse the extracted text as JSON
    # try:
        # # Combine the text content of all <pre> elements into a single JSON string
        # combined_json_data = ''.join(json_data_list)
        
        # data = json.loads(combined_json_data)

        # # Generate a timestamp
        # timestamp = time.strftime("%Y-%m-%d-%H%M%S")

        # # Define the JSON filename with the timestamp
        # json_filename = f"{directory_path}/dkp6_projections_{league}_{timestamp}.json"

        # # Save the JSON data to a file with pretty printing and without escaping characters
        # with open(json_filename, "w", encoding="utf-8") as json_file:
            # json.dump(data, json_file, ensure_ascii=False, indent=4)

        # print(f"Webpage data saved to {json_filename}")

    # except json.JSONDecodeError:
        # print("The extracted text is not valid JSON.")

# Close the browser window
driver.quit()
