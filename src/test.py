import requests
from bs4 import BeautifulSoup
#from googlesearch import search
import re
import time
import os
import csv
#import ScraperFC as sfc
from collections import Counter
import pandas as pd
import json
import lxml
from datetime import datetime, timedelta
import pytz
import subprocess
import whisper
from googleapiclient.discovery import build
import dateutil.parser
from openai import OpenAI

def transcript_youtube_video():
    API_KEY = "AIzaSyCkHe6LF97P2JzqTUW_xoefiP306_J_9DA"
    CHANNEL_ID = "UCk9fXOH4sM6C8dRpWztXKFQ"

    # YouTube API setup
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Get uploads playlist ID
    channel_info = youtube.channels().list(
        part='contentDetails',
        id=CHANNEL_ID
    ).execute()
    uploads_playlist_id = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Fetch videos from the uploads playlist
    playlist_items = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=5  # Check last 10 videos
    ).execute()
    
    # Find the latest video with "Vamos apostar" in the title from the last 24h
    cutoff_time = datetime.now(pytz.utc) - timedelta(days=1)
    cutoff_time = datetime.strptime(str(cutoff_time), '%Y-%m-%d %H:%M:%S.%f%z')
    target_video = None

    print(cutoff_time)
    
    for item in playlist_items.get('items', []):
        video_title = item['snippet']['title']
        publish_time = dateutil.parser.parse(item['snippet']['publishedAt'])
        
        print(publish_time)
        if datetime.strptime(str(publish_time), '%Y-%m-%d %H:%M:%S%z') < cutoff_time:
            continue  # Skip older videos
        
        if "Vamos Apostar" in video_title:
            target_video = item
            break
    
    if not target_video:
        print("No recent video found with 'Vamos apostar' in the title.")
        return
    
    # Extract video details
    video_id = target_video['snippet']['resourceId']['videoId']
    video_url = f"https://youtu.be/{video_id}"

    print(video_url)

    # Download audio using yt-dlp
    audio_file = f"{video_id}.mp3"
    # try:
    #     subprocess.run([
    #         'yt-dlp',
    #         '-x', '--audio-format', 'mp3',
    #         '-o', audio_file,
    #         video_url
    #     ], check=True, capture_output=True)
    # except subprocess.CalledProcessError as e:
    #     print(f"Failed to download audio: {e.stderr.decode()}")
    #     return

    # Transcribe with Whisper
    WHISPER_MODEL = "tiny"  # Choose from tiny, base, small, medium, large
    # model = whisper.load_model(WHISPER_MODEL)
    # result = model.transcribe(audio_file, language='pt')
    # transcription = result['text']
    
    # print('transcription done!')
    # # Save transcription
    # with open(f"{video_id}.txt", 'w', encoding='utf-8') as f:
    #     f.write(transcription)
    
    # # Cleanup audio file
    # os.remove(audio_file)
    # print(f"Transcription saved to {video_id}.txt")

    # for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
    client = OpenAI(api_key="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")
    f = open(f"{video_id}.txt", "r")

    response = client.chat.completions.create(
        model="text-moderation-latest",  # Use "gpt-3.5-turbo" for cheaper/faster
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um assistente que organiza tópicos detalhados de transcrições em português. "
                    "LISTE TODOS OS TÓPICOS MENCIONADOS, SEM OMITIR DETALHES. "
                    "Inclua até mesmo números, nomes específicos, e estratégias."
                )
            },
            {
                "role": "user",
                "content": f"Organize em tópicos detalhados esta transcrição:\n\n{f.read()}"
            }
        ],
        temperature=0.1  # Reduce creativity for factual accuracy
    )

    print(response.choices[0].message.content)

    return video_url

def replace_month_in_csv():
    # Mapping of month abbreviations to numbers
    month_mapping = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }

    current_month = None
    updated_rows = []

    csv_file = "/home/newData/data2013.csv"  # Replace with your actual file path

    with open(csv_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        # Check for month line
        month_match = re.match(r'^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*$', line.strip(), re.IGNORECASE)
        if month_match:
            current_month = month_mapping[month_match.group(1).lower()]
        else:
            # Replace -99- with the current month
            if current_month:
                line = re.sub(r'-99-', f'-{current_month}-', line)
            updated_rows.append(line)

    # Write the updated content to a new file
    with open(csv_file, 'w', encoding='utf-8') as file:
        file.writelines(updated_rows)

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
    csv_file = "/home/newData/matches22-23.csv"  # Replace with your actual file path
    
    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    data = pd.read_csv(csv_file, sep=',', dtype='unicode')
    rows_to_keep = []
    for _, row in data.iterrows():
        if comp_in_comps_list(row['competition'], comps) == True:
            rows_to_keep.append(row)

    data = pd.DataFrame(rows_to_keep)

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
    csv_file2 = "/home/newData/matches23-24.csv"  # Replace with your actual file path
    data2 = pd.read_csv(csv_file2, sep=',', dtype='unicode')
    results = []
    f_teams =[]
    for team in sorted(all_teams):
        x = matches_count[team]  # Count from the filtered matches
        y = total_matches_count[team]  # Count from the total matches array
        #results.append(f"{team} ; {x} ; {y} ; {x/y}")
        if y != 0 and y >= 10 and (x / y) >= 0.8:
            #f_teams.append(team)
            f_teams.append(f"{team} ; {x} ; {y} ; {str(x/y)}")
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
        if match_in_teams_list(row['match'],f_teams) == True and comp_in_comps_list(row['competition'], comps) == True:
            results.append(';'.join(map(str, row[:8].values)))  # Take the first 8 columns as a string
            # Append the filtered matches as a list of values (or a specific column, depending on what you need)
            # If you want to append rows as lists of column values:
            #results.append(filtered_matches.values.tolist())

    #return (results)
    return f_teams

# Function to check if both teams in a match are in the teams_list
def comp_in_comps_list(comp, comps_list):
    try:
        for c in comps_list:
            if c.replace(" ", "") in comp.replace(" ", ""):
                return True
    except (ValueError, AttributeError):
        # If the match is not a valid string or can't be split into two parts, skip it
        return False

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
    match_comp = matchInfo['2. competition']
    match_teams = matchInfo['3. match']

    # Generate search query
    query = f"final result of match {match_teams} for competition {match_comp} played on {match_date}"
    print(query)

    # Perform a Google search for the match details
    print(f"Searching for final result of the match: {match_teams} on {match_date}...\n")


    API_KEY = 'AIzaSyCkHe6LF97P2JzqTUW_xoefiP306_J_9DA'
    SEARCH_ENGINE_ID = 'd01a635f7d9ef4764'

    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}'
    try:
        html = requests.get(url).text
        data = json.loads(html)

        #print(html)
        
        if 'items' in data:
            if 'sofascore' in data['items'][0]['link']:
                return extract_ft_from_sofascore(data['items'][0]['link'])
            elif 'oddspedia' in data['items'][0]['link']:
                return extract_ft_from_oddspedia(data['items'][0]['link'])
        else:
            print("UPPPSSSS")
    except: 
        return ''
    


    # urls = []
    # for url in search(query, num_results=10):
    #     urls.append(url)
    #     print(f"Found URL: {url}")
    #     time.sleep(3)  # Delay to avoid rate limiting

    # Visit each URL and try to extract goal times
    all_goal_times = []
    # for url in urls:
    #     goal_times = extract_goal_times_from_url(url)
    #     if goal_times:
    #         all_goal_times.extend(goal_times)

    # Output the results
    # if all_goal_times:
    #     print("\nGoal times found:")
    #     print(sorted(set(all_goal_times)))
    # else:
    #     print("\nNo goal times found on searched pages.")
    
    return sorted(set(all_goal_times))

def extract_ft_from_sofascore(url):
    newUrl = url.replace("https", "http")
    ft_result = ''
    try:
        response = requests.get(newUrl, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            home_score_element = soup.find(attrs={"data-testid": "left_score"}).text
            away_score_element = soup.find(attrs={"data-testid": "right_score"}).text

            ft_result = home_score_element + '-' + away_score_element
            return ft_result
    except requests.RequestException as e:
        print(f"Could not retrieve data from {url}. Error: {e}")
        return ft_result

def extract_ft_from_oddspedia(url):
    newUrl = url.replace("https", "http")
    ft_result = ''
    try:
        response = requests.get(newUrl, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            return soup.find(attrs={"class": "event-score-text"}).text
    except requests.RequestException as e:
        print(f"Could not retrieve data from {url}. Error: {e}")
        return ft_result

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