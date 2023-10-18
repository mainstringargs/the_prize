import pandas as pd
import requests
from pandas import json_normalize
import json

import argparse


# Define arguments
parser = argparse.ArgumentParser(description="Script with command-line arguments")

parser.add_argument("--year", type=int, default=2023, help="Year")
parser.add_argument("--week", type=int, default=1, help="Week")
parser.add_argument("--pp_file", type=str, default="", help="pp file")

args = parser.parse_args()

# Access argument values
year = str(args.year)
week = str(args.week)

print("Grabbing....",year,week,args.pp_file)

#base64 encoded url:  aHR0cHM6Ly9hcGkucHJpemVwaWNrcy5jb20vcHJvamVjdGlvbnM/c2luZ2xlX3N0YXQ9dHJ1ZQ==
with open(str(args.pp_file), 'rb') as f:
    f_data = f.read()

    
json_info = json.loads(f_data.decode('utf-8'))

players = {}
for d in json_info["included"]:
    players[d["id"]] = d["attributes"]

data = []
for d in json_info['data']:
    data.append({
        **players[d['relationships']['new_player']['data']['id']],
        **d['attributes']
    })

df = pd.DataFrame(data)
df = df.applymap(lambda x: x.strip().replace('\t','') if isinstance(x, str) else x)
filter = df['combo']==True
filtered_df = df[~filter]
filtered_df.to_csv("processing/prop_lines_"+year+"_week_"+week+".csv")

