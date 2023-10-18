from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import base64

driver = webdriver.Chrome()

# Specify the directory path you want to create
directory_path = 'pp_data'

# Check if the directory already exists
if not os.path.exists(directory_path):
    # If it doesn't exist, create the directory
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")
else:
    print(f"Directory '{directory_path}' already exists.")

# Navigate to the desired URL (base 64 encoded)
url = "aHR0cHM6Ly9hcGkucHJpemVwaWNrcy5jb20vcHJvamVjdGlvbnM/c2luZ2xlX3N0YXQ9dHJ1ZQ=="
decoded_url = base64.b64decode(url).decode()

print("decoded_url",decoded_url, flush=True)

driver.get(decoded_url)

# Wait for at least one <pre> element to load (adjust the timeout as needed)
wait = WebDriverWait(driver, 10)
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
    timestamp = time.strftime("%Y-%m-%d-%H%M%S")

    # Define the JSON filename with the timestamp
    json_filename = f"pp_data/prize_picks_projections_{timestamp}.json"

    # Save the JSON data to a file with pretty printing and without escaping characters
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"Webpage data saved to {json_filename}")

except json.JSONDecodeError:
    print("The extracted text is not valid JSON.")

# Close the browser window
driver.quit()
