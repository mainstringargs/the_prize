import os
import pandas as pd

# Set the directory path
directory_path = "streak_data"

# List all files in the directory
files = [file for file in os.listdir(directory_path) if file.endswith("_results.csv")]

# Initialize an empty dataframe
merged_df = pd.DataFrame()

# Loop through the files and concatenate them into the merged dataframe
for file in files:
    file_path = os.path.join(directory_path, file)
    df = pd.read_csv(file_path)
    merged_df = pd.concat([merged_df, df], ignore_index=True)

# Check if 'Hit' column exists before converting it to boolean
if 'Hit' in merged_df.columns:
    merged_df['Hit'] = merged_df['Hit'].astype(bool)

    # Rename 'Hit' values to 'Miss' for better clarity
    merged_df['Hit'] = merged_df['Hit'].replace({True: 'Hit', False: 'Miss'})

    # Calculate the overall percentage of Hit and Miss
    total_rows = len(merged_df)
    hit_percent = (merged_df['Hit'] == 'Hit').sum() / total_rows * 100
    miss_percent = (merged_df['Hit'] == 'Miss').sum() / total_rows * 100

    # Calculate the percentage of Hit and Miss for each League
    league_percentages = merged_df.groupby('League')['Hit'].value_counts(normalize=True).unstack() * 100
    league_percentages = league_percentages.rename(columns={'Hit': 'Hit Percentage', 'Miss': 'Miss Percentage'})

    # Add "Total Count" column
    league_totals = merged_df.groupby('League')['Hit'].count().reset_index()
    league_percentages = pd.merge(league_percentages, league_totals, on='League', how='left')
    league_percentages = league_percentages.rename(columns={'Hit': 'Total Count'})

    # Add "Overall" row for overall percentages
    overall_row = pd.DataFrame({
        'League': ['Overall'],
        'Hit Percentage': [round(hit_percent, 1)],
        'Miss Percentage': [round(miss_percent, 1)],
        'Total Count': [total_rows]
    })

    # Concatenate the "Overall" row with the league-specific percentages
    league_percentages = pd.concat([league_percentages.reset_index(), overall_row], ignore_index=True).sort_values(by=['League', 'Hit Percentage'])

    # Reorder columns with "League" first
    columns_order = ['League', 'Hit Percentage', 'Miss Percentage', 'Total Count']
    league_percentages = league_percentages[columns_order]

    # Save the combined percentages to a CSV file with single-digit precision
    league_percentages.to_csv('streak_data/combined_summary_report.csv', index=False, float_format='%.1f')
else:
    print("The 'Hit' column does not exist in the dataframe.")
