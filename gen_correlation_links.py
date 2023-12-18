import json
import pandas as pd
import chardet
import datetime
import base64;

root_url = 'aHR0cHM6Ly9hcHAucHJpemVwaWNrcy5jb20vYm9hcmQ/cHJvamVjdGlvbnM9'
max_others_goalie_sports = 3
def gen_links_goalie_sports(player,other_players):
    decoded_url = base64.b64decode(root_url).decode('utf-8')
    prop_id = player['prop_id']
    line_score = player['line_score']   
    
    urls = []
    for ou in ['o','u']:
        url = decoded_url
        url = url+prop_id+"-"+ou+"-"+str(line_score)+","
        
        for other in other_players[:max_others_goalie_sports]:
            other_prop_id = other['prop_id']
            other_line_score = other['line_score']   
            url = url+other_prop_id+"-"+ou+"-"+str(other_line_score)+","
        
        url = url[:-1]+"&wager_id=action"
        urls.append(url)
    
    return urls
    
def key_function(item):
    start_time_str = item['start_time']
    return datetime.datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S%z')



def soccer_correlations(soccer_dict):
    events = {}
    # Sort the dictionary by start_time
    soccer_dict = (sorted(soccer_dict, key=key_function))  
    for data in soccer_dict:
        game_id = data['game_id']
        team = data['team_name']
        position = data['position']
        stat_type = data['stat_type']
        line = float(data['line_score'])
        start_time = data['start_time']
        
        if game_id is None or game_id == 'nan':
            print("game_id is null",data)
            continue;
        
        if game_id not in events:
            events[game_id] = {}
            events[game_id]['Goalie Saves'] = {}
            events[game_id]['Shots'] = {}
            
        if stat_type=="Shots":
            if team not in events[game_id]['Shots']:
                events[game_id]['Shots'][team] = []
                
            events[game_id]['Shots'][team].append(data)
            events[game_id]['Shots'][team] = sorted(events[game_id]['Shots'][team], key=lambda x: x['line_score'], reverse=True)
        
        if stat_type=="Goalie Saves":
            if team not in events[game_id]['Goalie Saves']:
                events[game_id]['Goalie Saves'][team] = []    
                
            events[game_id]['Goalie Saves'][team].append(data)
            
    for event in events:
        this_event = events[event]
        goalies = this_event['Goalie Saves']
        players = this_event['Shots']
        for key, value in goalies.items():
        
            other_key = ""
            
            for pkey, pvalue in players.items():
                if key != pkey:
                    other_key = pkey;
        
            if other_key in players and other_key is not None:
                print("SOCCER", datetime.datetime.strptime(value[0]['start_time'], '%Y-%m-%dT%H:%M:%S%z'))
                try:
                    print('key', key.encode('utf-8').decode('utf-8', 'ignore') ,'other_key', other_key.encode('utf-8').decode('utf-8', 'ignore'))
                except UnicodeEncodeError as e:
                    print('Unable to print keys due to UnicodeEncodeError:', e)
                    
                other_players = []


                links = gen_links_goalie_sports(value[0], players[other_key]);
                for link in links:
                    print(link)
            


def nhl_correlations(nhl_dict):
    events = {}
    # Sort the dictionary by start_time
    nhl_dict = (sorted(nhl_dict, key=key_function))  
    for data in nhl_dict:
        game_id = data['game_id']
        team = data['team_name']
        position = data['position']
        stat_type = data['stat_type']
        line = float(data['line_score'])
        start_time = data['start_time']
        
        if game_id is None or game_id == 'nan':
            print("game_id is null",data)
            continue;
        
        if game_id not in events:
            events[game_id] = {}
            events[game_id]['Goalie Saves'] = {}
            events[game_id]['Shots On Goal'] = {}
            
        if stat_type=="Shots On Goal":
            if team not in events[game_id]['Shots On Goal']:
                events[game_id]['Shots On Goal'][team] = []
                
            events[game_id]['Shots On Goal'][team].append(data)
            events[game_id]['Shots On Goal'][team] = sorted(events[game_id]['Shots On Goal'][team], key=lambda x: x['line_score'], reverse=True)
        
        if stat_type=="Goalie Saves":
            if team not in events[game_id]['Goalie Saves']:
                events[game_id]['Goalie Saves'][team] = []    
                
            events[game_id]['Goalie Saves'][team].append(data)
            
    for event in events:
        this_event = events[event]
        goalies = this_event['Goalie Saves']
        players = this_event['Shots On Goal']
        for key, value in goalies.items():
        
            other_key = ""
            
            for pkey, pvalue in players.items():
                if key != pkey:
                    other_key = pkey;
        
            if other_key in players and other_key is not None:
                print("NHL", datetime.datetime.strptime(value[0]['start_time'], '%Y-%m-%dT%H:%M:%S%z'))
                try:
                    print('key', key.encode('utf-8').decode('utf-8', 'ignore') ,'other_key', other_key.encode('utf-8').decode('utf-8', 'ignore'))
                except UnicodeEncodeError as e:
                    print('Unable to print keys due to UnicodeEncodeError:', e)
                    
                other_players = []


                links = gen_links_goalie_sports(value[0], players[other_key]);
                for link in links:
                    print(link)
            
def gen_links_pairs(team_1_players,team_1_direction,team_2_players,team_2_direction):
    decoded_url = base64.b64decode(root_url).decode('utf-8')
      
    url = decoded_url  
    #print(team_1_players)
    for player in team_1_players:
        prop_id = player['prop_id']
        line_score = player['line_score']   
        url = url+prop_id+"-"+team_1_direction+"-"+str(line_score)+","
            
    for player in team_2_players:
        prop_id = player['prop_id']
        line_score = player['line_score']   
        url = url+prop_id+"-"+team_1_direction+"-"+str(line_score)+","
            
    url = url[:-1]+"&wager_id=action"
    
    
    return url
    

def football_correlations(football_dict):
    events = {}
    # Sort the dictionary by start_time
    football_dict = (sorted(football_dict, key=key_function))  
    for data in football_dict:
        game_id = data['game_id']
        team = data['team_name']
        position = data['position']
        stat_type = data['stat_type']
        line = float(data['line_score'])
        start_time = data['start_time']
        
        if game_id is None or game_id == 'nan':
            print("game_id is null",data)
            continue;
        
        if game_id not in events:
            events[game_id] = {}
            events[game_id]['Pass Yards'] = {}
            events[game_id]['Receiving Yards'] = {}
            
        if stat_type=="Receiving Yards":
            if team not in events[game_id]['Receiving Yards']:
                events[game_id]['Receiving Yards'][team] = []
                
            events[game_id]['Receiving Yards'][team].append(data)
            events[game_id]['Receiving Yards'][team] = sorted(events[game_id]['Receiving Yards'][team], key=lambda x: x['line_score'], reverse=True)
        
        if stat_type=="Pass Yards":
            if team not in events[game_id]['Pass Yards']:
                events[game_id]['Pass Yards'][team] = []    
                
            events[game_id]['Pass Yards'][team].append(data)
            
    for event in events:
      #  print(events[event])
        this_event = events[event]
        qb = this_event['Pass Yards']
        players = this_event['Receiving Yards']
        
        pairs = []
        if len(qb)>1:
            qb_iter = iter(qb)
            first_qb = next(qb_iter)
            second_qb = next(qb_iter)
            #print(qb[first_qb])
            print(qb[first_qb][0]['league'], datetime.datetime.strptime(qb[first_qb][0]['start_time'], '%Y-%m-%dT%H:%M:%S%z'),qb[first_qb][0]['team'],'vs',qb[second_qb][0]['team'])
        for key, value in qb.items():
            #print(key, value)
            qb = value;
            other_players = []
            if key in players and key is not None:
                other_players = players[key]
                
            if len(other_players) > 0:
               # print('!!qb',qb)
                #print('!!!other_players',other_players[0])
                pairs.append([qb[0], other_players[0]])
                
        if len(pairs) == 2:
           #print('pairs[0]',pairs[0])
           #print('pairs[1]',pairs[1])           
           oo_url = gen_links_pairs(pairs[0],'o',pairs[1],'o')
           print(oo_url);
           oo_url = gen_links_pairs(pairs[0],'o',pairs[1],'u')
           print(oo_url);
           oo_url = gen_links_pairs(pairs[0],'u',pairs[1],'o')
           print(oo_url);
           oo_url = gen_links_pairs(pairs[0],'u',pairs[1],'u')
           print(oo_url);


def gen(json_file_ref):

    chardet_encoding = ""
    with open(str(json_file_ref), 'rb') as f:
        chardet_encoding = chardet.detect(f.read())

    with open(str(json_file_ref), 'rb') as f:
        f_data = f.read()
        
    json_info = json.loads(f_data.decode(chardet_encoding['encoding']))

    players = {}
    for d in json_info["included"]:
        players[d["id"]] = d["attributes"]

    data = []
    for d in json_info['data']:
        data.append({
            'player_id': d['relationships']['new_player']['data']['id'], 
            **players[d['relationships']['new_player']['data']['id']],
            **d['attributes'],
            'prop_id': d['id']
        })


    df = pd.DataFrame(data)
    df = df.applymap(lambda x: x.strip().replace('\t','') if isinstance(x, str) else x)

    filtered_df = df[df['league'].isin(['NFL', 'NHL', 'CFB','SOCCER'])]
    filtered_df = filtered_df[filtered_df['odds_type'].isin(['standard'])]
    
    soccer_correlations(filtered_df[filtered_df['league'].isin(['SOCCER'])].to_dict(orient='records'))
    nhl_correlations(filtered_df[filtered_df['league'].isin(['NHL'])].to_dict(orient='records'))
    football_correlations(filtered_df[filtered_df['league'].isin(['NFL'])].to_dict(orient='records'))
    football_correlations(filtered_df[filtered_df['league'].isin(['CFB'])].to_dict(orient='records'))