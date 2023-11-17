import os
import sheets

directory = 'combined'

# List all files in the directory with the .csv extension
csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

csv_files.reverse()
print(csv_files)

for csv in csv_files:
    sheets.write_to_spreadsheet(directory+"/"+csv,"PP Results",csv.replace("_condensed_report_2023-11-17.csv","")+" Combined",0)