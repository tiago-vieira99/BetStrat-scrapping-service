import requests
from bs4 import BeautifulSoup
#from googlesearch import search
import re
import time
import os
#import ScraperFC as sfc
from collections import Counter
import pandas as pd

def calculate_stake(odd, target_profit):
    # Calculate the stake required based on the target profit and the odd
    return target_profit / (odd - 1)

def ternary_progression(sequence, odd, initial_target):
    results = []
    target = initial_target
    max_bets_per_progression = 3
    waiting_for_green = False
    current_progression = 0
    consecutive_bets = 0

    translatedSequence = []  # To store the translated results
    
    # Process all elements except the last
    for n in sequence[:-2]:
        if n == 1:  # Single green
            translatedSequence.append('g')
        elif n > 1:  # Red(s) followed by a green
            translatedSequence.extend(['r'] * (n - 1))  # Add `n-1` reds
            translatedSequence.append('g')  # Add a green
    
    # Handle the last number
    last_number = sequence[-2]
    final_indicator = sequence[-1]
    if final_indicator == 0:
        translatedSequence.extend(['r'] * (last_number - 1))  # Add `n-1` reds
        translatedSequence.append('g')  # Final green
    elif final_indicator == -1:
        translatedSequence.extend(['r'] * abs(last_number))  # Add all reds

    total_rounds = len(translatedSequence)
    stake = initial_target / (odd - 1) #initial stake
    balance = 0
    num_increases = 0

    for i, outcome in enumerate(translatedSequence, start=1):
        if balance >= 100 or balance < -60:
            break

        if waiting_for_green:
            if outcome == "g":
                waiting_for_green = False
                consecutive_bets = 0
                #target = initial_target  # Reset target for new progression
                current_progression += 1
                results.append({"round": i, "target": "", "stake": "", "result": "GREEN"})
            else:
                # Append empty result for skipped rounds
                results.append({"round": i, "target": "", "stake": "", "result": "RED"})
            continue

        # Calculate stake if within a progression 3, 2, 1, 4, 3, 3, 2, 2, 1, 2, 2, 3, 2, -1
        if consecutive_bets < max_bets_per_progression:
            results.append({"round": i, "target": round(target, 2), "stake": round(stake, 2), "result": "GREEN" if outcome == "g" else "RED"})
            consecutive_bets += 1

            if outcome == "r":
                #stake = (target + sum(res['stake'] for res in results if res['round'] in range(i - consecutive_bets, i) and res['stake'])) / (odd - 1)
                balance -= stake
                target += stake
                if consecutive_bets == max_bets_per_progression:
                    waiting_for_green = True
            else:  # outcome == "g"
                profit = stake * (odd - 1)  # Calculate profit
                balance += profit
                num_increases += 0
                consecutive_bets = 0
                if num_increases >= 4:
                    num_increases = 0
                target = initial_target + num_increases
                #waiting_for_green = True  # Reset waiting flag after a green
            stake = target / (odd - 1)
        else:
            # Append empty result for skipped rounds
            #target = initial_target
            #stake = target / (odd - 1)
            num_increases = 0
            results.append({"round": i, "target": "", "stake": "", "result": "GREEN" if outcome == "g" else "RED"})
            waiting_for_green = True  # Stop progression after max bets
        print('round ' + str(i) + ": " + str(balance))

    #return str(balance).replace('.',',')
    #return convert_to_single_line(results).replace('.',',')
    return results


def simulate_sequence(sequence, odd, initial_target_profit):
    translatedSequence = []  # To store the translated results
    
    # Process all elements except the last
    for n in sequence[:-2]:
        if n == 1:  # Single green
            translatedSequence.append('g')
        elif n > 1:  # Red(s) followed by a green
            translatedSequence.extend(['r'] * (n - 1))  # Add `n-1` reds
            translatedSequence.append('g')  # Add a green
    
    # Handle the last number
    last_number = sequence[-2]
    final_indicator = sequence[-1]
    if final_indicator == 0:
        translatedSequence.extend(['r'] * (last_number - 1))  # Add `n-1` reds
        translatedSequence.append('g')  # Final green
    elif final_indicator == -1:
        translatedSequence.extend(['r'] * abs(last_number))  # Add all reds

    max_target_increases = 4
    num_increases = 0
    max_consecutive_reds = 4
    max_stake = 30
    balance = 0
    target = initial_target_profit
    consecutive_reds = 0
    round_number = 1
    results = []

    # Calculate initial stake based on the initial target profit
    stake = target / (odd - 1)  

    for outcome in translatedSequence:
        if balance >= 70 * initial_target_profit or balance < -500:
            break

        if consecutive_reds < max_consecutive_reds:
            if outcome == "g":
                # Win
                profit = stake * (odd - 1)  # Calculate profit
                balance += profit

                results.append({
                    "result": "GREEN",
                    #"round": round_number,
                    "stake": round(stake, 2),
                    "target": round(target, 2)
                })

                # Update target for the next round
                if num_increases < max_target_increases:
                    num_increases += 1
                    target = initial_target_profit + num_increases
                else:
                    target = initial_target_profit
                    num_increases = 0

                # Calculate the next stake based only on the new target profit
                stake = target / (odd - 1)  # Update stake for the next round
                if stake > max_stake:
                    stake = max_stake
                consecutive_reds = 0

            elif outcome == "r":
                # Loss
                balance -= stake
                consecutive_reds += 1

                results.append({
                    "result": "RED",
                    #"round": round_number,
                    "stake": round(stake, 2),
                    "target": round(target, 2)
                })

                # Update target for the next round
                target += stake  # Increase target by the stake lost in the last round

                # Calculate next stake to recover previous losses
                stake = target / (odd - 1)  # Update stake based on new target
                if stake > max_stake:
                    stake = max_stake

        else:
            # We hit 3 reds, stop betting until next green
            results.append({
                "result": "",
                #"round": round_number,
                "stake": "",
                "target": ""
            })
            consecutive_reds += 1

        
        if consecutive_reds >= max_consecutive_reds and outcome == "g":
            consecutive_reds = 0
            target = initial_target_profit
            stake = target / (odd - 1)
            if stake > max_stake:
                stake = max_stake
            num_increases = 0

        print('round ' + str(round_number) + ": " + str(balance))
        round_number += 1

    # Fill in remaining rounds with empty results if needed
    while round_number <= len(sequence):
        results.append({
            "result": "",
            #"round": round_number,
            "stake": "",
            "target": ""
        })
        round_number += 1

    #return convert_to_single_line(results).replace('.',',')
    return str(balance).replace('.',',')

def simulate_sequence_w_recovery(sequence, odd, initial_target_profit):
    translatedSequence = []  # To store the translated results
    
    # Process all elements except the last
    for n in sequence[:-2]:
        if n == 1:  # Single green
            translatedSequence.append('g')
        elif n > 1:  # Red(s) followed by a green
            translatedSequence.extend(['r'] * (n - 1))  # Add `n-1` reds
            translatedSequence.append('g')  # Add a green
    
    # Handle the last number
    last_number = sequence[-2]
    final_indicator = sequence[-1]
    if final_indicator == 0:
        translatedSequence.extend(['r'] * (last_number - 1))  # Add `n-1` reds
        translatedSequence.append('g')  # Final green
    elif final_indicator == -1:
        translatedSequence.extend(['r'] * abs(last_number))  # Add all reds

    max_target_increases = 3
    num_increases = 0
    max_consecutive_reds = 3
    balance = 0
    target = initial_target_profit
    consecutive_reds = 0
    round_number = 1
    results = []

    # Calculate initial stake based on the initial target profit
    stake = target / (odd - 1)  

    for outcome in translatedSequence:
        if balance >= 10 * initial_target_profit or balance < -50:
            break

        if consecutive_reds < max_consecutive_reds:
            if outcome == "g":
                # Win
                profit = stake * (odd - 1)  # Calculate profit
                balance += profit

                results.append({
                    "result": "GREEN",
                    #"round": round_number,
                    "stake": round(stake, 2),
                    "target": round(target, 2)
                })

                # Update target for the next round
                if num_increases < max_target_increases:
                    num_increases += 1
                    target = initial_target_profit + num_increases
                else:
                    target = initial_target_profit
                    num_increases = 0

                # Calculate the next stake based only on the new target profit
                stake = target / (odd - 1)  # Update stake for the next round
                consecutive_reds = 0

            elif outcome == "r":
                # Loss
                balance -= stake
                consecutive_reds += 1

                results.append({
                    "result": "RED",
                    #"round": round_number,
                    "stake": round(stake, 2),
                    "target": round(target, 2)
                })

                # Update target for the next round
                target += stake  # Increase target by the stake lost in the last round

                # Calculate next stake to recover previous losses
                stake = target / (odd - 1)  # Update stake based on new target

        else:
            # We hit 3 reds, stop betting until next green
            results.append({
                "result": "",
                #"round": round_number,
                "stake": "",
                "target": ""
            })
            consecutive_reds += 1

        
        if consecutive_reds >= max_consecutive_reds and outcome == "g":
            consecutive_reds = 0
            target = initial_target_profit
            stake = target / (odd - 1)
            num_increases = 0

        print('round ' + str(round_number) + ": " + str(balance))
        round_number += 1

    # Fill in remaining rounds with empty results if needed
    while round_number <= len(sequence):
        results.append({
            "result": "",
            #"round": round_number,
            "stake": "",
            "target": ""
        })
        round_number += 1

    return convert_to_single_line(results).replace('.',',')
    #return str(balance).replace('.',',')


def convert_to_single_line(data):
    line = []
    for entry in data:
        line.extend([entry["target"], entry["stake"], entry["result"]])
    return ";".join(map(str, line))

def testTeamsCount():
    # Input array of matches
    # Load the CSV file
    csv_file = "/home/matches23-24.csv"  # Replace with your actual file path
    data = pd.read_csv(csv_file)

    # Extract the total matches from the relevant column
    data['match'] = data['match'].fillna('').astype(str)  # Replace 'matches_column' with the actual column name
    total_matches = data['match'].tolist()  # Replace 'matches_column' with the actual column name

    # Filter matches where the "2nd goal" column is <= 60
    #filtered_data = data[data['2nd goal "'] <= 60]  # Replace '2nd goal' with the exact column name
    filtered_data = data[
        pd.to_numeric(
            data['total goals'].fillna('').str.replace(',', '.').str.replace('#VALUE', '', regex=False),
            errors='coerce'  # Invalid entries (e.g., '#VALUE') will become NaN
        ) >= 2
    ]
    matches = filtered_data['match'].tolist()

    # Flatten the lists into individual teams
    teams_from_matches = []
    teams_from_total_matches = []

    for match in matches:
        teams_from_matches.extend(split_match(match))

    for match in total_matches:
        teams_from_total_matches.extend(split_match(match))

    # Count occurrences in both arrays
    matches_count = Counter(teams_from_matches)
    total_matches_count = Counter(teams_from_total_matches)

    # Combine results into a unified list
    all_teams = set(matches_count.keys()).union(set(total_matches_count.keys()))

    # Output results in the format "Team - X / Y"
    csv_file2 = "/home/matches24-25.csv"  # Replace with your actual file path
    data2 = pd.read_csv(csv_file2)
    results = []
    f_teams =[]
    for team in sorted(all_teams):
        x = matches_count[team]  # Count from the filtered matches
        y = total_matches_count[team]  # Count from the total matches array
        #results.append(f"{team} ; {x} ; {y} ; {x/y}")
        if y != 0 and y >= 15 and (x / y) >= 0.8:
            f_teams.append(team)
            #f_teams.append(f"{team} ; {x} ; {y} ; {str(x/y)}")
            #print(f"{team} ; {x} ; {y} ; {x/y}")
    
    
    # Filter the rows where the 'match' column contains the team name
    #filtered_matches = data2[data2['match'].str.contains(team, case=False, na=False)]
    # Filter matches where both teams belong to the teams_list
    #filtered_matches = data2[data2['match'].apply(lambda match: match_in_teams_list(match, f_teams))]
    filtered_matches = data2
    # Select the first 8 columns
    #filtered_matches = filtered_matches.iloc[:, :8]

    # Iterate over each row in filtered_matches
    for _, row in filtered_matches.iterrows():
        if match_in_teams_list(row['match'],f_teams) == True:
            results.append(';'.join(map(str, row[:8].values)))  # Take the first 8 columns as a string
            # Append the filtered matches as a list of values (or a specific column, depending on what you need)
            # If you want to append rows as lists of column values:
            #results.append(filtered_matches.values.tolist())

    return (results)
    #return f_teams

# Function to check if both teams in a match are in the teams_list
def match_in_teams_list(match, teams_list):
    try:
        # Ensure the match is treated as a string
        match = str(match)
        # Split match into two teams using the last occurrence of " - "
        team1, team2 = match.rsplit(' - ', 1)  # Safely split by the last ' - '
        # Check if both teams are in the teams_list
        return team1.strip() in teams_list and team2.strip() in teams_list
    except (ValueError, AttributeError):
        # If the match is not a valid string or can't be split into two parts, skip it
        return False

# Function to split match into exactly two teams
def split_match(match):
    # Split by ' - ' and assume the last ' - ' divides the two teams
    parts = match.rsplit(" - ", 1)
    if len(parts) == 2:
        return parts  # Two teams found
    else:
        return [match]  # Handle any malformed cases gracefully

def testSofaScore():
    ss = sfc.FBref()
    #player_data = ss.scrape_match("https://fbref.com/en/matches/62eea1d6/Leicester-City-Tottenham-Hotspur-August-19-2024-Premier-League")
    fb = sfc.FBref()
    match = fb.scrape_match('https://fbref.com/en/matches/67ed3ba2/Brentford-Tottenham-Hotspur-August-13-2023-Premier-League')    
    print("ok")


def get_goals_mins(matchInfo):

    os.environ["REQUESTS_CA_BUNDLE"] = ""
    # Define the match details
    match_date = matchInfo['1. datetime']
    match_teams = matchInfo['3. match']

    # Generate search query
    query = f"on date {match_date} {match_teams} goals minutes from sofacore"

    # Perform a Google search for the match details
    print(f"Searching for goal times of the match: {match_teams} on {match_date}...\n")
    urls = []
    for url in search(query, num_results=1):
        urls.append(url)
        #print(f"Found URL: {url}")
        time.sleep(3)  # Delay to avoid rate limiting

    # Visit each URL and try to extract goal times
    all_goal_times = []
    for url in urls:
        goal_times = extract_goal_times_from_url(url)
        if goal_times:
            all_goal_times.extend(goal_times)

    # Output the results
    # if all_goal_times:
    #     print("\nGoal times found:")
    #     print(sorted(set(all_goal_times)))
    # else:
    #     print("\nNo goal times found on searched pages.")
    
    return sorted(set(all_goal_times))

# Define a function to extract goal times from a webpage
def extract_goal_times_from_url(url):
    time.sleep(4)
    newUrl = url.replace("https", "http") 
    goal_minutes = []
    try:
        response = requests.get(newUrl, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div with the specific class
            target_div = soup.find('div', {'data-testid': 'scorer_list'})

            # Try to find text patterns that could indicate goal times (e.g., "23'", "45+2'", etc.)
            #possible_minutes = re.findall(r'\b\d{1,2}\'\b|\b\d{1,2}\+\d{1,2}\'\b', soup.text)
            # Regular expression to capture goal times, including extra time and multiple times
            possible_minutes = []
            if target_div:
                possible_minutes = re.findall(r'\b\d{1,2}(?:\+\d{1,2})?\'', target_div.text)
            if possible_minutes:
                print(f"Goal minutes found at {url}: {possible_minutes}")
            return possible_minutes

            # Filter out unlikely results
            #goal_minutes = [minute for minute in possible_minutes if int(minute.split("'")[0]) <= 90]
            for minute in possible_minutes:
                try:
                    # Split on '+' to handle cases like '45+2'
                    main_minute = int(minute.split("+")[0].replace("'", ""))

                    # Filter based on the main minute (e.g., 45 in "45+2'")
                    if main_minute <= 90:
                        goal_minutes.append(minute)
                except ValueError:
                    # If conversion fails (e.g., due to unexpected format), skip this entry
                    print(f"Skipping unrecognized format: {minute}")
            
            if goal_minutes:
                print(f"Goal minutes found at {url}: {goal_minutes}")
                return goal_minutes
            else:
                print(f"No goal data found at {url}.")
                return goal_minutes
    except requests.RequestException as e:
        print(f"Could not retrieve data from {url}. Error: {e}")
        return goal_minutes