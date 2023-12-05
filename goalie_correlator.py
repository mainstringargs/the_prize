import os
import csv
from datetime import datetime
import json
import argparse
from collections import Counter
import find_team_abbr
import chardet

goalie_prop_prefix = "G_"

def process_csv_files(
    goalie_prop="Goalie Saves",
    other_prop="Shots On Target",
    num_other=1,
    reverse_other=True,
    push_as_match=True,
    league="SOCCER",
):

    #print('reverse_other',reverse_other)
    goalie_prop = goalie_prop_prefix + goalie_prop
    relevant_props = {goalie_prop, other_prop}

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
    team_data = {}

    directory_path = "processing"
    filename_format = "prop_lines_"
    combined_dataframe = find_team_abbr.combine_csv_files(
        directory_path, filename_format
    )

    # Loop through CSV files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and (league + "_all-data-raw_") in filename:
            file_path = os.path.join(directory, filename)
            league = filename.split("_")[0]  # Extract the league name from the filename
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())

            # Print the detected encoding
            print("Detected encoding:", result['encoding'])
          
            with open(file_path, newline="", encoding=result['encoding']) as csvfile:
                reader = csv.DictReader(csvfile)
                event = {}
                for row in reader:
                    # print(row)
                    if "game_id" in row:
                        #print(row)
                        prop = row["prop"]
                        team = row["team_abbr"]
                        opp_team = row["opp_team_abbr"]
                        game_id = row["game_id"]
                        start_time = row["start_time"]
                        name = row["name"]
                        position = row["position"]
                        
                        if position == 'Goalkeeper' or position == 'G':
                            prop = goalie_prop_prefix + prop

                        line = row["line"]
                        actual = row["actual"]
                        result = row["result"]

                        if prop in relevant_props:
                            if "Owen" in name:
                                print(row)
                            if team not in team_data:
                                team_data[team] = []

                            if team not in event:
                                event[team] = {}

                            if prop not in event[team]:
                                event[team][prop] = {}

                            if name not in event[team][prop]:
                                event[team][prop][name] = {}

                            event[team][prop][name]["prop"] = prop
                            event[team][prop][name]["line"] = float(line)
                            event[team][prop][name]["actual"] = float(actual)
                            event[team][prop][name]["result"] = result
                            event[team][prop][name]["name"] = name
                            event[team][prop][name]["team"] = team
                            event[team][prop][name]["opp_team"] = opp_team
                            event[team][prop][name]["game_id"] = game_id
                            event[team][prop][name]["start_time"] = start_time                            
                        #print(team,prop,event[team][prop])

                for team in event:
                    team_data[team].append(event[team])
                    
        
    game_data = {}

    for team in team_data:
        data = team_data[team]
        
        for evt in data:
            for key, value in evt.items():
                #print(team,key,value)
                
                for k, v in value.items():
                    game_id = v['game_id']
                    is_goalie = (v['prop'] == goalie_prop)
                    opp_team = v['opp_team']  
                    team = v['team']     
                    name = v['name']     
                    
                    if game_id not in game_data:
                        game_data[game_id] = {}
                        game_data[game_id]["Goalie "+team+" Other "+opp_team] = {}
                        game_data[game_id]["Goalie "+opp_team+" Other "+team] = {}    
                        game_data[game_id]["Goalie "+team+" Other "+opp_team]['Goalie'] = {} 
                        game_data[game_id]["Goalie "+team+" Other "+opp_team]['Other'] = {}
                        game_data[game_id]["Goalie "+opp_team+" Other "+team]['Goalie'] = {} 
                        game_data[game_id]["Goalie "+opp_team+" Other "+team]['Other'] = {}                        
                    if is_goalie:
                        game_data[game_id]["Goalie "+team+" Other "+opp_team]['Goalie'][name] = v
                    else:
                        game_data[game_id]["Goalie "+opp_team+" Other "+team]['Other'][name] = v
    return game_data


def calculate_correlations(
    game_data,
    goalie_prop="Goalie Saves",
    other_prop="Shots On Target",
    num_other=1,
    reverse_other=True,
    push_as_match=True,
):
    raw_match_count = 0
    raw_over_match_count = 0
    raw_under_match_count = 0
    raw_total_events = 0

    team_correlations = {}

    goalie_prop = goalie_prop_prefix + goalie_prop
    
    def all_values_match(results, result_to_match, allow_push, max_results):
        #print('all_values_match','max_results',max_results,'result_to_match',result_to_match,'results',results)
        for val in range(max_results):
            #print('results[val][0]',results[val][0],'result_to_match',result_to_match)
            if results[val][0] != result_to_match or (
                allow_push and not results[val][0] != "Push"
            ):
                return False

        return True

    for game_id in game_data:



        for event in game_data[game_id]:
        
            team_raw_match = 0
            team_raw_over = 0
            team_raw_under = 0
            team_raw_total = 0
            tally = {}
            team_matches = []
            print(event)
            matchup_goalie = game_data[game_id][event]['Goalie']
            matchup_other = game_data[game_id][event]['Other']
            #print(matchup_other)
            matchup_other = dict(sorted(matchup_other.items(), key=lambda x: x[1]['line'], reverse=reverse_other))


            if (
                len(matchup_goalie) >= 1
                and len(matchup_other) >= num_other
            ):
                pass_yards = matchup_goalie
                receiving_yards = matchup_other
                pass_event = next(iter(pass_yards.values()))
                pass_result = pass_event["result"]
                pass_name = pass_event["name"]
                rriter = iter(receiving_yards.values())
                results = []
                others = []
                for i in range(num_other):
                    result = next(rriter)
                    result_val = result["result"]
                    result_name = result["name"]
                    results.append((result_val, result_name))
                    others.append(result_name)

                all_over_match = all_values_match(results, "Over", push_as_match, num_other)
                all_under_match = all_values_match(
                    results, "Under", push_as_match, num_other
                )

                raw_total_events = raw_total_events + 1
                team_raw_total = team_raw_total + 1

                if (
                    (all_over_match and pass_result == "Over")
                    or (all_under_match and pass_result == "Under")
                    or (pass_result == "Push" and push_as_match)
                ):
                    raw_match_count = raw_match_count + 1
                    team_raw_match = team_raw_match + 1
                    direction = None
                    if all_under_match or (pass_result == "Push" and push_as_match):
                        raw_under_match_count = raw_under_match_count + 1
                        team_raw_under = team_raw_under + 1
                        direction = "Under"
                    elif all_over_match or (pass_result == "Push" and push_as_match):
                        raw_over_match_count = raw_over_match_count + 1
                        team_raw_over = team_raw_over + 1
                        direction = "Over"
                    if direction != None:
                        tuple_match = (pass_name, tuple(others), direction)
                        team_matches.append(tuple_match)

                tally["raw_match_count"] = team_raw_match
                tally["raw_over_match_count"] = team_raw_over
                tally["raw_under_match_count"] = team_raw_under
                tally["raw_total_events"] = team_raw_total
                tally["team_matches"] = Counter(team_matches)
                if team_raw_total > 0:
                    tally["percent"] = round(team_raw_match / team_raw_total, 2)
                else:
                    tally["percent"] = 0

                if game_id not in team_correlations:
                    team_correlations[game_id] = {}
                team_correlations[game_id][event] = tally

  #  team_correlations = dict(
  #      sorted(team_correlations.items(), key=lambda x: x[1]["percent"], reverse=True)
   # )

   
    all_tally = {}
    all_tally["raw_match_count"] = raw_match_count
    all_tally["raw_over_match_count"] = raw_over_match_count
    all_tally["raw_under_match_count"] = raw_under_match_count
    all_tally["raw_total_events"] = raw_total_events

    if raw_total_events > 0:
        all_tally["percent"] = round(raw_match_count / raw_total_events, 2)
    else:
        all_tally["percent"] = 0
    
    team_correlations['All']={}
    team_correlations['All']['All'] = all_tally
    
    return team_correlations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script with command-line arguments")

    parser.add_argument("--goalie_prop", type=str, default="Goalie Saves", help="Goalie Prop")
    parser.add_argument(
        "--other_prop", type=str, default="Shots On Target", help="Other Prop"
    )
    parser.add_argument("--num_other", type=int, default=1, help="Num Other")
    parser.add_argument(
        "--reverse_other", type=str, default='True', help="Reverse Other Ordering"
    )
    parser.add_argument(
        "--push_as_match", type=str, default='True', help="Treat push as a match"
    )
    parser.add_argument("--league", type=str, default="SOCCER", help="League")

    args = parser.parse_args()
    goalie_prop = args.goalie_prop
    other_prop = args.other_prop
    num_other = args.num_other
    reverse_other = (args.reverse_other) == 'True'
    push_as_match = (args.push_as_match) == ' True'
    league = args.league
    
    print('args',args)
    print('goalie_prop',goalie_prop,'other_prop',other_prop,'num_other',num_other,'reverse_other',reverse_other,'push_as_match',push_as_match)    
    game_data = process_csv_files(
        goalie_prop, other_prop, num_other, reverse_other, push_as_match, league
    )
    
    # Save game_data to a JSON file
    with open("game_data.json", "w") as team_data_file:
        json.dump(game_data, team_data_file, indent=4)
        
    correlations = calculate_correlations(
        game_data, goalie_prop, other_prop, num_other, reverse_other, push_as_match
    )



    # Save team_correlations to a JSON file
    #with open("team_correlations.json", "w") as team_correlations_file:
    #    json.dump(team_correlations, team_correlations_file, indent=4)
        
   # print(team_correlations)

    for game_id in correlations:
       # print(game_id)
        for matchup in correlations[game_id]:
          #  print(matchup)
            if correlations[game_id][matchup]['raw_total_events'] > 0:
                print(game_id,matchup,correlations[game_id][matchup],"\n")