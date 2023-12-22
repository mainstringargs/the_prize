import os
import datetime
import pandas as pd
import sheets
import pytz
from operator import itemgetter

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

def remove_name_extension(name):
    """
    Remove specific name extensions from a given name.
    """
    suffixes_to_remove = ["Jr.", "Sr.", "II", "III", "IV", "Ph.D."]  # Add more suffixes if needed
    cleaned_name = name.replace("'","").replace("-","")
    for suffix in suffixes_to_remove:
        cleaned_name = cleaned_name.replace(suffix, "").strip()
    return cleaned_name

def convert_dataframe_to_dict(name_column, dataframe):
    """
    Convert a DataFrame into a dictionary where the keys are values from the specified column (with certain extensions removed),
    and the values are lists of matching rows as dictionaries.

    Parameters:
    - name_column (str): The name of the column to use as keys.
    - dataframe (pd.DataFrame): The DataFrame to convert.

    Returns:
    - dict: The converted dictionary.
    """
    if name_column not in dataframe.columns:
        raise ValueError(f"Column '{name_column}' not found in the DataFrame.")

    result_dict = {}
    grouped_data = dataframe.groupby(name_column)
    
    for name, group in grouped_data:
        # Remove specific name extensions from the name
        cleaned_name = remove_name_extension(name)
        result_dict[cleaned_name] = group.to_dict(orient='records')

    return result_dict



print(f"Running for date {formatted_date}.")

directory_path = "normalized_props"

pp_props_file = find_newest_file_from_day(directory_path, formatted_date, "pp_props")
print("pp_props_file", pp_props_file)

pp_properties_dataframe = pd.read_csv(pp_props_file, encoding='utf-8') if pp_props_file else None

ud_props_file = find_newest_file_from_day(directory_path, formatted_date, "ud_props")
print("ud_props_file", ud_props_file)

ud_properties_dataframe = pd.read_csv(ud_props_file, encoding='utf-8') if ud_props_file else None

dkp6_props_file = find_newest_file_from_day(directory_path, formatted_date, "dkp6_props")
print("dkp6_props_file", dkp6_props_file)

dkp6_properties_dataframe = pd.read_csv(dkp6_props_file, encoding='utf-8') if dkp6_props_file else None

sleeper_props_file = find_newest_file_from_day(directory_path, formatted_date, "sleeper_props")
print("sleeper_props_file", sleeper_props_file)

sleeper_properties_dataframe = pd.read_csv(sleeper_props_file, encoding='utf-8') if sleeper_props_file else None


# Convert DataFrames to dictionaries
pp_properties_dict = convert_dataframe_to_dict("display_name",pp_properties_dataframe) if pp_properties_dataframe is not None else None
ud_properties_dict = convert_dataframe_to_dict("Full Name",ud_properties_dataframe) if ud_properties_dataframe is not None else None
dkp6_properties_dict = convert_dataframe_to_dict("display_name",dkp6_properties_dataframe) if dkp6_properties_dataframe is not None else None

sleeper_properties_dict = convert_dataframe_to_dict("full_name",sleeper_properties_dataframe) if sleeper_properties_dataframe is not None else None


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


pp_to_dkp6_props = {}
pp_to_dkp6_props['NBA'] = {
    "3-PT Made": "3PM",
    "Points": "PTS",
    "Rebounds": "REB",
    "Pts+Rebs+Asts": "P+A+R",    
    "Steals":"STL",
    "Assists":"AST",   
    "Blocked Shots":"BLK",
}

pp_to_dkp6_props['NFL'] = {
    "Kicking Points":"KPTS",  
    "Pass Attempts":"ATT",    
    "Pass Completions":"COMP",    
    "Pass TDs":"PaTD",       
    "Pass Yards":"PaYds",    
    "Receiving Yards":"RecYds",   
    "Receptions":"REC",       
    "Rush Yards":"RuYds",       
    "Rush+Rec Yds":"Ru+Rec",        
    "Rush+Rec TDs":"TD"
}

pp_to_sleeper_props = {}

pp_to_sleeper_props['NBA'] = {
    "3-PT Made": "threes_made",
    "Points": "points",
    "Rebounds": "rebounds",
    "Pts+Rebs+Asts": "pts_reb_ast",    
    "Steals":"steals",
    "Assists":"assists",   
    "Turnovers":"turnovers",  
    "Blocked Shots":"blocks",
}

pp_to_sleeper_props['NFL'] = {
    "Kicking Points":"kicking_points",  
    "Pass Attempts":"pass_attempts",    
    "Pass Completions":"pass_completions",    
    "Pass TDs":"passing_touchdowns",       
    "Rush TDs":"rushing_touchdowns",    
    "Pass Yards":"passing_yards",    
    "Receiving Yards":"receiving_yards",   
    "Receptions":"receptions",       
    "Rush Yards":"rushing_yards",       
    "Rush+Rec Yds":"Ru+Rec",        
    "Rush+Rec TDs":"TD",
    "INT":"interceptions", 
    "Fantasy Score":"fantasy_points",
    "Rush+Rec Yds":"rushing_and_receiving_yards",       
    "FG Made":"field_goals_made",  
    "Rush+Rec TDs":"anytime_touchdowns",      
    "Pass+Rush Yds":"passing_and_rushing_yds"
}

pp_to_ud_props['NHL'] = {
    "Points": "points",
    "Assists":"assists",       
    "Blocked Shots":"blocked_shots",
    "Goals":"goals",     
    "Shots On Goal":"shots",   
}

pp_to_sleeper_props['CBB'] = pp_to_sleeper_props['NBA']
pp_to_sleeper_props['CFB'] = pp_to_sleeper_props['NFL']

def invert_dict(mydict):
    return dict(map(reversed, mydict.items()))

ud_dkp6_prop_diffs = {}
ud_pp_prop_diffs = {}
dkp6_pp_prop_diffs = {}
sleeper_pp_prop_diffs = {}

def get_line(pick_dict, site):
    if pick_dict:
        if site == "pp":
            if "line_score" in pick_dict:
                return float(pick_dict["line_score"])
        elif site == "ud":
            if "Stat Value" in pick_dict and not pick_dict['Boosted']:
                return float(pick_dict["Stat Value"])
        elif site == "dkp6":
            if "prop_line" in pick_dict:
                return float(pick_dict["prop_line"])
    return None;
    
def get_sport(prop_data):
    for key, value in prop_data.items():
        if key == "pp" and "league" in value:
            return value["league"].upper().strip()
        elif key == "ud" and "Sport" in value:
            return value["Sport"].upper().strip()
        elif key == "dkp6" and "competition_sport" in value:
            return value["competition_sport"].upper().strip()
        elif key == "sl" and "sport" in value:
            return value["sport"].upper().strip()       
    return None;

def get_team(prop_data):
    for key, value in prop_data.items():
        if key == "pp" and "team" in value:
            return value["team"].upper().strip()
        elif key == "ud" and "Team Abbr" in value:
            return value["Team Abbr"].upper().strip()
        elif key == "dkp6" and "team_abbr" in value:
            return value["team_abbr"].upper().strip()
        elif key == "sl" and "team" in value:
            return value["team"].upper().strip()       
    return None;
    
def get_name(prop_data):
    for key, value in prop_data.items():
        if key == "pp" and "display_name" in value:
            return value["display_name"].strip()
        elif key == "ud" and "Full Name" in value:
            return value["Full Name"].strip()
        elif key == "dkp6" and "display_name" in value:
            return value["display_name"].strip()
        elif key == "sl" and "full_name" in value:
            return value["full_name"].strip()       
    return None;

def get_position(prop_data):
    for key, value in prop_data.items():
        if key == "pp" and "position" in value:
            return value["position"].upper().strip()
        elif key == "ud" and "position" in value:
            return value["position"].upper().strip()
        elif key == "dkp6" and "position_name" in value:
            return value["position_name"].upper().strip()
        elif key == "sl" and "position" in value:
            return value["position"].upper().strip()       
    return None;
    
def get_pp_line(prop_data):
    for key, value in prop_data.items():
        if key == "pp" and "line_score" in value:
            return float(value["line_score"])
    return None;
    
def get_ud_line(prop_data):
    for key, value in prop_data.items():
        if key == "ud" and "Stat Value" in value:
            return float(value["Stat Value"])
    return None;
    
def get_dkp6_line(prop_data):
    for key, value in prop_data.items():
        if key == "dkp6" and "prop_line" in value:
            return float(value["prop_line"])
    return None;

def get_sleeper_line(prop_data):
    for key, value in prop_data.items():
        if key == "sl" and "line" in value:
            return float(value["line"])
    return None;
    
def get_line(prop_data, source):
    if source == "pp":
        return get_pp_line(prop_data)
    if source == "ud":
        return get_ud_line(prop_data)
    if source == "dkp6":
        return get_dkp6_line(prop_data)
    if source == "sl":
        return get_sleeper_line(prop_data)        
    return None;
    
    
def get_sleeper_over_odds(prop_data):
    for key, value in prop_data.items():
        if key == "sl" and "over_multiplier" in value:
            return float(value["over_multiplier"])
    return None;
    
def get_sleeper_under_odds(prop_data):
    for key, value in prop_data.items():
        if key == "sl" and "under_multiplier" in value:
            return float(value["under_multiplier"])
    return None;

def get_sleeper_sleeper_popularity(prop_data):
    for key, value in prop_data.items():
        if key == "sl" and "popularity" in value:
            return float(value["popularity"])
    return None;
    
def get_high_line_source(prop_data):
    curr_high = 0.0;
    high_source = None;
    lines = set()
    
    for key, value in prop_data.items():
        if key == "dkp6":
            line = get_dkp6_line(prop_data);
            lines.add(line)
            if line > curr_high:
                curr_high = line
                high_source = "dkp6"
              #  print(key,line)
        elif key == "pp":
            line = get_pp_line(prop_data);
            lines.add(line)
            if line > curr_high:
                curr_high = line
                high_source = "pp"
               # print(key,line)
        elif key == "ud":
            line = get_ud_line(prop_data);
            lines.add(line)
            if line > curr_high:
                curr_high = line
                high_source = "ud"
              #  print(key,line)
        elif key == "sl":    
            line = get_sleeper_line(prop_data);
            lines.add(line)
            if line > curr_high:
                curr_high = line
                high_source = "sl" 
             #   print(key,line)                
    if len(lines) == 1:
       #print("all equals, no high")
        return None
        
    return high_source;
    
def get_low_line_source(prop_data):
    curr_low = 99999999999;
    low_source = None;
    lines = set()
    
    for key, value in prop_data.items():
        if key == "dkp6":
            line = get_dkp6_line(prop_data);
            lines.add(line)
            if line < curr_low:
                curr_low = line
                low_source = "dkp6"
        elif key == "pp":
            line = get_pp_line(prop_data);
            lines.add(line)
            if line < curr_low:
                curr_low = line
                low_source = "pp"
        elif key == "ud":
            line = get_ud_line(prop_data);
            lines.add(line)
            if line < curr_low:
                curr_low = line
                low_source = "ud"
        elif key == "sl":    
            line = get_sleeper_line(prop_data);
            lines.add(line)
            if line < curr_low:
                curr_low = line
                low_source = "sl"  
    if len(lines) == 1:
       # print("all equals, no low")
        return None
        
    return low_source;
    
def get_high_low_line_diff(prop_data, low_source, high_source):
    low_line = get_line(prop_data, low_source)
    high_line = get_line(prop_data, high_source)
    return (high_line - low_line);
    
def get_start_time(prop_data):    
    for key, value in prop_data.items():
        if key == "pp" and "start_time" in value:
            start_time = datetime.datetime.fromisoformat(value['start_time'])            
            start_time = start_time.astimezone(central_tz)
            return start_time;
        elif key == "ud" and "Scheduled Time" in value:
            scheduled_time_str = value['Scheduled Time']
            # Convert to datetime object
            start_time = datetime.datetime.strptime(scheduled_time_str, "%Y-%m-%dT%H:%M:%SZ")
            # Assuming the time is in UTC, you might want to localize it
            start_time = start_time.replace(tzinfo=pytz.utc).astimezone(central_tz)
            return start_time;
        elif key == "dkp6" and "competition_start_time" in value:
            start_time = datetime.datetime.fromisoformat(value['competition_start_time'][:26])            
            start_time = start_time.astimezone(central_tz)
            return start_time;
    return None;

# Accumulate data in a list
analysis_results = []

supported_sports = ["NFL","NHL","MLB","CFB","CBB","NBA"]
central_tz = pytz.timezone('America/Chicago')  # Change 'America/Chicago' to the appropriate time zone
for name in pp_properties_dict:
    pp = pp_properties_dict[name]
    ud = None
    dkp6 = None
    sleeper = None

    if name in ud_properties_dict:
        ud = ud_properties_dict[name]
    if name in dkp6_properties_dict:
        dkp6 = dkp6_properties_dict[name]   
    if name in sleeper_properties_dict:
        sleeper = sleeper_properties_dict[name]         
         
    pp_props_for_player = {}
    ud_props_for_player = {}
    dkp6_props_for_player = {}
    sleeper_props_for_player = {}    
    
    pp_props_set = set()

    if pp:    
        for p in pp:
            pp_props_for_player[p['stat_type']] = p
            pp_props_set.add(p['stat_type'])
    
    if ud:
        for u in ud:
            key = u['Prop Name']
            sport = u['Sport']
            if sport in pp_to_ud_props:
                inverted = invert_dict(pp_to_ud_props[sport])
                if key in inverted:
                    pp_key = inverted[key]
                    ud_props_for_player[pp_key] = u  
                    pp_props_set.add(pp_key)
    if dkp6:
        for d in dkp6:
            key = d['prop_abbr']
            sport = d['competition_sport']
            if sport in pp_to_dkp6_props:
                inverted = invert_dict(pp_to_dkp6_props[sport])
                if key in inverted:
                    pp_key = inverted[key]
                    dkp6_props_for_player[pp_key] = d 
                    pp_props_set.add(pp_key)
                    
    if sleeper:
        for d in sleeper:
            key = d['wager_type']
            sport = d['sport']
            if sport in pp_to_dkp6_props:
                inverted = invert_dict(pp_to_sleeper_props[sport])
                if key in inverted:
                    pp_key = inverted[key]
                    sleeper_props_for_player[pp_key] = d 
                    pp_props_set.add(pp_key)
                    
    for pp_prop in pp_props_set:
        
        pp_prop_data = None;
        ud_prop_data = None;
        dkp6_prop_data = None;
        sleeper_prop_data = None;
        
        prop_data = {}
        
        
        if pp_prop in pp_props_for_player:
            pp_prop_data = pp_props_for_player[pp_prop]
            if pp_prop_data:
                prop_data['pp'] = pp_prop_data
        if pp_prop in ud_props_for_player:
            ud_prop_data = ud_props_for_player[pp_prop]
            if ud_prop_data['Boosted']:
                ud_prop_data = None;
            if ud_prop_data:
                prop_data['ud'] = ud_prop_data
        if pp_prop in dkp6_props_for_player:
            dkp6_prop_data = dkp6_props_for_player[pp_prop]
            if dkp6_prop_data:
                prop_data['dkp6'] = dkp6_prop_data
        if pp_prop in sleeper_props_for_player:
            sleeper_prop_data = sleeper_props_for_player[pp_prop]
            if sleeper_prop_data:
                prop_data['sl'] = sleeper_prop_data        

        if len(prop_data)>1:
#updated | sport | team | name | prop | PP line | UD line | DKP6 line | Sleeper line | Sleeper oOdds | Sleeper uOdds | start time

            sport = get_sport(prop_data)
            if sport in supported_sports:
                high_line_source = get_high_line_source(prop_data)
                low_line_source = get_low_line_source(prop_data)

                #if high_line_source and low_line_source and high_line_source!=low_line_source:
                team = get_team(prop_data)
                name = get_name(prop_data)
                position = get_position(prop_data)
                prop =  pp_prop
                pp_line =  get_pp_line(prop_data)
                ud_line = get_ud_line(prop_data)
                dkp6_line = get_dkp6_line(prop_data)
                sleeper_line = get_sleeper_line(prop_data)
                sleeper_over_odds = get_sleeper_over_odds(prop_data)
                sleeper_under_odds = get_sleeper_under_odds(prop_data)
                sleeper_popularity = get_sleeper_sleeper_popularity(prop_data)
                
                if sleeper_over_odds:
                    sleeper_over_odds = round(sleeper_over_odds,3)
                if sleeper_under_odds:
                    sleeper_under_odds = round(sleeper_under_odds,3)
                if sleeper_popularity:
                    sleeper_popularity = round(sleeper_popularity,3)                
                
                if sleeper_over_odds and sleeper_under_odds:
                    sleeper_over = (1.0/sleeper_over_odds) * 100.0
                    sleeper_under = (1.0/sleeper_under_odds) * 100.0
                    sleeper_hold = sleeper_over + sleeper_under
                    sleeper_over_odds = round(sleeper_over / sleeper_hold,3)
                    sleeper_under_odds = round(sleeper_under / sleeper_hold,3)
                    
                start_time = get_start_time(prop_data)
                high_low_line_diff = None;
                if low_line_source and high_line_source:
                    high_low_line_diff = round(get_high_low_line_diff(prop_data,low_line_source,high_line_source),3)
                    print("high_low_line_diff",high_low_line_diff)
                
                print("sport",sport,"team",team,"name",name,"position",position,"prop",prop,"pp_line",pp_line,"ud_line",ud_line,"dkp6_line",dkp6_line,"sleeper_line",sleeper_line,"sleeper_over_odds",sleeper_over_odds,"sleeper_under_odds",sleeper_under_odds,"sleeper_popularity",sleeper_popularity,"low_line_source",low_line_source,"high_line_source",high_line_source,"high_low_line_diff",high_low_line_diff,"start_time",start_time)

                # Append data to the list
                analysis_results.append({
                    "Sport": sport,
                    "Team": team,
                    "Name": name,
                    "Position": position,
                    "Prop": prop,
                    "PrizePicks Line": pp_line,
                    "Underdog Line": ud_line,
                    "DKP6 Line": dkp6_line,
                    "Sleeper Line": sleeper_line,
                    "Sleeper Over Odds": sleeper_over_odds,
                    "Sleeper Under Odds": sleeper_under_odds,
                    "Sleeper Popularity": sleeper_popularity,
                    "Low Line Source": low_line_source,
                    "High Line Source": high_line_source,
                    "Line Difference": high_low_line_diff,
                    "Start Time": start_time,
                })

# Sort the list by "Sport", "Position", and "Name"
analysis_results = sorted(analysis_results, key=itemgetter("Sport", "Position", "Name"))

# Then, sort by "Line_Difference" in descending order
analysis_results = sorted(analysis_results, key=lambda x: x.get("Line Difference", float('-inf')) if x.get("Line Difference") is not None else float('-inf'), reverse=True)

formatted_stamp = datetime.datetime.now().strftime("%Y%m%d")

# Define the CSV file path
csv_file_path = f"normalized_props/analysis_results_{formatted_stamp}.csv"

# Write data to a CSV file
df = pd.DataFrame(analysis_results)
df.columns = [col.strip() for col in df.columns]  # Capitalize first letter and remove underscores
df.to_csv(csv_file_path, index=False)

print(f"Analysis results written to {csv_file_path}")
formatted_stamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            
# Optionally, you can also write this filtered dataframe to a separate sheet in a Google Spreadsheet
sheets.write_to_spreadsheet(csv_file_path, "Prop Differencer", f'Difference Report', add_column_name="Updated", add_column_data=formatted_stamp, index=0, overwrite=True, append=False)