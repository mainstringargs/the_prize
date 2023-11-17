import os
import csv
from datetime import datetime
import sheets

# Directory containing the CSV files
directory = "results"

# Directory to store the condensed CSVs
output_directory = "combined"

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Get the current date in YYYY-MM-DD format
current_date = datetime.now().strftime('%Y-%m-%d')

# Initialize a dictionary to store combined data for each league and prop
league_data = {}

# Loop through CSV files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv") and   "_all-data-grouped-by-prop" in filename:
        file_path = os.path.join(directory, filename)
        league = filename.split("_")[0]  # Extract the league name from the filename

        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #print(row)
                prop = row['prop']
                over = int(row.get('Over', 0))  # Use get() to handle missing key
                under = int(row.get('Under', 0))  # Use get() to handle missing key
                push = int(row.get('Push', 0))  # Use get() to handle missing key

                # Initialize league data if it doesn't exist
                if league not in league_data:
                    league_data[league] = {}

                # Initialize prop data for the league if it doesn't exist
                if prop not in league_data[league]:
                    league_data[league][prop] = {
                        'Over': 0,
                        'Under': 0,
                        'Push': 0,
                    }

                # Combine data for the league and prop
                league_data[league][prop]['Over'] += over
                league_data[league][prop]['Under'] += under
                league_data[league][prop]['Push'] += push

# Calculate "Over %" percentages
for league, prop_data in league_data.items():
    for prop, data in prop_data.items():
        total = data['Over'] + data['Under'] + data['Push']
        over_percentage = round((data['Over'] / total) , 3) if total > 0 else 0.0
        data['Over %'] = over_percentage

reversed_keys = list(reversed(league_data.keys()))

# Generate and save a condensed report for each league, with all columns and percentages
for league in reversed_keys:
    prop_data = league_data[league]
    report_filename = f"{league}_condensed_report_{current_date}.csv"
    report_path = os.path.join(output_directory, report_filename)

    with open(report_path, 'w', newline='') as reportfile:
        writer = csv.DictWriter(reportfile, fieldnames=['prop', 'Over', 'Under', 'Push', 'Total', 'Over %', 'Under %', 'Push %'])
        writer.writeheader()

        # Sort the data by "Over %" column (descending order)
        sorted_data = sorted(
            prop_data.items(),
            key=lambda item: item[1]['Over %'],
            reverse=True
        )

        for prop, data in sorted_data:
            total = data['Over'] + data['Under'] + data['Push']
            over_percentage = data['Over %']  # Use the precalculated "Over %" value
            under_percentage = round((data['Under'] / total) , 3) if total > 0 else 0.0
            push_percentage = round((data['Push'] / total) , 3) if total > 0 else 0.0
            writer.writerow({
                'prop': prop,
                'Over': data['Over'],
                'Under': data['Under'],
                'Push': data['Push'],
                'Total': total,
                'Over %': over_percentage,
                'Under %': under_percentage,
                'Push %': push_percentage
            })
            
    today = datetime.now()
    formatted_date = today.strftime("%Y-%m-%d %H:%M")        

    print(f"Condensed report for {league} has been saved as {report_path}")
    sheets.write_to_spreadsheet(report_path,"PP Results",league+" Combined",add_column_name="Updated",add_column_data=formatted_date,index=0,overwrite=True)    