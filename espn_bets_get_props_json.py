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
from seleniumwire.utils import decode


def sleep_random_time():
    # Generate a random sleep time between 30 seconds and 1 minutes
    sleep_time = random.uniform(0, 1)  # seconds

    print(f"Sleeping for {sleep_time} seconds...", flush=True)
    time.sleep(sleep_time)
    print("Awake now!", flush=True)


chrome_options = Options()


# chrome_options.add_argument("--headless")

def is_string_in_json(data, search_string):
    if isinstance(data, dict):
        # If it's a dictionary, search values
        for value in data.values():
            if is_string_in_json(value, search_string):
                return True
    elif isinstance(data, list):
        # If it's a list, search elements
        for item in data:
            if is_string_in_json(item, search_string):
                return True
    elif isinstance(data, str):
        # If it's a string, check for the search string
        if search_string in data:
            return True
    return False


# Specify the directory path you want to create
directory_path = 'espn_bets'

# Check if the directory already exists
if not os.path.exists(directory_path):
    # If it doesn't exist, create the directory
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")
else:
    print(f"Directory '{directory_path}' already exists.")

# Navigate to the desired URL (base 64 encoded)
urls = {
    "NBA": "aHR0cHM6Ly9lc3BuYmV0LmNvbS9zcG9ydC9iYXNrZXRiYWxsL29yZ2FuaXphdGlvbi91bml0ZWQtc3RhdGVzL2NvbXBldGl0aW9uL25iYS9mZWF0dXJlZC1wYWdl",
    "NFL": "aHR0cHM6Ly9lc3BuYmV0LmNvbS9zcG9ydC9mb290YmFsbC9vcmdhbml6YXRpb24vdW5pdGVkLXN0YXRlcy9jb21wZXRpdGlvbi9uZmwvZmVhdHVyZWQtcGFnZQo=",
    "NHL": "aHR0cHM6Ly9lc3BuYmV0LmNvbS9zcG9ydC9ob2NrZXkvb3JnYW5pemF0aW9uL3VuaXRlZC1zdGF0ZXMvY29tcGV0aXRpb24vbmhsL2ZlYXR1cmVkLXBhZ2U=",
    "CBB": "aHR0cHM6Ly9lc3BuYmV0LmNvbS9zcG9ydC9iYXNrZXRiYWxsL29yZ2FuaXphdGlvbi91bml0ZWQtc3RhdGVzL2NvbXBldGl0aW9uL25jYWFiL2ZlYXR1cmVkLXBhZ2U="}


def base64ToString(b):
    return str(b)


retrieved = set()

for league, url in urls.items():
    driver = webdriver.Chrome(options=chrome_options)

    decoded_url = str(base64.b64decode(url).decode()).replace("/featured-page", "")

    print("decoded_url", decoded_url, flush=True)

    driver.get(decoded_url)
    sleep_random_time()
    element_id_prefix = "MarketplaceShelf"
    # Wait for at least one <pre> element to load (adjust the timeout as needed)
    wait = WebDriverWait(driver, 60)
    element = wait.until(
        EC.presence_of_element_located((By.XPATH, f"//div[starts-with(@id, '{element_id_prefix}')]"))
    )

    # Get all children of the selected element
    children = list(element.find_elements(By.XPATH, "./div/*"))
    curr_map = {}
    for child in children:
        a_list = list(child.find_elements(By.TAG_NAME, 'div'));

        for a in a_list:
            id_val = a.get_attribute('id')
            if "default" in id_val:
                id_val_arr = id_val.split("|")
                if len(id_val_arr) == 3:
                    print("id", id_val_arr[1], flush=True)
                    curr_map[id_val_arr[1]] = decoded_url + "/event/" + id_val_arr[1] + "/section/player_props"

    # driver.close()

    for key, value in curr_map.items():
        if key in retrieved:
            break
        #  driver = webdriver.Chrome(options=chrome_options)

        href = value
        print("loading...", href, flush=True)
        driver.get(href)
        wait = WebDriverWait(driver, 60)
        element = wait.until(
            EC.presence_of_element_located((By.XPATH, f"//div[starts-with(@class, visible)]"))
        )

        for request in list(driver.requests):
            if request.response and 'graphql/persisted_queries' in request.url:
                print(
                    request.url,
                    request.response.status_code,
                    request.response.headers['Content-Type'],
                    flush=True
                )
                body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                json_data = json.loads(body)
                retrieved.add(key)
                if "data" in json_data and "node" in json_data['data'] and "label" in json_data['data'][
                    'node'] and "Player Props" == json_data['data']['node']['label']:

                    try:
                        with open("espn_bets/" + league + "_" + key + ".json", 'w') as file:
                            json.dump(json_data, file, indent=4)
                        print("JSON data has been written to the file.")
                    except Exception as e:
                        print(f"An error occurred: {e}")

    # driver.close()
    driver.close()


def extract_parameters(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params

    # driver.get(request.url)
    #
    # sleep_random_time()
    #
    # # Wait for at least one <pre> element to load (adjust the timeout as needed)
    # wait = WebDriverWait(driver, 60)
    # elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'pre')))
    #
    # # Initialize an empty list to store the text content of all <pre> elements
    # json_data_list = []
    #
    # # Extract the text content of all <pre> elements
    # for element in elements:
    #     json_data_list.append(element.text)
    #
    # # Attempt to parse the extracted text as JSON
    # try:
    #     # Combine the text content of all <pre> elements into a single JSON string
    #     combined_json_data = ''.join(json_data_list)
    #
    #     data = json.loads(combined_json_data)
    #
    #     # Generate a timestamp
    #     timestamp = time.strftime("%Y-%m-%d")
    #
    #     url_info = extract_parameters(request.url)
    #
    #     book = None
    #     sport = None
    #     event = None
    #
    #     if 'book' in url_info and 'sport' in url_info and 'event' in url_info:
    #         book = next(iter(url_info['book']))
    #         sport = next(iter(url_info['sport']))
    #         event = next(iter(url_info['event']))
    #
    #     print('book', book, 'sport', sport, 'event', event, flush=True)
    #
    #     if book and sport and event:
    #         # Define the JSON filename with the timestamp
    #         json_filename = f"{directory_path}/{book}_projections_{sport.upper()}_{event}_{timestamp}.json"
    #
    #         # Save the JSON data to a file with pretty printing and without escaping characters
    #         with open(json_filename, "w", encoding="utf-8") as json_file:
    #             json.dump(data, json_file, ensure_ascii=False, indent=4)
    #
    #         print(f"Webpage data saved to {json_filename}", flush=True)
    #
    # except json.JSONDecodeError:
    #     print("The extracted text is not valid JSON.")
