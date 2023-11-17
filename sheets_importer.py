import os
import sheets

directory = 'streak_data'

# List all files in the directory with the .csv extension
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and "results" in f]

print(csv_files)

for csv in csv_files:
    sheets.write_to_spreadsheet(directory+"/"+csv,"Last Five Streaker",'Individual Streaks',add_column_name="Event Date",add_column_data=csv.replace("pp_streaks_","").replace("_results.csv",""),index=0,overwrite=False,append=True)