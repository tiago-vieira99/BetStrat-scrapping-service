import csv
from collections import Counter
import pandas as pd
from datetime import datetime, timedelta
import requests
import sys, os
from bs4 import BeautifulSoup

def generateFileForNextMatchesEbookStrategy():
    matches = []

    # Get today's date
    today = datetime.now()

    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];
    
    teams = filterTeamsBySeason("23-24")

    #csv file header
    matches.append("datetime ; competition ; match ; h2h matches ; h2h goals")
    for k in range(0, 15):
        print(datetime.now())
        current_date = today + timedelta(days=k)
        month = current_date.strftime("%b").lower()
        day = current_date.day
        formatted_date = f"{current_date.year}/{month}/{day}/"
        response = requests.get("https://www.worldfootball.net/matches_today/" + formatted_date)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Perform scraping operations using BeautifulSoup here
            table = soup.find('table', class_="standard_tabelle")
        
            # then we can iterate through each row and extract either header or row values:
            header = []
            rows = []
            competition = ''
            for i, row in enumerate(table.find_all('tr')):
                rows.append([el.text.strip() for el in row])

                h2hmatches = ''
                h2hgoals = ''
                
                try:
                    r = [el.text.strip() for el in row]
                    if len(r) <= 7:
                        competition = r[3]

                    if (len(r) > 7) and any(item.lower().replace(' ', '') in competition.lower().replace(' ', '') for item in comps) and r[3] in teams and r[7] in teams:
                        if len(row.find_all('a')) > 2:
                            response3 = requests.get("https://www.worldfootball.net/" + row.find_all('a')[2]['href'])
                            
                            if response3.status_code == 200:
                                soup3 = BeautifulSoup(response3.content, 'html.parser')
                                table3 = soup3.find_all('table', class_="standard_tabelle")[1]
                                
                                h2hurl = soup3.find_all('table', class_="auswahlbox")[1].find_all('a')[-1]['href']
                                response4 = requests.get("https://www.worldfootball.net" + h2hurl)
                            
                                if response4.status_code == 200:
                                    soup4 = BeautifulSoup(response4.content, 'html.parser')
                                    table4 = soup4.find_all('table', class_="standard_tabelle")[0]
                                    h2hmatches = table4.find_all('tr')[-1].find_all('td')[2].text
                                    h2hgoals = int(table4.find_all('tr')[-1].find_all('td')[-3].text) + int(table4.find_all('tr')[-1].find_all('td')[-1].text)
                        
                        if (float(h2hgoals)/float(h2hmatches) >= 3.5):
                            matches.append(formatted_date + " " + r[1] + " ; " + competition + " ; " + r[3] + " - " + r[7] + " ; " + h2hmatches + " ; " + str(h2hgoals))       
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)                        
        else:
            raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    # Open file in write mode
    # with open("/home/data.csv", "a", newline='') as file:
    #     writer = csv.writer(file)
    #     # Write each element as a row
    #     for item in matches:
    #         writer.writerow([item])

    return matches

def compile_matches_by_team(previousSeason, season):
    matches = getMatchesBetweenFilteredTeams(previousSeason, season)
    team_matches = {}
    
    for match in matches:
        parts = match.split(";")
        if len(parts) < 4:
            continue  # Skip invalid match entries

        if (float(parts[5]) / float(parts[4]) < 3.5) or parts[5] == "nan":
            continue
        
        teams = parts[2].split(" - ")
        if len(teams) != 2:
            continue  # Skip invalid team entries
        
        team1, team2 = teams
        
        # Add match to team1
        if team1 not in team_matches:
            team_matches[team1] = []
        team_matches[team1].append(match)
        
        # Add match to team2
        if team2 not in team_matches:
            team_matches[team2] = []
        team_matches[team2].append(match)
    
    return team_matches

def getAllMatchesByTeam(season, team):
    # Input array of matches
    # Load the CSV file
    csv_file = "/home/newData/matches" + season + ".csv"  # Replace with your actual file path
    
    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    data = pd.read_csv(csv_file, sep=',', dtype='unicode')
    results = []

    # Iterate over each row in filtered_matches
    for _, row in data.iterrows():
        if team_in_match(row['match'], team) == True and comp_in_comps_list(row['competition'], comps) == True:
            results.append(';'.join(map(str, row[:4].values.tolist() + row[6:8].values.tolist())))  # Take the first 8 columns as a string
            # Append the filtered matches as a list of values (or a specific column, depending on what you need)
            # If you want to append rows as lists of column values:
            #results.append(filtered_matches.values.tolist())

    return (results)

def getMatchesBetweenFilteredTeams(previousSeason, season):
    # Input array of matches
    # Load the CSV file
    csv_file = "/home/newData/matches" + season + ".csv"  # Replace with your actual file path
    
    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    data = pd.read_csv(csv_file, sep=',', dtype='unicode')
    results = []
    #f_teams = filterTeamsBySeason(previousSeason)

    f_teams = ["AC Milan","FC Ashdod","Galatasaray","Jeju United","Melbourne City FC","Real Madrid","Sevilla FC","Sivasspor","Sydney FC"]

    # Iterate over each row in filtered_matches
    for _, row in data.iterrows():
        if match_in_teams_list(row['match'], f_teams) == True and comp_in_comps_list(row['competition'], comps) == True:
            results.append(';'.join(map(str, row[:4].values.tolist() + row[6:8].values.tolist())))  # Take the first 8 columns as a string
            # Append the filtered matches as a list of values (or a specific column, depending on what you need)
            # If you want to append rows as lists of column values:
            #results.append(filtered_matches.values.tolist())

    return (results)

def filterTeamsBySeason(season):
    # Input array of matches
    # Load the CSV file
    csv_file = "/scrapper/newData/matches" + season + ".csv"  # Replace with your actual file path
    
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

    f_teams =[]
    for team in sorted(all_teams):
        x = matches_count[team]  # Count from the filtered matches
        y = total_matches_count[team]  # Count from the total matches array
        if y != 0 and y >= 20 and (x / y) >= 0.8:
            ratio = str(x / y).replace(".", ",")
            #f_teams.append(f"{team} ; {x} ; {y} ; {ratio}")
            f_teams.append(f"{team}")
            #print(f"{team} ; {x} ; {y} ; {x/y}")

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

# Function to split match into exactly two teams
def split_match(match):
    # Split by ' - ' and assume the last ' - ' divides the two teams
    parts = match.rsplit(" - ", 1)
    if len(parts) == 2:
        return parts  # Two teams found
    else:
        return [match]  # Handle any malformed cases gracefully

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

# Function to check if team is in a match
def team_in_match(match, team):
    try:
        # Ensure the match is treated as a string
        match = str(match)
        # Split match into two teams using the last occurrence of " - "
        team1, team2 = match.rsplit(' - ', 1)  # Safely split by the last ' - '
        # Check if both teams are in the teams_list
        return team1.strip() == team.strip() or team2.strip() == team.strip()
    except (ValueError, AttributeError):
        # If the match is not a valid string or can't be split into two parts, skip it
        return False