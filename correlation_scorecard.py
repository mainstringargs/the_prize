import chardet
import pandas as pd
from scipy.stats import pearsonr
import pandas as pd
import numpy as np


def calculate_correlation(team_df):
    players = team_df['name'].unique()
    correlations = {}

    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player1_name = players[i]
            player2_name = players[j]

            common_events = set(team_df[team_df['name'] == player1_name]['Event Date']) & set(
                team_df[team_df['name'] == player2_name]['Event Date'])

            if len(common_events) >= 2:  # Ensure there are at least two common events
                player1_data = team_df[(team_df['name'] == player1_name) & team_df['Event Date'].isin(common_events)][
                    'result'].map({'Over': 1, 'Under': -1, 'Push': 0})
                player2_data = team_df[(team_df['name'] == player2_name) & team_df['Event Date'].isin(common_events)][
                    'result'].map({'Over': 1, 'Under': -1, 'Push': 0})

                if len(player1_data.unique()) > 1 and len(player2_data.unique()) > 1:  # Check for variability
                    correlation = np.corrcoef(player1_data, player2_data)[0, 1]
                    correlations[f"{player1_name} & {player2_name}"] = correlation
                    num_common_events = len(common_events)
                    # print(f"Number of events together for {player1_name} vs {player2_name}: {num_common_events}")

    return correlations


def get_correlations(team_name, correlations, team_df):
    # print(f"Team: {team_name}")
    if not correlations:
        # print("No correlations found.")
        return

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

    max_events_together = sorted(max_events_together)
    max_events_together_overs = sorted(max_events_together_overs)
    max_events_together_unders = sorted(max_events_together_unders)
    min_events_together = sorted(min_events_together)
    min_events_together_overs = sorted(min_events_together_overs)
    min_events_together_unders = sorted(min_events_together_unders)

    return (
        max_correlation_pair, max_correlation, max_events_together, max_events_together_overs,
        max_events_together_unders,
        min_correlation_pair, min_correlation, min_events_together, min_events_together_overs,
        min_events_together_unders)

    # Check the condition before printing


# if len(max_events_together) >= min_events:
#    print(f"Highest correlation: {max_correlation_pair} - Correlation: {max_correlation:.2f}")
#   print(f"Events together for highest correlation: {len(max_events_together)} {max_events_together}")
#  print(f"Events together for highest correlation (Overs): {len(max_events_together_overs)} {max_events_together_overs}")
# print(f"Events together for highest correlation (Unders): {len(max_events_together_unders)} {max_events_together_unders}")

# if len(min_events_together) >= min_events:
#   print(f"Lowest correlation: {min_correlation_pair} - Correlation: {min_correlation:.2f}")
#  print(f"Events together for lowest correlation: {len(min_events_together)} {min_events_together}")
# print(f"Events together for lowest correlation (Overs): {len(min_events_together_overs)} {min_events_together_overs}")
# print(f"Events together for lowest correlation (Unders): {len(min_events_together_unders)} {min_events_together_unders}")


if __name__ == "__main__":
    file_path = "pp_results.csv"  # Replace with the actual path to your CSV file

    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        chardet_encoding = result['encoding']

    # Load data
    df = pd.read_csv(file_path, encoding=chardet_encoding)

    df = df[(df['league'] == 'NBA')]
    df = df[(df['prop'] == 'Points')]

    unique_teams = df['team'].unique()

    team_correlations_list = []

    for team in unique_teams:
        team_df = df[df['team'] == team]

        # Check if there are enough players for correlation calculation
        if len(team_df['name'].unique()) >= 2:
            team_correlations = calculate_correlation(team_df)
            max_correlation = max(team_correlations.values(), default=None)
            team_correlations_list.append((team, max_correlation))

    # Sort teams by their highest correlation values (highest to lowest)
    sorted_teams = sorted(team_correlations_list, key=lambda x: x[1], reverse=False)

    all_correlations = []
    team_correlations = {}

    for team, max_correlation in sorted_teams:
        team_df = df[df['team'] == team]
        calculated_correlations = calculate_correlation(team_df)

        correlations = get_correlations(team, calculated_correlations, team_df)
        all_correlations.append(correlations)
        team_correlations[team] = correlations

    all_correlations.sort(key=lambda a: a[1])
    min_corrs = 8
    for corr in all_correlations:
        if len(corr[2]) >= min_corrs:
            print("==========>")
            print("Corr Pair", corr[0], "Corr", round(corr[1], 2), "Events", len(corr[2]), "Up Events", len(corr[3]),
                  "Down Events", len(corr[4]))
            print("All Events", (corr[2]))
            print("Corr Up Events", (corr[3]))
            print("Corr Down Events", (corr[4]))

    all_correlations.sort(key=lambda a: a[6],reverse=True)
    min_corrs = 7
    for corr in all_correlations:
        if len(corr[7]) >= min_corrs:
            print("==========>")
            print("Noncorr Pair", corr[5], "Corr", round(corr[6], 2), "Events", len(corr[7]), "Up Events", len(corr[8]),
                  "Down Events", len(corr[9]))
            print("All Events", (corr[7]))
            print("Corr Up Events", (corr[8]))
            print("Corr Down Events", (corr[9]))
