import os
import csv

# Directory containing the CSV files
directory = "results"

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
                prop = row['prop']
                over = int(row.get('Over', 0))  # Use get() to handle missing key
                under = int(row.get('Under', 0))  # Use get() to handle missing key
                push = int(row.get('Push', 0))  # Use get() to handle missing key
                total = over + under + push  # Calculate total as the sum of Over, Under, and Push
                over_percentage = round((over / total) * 100, 1) if total > 0 else 0.0
                under_percentage = round((under / total) * 100, 1) if total > 0 else 0.0
                push_percentage = round((push / total) * 100, 1) if total > 0 else 0.0

                # Ensure that percentages do not exceed 100%
                over_percentage = min(over_percentage, 100)
                under_percentage = min(under_percentage, 100)
                push_percentage = min(push_percentage, 100)

                # Initialize league data if it doesn't exist
                if league not in league_data:
                    league_data[league] = {}

                # Initialize prop data for the league if it doesn't exist
                if prop not in league_data[league]:
                    league_data[league][prop] = {
                        'Over': 0,
                        'Under': 0,
                        'Push': 0,
                        'Total': 0,
                        'Over %': 0.0,
                        'Under %': 0.0,
                        'Push %': 0.0
                    }

                # Combine and recalculate data for the league and prop
                league_data[league][prop]['Over'] += over
                league_data[league][prop]['Under'] += under
                league_data[league][prop]['Push'] += push
                league_data[league][prop]['Total'] += total
                league_data[league][prop]['Over %'] = over_percentage
                league_data[league][prop]['Under %'] = under_percentage
                league_data[league][prop]['Push %'] = push_percentage

# Generate and save a condensed report for each league, with all columns
for league, prop_data in league_data.items():
    report_filename = f"{league}_condensed_report.csv"
    with open(report_filename, 'w', newline='') as reportfile:
        writer = csv.DictWriter(reportfile, fieldnames=['prop', 'Over', 'Under', 'Push', 'Total', 'Over %', 'Under %', 'Push %'])
        writer.writeheader()
        for prop, data in prop_data.items():
            writer.writerow({
                'prop': prop,
                'Over': data['Over'],
                'Under': data['Under'],
                'Push': data['Push'],
                'Total': data['Total'],
                'Over %': data['Over %'],
                'Under %': data['Under %'],
                'Push %': data['Push %']
            })

    print(f"Condensed report for {league} has been saved as {report_filename}")
