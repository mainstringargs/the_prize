from seleniumwire import webdriver
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
from urllib.parse import urlparse, parse_qs

def sleep_random_time():
    # Generate a random sleep time between 30 seconds and 1 minutes
    sleep_time = random.uniform(0, 2)  # seconds

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
urls = {"NBA":"aHR0cHM6Ly93d3cuc2NvcmVzYW5kb2Rkcy5jb20vbmJhL3BhcmxheQ==",
 "NFL":"aHR0cHM6Ly93d3cuc2NvcmVzYW5kb2Rkcy5jb20vbmZsL3BhcmxheQ==",
    "MLB":"aHR0cHM6Ly93d3cuc2NvcmVzYW5kb2Rkcy5jb20vbWxiL3BhcmxheQ=="}

books = ["fanduel", "bet365","betmgm","caesars","draftkings"]

def base64ToString(b):
    return str(b)

for book in books:
    for league, url in urls.items():
        decoded_url = str(base64.b64decode(url).decode())+"?book="+book

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
        children = list(element.find_elements(By.XPATH, "./*"))
        curr_list = []
        for child in children:
            a_list = list(child.find_elements(By.TAG_NAME, 'a'));
            for a in a_list:
                curr_list.append(a.get_attribute('href'))
            
            
        for a in curr_list:
            href = a
            print("loading...",href, flush=True)
            driver.get(href)
            
            selector = '//*[@id="simiq-game-select"]'
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
    
def extract_parameters(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params

for request in list(driver.requests):
    if request.response and 'simiq-query' in request.url:
        print(
            request.url,
            request.response.status_code,
            request.response.headers['Content-Type'],
            flush=True
        )
        

        driver.get(request.url)

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
            
            url_info = extract_parameters(request.url)
            
            book = None
            sport = None
            event = None
            
            if 'book' in url_info and 'sport' in url_info and 'event' in url_info:
                book = next(iter(url_info['book']))
                sport = next(iter(url_info['sport']))
                event = next(iter(url_info['event']))
                
            print('book',book,'sport',sport,'event',event, flush=True)
            
            if book and sport and event:
                # Define the JSON filename with the timestamp
                json_filename = f"{directory_path}/{book}_projections_{sport.upper()}_{event}_{timestamp}.json"

                # Save the JSON data to a file with pretty printing and without escaping characters
                with open(json_filename, "w", encoding="utf-8") as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)

                print(f"Webpage data saved to {json_filename}", flush=True)

        except json.JSONDecodeError:
            print("The extracted text is not valid JSON.")

# Close the browser window
driver.quit()
