import os
import sheets

directory = 'streak_data'

# List all files in the directory with the .csv extension
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv') and "_results" in f and "combined" not in f]

print(csv_files)

for csv in csv_files:
    sheets.write_to_spreadsheet(directory+"/"+csv,"Last Five Streaker",csv.replace("pp_streaks_","").replace('_results.csv',''),1)