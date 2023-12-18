import os
import csv
from datetime import datetime
import json
import argparse
from collections import Counter
import find_team_abbr
import football_correlator

def find_props_per_positions(
    props_position=["QB"],
    league="NFL",
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
    
    
qb_props = (find_props_per_positions(["QB"],"NFL"))

rx_props = (find_props_per_positions(["WR","TE","RB"],"NFL"))

team_correlations = []

full_correlations = []

print("Num combos to check",(len(qb_props)*len(rx_props)))


                
for qb_prop_check in qb_props:
    for rx_prop_check in rx_props:
        qb_prop = qb_prop_check
        other_prop = rx_prop_check
        num_other = 1
        reverse_other = True
        push_as_match = True
        league = "NFL"
        pairwise_correlation = True
        
        print("Running...",'qb_prop',qb_prop,'other_prop',other_prop,'num_other',num_other,'reverse_other',reverse_other,'push_as_match',push_as_match, flush=True)    
        team_data = football_correlator.process_csv_files(
            qb_prop, other_prop, num_other, reverse_other, push_as_match, league
        )
        
        team_correlation = football_correlator.calculate_correlations(
            team_data, qb_prop, other_prop, num_other, reverse_other, push_as_match, pairwise_correlation
        )
        

        team_correlations.append((qb_prop,other_prop,num_other,reverse_other,team_correlation))
        

team_correlations.sort(key=lambda x: x[4]['All']["percent"], reverse=False)

pairwise = {}
total_combo_counter = Counter()

for corr in team_correlations:
    qb_prop = corr[0]
    other_prop = corr[1]
    num_other = corr[2]
    reverse_other = corr[3]
    team_correlation = corr[4]
    prop_combo_counter = Counter()
    #print('qb_prop',qb_prop,'other_prop',other_prop,'num_other',num_other,'reverse_other',reverse_other,'team_correlation',team_correlation)   
    
    for team_data in team_correlation:
        print('team_data',team_data)
        if team_data != 'All':
            team_matches = team_correlation[team_data]['team_matches'];
            if len(team_matches) > 0:
                prop_combo_counter = prop_combo_counter + team_matches
                pairwise[(qb_prop,other_prop)] = prop_combo_counter
                total_combo_counter = total_combo_counter + team_matches


for key, value in dict(reversed(total_combo_counter.most_common())).items():
    print(f"Key: {key}, Value: {value}")

#print("Dumping out",flush=True)
#for corr in team_correlations:
 #   print(corr[0],corr[1],corr[2],corr[3],corr[4]['All'])
#print("Done out",flush=True)