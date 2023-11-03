import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import base64;



# Function to scrape and save data
def scrape_and_save_data(base_url, output_folder, sport):
    # Initialize empty lists to store data
    player_list, team_list, stat_list, line_list, bet_list, win_percent_list = [], [], [], [], [], []

    # Set up the web driver (make sure to specify the path to your browser driver)
    driver = webdriver.Chrome()

    decoded_url = base64.b64decode(base_url).decode()
    # Open the initial page
    driver.get(decoded_url)

    while True:


        # Find the table using Selenium
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'rt-tbody'))
        )

        rows = table.find_elements(By.CLASS_NAME, 'rt-tr-group')
       
        # Iterate through the rows of the table
        for row in rows:
            #print(row.text,flush=True)

            row_data = row.text.split("\n");
            if len(row_data)<6:
                break;

            player, team, stat, line, bet, win_percent = row_data
            player_list.append(player.strip())
            team_list.append(team.strip())
            stat_list.append(stat.strip())
            line_list.append(line.strip())
            bet_list.append(bet.strip())
            win_percent_list.append(win_percent.strip())
            print(player, team, stat, line, bet, win_percent,flush=True)
            
        # Find the "Next" button and click it
        try:
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
        except:
            # If the "Next" button is not found, break the loop
            break
        next_button.click()

        # Wait for the new page to load (you may need to adjust the waiting time)
        time.sleep(5)

    # Create a DataFrame from the scraped data
    data = {
        'Player': player_list,
        'Team': team_list,
        'Stat': stat_list,
        'Line': line_list,
        'Bet': bet_list,
        'Win%': win_percent_list
    }
    df = pd.DataFrame(data)

    # Create a folder for the output if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate a filename with the current date
    current_datetime = time.strftime("%Y-%m-%d_%H%M%S")
    file_name = os.path.join(output_folder, f"{sport}_data_{current_datetime}.csv")

    # Save the data to a CSV file
    df.to_csv(file_name, index=False)

    # Close the browser
    driver.quit()
    
    
# URLs and output folder
nba_url = "aHR0cHM6Ly9mdG5uZXR3b3JrLnNoaW55YXBwcy5pby9wcE5CQS8="
#mlb_url = "aHR0cHM6Ly9mdG5uZXR3b3JrLnNoaW55YXBwcy5pby9wcF9tbGIv"
nfl_url = "aHR0cHM6Ly9mdG5uZXR3b3JrLnNoaW55YXBwcy5pby9wcF9uZmwv"
output_folder = "ftn_prop_predictions"

# Scraping and saving data for NBA, MLB, and NFL
scrape_and_save_data(nba_url, output_folder, "NBA")
#scrape_and_save_data(mlb_url, output_folder, "MLB")
scrape_and_save_data(nfl_url, output_folder, "NFL")

