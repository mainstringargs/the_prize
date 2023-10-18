import json
import csv
import requests
from tabulate import tabulate
import argparse
import base64

default_year = 2023
default_week = 0

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

url = "aHR0cHM6Ly9sbS1hcGktcmVhZHMuZmFudGFzeS5lc3BuLmNvbS9hcGlzL3YzL2dhbWVzL2ZmbC9zZWFzb25zLw=="
decoded_url = base64.b64decode(url).decode()

print("decoded_url",decoded_url, flush=True)

with open('processing/fantasy_actuals_'+str(year)+'_week_'+str(week)+'.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["year","week","name","fantasyScore"])
    
    print("Grab offense...",flush=True);
    #offense
    for i in range(1,35):

        filter_string = {"players":{"filterSlotIds":{"value":[0,2,23,4,6]},"filterStatsForCurrentSeasonScoringPeriodId":{"value":[6]},"filterProTeamIds":{"value":[i]},"sortPercOwned":{"sortPriority":3,"sortAsc":False},"limit":50,"offset":0,"sortAppliedStatTotalForScoringPeriodId":{"sortAsc":False,"sortPriority":1,"value":6},"filterRanksForScoringPeriodIds":{"value":[6]},"filterRanksForRankTypes":{"value":["STANDARD"]},"filterRanksForSlotIds":{"value":[0,2,4,6,17,16]}}}

        headers = {
            "x-fantasy-filter": json.dumps(filter_string)
        }

        api_url = decoded_url+str(year)+"/segments/0/leaguedefaults/1?scoringPeriodId="+str(week)+"&view=kona_player_info"
        response = requests.get(api_url, headers=headers).json()

        if response and 'players' in response:
            for p in response["players"]:
                #print(p["player"]["fullName"])
                if 'stats' in p["player"] and len(p["player"]["stats"])>0:
                    writer.writerow([year,week,p["player"]["fullName"],p["player"]["stats"][0]['appliedTotal']]);
                else:
                    print("BYE")
   
    print("Grab defense...",flush=True);   
    #defense/st
    for i in range(1,35):

        filter_string = {"players":{"filterSlotIds":{"value":[16]},"filterStatsForCurrentSeasonScoringPeriodId":{"value":[6]},"filterProTeamIds":{"value":[i]},"sortPercOwned":{"sortPriority":3,"sortAsc":False},"limit":50,"offset":0,"sortAppliedStatTotalForScoringPeriodId":{"sortAsc":False,"sortPriority":1,"value":6},"filterRanksForScoringPeriodIds":{"value":[6]},"filterRanksForRankTypes":{"value":["STANDARD"]},"filterRanksForSlotIds":{"value":[0,2,4,6,17,16]}}}
        headers = {
            "x-fantasy-filter": json.dumps(filter_string)
        }

        api_url = decoded_url+str(year)+"/segments/0/leaguedefaults/1?scoringPeriodId="+str(week)+"&view=kona_player_info&lineupSlot=16"
        response = requests.get(api_url, headers=headers).json()

        if response and 'players' in response:
            for p in response["players"]:
                #print(p["player"]["fullName"])
                if 'stats' in p["player"] and len(p["player"]["stats"])>0:
                    writer.writerow([year,week,p["player"]["fullName"],p["player"]["stats"][0]['appliedTotal']]);
                else:
                    print("BYE")
   
    print("Grab Kickers...",flush=True);
    #Grab kickers..
    for i in range(1,35):

        filter_string = {"players":{"filterSlotIds":{"value":[17]},"filterStatsForCurrentSeasonScoringPeriodId":{"value":[6]},"sortPercOwned":{"sortPriority":3,"sortAsc":False},"filterProTeamIds":{"value":[i]},"limit":50,"offset":0,"sortAppliedStatTotalForScoringPeriodId":{"sortAsc":False,"sortPriority":1,"value":6},"filterRanksForScoringPeriodIds":{"value":[6]},"filterRanksForRankTypes":{"value":["STANDARD"]},"filterRanksForSlotIds":{"value":[0,2,4,6,17,16]}}}

        headers = {
            "x-fantasy-filter": json.dumps(filter_string)
        }

        api_url = decoded_url+str(year)+"/segments/0/leaguedefaults/1?scoringPeriodId="+str(week)+"&view=kona_player_info&lineupSlot=17"
        response = requests.get(api_url, headers=headers).json()

        if response and 'players' in response:
            for p in response["players"]:
                #print(p["player"]["fullName"])
                if 'stats' in p["player"] and len(p["player"]["stats"])>0:
                    writer.writerow([year,week,p["player"]["fullName"],p["player"]["stats"][0]['appliedTotal']]);
                else:
                    print("BYE")
        
    print("DONE",flush=True)