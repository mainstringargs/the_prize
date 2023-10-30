import datetime
import os 
import json

# Specify the directory path you want to create
pp_result_data_path = 'pp_result_data'


def find_newest_file_from_day(directory_path, specific_day):
    # Initialize variables to store information about the newest file
    newest_file = None
    newest_file_time = None

    # Iterate over the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path):
            file_time = os.path.getctime(file_path)
            file_date = str(datetime.datetime.fromtimestamp(file_time).date())

            # Check if the file's date matches the specific day
            if file_date == specific_day:
                # If it's the first file matching the specific day or newer than the previous newest file
                if newest_file is None or file_time > newest_file_time:
                    newest_file = file_path
                    newest_file_time = file_time

    return newest_file
    
# Get today's date
today = datetime.datetime.now()

formatted_date = today.strftime("%Y-%m-%d")
newest_file = find_newest_file_from_day(pp_result_data_path, formatted_date)

print("found",newest_file)

with open(str(newest_file), 'rb') as f:
    f_data = f.read()
    
json_info = json.loads(f_data.decode('utf-8'))

for data in json_info:
    print(data)