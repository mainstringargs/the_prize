import os
import pandas as pd
import sheets
import datetime 

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
    hit_count = (merged_df['Hit'] == 'Hit').sum()
    miss_count = (merged_df['Hit'] == 'Miss').sum()

    # Check if there are any NaN values in the counts and fill them with 0
    hit_percent = (hit_count / total_rows * 100) if not pd.isna(hit_count) else 0.0
    miss_percent = (miss_count / total_rows * 100) if not pd.isna(miss_count) else 0.0

    # Calculate the percentage of Hit and Miss for each League
    league_percentages = merged_df.groupby('League')['Hit'].value_counts(normalize=True).unstack() * 100
    league_percentages = league_percentages.rename(columns={'Hit': 'Hit Percentage', 'Miss': 'Miss Percentage'})

    # Add "Total Count" column for overall
    league_totals = merged_df.groupby('League')['Hit'].count().reset_index()
    league_percentages = pd.merge(league_percentages, league_totals, on='League', how='left')
    league_percentages = league_percentages.rename(columns={'Hit': 'Total Count'})

    # Calculate the percentage of Hit and Miss for each Prop within each League
    prop_percentages = merged_df.groupby(['League', 'Prop'])['Hit'].value_counts(normalize=True).unstack() * 100
    prop_percentages = prop_percentages.rename(columns={'Hit': 'Prop Hit Percentage', 'Miss': 'Prop Miss Percentage'})
    prop_percentages = prop_percentages.fillna(0.0)

    # Add "Total Count" column for per Prop
    prop_totals = merged_df.groupby(['League', 'Prop'])['Hit'].count().reset_index()
    prop_percentages = pd.merge(prop_percentages, prop_totals, on=['League', 'Prop'], how='left')
    prop_percentages = prop_percentages.rename(columns={'Hit': 'Prop Total Count'})

    # Sort the prop data within each league by "Prop Hit Percentage"
    prop_percentages = prop_percentages.sort_values(by=['League', 'Prop Hit Percentage'], ascending=[True, False])

    # Add "Overall" row for overall percentages
    overall_row = pd.DataFrame({
        'League': ['Overall'],
        'Hit Percentage': [round(hit_percent, 1)],
        'Miss Percentage': [round(miss_percent, 1)],
        'Total Count': [total_rows]
    })

    # Interleave prop and overall data per league
    interleaved_df = pd.concat([league_percentages.reset_index(), prop_percentages], ignore_index=True).sort_values(
        by=['League', 'Hit Percentage'])
        
        
    interleaved_df = pd.concat([overall_row, interleaved_df], ignore_index=True)     

    # Reorder columns with "League" first
    columns_order = ['League', 'Hit Percentage', 'Miss Percentage', 'Total Count', 'Prop', 'Prop Hit Percentage', 'Prop Miss Percentage', 'Prop Total Count']
    interleaved_df = interleaved_df[columns_order]

    # Save the combined percentages to a CSV file with single-digit precision
    interleaved_df.to_csv('streak_data/combined_summary_report.csv', index=False, float_format='%.1f')
    
    today = datetime.datetime.now()
    formatted_date = today.strftime("%Y-%m-%d")
    
    sheets.write_to_spreadsheet('streak_data/combined_summary_report.csv',"Last Five Streaker",'Combined',add_column_name="Event Date",add_column_data=formatted_date,index=0,overwrite=True,append=False)
else:
    print("The 'Hit' column does not exist in the dataframe.")
