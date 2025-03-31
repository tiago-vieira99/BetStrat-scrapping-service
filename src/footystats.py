import pandas as pd
import os, sys
import requests
from bs4 import BeautifulSoup

def merge_csv_files():
    # List to hold DataFrames
    dataframes = []

    folder_path = "scrapper/footyStats/2023-24"
    output_file = "scrapper/footyStats/data2023-24_merged.csv"

    # Iterate over all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            # Read the CSV file and append the DataFrame to the list
            df = pd.read_csv(file_path)
            # Extract the competition name from the filename
            competition_name = filename.split('-matches')[0]

            # Add a new column to the DataFrame
            df['competition'] = competition_name

            dataframes.append(df)

    # Concatenate all DataFrames in the list into a single DataFrame
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(output_file, index=False)



def add_new_match_columns():
    # Read the CSV file into a DataFrame
    df = pd.read_csv("scrapper/footyStats/data2023-24_merged.csv")

    # Convert the timestamp to datetime and sort DataFrame by date
    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    df.sort_values(by='date', inplace=True)

    # Initialize dictionaries to hold match data
    home_match_count = {}
    away_match_count = {}
    home_goals_scored = {}
    away_goals_scored = {}
    home_goals_conceded = {}
    away_goals_conceded = {}

    # Initialize new columns in the DataFrame
    df['at_home_matches_count'] = 0
    df['at_away_matches_count'] = 0
    df['total_hometeam_matches_count'] = 0
    df['total_awayteam_matches_count'] = 0
    df['teamA_home_scored_goals_pre'] = 0
    df['teamA_away_scored_goals_pre'] = 0
    df['teamA_home_conceeded_goals_pre'] = 0
    df['teamA_away_conceeded_goals_pre'] = 0
    df['teamB_home_scored_goals_pre'] = 0
    df['teamB_away_scored_goals_pre'] = 0
    df['teamB_home_conceeded_goals_pre'] = 0
    df['teamB_away_conceeded_goals_pre'] = 0

    # Iterate over the sorted DataFrame to populate the dictionaries and new columns
    for index, row in df.iterrows():
        try:
            home_team = row['home_team_name']
            away_team = row['away_team_name']
            home_goals = row['home_team_goal_count']
            away_goals = row['away_team_goal_count']

            # if home_team not in teams and away_team not in teams:
            #     continue 

            # Update home team stats (before updating current match)
            if home_team not in home_match_count:
                home_match_count[home_team] = 0
                home_goals_scored[home_team] = 0
                home_goals_conceded[home_team] = 0
            if away_team not in away_match_count:
                away_match_count[away_team] = 0
                away_goals_scored[away_team] = 0
                away_goals_conceded[away_team] = 0

            # Store current cumulative statistics before updating
            df.at[index, 'teamA_home_scored_goals_pre'] = home_goals_scored.get(home_team, 0)
            df.at[index, 'teamA_away_scored_goals_pre'] = away_goals_scored.get(home_team, 0)
            df.at[index, 'teamA_home_conceeded_goals_pre'] = home_goals_conceded.get(home_team, 0)
            df.at[index, 'teamA_away_conceeded_goals_pre'] = away_goals_conceded.get(home_team, 0)

            df.at[index, 'teamB_home_scored_goals_pre'] = home_goals_scored.get(away_team, 0)
            df.at[index, 'teamB_away_scored_goals_pre'] = away_goals_scored.get(away_team, 0)
            df.at[index, 'teamB_home_conceeded_goals_pre'] = home_goals_conceded.get(away_team, 0)
            df.at[index, 'teamB_away_conceeded_goals_pre'] = away_goals_conceded.get(away_team, 0)

            # Update match count and goals after setting pre-match data
            home_match_count[home_team] += 1
            away_match_count[away_team] += 1

            home_goals_scored[home_team] += home_goals
            home_goals_conceded[home_team] += away_goals

            away_goals_scored[away_team] += away_goals
            away_goals_conceded[away_team] += home_goals

            # Add match number columns
            df.at[index, 'at_home_matches_count'] = home_match_count[home_team]
            df.at[index, 'at_away_matches_count'] = away_match_count[away_team]
            #df.at[index, 'total_hometeam_matches_count'] = int(home_match_count[home_team]) + int(away_match_count[home_team])
            #df.at[index, 'total_awayteam_matches_count'] = home_match_count[away_team] + away_match_count[away_team]
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    # Save the updated DataFrame to a new CSV file
    df.to_csv("scrapper/footyStats/data2023-24_merged_new.csv", index=False)


#https://www.financial-spread-betting.com/sports/Goals-betting-system.html
def strat1():
    # Read the merged CSV file into a DataFrame
    df = pd.read_csv("scrapper/footyStats/data2023-24_merged_new.csv")

    # Convert date column to datetime if it exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        raise ValueError("The DataFrame must contain a 'date' column.")

    # Sort DataFrame by date
    df.sort_values(by='date', inplace=True)

    # Initialize a list to hold filtered matches
    filtered_matches = []

    # Iterate over each match in the DataFrame
    for index, row in df.iterrows():
        home_team = row['home_team_name']
        away_team = row['away_team_name']
        home_goals = row['home_team_goal_count']
        away_goals = row['away_team_goal_count']
        total_goals = home_goals + away_goals
        match_date = row['date']

        # Filter previous matches for home team
        home_previous_matches = df[(df['home_team_name'] == home_team) & (df['date'] < match_date)]
        away_previous_matches = df[(df['away_team_name'] == away_team) & (df['date'] < match_date)]

        # Check home team conditions
        if len(home_previous_matches) >= 3:
            home_last_3 = home_previous_matches.tail(3)
            home_goals_last_3 = home_last_3['home_team_goal_count'].sum()
            home_over_2_5_count = (home_last_3['home_team_goal_count'] + home_last_3['away_team_goal_count'] > 2.5).sum()

            home_conditions_met = (
                home_goals_last_3 >= 7 and
                home_over_2_5_count >= 2
            )
        else:
            home_conditions_met = False

        # Check away team conditions
        if len(away_previous_matches) >= 3:
            away_last_3 = away_previous_matches.tail(3)
            away_goals_last_3 = away_last_3['away_team_goal_count'].sum()
            away_over_2_5_count = (away_last_3['home_team_goal_count'] + away_last_3['away_team_goal_count'] > 2.5).sum()

            # Check if the most recent away game had 2 or more goals
            previous_game = away_previous_matches.tail(1)
            previous_game_goals = previous_game['home_team_goal_count'].values[0] + previous_game['away_team_goal_count'].values[0] if not previous_game.empty else 0

            away_conditions_met = (
                away_goals_last_3 >= 7 and
                previous_game_goals >= 2 and
                (away_last_3['away_team_goal_count'] > 0).sum() >= 2 and
                away_over_2_5_count >= 2
            )
        else:
            away_conditions_met = False

        # If both conditions are met, add the match to the filtered list
        if home_conditions_met and away_conditions_met:
            filtered_matches.append(row)

    # Create a DataFrame from the filtered matches
    filtered_df = pd.DataFrame(filtered_matches)

    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv("scrapper/footyStats/filtered_matches_2023-24.csv", index=False)

# double minLimit = Math.min(awayGoalsConcededValue, awayGoalsScoredValue) + Math.min(homeGoalsConcededValue, homeGoalsScoredValue);
# double maxLimit = Math.max(awayGoalsConcededValue, awayGoalsScoredValue) + Math.max(homeGoalsConcededValue, homeGoalsScoredValue);
# double finalScore = (minLimit + maxLimit) / 2;
# int matchesPlayedCurrentSeason = Integer.parseInt(h2hDocument.getElementsByAttributeValueContaining("id", "mainStatisticsType_a").get(0).childNode(3).childNode(5).childNode(3).childNode(0).toString().trim());

# if (finalScore >= 3.5 && matchesPlayedCurrentSeason >= 5) : OVER
def strat2():
    # Read the merged CSV file into a DataFrame
    df = pd.read_csv("scrapper/footyStats/data2023-24_merged_new.csv")

    # Convert date column to datetime if it exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        raise ValueError("The DataFrame must contain a 'date' column.")

    # Sort DataFrame by date
    df.sort_values(by='date', inplace=True)

    # Initialize a list to hold filtered matches
    filtered_matches = []

    # Iterate over each match in the DataFrame
    for index, row in df.iterrows():
        home_team = row['home_team_name']
        away_team = row['away_team_name']
        home_goals = row['home_team_goal_count']
        away_goals = row['away_team_goal_count']
        total_goals = home_goals + away_goals
        match_date = row['date']
        home_scored_goals_pre = row['teamA_home_scored_goals_pre']
        home_conceeded_goals_pre = row['teamA_home_conceeded_goals_pre']
        away_scored_goals_pre = row['teamB_away_scored_goals_pre']
        away_conceeded_goals_pre = row['teamB_away_conceeded_goals_pre']
        home_match_number = row['home_match_number']
        away_match_number = row['away_match_number']

        minLimit = min(away_conceeded_goals_pre, away_scored_goals_pre) + min(home_conceeded_goals_pre, home_scored_goals_pre)
        maxLimit = max(away_conceeded_goals_pre, away_scored_goals_pre) + max(home_conceeded_goals_pre, home_scored_goals_pre)

        finalScore = (minLimit + maxLimit) / 2

        # If both conditions are met, add the match to the filtered list
        if finalScore >= 3.5 and home_match_number >= 4 and away_match_number >= 4:
            filtered_matches.append(row)

    # Create a DataFrame from the filtered matches
    filtered_df = pd.DataFrame(filtered_matches)

    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv("scrapper/footyStats/filtered_matches_2023-24_strat2.csv", index=False)

def identify_teams_with_high_goal_percentage():
    # Load the CSV file into a DataFrame
    df = pd.read_csv("scrapper/footyStats/data2022-23_merged_new.csv")

    # Initialize a dictionary to store the counts
    team_stats = {}

    # Iterate through the DataFrame to populate the team_stats dictionary
    for index, row in df.iterrows():
        home_team = row['home_team_name']
        away_team = row['away_team_name']
        total_goals = row['total_goal_count']

        # Update home team stats
        if home_team not in team_stats:
            team_stats[home_team] = {'matches': 0, 'matches_with_2_or_more_goals': 0}
        team_stats[home_team]['matches'] += 1
        if total_goals >= 2:
            team_stats[home_team]['matches_with_2_or_more_goals'] += 1

        # Update away team stats
        if away_team not in team_stats:
            team_stats[away_team] = {'matches': 0, 'matches_with_2_or_more_goals': 0}
        team_stats[away_team]['matches'] += 1
        if total_goals >= 2:
            team_stats[away_team]['matches_with_2_or_more_goals'] += 1

    # Identify teams with >= 90% of matches with 2 or more goals
    teams_with_high_goal_percentage = []
    for team, stats in team_stats.items():
        if stats['matches'] > 0:  # Avoid division by zero
            percentage = (stats['matches_with_2_or_more_goals'] / stats['matches']) * 100
            if percentage >= 90:
                teams_with_high_goal_percentage.append(team)

    return teams_with_high_goal_percentage


def get_leagues_stats_rates():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }

        response = requests.get("http://www.fcstats.com/", headers=headers, verify=True)

        return_list = []

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            country_links = soup.find_all(attrs={"class": "menuCountry"})

            # iterate over all countries
            for link in country_links:
                country_url = "http://www.fcstats.com/" + link.get('href')
                
                response2 = requests.get(country_url, headers=headers, verify=True)
                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.text, 'html.parser')
                    print(country_url)

                    # iterate over all leagues by country
                    if len(soup2.find_all(attrs={"class": "countryLeaguesBox"})) > 0:
                        leagues_by_country = soup2.find_all(attrs={"class": "countryLeaguesBox"})[0].find_all('a')
                    else: 
                        leagues_by_country = [link]

                    for league in leagues_by_country:
                        league_url = "http://www.fcstats.com/" + league.get('href')

                        response5 = requests.get(league_url, headers=headers, verify=True)
                        if response5.status_code == 200:
                            soup5 = BeautifulSoup(response5.text, 'html.parser')
                    
                            league_name = soup5.find('h1').text
                            print(league_name)

                            # iterate over seasons
                            seasons_list = soup5.find_all(attrs={"class": "yearPhasesBox"})
                            for season in seasons_list:
                                season_name = season.find_all('div')[0].text
                                season_url = "http://www.fcstats.com/" + season.find_all('a')[0]['href'].replace('league','statistics')
                                season_url = season_url[:season_url.rfind(',') + 1] + '1,' + season_url[season_url.rfind(',') + 1:]

                                league_stats = {}

                                response3 = requests.get(season_url, headers=headers, verify=True)
                                if response3.status_code == 200:
                                    soup3 = BeautifulSoup(response3.text, 'html.parser')
                                    print(season_name)

                                    # Find the <td> element that contains text "Draws"
                                    draws_td = soup3.find('td', string=lambda text: text and "Draws" in text)
                                    overs_td = soup3.find('td', string=lambda text: text and "Over 2.5" in text)

                                    if draws_td:
                                        # Get the parent <tr> to find the next <td> that contains the value
                                        draws_row = draws_td.find_parent('tr')

                                        # Get the value from the next <td> in the same row
                                        if draws_row:
                                            draws_value = draws_row.find_all('td')[1].text.strip()  # Get the second <td>
                                            draws_value = draws_value.split('[')[1][:-2]
                                            print(f"Draws: {draws_value}")
                                    else:
                                        print("Draws element not found.")

                                    if overs_td:
                                        # Get the parent <tr> to find the next <td> that contains the value
                                        overs_row = overs_td.find_parent('tr')

                                        # Get the value from the next <td> in the same row
                                        if overs_row:
                                            overs_value = overs_row.find_all('td')[1].text.strip()  # Get the second <td>
                                            overs_value = overs_value.split('[')[1][:-2]
                                            print(f"Overs: {overs_value}")
                                    else:
                                        print("Overs element not found.")

                                # get btts rate
                                btts_stats_url = season_url.replace(',1,', ',5,')
                                response4 = requests.get(btts_stats_url, headers=headers, verify=True)
                                if response4.status_code == 200:
                                    soup4 = BeautifulSoup(response4.text, 'html.parser')
                                    # Initialize the sum for Repetitions
                                    total_repetitions = 0
                                    total_matches = 0

                                    # Find the table
                                    table = soup4.find('table')

                                    # Iterate through each row in the table (skip the header row)
                                    for row in table.find_all('tr')[1:]:  # Skip the header row
                                        cells = row.find_all('td')

                                        if len(cells) >= 2:  # Ensure there are at least two cells
                                            result = cells[0].text.strip()  # Result is in the first cell
                                            repetitions = cells[1].text.strip()  # Repetitions is in the second cell
                                            total_matches += int(repetitions)

                                            # Check if the result does not contain '0'
                                            if '0' not in result:
                                                # Convert repetitions to an integer and add to total
                                                total_repetitions += int(repetitions)

                                    league_stats['league_name'] = league_name
                                    league_stats['season'] = season_name
                                    league_stats['draws_rate'] = draws_value
                                    league_stats['overs_rate'] = overs_value
                                    if total_repetitions == 0 or total_matches == 0:
                                        league_stats['btts_rate'] = "0"
                                    else:
                                        league_stats['btts_rate'] = f"{100 * total_repetitions / total_matches:.2f}"
                                    return_list.append(league_stats)
                                #break
                        #break
                #break

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return return_list

def split_leagues():
    # Read the data from the string
    df = pd.read_csv("scrapper/newData/eng_premier_league_stats.csv")

    # Pivot for each stat
    btts_df = df.pivot(index='league_name', columns='season', values='btts_rate')
    draws_df = df.pivot(index='league_name', columns='season', values='draws_rate')
    overs_df = df.pivot(index='league_name', columns='season', values='overs_rate')

    # Save each pivoted DataFrame to a CSV file
    btts_df.to_csv('scrapper/newData/btts_rates2.csv')
    draws_df.to_csv('scrapper/newData/draws_rates2.csv')
    overs_df.to_csv('scrapper/newData/overs_rates2.csv')

    print("CSV files have been created.")

#input: https://fcstats.com/table,canadian-premier-league-canada,203,1,4641.php
def get_team_draw_stats_by_league(league_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }

        response = requests.get(league_url, headers=headers, verify=True)

        return_map = {}

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            teams_list = soup.find_all(attrs={"class": "xScrollableContent"})[0].find_all(attrs={"class": "teamName"})

            for team in teams_list:
                teamName = team.find('a').text
                teamUrl = team.find('a')['href']

                return_map[teamName] = {}

                response2 = requests.get("http://www.fcstats.com/" + teamUrl, headers=headers, verify=True)
                if response2.status_code == 200:
                    soup2 = BeautifulSoup(response2.text, 'html.parser')

                    # iterate over seasons
                    seasons_list = soup2.find_all(attrs={"class": "yearPhasesBox"})[1:5]
                    for season in seasons_list:
                        season_name = season.find_all('div')[0].text
                        season_comps = season.find_all(attrs={"class": "leagueName"})

                        return_map[teamName][season_name] = {}
                        for i in range(0, len(season_comps)):
                            season_url = "http://www.fcstats.com/" + season.find_all('a')[i]['href'].replace('league','statistics')
                            comp_name = season.find_all(attrs={"class": "leagueName"})[i].text

                            return_map[teamName][season_name][comp_name] = {}

                            response3 = requests.get(season_url, headers=headers, verify=True)
                            if response3.status_code == 200:
                                soup3 = BeautifulSoup(response3.text, 'html.parser')

                                # Find the <td> element that contains text "Draws"
                                draws_td = soup3.find('td', string=lambda text: text and "Draws" in text)
                                overs_td = soup3.find('td', string=lambda text: text and "Over 2.5" in text)

                                return_map[teamName][season_name][comp_name]['negSeq'] = get_neg_sequence_by_team(season_url.replace('statistics', 'matches'))

                                if draws_td:
                                    # Get the parent <tr> to find the next <td> that contains the value
                                    draws_row = draws_td.find_parent('tr')

                                    # Get the value from the next <td> in the same row
                                    if draws_row:
                                        draws_value = draws_row.find_all('td')[1].text.strip()  # Get the second <td>
                                        #draws_value = draws_value.split('[')[1][:-2]
                                        return_map[teamName][season_name][comp_name]['drawsRate'] = draws_value
                                        print(f"Draws: {draws_value}")
                                else:
                                    print("Draws element not found.")

                
                #break

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return return_map


def get_neg_sequence_by_team(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }

        response = requests.get(url, headers=headers, verify=True)

        neg_seq = []

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = soup.find_all(attrs={"class": "matchResult"})[1:]

            current = 0
            for match in matches:
                current = current + 1
                if (match.text.split(':')[0] == match.text.split(':')[1]):
                    neg_seq.append(current)
                    current = 0

            if current == 0:
                neg_seq.append(0)
            else:
                neg_seq.append(current)
                neg_seq.append(-1)

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return str(neg_seq)