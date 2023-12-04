import os
import pandas as pd

def city_to_abbreviation(city_name):
    team_mappings = {
        'Arizona': 'ARI',
        'Atlanta': 'ATL',
        'Baltimore': 'BAL',
        'Buffalo': 'BUF',
        'Carolina': 'CAR',
        'Chicago': 'CHI',
        'Cincinnati': 'CIN',
        'Cleveland': 'CLE',
        'Dallas': 'DAL',
        'Denver': 'DEN',
        'Detroit': 'DET',
        'Green Bay': 'GB',
        'Houston': 'HOU',
        'Indianapolis': 'IND',
        'Jacksonville': 'JAX',
        'Kansas City': 'KC',
        'Las Vegas': 'LV',
        'Los Angeles Rams': 'LAR',  # Rams
        'Los Angeles Chargers': 'LAC',
        'Miami': 'MIA',
        'Minnesota': 'MIN',
        'New England': 'NE',
        'New Orleans': 'NO',
        'New York Giants': 'NYG',
        'New York Jets': 'NYJ',
        'Philadelphia': 'PHI',
        'Pittsburgh': 'PIT',
        'San Francisco': 'SF',
        'Seattle': 'SEA',
        'Tampa Bay': 'TB',
        'Tennessee': 'TEN',
        'Washington': 'WAS',
        # Add more city-to-abbreviation mappings as needed
    }

    # Convert the input city name to title case to handle case variations
    city_name = city_name.title()

    # Use the mapping dictionary to get the abbreviation, or return None if not found
    abbreviation = team_mappings.get(city_name)

    return abbreviation



def combine_csv_files(directory, filename_format):
    """
    Combine all CSV files in the specified directory matching the given filename format.

    Parameters:
    - directory: The path to the directory containing the CSV files.
    - filename_format: The common format of the CSV filenames.

    Returns:
    - combined_df: The combined DataFrame.
    """

    # Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv') and file.startswith(filename_format)]

    # Initialize an empty DataFrame to store the concatenated data
    combined_df = pd.DataFrame()

    # Loop through each CSV file and concatenate it to the DataFrame
    for csv_file in csv_files:
        # Construct the full path to the CSV file
        file_path = os.path.join(directory, csv_file)

        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
       # print("loading",file_path,flush=True)

        # Concatenate the DataFrame to the combined DataFrame
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df

def find_team_abbr(combined_df, display_name, league):
    player_info = combined_df[(combined_df['display_name'] == display_name) & (combined_df['league'] == league)]

    # Check if the player is found in the DataFrame
    if not player_info.empty:
        # Extract the team abbreviation
        team_abbr = player_info.iloc[0]['team']
        return team_abbr
    else:
        # Return None if player not found
        return None
    
    
