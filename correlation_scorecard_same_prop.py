import json
from datetime import datetime

import chardet
import numpy as np
import pandas as pd
import sheets


def calculate_correlation(team_df):
    players = team_df['name'].unique()
    correlations = {}

    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player1_name = players[i]
            player2_name = players[j]

            common_events = set(team_df[team_df['name'] == player1_name]['Event Date']) & set(
                team_df[team_df['name'] == player2_name]['Event Date'])

            common_events = sorted(common_events)

            if len(common_events) >= 2:
                player_1_latest_team = \
                    team_df[(team_df['name'] == player1_name) & (team_df['Event Date'] == common_events[-1])][
                        'team'].iloc[0]
                player_2_latest_team = \
                    team_df[(team_df['name'] == player2_name) & (team_df['Event Date'] == common_events[-1])][
                        'team'].iloc[0]

                for ce in common_events.copy():
                    player1_event_team = \
                        team_df[(team_df['name'] == player1_name) & (team_df['Event Date'] == ce)][
                            'team'].iloc[0]
                    player2_event_team = \
                        team_df[(team_df['name'] == player2_name) & (team_df['Event Date'] == ce)][
                            'team'].iloc[0]

                    if (player1_event_team != player2_event_team or
                            player_1_latest_team != player1_event_team or
                            player_2_latest_team != player2_event_team):
                        common_events.remove(ce)

                if len(common_events) >= 2:  # Ensure there are at least two common events
                    player1_data = \
                        team_df[(team_df['name'] == player1_name) & team_df['Event Date'].isin(common_events)][
                            'result'].map({'Over': 1, 'Under': -1, 'Push': 0})
                    player2_data = \
                        team_df[(team_df['name'] == player2_name) & team_df['Event Date'].isin(common_events)][
                            'result'].map({'Over': 1, 'Under': -1, 'Push': 0})

                    if len(player1_data.unique()) > 1 and len(player2_data.unique()) > 1:  # Check for variability
                        correlation = np.corrcoef(player1_data, player2_data)[0, 1]
                        correlations[f"{player1_name} & {player2_name}"] = correlation
                        num_common_events = len(common_events)
                        # print(f"Number of events together for {player1_name} vs {player2_name}: {num_common_events}")

    return correlations


def get_same_prop_correlations(team_name, correlations, team_df):
    if not correlations:
        return None

    max_correlation_pair = max(correlations, key=correlations.get)
    min_correlation_pair = min(correlations, key=correlations.get)

    max_correlation = correlations[max_correlation_pair]
    min_correlation = correlations[min_correlation_pair]

    # Get the names of players from the correlation pairs
    max_player1, max_player2 = max_correlation_pair.split(' & ')
    min_player1, min_player2 = min_correlation_pair.split(' & ')

    # Count the number of events the correlated players have been in together
    max_events_together = set(team_df[team_df['name'] == max_player1]['Event Date']) & set(
        team_df[team_df['name'] == max_player2]['Event Date'])

    min_events_together = set(team_df[team_df['name'] == min_player1]['Event Date']) & set(
        team_df[team_df['name'] == min_player2]['Event Date'])

    # Count overs and unders
    max_events_together_overs = set(
        team_df[(team_df['name'] == max_player1) & (team_df['result'] == 'Over')]['Event Date']) & set(
        team_df[(team_df['name'] == max_player2) & (team_df['result'] == 'Over')]['Event Date'])
    max_events_together_unders = set(
        team_df[(team_df['name'] == max_player1) & (team_df['result'] == 'Under')]['Event Date']) & set(
        team_df[(team_df['name'] == max_player2) & (team_df['result'] == 'Under')]['Event Date'])

    min_events_together_overs = set(
        team_df[(team_df['name'] == min_player1) & (team_df['result'] == 'Over')]['Event Date']) & set(
        team_df[(team_df['name'] == min_player2) & (team_df['result'] == 'Over')]['Event Date'])
    min_events_together_unders = set(
        team_df[(team_df['name'] == min_player1) & (team_df['result'] == 'Under')]['Event Date']) & set(
        team_df[(team_df['name'] == min_player2) & (team_df['result'] == 'Under')]['Event Date'])

    raw_corr_percent = float(len(max_events_together_overs) + len(max_events_together_unders)) / float(
        len(max_events_together))
    raw_noncorr_percent = float(
        len(max_events_together) - (len(max_events_together_overs) + len(max_events_together_unders))) / float(
        len(max_events_together))

    raw_corr_over_percent = 0.0
    raw_corr_under_percent = 0.0
    if (len(max_events_together_overs) + len(max_events_together_unders)) > 0:
        raw_corr_over_percent = float(len(max_events_together_overs)) / float(
            len(max_events_together_overs) + len(max_events_together_unders))
        raw_corr_under_percent = float(len(max_events_together_unders)) / float(
            len(max_events_together_overs) + len(max_events_together_unders))

    result_dict = {
        'max_correlation_pair': max_correlation_pair,
        'max_correlation': max_correlation,
        'max_events_together': sorted(max_events_together),
        'max_events_together_overs': sorted(max_events_together_overs),
        'max_events_together_unders': sorted(max_events_together_unders),
        'min_correlation_pair': min_correlation_pair,
        'min_correlation': min_correlation,
        'min_events_together': sorted(min_events_together),
        'min_events_together_overs': sorted(min_events_together_overs),
        'min_events_together_unders': sorted(min_events_together_unders),
        'team_name': team_name,
        'raw_corr_percent': raw_corr_percent,
        'raw_corr_over_percent': raw_corr_over_percent,
        'raw_corr_under_percent': raw_corr_under_percent,
        'raw_noncorr_percent': raw_noncorr_percent
    }

    return result_dict


def get_same_prop_correlation_scorecard(min_corrs=6):
    # file_path = "pp_results.csv"  # Replace with the actual path to your CSV file
    #
    # with open(file_path, 'rb') as f:
    #     result = chardet.detect(f.read())
    #     chardet_encoding = result['encoding']
    #
    # # Load data
    # df = pd.read_csv(file_path, encoding=chardet_encoding)

    print("Loading pp results...", flush=True);
    sheets_df = sheets.load_google_sheet_into_dataframe("PP Results", "Individual Props")
    print("Finished loading pp results... There are", len(sheets_df), "entries", flush=True)
    # Get distinct pairs of 'league' and 'prop' as a list of tuples
    league_prop_pairs = sheets_df[['league', 'prop']].drop_duplicates().to_records(index=False).tolist()
    # Print the list of distinct pairs
    print("league_prop_pairs", league_prop_pairs)

    # league_prop_pairs = [("CFB","Receiving Yards")]

    correlation_scorecard = {"positive": {}, "negative": {}}

    for league, prop in league_prop_pairs:
        df = sheets_df.copy()
        df = df[(df['league'] == league)]
        df = df[(df['prop'] == prop)]
        # print(df)

        if league not in correlation_scorecard["positive"]:
            correlation_scorecard["positive"][league] = {}
            correlation_scorecard["negative"][league] = {}

        if prop not in correlation_scorecard["positive"][league]:
            correlation_scorecard["positive"][league][prop] = {}
            correlation_scorecard["negative"][league][prop] = {}

        unique_teams = df['team'].unique()

        team_correlations_list = []

        for team in unique_teams:
            team_df = df[df['team'] == team]

            # Check if there are enough players for correlation calculation
            if len(team_df['name'].unique()) >= 2:
                team_corrs = calculate_correlation(team_df)
                max_correlation = max(team_corrs.values(), default=None)
                if max_correlation:
                    team_correlations_list.append((team, max_correlation, team_corrs))

        print('team_correlations_list len', len(team_correlations_list))
        # Sort teams by their highest correlation values (highest to lowest)
        sorted_teams = sorted(team_correlations_list, key=lambda x: x[1], reverse=False)

        all_correlations = []
        team_correlations = {}

        for team, max_correlation, team_corrs in sorted_teams:
            team_df = df[df['team'] == team]
           # calculated_correlations = calculate_correlation(team_df)

            correlations = get_same_prop_correlations(team, team_corrs, team_df)
            all_correlations.append(correlations)
            team_correlations[team] = correlations

        all_correlations.sort(key=lambda a: a['max_correlation'])

        for corr in all_correlations:
            if len(corr['max_events_together']) >= min_corrs:

                player_pair = [part.strip() for part in corr['max_correlation_pair'].split('&')]

                if player_pair[0] not in correlation_scorecard["positive"][league][prop]:
                    correlation_scorecard["positive"][league][prop][player_pair[0]] = {}
                if player_pair[1] not in correlation_scorecard["positive"][league][prop]:
                    correlation_scorecard["positive"][league][prop][player_pair[1]] = {}

                correlation_scorecard["positive"][league][prop][player_pair[0]][player_pair[1]] = (corr)
                correlation_scorecard["positive"][league][prop][player_pair[1]][player_pair[0]] = (corr)

                print("==========>", corr['team_name'], league, prop)
                print("Corr Pair", corr['max_correlation_pair'], "Corr", round(corr['max_correlation'], 2), "Events",
                      len(corr['max_events_together']), "Up Events",
                      len(corr['max_events_together_overs']),
                      "Down Events", len(corr['max_events_together_unders']))
                print("All Events", (corr['max_events_together']))
                print("Corr Up Events", (corr['max_events_together_overs']))
                print("Corr Down Events", (corr['max_events_together_unders']))

        all_correlations.sort(key=lambda a: a['min_correlation'], reverse=True)
        for corr in all_correlations:
            if len(corr['min_events_together']) >= min_corrs:
                player_pair = [part.strip() for part in corr['min_correlation_pair'].split('&')]
                if player_pair[0] not in correlation_scorecard["negative"][league][prop]:
                    correlation_scorecard["negative"][league][prop][player_pair[0]] = {}
                if player_pair[1] not in correlation_scorecard["negative"][league][prop]:
                    correlation_scorecard["negative"][league][prop][player_pair[1]] = {}

                correlation_scorecard["negative"][league][prop][player_pair[0]][player_pair[1]] = (corr)
                correlation_scorecard["negative"][league][prop][player_pair[1]][player_pair[0]] = (corr)

                print("==========>", corr['team_name'], league, prop)
                print("Noncorr Pair", corr['min_correlation_pair'], "Corr", round(corr['min_correlation'], 2), "Events",
                      len(corr['min_events_together']), "Up Events",
                      len(corr['min_events_together_overs']),
                      "Down Events", len(corr['min_events_together_unders']))
                print("All Events", (corr['min_events_together']))
                print("Corr Up Events", (corr['min_events_together_overs']))
                print("Corr Down Events", (corr['min_events_together_unders']))

    return correlation_scorecard;


if __name__ == "__main__":
    scorecord = get_same_prop_correlation_scorecard()

    # Generate the file name with today's date
    today_date = datetime.now().strftime('%Y%m%d')
    json_file_path = f'normalized_props/same_prop_correlation_scorecard_{today_date}.json'

    # Write the dictionary to the JSON file
    with open(json_file_path, 'w') as jsonfile:
        json.dump(scorecord, jsonfile, indent=2)
