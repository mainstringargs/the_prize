import os
import datetime
import pandas as pd
import sheets
import pytz

today = datetime.datetime.now()
formatted_date = today.strftime("%Y-%m-%d")

# Specify the directory path you want to create
pp_result_data_path = 'normalized_props'

def find_newest_file_from_day(directory_path, specific_day, prefix):
    """
    Find the newest file in the specified directory based on a specific day and prefix.

    Parameters:
    - directory_path (str): The directory to search for files.
    - specific_day (str): The specific day to match files.
    - prefix (str): The prefix to match in file names.

    Returns:
    - str or None: The path of the newest file, or None if no matching file is found.
    """
    newest_file = None
    newest_file_time = None

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path) and prefix in filename and filename.endswith(".csv"):
            file_time = os.path.getctime(file_path)
            file_date = str(datetime.datetime.fromtimestamp(file_time).date())

            if file_date == specific_day:
                if newest_file is None or file_time > newest_file_time:
                    newest_file = file_path
                    newest_file_time = file_time

    return newest_file

def convert_dataframe_to_dict(name_column, dataframe):
    """
    Convert a DataFrame into a dictionary where the keys are values from the "Name" column,
    and the values are lists of matching rows as dictionaries.

    Parameters:
    - dataframe (pd.DataFrame): The DataFrame to convert.

    Returns:
    - dict: The converted dictionary.
    """
    result_dict = {}
    for index, row in dataframe.iterrows():
        name = row[name_column]
        row_dict = row.to_dict()
        if name not in result_dict:
            result_dict[name] = []
        result_dict[name].append(row_dict)
    return result_dict

print(f"Running for date {formatted_date}.")

directory_path = "normalized_props"

pp_props_file = find_newest_file_from_day(directory_path, formatted_date, "pp_props")
print("pp_props_file", pp_props_file)

pp_properties_dataframe = pd.read_csv(pp_props_file, encoding='utf-8') if pp_props_file else None

ud_props_file = find_newest_file_from_day(directory_path, formatted_date, "ud_props")
print("ud_props_file", ud_props_file)

ud_properties_dataframe = pd.read_csv(ud_props_file, encoding='utf-8') if ud_props_file else None

# Convert DataFrames to dictionaries
pp_properties_dict = convert_dataframe_to_dict("display_name",pp_properties_dataframe) if pp_properties_dataframe is not None else None
ud_properties_dict = convert_dataframe_to_dict("Full Name",ud_properties_dataframe) if ud_properties_dataframe is not None else None

pp_to_ud_props = {}
pp_to_ud_props['NBA'] = {
    "3-PT Made": "three_points_made",
    "Points": "points",
    "Rebounds": "rebounds",
    "Pts+Rebs+Asts": "pts_rebs_asts",    
    "Steals":"steals",
    "Fantasy Score":"fantasy_points",
    "Assists":"assists",   
    "Blks+Stls":"blks_stls",      
    "Blocked Shots":"blocks",
    "Pts+Asts":"pts_asts",
    "Pts+Rebs":"pts_rebs",
    "Rebs+Asts":"rebs_asts",
    "Turnovers":"turnovers",    
}

pp_to_ud_props['CBB'] = pp_to_ud_props['NBA']

pp_to_ud_props['NFL'] = {
    "Fantasy Score":"fantasy_points",
    "FG Made":"field_goals_made",   
    "INT":"passing_ints",   
    "Kicking Points":"kicking_points",  
    "Pass Attempts":"passing_att",    
    "Pass Completions":"passing_comps",    
    "Pass TDs":"passing_tds",       
    "Pass Yards":"passing_yds",    
    "Pass+Rush Yds":"passing_and_rushing_yds",   
    "Punts":"punts",     
    "Rec Targets":"receiving_tgts",    
    "Receiving Yards":"receiving_yds",   
    "Receptions":"receiving_rec",     
    "Rush Attempts":"rushing_att",     
    "Rush TDs":"rushing_tds",     
    "Rush Yards":"rushing_yds",       
    "Rush+Rec TDs":"rush_rec_tds",    
    "Rush+Rec Yds":"rush_rec_yds",     
    "Sacks":"sacks",     
    "Tackles":"tackles",       
    "Tackles+Ast":"tackles_and_assists",            
}

pp_to_ud_props['NHL'] = {
    "Points": "points",
    "Fantasy Score":"fantasy_points",
    "Assists":"assists",       
    "Blocked Shots":"blocked_shots",
    "Goals":"goals",     
    "Goalie Saves": "saves",
    "Shots On Goal":"shots",   
}

pp_to_ud_props['CFB'] = pp_to_ud_props['NFL']

prop_diffs = {}

for name in pp_properties_dict:
    pp = pp_properties_dict[name]
    ud = None
    if name in ud_properties_dict:
        ud = ud_properties_dict[name]
    
    pp_props_for_player = {}
    ud_props_for_player = {}
    
    if pp and ud:
        #print("Found in both",name, len(pp), len(ud))
        
        for p in pp:
            pp_props_for_player[p['stat_type']] = p
           # print("-->PrizePicks",p['league'],p['stat_type'])

        for u in ud:
            ud_props_for_player[u['Prop Name']] = u  
            #print("-->Underdog",u['Sport'],u['Prop Name'])
            
        for pp_prop in pp_props_for_player:
            sport = pp_props_for_player[pp_prop]['league']
            team = pp_props_for_player[pp_prop]['team']
            
                        
            pp_board_time = datetime.datetime.fromisoformat(pp_props_for_player[pp_prop]['board_time'])
            central_tz = pytz.timezone('America/Chicago')  # Change 'America/Chicago' to the appropriate time zone
            pp_board_time = pp_board_time.astimezone(central_tz)
            pp_start_time = datetime.datetime.fromisoformat(pp_props_for_player[pp_prop]['start_time'])            
            pp_board_time = pp_board_time.astimezone(central_tz)
            
            if sport in pp_to_ud_props and pp_prop in pp_to_ud_props[sport]:
                ud_prop = pp_to_ud_props[sport][pp_prop]
                
                if ud_prop in ud_props_for_player:

                    ud_info = ud_props_for_player[ud_prop]
                    pp_info = pp_props_for_player[pp_prop]
                    
                    ud_val = float(ud_info['Stat Value'])
                    pp_val = float(pp_info['line_score'])
                    
                    # Define a small threshold for floating-point comparisons
                    threshold = 0.0001

                    if abs(ud_val - pp_val) > threshold:
                    
                        if sport not in prop_diffs:
                            prop_diffs[sport] = {}
                         
                        if name not in prop_diffs[sport]:
                            prop_diffs[sport][name] = {}                        
                    
                        diff_value = round(ud_val - pp_val, 2)
                        
                        lower = "underdog"
                        
                        if ud_val > pp_val:
                            lower = "prizepicks"
                        
                        prop_diffs[sport][name][pp_prop] = {"team": team, 
                                                            "ud_val":ud_val,
                                                            "pp_val":pp_val,
                                                            "diff": abs(diff_value), "lower_source": lower, "pp_board_time":pp_board_time, "pp_start_time":pp_start_time}





flattened_diffs = []
for sport, sport_diffs in prop_diffs.items():
    for name, name_diffs in sport_diffs.items():
        for prop, diff in name_diffs.items():
            flattened_diffs.append({
                'Sport': sport,
                'Team': diff['team'],
                'Name': name,
                'Property': prop,
                'Underdog Prop Line': diff['ud_val'],
                'PrizePicks Prop Line': diff['pp_val'],
                'Line Difference': diff['diff'],
                'Lower Source': diff['lower_source'],
                'PP Post Time': diff['pp_board_time'],
                'Event Start': diff['pp_start_time']
            })

# Create a DataFrame
diff_df = pd.DataFrame(flattened_diffs)

# Sort by the 'Difference' column
diff_df = diff_df.sort_values(by='Line Difference', ascending=False)



# Iterate over each sport in prop_diffs
for sport, sport_diffs in prop_diffs.items():
    # Filter the dataframe for the current sport
    sport_df = diff_df[diff_df['Sport'] == sport]

    # Sort by the 'Line Difference' column
    sport_df = sport_df.sort_values(by='Line Difference', ascending=False)

    formatted_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")

    # Define the CSV file name with the current date and sport
    sport_output_csv_path = f"normalized_props/prop_diffs_{sport}_{formatted_stamp}.csv"

    # Save the filtered dataframe to a CSV file
    sport_df.to_csv(sport_output_csv_path, index=False)

    print(f'Differences for {sport} saved to {sport_output_csv_path}')
    
    formatted_stamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

    # Optionally, you can also write this filtered dataframe to a separate sheet in a Google Spreadsheet
    sheets.write_to_spreadsheet(sport_output_csv_path, "Prop Differencer", f'{sport} Differences', add_column_name="Updated", add_column_data=formatted_stamp, index=0, overwrite=True, append=False)
