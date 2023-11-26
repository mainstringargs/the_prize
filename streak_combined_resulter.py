import os
import pandas as pd
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
    
merged_df.to_csv('out.csv')

# Check if 'Hit' column exists before converting it to boolean
if 'Hit' in merged_df.columns:
    merged_df['Hit'] = merged_df['Hit'].astype(bool)

    # Rename 'Hit' values to 'Miss' for better clarity
    merged_df['Hit'] = merged_df['Hit'].replace({True: 'Hit', False: 'Miss'})


    # Calculate the overall percentage of Hit, Miss, and Push
    total_rows = float(merged_df['Streak'].count())

    over_hit_count = float(((merged_df['Streak'] == 'Over') & (merged_df['Prop Result'] == 'Over')).sum())
    under_hit_count = float(((merged_df['Streak'] == 'Under') & (merged_df['Prop Result'] == 'Under')).sum())
    hit_count = over_hit_count + under_hit_count
    push_count = float((merged_df['Prop Result'] == 'Push').sum())
    miss_count = total_rows - (hit_count + push_count)
    
    print('hit_count', hit_count, 'miss_count', miss_count, 'push_count', push_count)
    print((hit_count+miss_count+push_count))

    # Check if there are any NaN values in the counts and fill them with 0
    hit_percent = (hit_count / total_rows) if not pd.isna(hit_count) else 0.0
    miss_percent = (miss_count / total_rows) if not pd.isna(miss_count) else 0.0
    push_percent = (push_count / total_rows) if not pd.isna(push_count) else 0.0
    
    print('hit_percent',hit_percent,'miss_percent',miss_percent,'push_percent',push_percent)
    print((hit_percent+miss_percent+push_percent))
    
    merged_df.to_csv('out2.csv')

    # Calculate the percentage of Hit, Miss, and Push for each League
    league_percentages = merged_df.groupby('League')['Hit'].value_counts(normalize=True).unstack(fill_value=0)
    league_percentages['Push Percentage'] = merged_df.groupby('League')['Prop Result'].value_counts(normalize=True).unstack().get('Push', 0)
    league_percentages = league_percentages.rename(columns={'Hit': 'Hit Percentage', 'Miss': 'Miss Percentage'})

    # Add "Total Count" column for overall
    league_totals = merged_df.groupby('League')['Hit'].count().reset_index()
    league_percentages = pd.merge(league_percentages, league_totals, on='League', how='left')
    league_percentages = league_percentages.rename(columns={'Hit': 'Total Count'})

    # Calculate the percentage of Hit, Miss, and Push for each Prop within each League
    prop_percentages = merged_df.groupby(['League', 'Prop'])['Hit'].value_counts(normalize=True).unstack(fill_value=0)
    prop_percentages['Prop Push Percentage'] = merged_df.groupby(['League', 'Prop'])['Prop Result'].value_counts(normalize=True).unstack().get('Push', 0)
    prop_percentages = prop_percentages.rename(columns={'Hit': 'Prop Hit Percentage', 'Miss': 'Prop Miss Percentage'})
    prop_percentages = prop_percentages.fillna(0.0)

    # Add "Total Count" column for per Prop
    prop_totals = merged_df.groupby(['League', 'Prop'])['Hit'].count().reset_index()
    prop_percentages = pd.merge(prop_percentages, prop_totals, on=['League', 'Prop'], how='left')
    prop_percentages = prop_percentages.rename(columns={'Hit': 'Prop Total Count'})

    # Sort the prop data within each league by "Prop Hit Percentage"
    prop_percentages = prop_percentages.sort_values(by=['League', 'Prop Hit Percentage'], ascending=[True, False])

    
    # Calculate the overall percentage of Hit, Miss, and Push
    total_rows = float(merged_df['Streak'].count())

    over_hit_count = float(((merged_df['Streak'] == 'Over') & (merged_df['Prop Result'] == 'Over')).sum())
    under_hit_count = float(((merged_df['Streak'] == 'Under') & (merged_df['Prop Result'] == 'Under')).sum())

    over_total_count = float((merged_df['Streak'] == 'Over').sum())
    under_total_count = float((merged_df['Streak'] == 'Under').sum())

    over_hit_percent = (over_hit_count / over_total_count) if over_total_count != 0 else 0.0
    under_hit_percent = (under_hit_count / under_total_count) if under_total_count != 0 else 0.0
    
    over_miss_count = float(((merged_df['Streak'] == 'Over') & (merged_df['Prop Result'] == 'Under')).sum())
    under_miss_count = float(((merged_df['Streak'] == 'Under') & (merged_df['Prop Result'] == 'Over')).sum())

    over_miss_percent = (over_miss_count / over_total_count) if over_total_count != 0 else 0.0
    under_miss_percent = (under_miss_count / under_total_count) if under_total_count != 0 else 0.0

    over_push_count = float(((merged_df['Streak'] == 'Over') & (merged_df['Prop Result'] == 'Push')).sum())
    under_push_count = float(((merged_df['Streak'] == 'Under') & (merged_df['Prop Result'] == 'Push')).sum())

    over_push_percent = (over_push_count / over_total_count) if over_total_count != 0 else 0.0
    under_push_percent = (under_push_count / under_total_count) if under_total_count != 0 else 0.0

    print('Over Hit Percentage:', over_hit_percent)
    print('Under Hit Percentage:', under_hit_percent)
    
    print('Over Miss Percentage:', over_miss_percent)
    print('Under Miss Percentage:', under_miss_percent)
    
    print('Over Push Percentage:', over_push_percent)
    print('Under Push Percentage:', under_push_percent)

    print('Over Total Percentage:', (over_hit_percent+over_miss_percent+over_push_percent))
    print('Under Total Percentage:', (under_hit_percent+under_miss_percent+under_push_percent))

    # Add "Overall" row for overall percentages
    overall_row = pd.DataFrame({
        'League': ['Overall'],
        'Hit Percentage': [round(hit_percent, 2)],
        'Miss Percentage': [round(miss_percent, 2)],
        'Push Percentage': [round(push_percent, 2)],
        'Total Count': [total_rows]
    })
    
    # Add "Overall" row for overall percentages
    overall_row_over = pd.DataFrame({
        'League': ['Overall_Over'],
        'Hit Percentage': [round(over_hit_percent, 2)],
        'Miss Percentage': [round(over_miss_percent, 2)],
        'Push Percentage': [round(over_push_percent, 2)],
        'Total Count': [over_total_count]
    })    

    # Add "Overall" row for overall percentages
    overall_row_under = pd.DataFrame({
        'League': ['Overall_Under'],
        'Hit Percentage': [round(under_hit_percent, 2)],
        'Miss Percentage': [round(under_miss_percent, 2)],
        'Push Percentage': [round(under_push_percent, 2)],
        'Total Count': [under_total_count]
    })    

    # Interleave prop and overall data per league
    interleaved_df = pd.concat([league_percentages.reset_index(), prop_percentages], ignore_index=True).sort_values(
        by=['League', 'Hit Percentage'])
        
    interleaved_df = pd.concat([overall_row, overall_row_over, overall_row_under, interleaved_df], ignore_index=True)     

    # Reorder columns with "League" first
    columns_order = ['League', 'Hit Percentage', 'Miss Percentage', 'Push Percentage', 'Total Count', 'Prop', 'Prop Hit Percentage', 'Prop Miss Percentage', 'Prop Push Percentage', 'Prop Total Count']
    interleaved_df = interleaved_df[columns_order]

    # Save the combined percentages to a CSV file with single-digit precision
    interleaved_df.to_csv('streak_data/combined_summary_report.csv', index=False, float_format='%.2f')
    
    today = datetime.datetime.now()
    formatted_date = today.strftime("%Y-%m-%d %H:%M")      
    
    #sheets.write_to_spreadsheet('streak_data/combined_summary_report.csv',"Last Five Streaker",'Combined',add_column_name="Updated",add_column_data=formatted_date,index=0,overwrite=True,append=False)
else:
    print("The 'Hit' column does not exist in the dataframe.")
