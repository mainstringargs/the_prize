import json
import csv
import requests
from tabulate import tabulate
import argparse
import base64
import requests
from bs4 import BeautifulSoup

default_year = 2023
default_week = 8

# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")

parser.add_argument("--year", type=int, default=default_year, help="Year")
parser.add_argument("--week", type=int, default=default_week, help="Week")

# Parse arguments
args = parser.parse_args()

# Access argument values
year = str(args.year)
week = str(args.week)

print("Generating results for",year,week);

url = "aHR0cHM6Ly9mYW50YXN5ZGF0YS5jb20vQ0ZCX0ZhbnRhc3lTdGF0cy9GYW50YXN5U3RhdHNfUmVhZA=="
decoded_url = base64.b64decode(url).decode()

print("decoded_url",decoded_url, flush=True)

with open('processing/fantasy_actuals_cfb_'+str(year)+'_week_'+str(week)+'.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["year","week","name","fantasyScore","rawJson"])

    url = decoded_url

    data = {
        "sort": "FantasyPoints-asc",
        "pageSize": "3000",
        "group": None,
        "filter": None,       
        "filters.scope": "2",
        "filters.subscope": None,
        "filters.season": str(year),
        "filters.seasontype": "1",
        "filters.scoringsystem": "2",
        "filters.startweek": str(week),
        "filters.endweek": str(week),
    }

    print("request asc");
    response = requests.post(url, data=data)
    response.raise_for_status()

    players = list(response.json()["Data"])
    
    data = {
        "sort": "FantasyPoints-desc",
        "pageSize": "3000",
        "group": None,
        "filter": None,       
        "filters.scope": "2",
        "filters.subscope": None,
        "filters.season": str(year),
        "filters.seasontype": "1",
        "filters.scoringsystem": "2",
        "filters.startweek": str(week),
        "filters.endweek": str(week),
    }

    print("request desc");
    response = requests.post(url, data=data)
    response.raise_for_status()    
    
    players.extend(response.json()["Data"])
    players.reverse()
    
        # Remove duplicates by converting the list to a set and back to a list
    #unique_players = list({player["Name"]: player for player in players}.values())

    
    print("Number players",len(players));
    for player in players:
        if player['Week'] is not None:
            writer.writerow([player['Season'],player['Week'],player['Name'].encode("ascii", errors="ignore").decode(),player['FantasyPoints']])

