import os
import csv
from datetime import datetime
import json
import argparse
from collections import Counter
import find_team_abbr
import goalie_correlator

def find_props_per_positions(
    props_position=["G"],
    league="NHL",
):

    # Directory containing the CSV files
    directory = "results"

    # Directory to store the condensed CSVs
    output_directory = "correlated"

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Initialize a dictionary to store combined data for each league and prop
    props = set()

    directory_path = "processing"
    filename_format = "prop_lines_"

    # Loop through CSV files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and (league + "_all-data-raw_") in filename:
            file_path = os.path.join(directory, filename)
            league = filename.split("_")[0]  # Extract the league name from the filename
            with open(file_path, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                event = {}
                for row in reader:
                    # print(row)
                    prop = row["prop"]
                    team = row["team"]
                    name = row["name"]
                    position = row["position"]
                    if position in props_position:
                        props.add(prop)

    return props
    
    
qb_props = (find_props_per_positions(["G"],"NHL"))

rx_props = (find_props_per_positions(['F','D'],"NHL"))

team_correlations = []

print("Num combos to check",(len(qb_props)*len(rx_props)))

#for other in [1,2,3,4]:
for reverse in [False,True]:
    for qb_prop_check in qb_props:
        for rx_prop_check in rx_props:
            qb_prop = qb_prop_check
            other_prop = rx_prop_check
            num_other = 1
            reverse_other = reverse
            push_as_match = True
            league = "NHL"
            
            #print("Running...",'qb_prop',qb_prop,'other_prop',other_prop,'num_other',num_other,'reverse_other',reverse_other,'push_as_match',push_as_match, flush=True)    
            team_data = goalie_correlator.process_csv_files(
                qb_prop, other_prop, num_other, reverse_other, push_as_match, league
            )
            
            #print(team_data)
            
            team_correlation = goalie_correlator.calculate_correlations(
                team_data, qb_prop, other_prop, num_other, reverse_other, push_as_match
            )
            
            #print('team_correlation',(team_correlation['All']))
            if 'All' in team_correlation and 'All' in team_correlation['All'] and 'raw_total_events' in team_correlation['All']['All'] and team_correlation['All']['All']['raw_total_events']>20:
                team_correlations.append((qb_prop,other_prop,num_other,reverse_other,team_correlation))
        

team_correlations.sort(key=lambda x: x[4]['All']['All']["percent"], reverse=False)

print("Dumping out",flush=True)
for corr in team_correlations:
    print(corr[0],corr[1],corr[2],corr[3],corr[4]['All']['All'])
print("Done out",flush=True)