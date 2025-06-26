import requests
from flask import jsonify
from bs4 import BeautifulSoup
from obj.match import Match
import re
import Levenshtein
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import scrapping
from collections import OrderedDict
import traceback
import os,sys
import json, csv
import gc
import psycopg2
import urllib.parse

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized") 
    chrome_options.add_argument("--disable-extensions") 
    chrome_options.add_argument("--disable-infobars") 
    chrome_options.add_argument("--disable-notifications") 

    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

def json_to_csv(json_file_path, csv_file_path):
    """
    Converts a JSON file containing an array of objects to a CSV file.
    
    Args:
        json_file_path (str): Path to the input JSON file.
        csv_file_path (str): Path to save the output CSV file.
        
    Limitations:
        - Handles only flat structures (nested JSON objects/arrays will be converted to strings)
        - All JSON entries must be dictionaries
        - CSV columns will be sorted alphabetically
    """
    # Load JSON data
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    # Validate data format
    if not isinstance(data, list):
        raise ValueError("JSON root should be an array of objects")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError("All JSON entries must be dictionaries")
    if not data:
        print("No data found in JSON file")
        return

    # Collect all unique field names alphabetically sorted
    fieldnames = sorted({key for item in data for key in item.keys()})

    # Write CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for item in data:
            # Convert nested structures to strings
            row = {
                key: str(value) if isinstance(value, (list, dict)) else value
                for key, value in item.items()
            }
            writer.writerow(row)

def getAdaMatchesLinks(url):
    matches = []
    ## COLLECT MATCHES_LINKS FOR EACH DAY
    driver = webdriver.Remote("http://172.17.0.2:4444", options=webdriver.ChromeOptions())
    driver.maximize_window()

    try:
        driver.get(url)
        #delete the cookies  
        driver.delete_all_cookies()  

        table = driver.find_element(By.ID, "fh_main_tab")
        moreButton = table.find_elements(By.CLASS_NAME, "footer")

        i = 0 #prevent infinte loops!!
        while len(moreButton) > 0:
            i += 1
            if i >= 10:
                break
            actions = ActionChains(driver)
            #driver.execute_script(f"window.scrollTo(0, {moreButton[0].location['y']});")
            moreButton[0].click()
            actions.move_to_element(moreButton[0])
            # actions.click(moreButton[0])
            # actions.perform()
            time.sleep(3)  
            table = driver.find_element(By.ID, "fh_main_tab")
            moreButton = table.find_elements(By.CLASS_NAME, "footer")

        todayMatches = driver.find_elements(By.CLASS_NAME, "live-subscription")
        gc.collect()
        print(len(todayMatches))
        for match in todayMatches:
            html = match.get_attribute('outerHTML')
            matches.append(html)
            soup = BeautifulSoup(html, 'html.parser')

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        
    driver.close()
    return matches

# docker run -d -p 4444:4444 -p 7900:7900  --shm-size="2g" --platform linux/x86_64 -e SE_NODE_SESSION_TIMEOUT='20' selenium/standalone-chrome:latest
def scrappAdAStatsBulk(monthh, day):

    matches = []

    ## COLLECT MATCHES_STATS FROM MATCHES_LINKS FILES
    folder_path = "scrapper/newData/aDa/matches_links/"
    errors = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Check if it's a JSON file
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)  # Load the JSON data

                    print("########## FILE: " + filename)
                    if isinstance(data, list): # Check if the loaded data is a list (array)
                        for element in data:
                            try:
                                match = getAdaMatchesStats(element)
                                #matches += match
                                if len(match) > 0:
                                    insertMatchInDB(match[0])
                                #break
                                # with open("scrapper/newData/aDa/matches_stats/" + filename.replace('Links', 'Stats'), 'a', encoding='utf-8') as file:
                                #     json.dump(matches, file, ensure_ascii=False, indent=4)
                                #     matches = []
                                
                                #time.sleep(2)
                            except Exception as e:
                                print(e)
                                errors.append(e)
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                print(exc_type, fname, exc_tb.tb_lineno)
                                matches = []
                                continue
                    else:
                        print(f"Warning: File '{filename}' does not contain a JSON array. Skipping.")
            except Exception as e:
                print(e)
            #break

    print(errors)
    return errors

def insertMatchInDB(match):
    ca_file = "ca.pem"
    db_params = {
        'dbname': 'defaultdb',
        'user': 'avnadmin',
        'password': 'AVNS_xilofcVMIxDNHVjsmDg',
        'host': 'pg-186b9d39-betstrat-ea12.h.aivencloud.com',
        'port': '23138',
        'sslmode': 'require',
        'sslrootcert': ca_file
    }
    
    conn = None  # Initialize conn to None
    try:
         # Connect to the database
        conn = psycopg2.connect(**db_params)
        print(f"Connected to database !")

        cursor = conn.cursor()

        columns = ', '.join(match.keys())
        placeholders = ', '.join(['%s'] * len(match))  # Use %s for PostgreSQL

        query = f"INSERT INTO backtesting.matches_stats ({columns}) VALUES ({placeholders})"

        cursor.execute(query, tuple(match.values()))
        conn.commit()
        print("Data inserted successfully!")
        return True

    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            cursor = conn.cursor()  # Create a cursor before closing it
            cursor.close()
            conn.close()


def getAdaMatchesStats(element):
    matchesToBet = []
    soup = BeautifulSoup(element, 'html.parser')

    #filtered_competitions = ["Mundo - FIFA Club World Cup", "Albânia - 1st Division", "Albânia - Cup", "Albânia - Super Cup", "Albânia - Superliga", "Alemanha - 2. Bundesliga", "Alemanha - 3. Liga", "Alemanha - Bundesliga", "Alemanha - DFB Pokal", "Alemanha - DFB Pokal Women", "Alemanha - Oberliga", "Alemanha - Regionalliga", "Alemanha - Super Cup", "Algéria - Coupe Nationale", "Algéria - Ligue 1", "América do Sul - CONMEBOL Libertadores", "América do Sul - CONMEBOL Recopa", "América do Sul - CONMEBOL Sudamericana", "Angola - Girabola", "Argentina - Copa Argentina", "Argentina - Copa de la Superliga", "Argentina - Primera División", "Argentina - Primera Nacional", "Arménia - Cup", "Arménia - Premier League", "Arábia Saudita - King's Cup", "Arábia Saudita - Pro League", "Austrália - A-League", "Austrália - FFA Cup", "Azerbaijão - Cup", "Azerbaijão - Premyer Liqa", "Bielorrússia - 1. Division", "Bielorrússia - Cup", "Bielorrússia - Premier League", "Bielorrússia - Super Cup", "Bolívia - Primera División", "Brasil - Serie A", "Brasil - Serie B", "Brasil - Serie C", "Brasil - Copa do Brasil", "Bulgária - A PFG", "Bulgária - B PFG", "Bulgária - Cup", "Bulgária - Super Cup", "Bélgica - Cup", "Bélgica - Super Cup", "Bélgica - First Division B", "Bélgica - Pro League", "Bósnia-Herzegovina - Cup", "Bósnia-Herzegovina - Premier Liga", "Canadá - Canadian Championship", "Catar - Play-offs 1/2", "Catar - QSL Cup", "Catar - Stars League", "Cazaquistão - Cup", "Cazaquistão - Premier League", "Chile - Copa Chile", "Chile - Primera B", "Chile - Primera División", "Chipre - 1. Division", "Chipre - Cup", "Colômbia - Copa Colombia", "Colômbia - Primera A", "Colômbia - Primera B", "Costa Rica - Primera División", "Croácia - 1. HNL", "Croácia - 2. HNL", "Croácia - Cup", "Dinamarca - 1st Division", "Dinamarca - DBU Pokalen", "Dinamarca - Superliga", "Egipto - Premier League", "Egipto - Super Cup", "El Salvador - Primera Division", "Emirados Árabes Unidos - Arabian Gulf League", "Emirados Árabes Unidos - League Cup", "Emirados Árabes Unidos - Super Cup", "Equador - Liga Pro", "Equador - Primera B", "Escócia - Championship", "Escócia - FA Cup", "Escócia - Premiership", "Escócia - Taça da Liga", "Eslováquia - 2. liga", "Eslováquia - Cup", "Eslováquia - Super Liga", "Eslovénia - 1. SNL", "Eslovénia - 2. SNL", "Eslovénia - Cup", "Eslovénia - Play-offs 1/2", "Espanha - Copa del Rey", "Espanha - Super Cup", "Espanha - Primera División", "Espanha - Segunda División", "Estados Unidos da América - MLS", "Estados Unidos da América - US Open Cup", "Estados Unidos da América - USL Championship", "Estónia - Cup", "Estónia - Esiliiga A", "Estónia - Meistriliiga", "Estónia - Super Cup", "Europa - Europa Conference League", "Europa - UEFA Champions League", "Europa - UEFA Europa League", "Europa - UEFA Youth League", "Finlândia - Suomen Cup", "Finlândia - Veikkausliiga", "Finlândia - Ykkönen", "França - Coupe de France", "França - Ligue 1", "França - Ligue 2", "França - National", "Gales - Premier League", "Gales - Welsh Cup", "Gana - Premier League", "Grécia - Cup", "Grécia - Super League", "Guatemála - Liga Nacional", "Honduras - Liga Nacional", "Hong Kong - FA Cup", "Hong Kong - HKFA 1st Division", "Hong Kong - Premier League", "Húngria - Magyar Kupa", "Húngria - NB I", "Húngria - NB II", "Indonésia - Liga 1", "Inglaterra - Championship", "Inglaterra - Taça da Liga", "Inglaterra - FA Cup", "Inglaterra - League One", "Inglaterra - League Two", "Inglaterra - Premier League", "Iraque - Iraqi League", "Irlanda do Norte - Premiership", "Irlanda do Norte - Taça da Liga", "Irão - Azadegan League", "Irão - Persian Gulf Pro League", "Islândia - 1. Deild", "Islândia - Cup", "Islândia - Úrvalsdeild", "Israel - Liga Leumit", "Israel - Ligat ha'Al", "Israel - State Cup", "Israel - Toto Cup Ligat Al", "Itália - Coppa Italia", "Itália - Lega Pro", "Itália - Serie A", "Itália - Serie B", "Jamaica - Premier League", "Japão - Emperor Cup", "Japão - J1 League", "Japão - J2 League", "Japão - Super Cup", "Japão - Taça da J-Liga", "Letónia - Cup", "Letónia - Virsliga", "Lituânia - A Lyga", "Lituânia - Cup", "Luxemburgo - National Division", "Luxemburgo - Play-offs 1/2", "Malta - FA Trophy", "Malta - Premier League", "Malta - Super Cup", "Malásia - Super League", "Moldávia - Cupa", "Moldávia - Divizia Națională", "Moçambique - Moçambola", "Mundo - Amigáveis", "Mundo - Amigáveis de clubes", "Mundo - Concacaf Champions League", "México - Liga de Expansión MX", "México - Liga MX", "México - Copa MX", "Nigéria - NPFL", "Noruega - 1. Division", "Noruega - Eliteserien", "Noruega - NM Cupen", "Nova Zelândia - National League", "Panamá - LPF", "Paraguai - Division Profesional", "Países Baixos - Eerste Divisie", "Países Baixos - Eredivisie", "Países Baixos - KNVB Beker", "Países Baixos - Super Cup", "Perú - Primera División", "Perú - Segunda División", "Polónia - Cup", "Polónia - Ekstraklasa", "Polónia - I Liga", "Portugal - Liga Portugal Betclic", "Portugal - Segunda Liga", "Portugal - Supertaça", "Portugal - Taça da Liga", "Portugal - Taça de Portugal", "República Checa - Cup", "República Checa - Czech Liga", "República Checa - FNL", "República da Coreia - FA Cup", "República da Coreia - K League 1", "República da Coreia - K League 2", "República da Irlanda - FAI Cup", "República da Irlanda - First Division", "República da Irlanda - Premier Division", "Roménia - Cupa României", "Roménia - Liga I", "Roménia - Liga II", "RP China - CSL", "Rússia - FNL", "Rússia - Cup", "Rússia - Premier League", "Singapura - Cup", "Singapura - Premier League", "Suécia - Allsvenskan", "Suécia - Superettan", "Suécia - Svenska Cupen", "Suíça - Challenge League", "Suíça - Super League", "Suíça - Schweizer Pokal", "Sérvia - Cup", "Sérvia - Prva Liga", "Sérvia - Super Liga", "Tailândia - Thai League 1", "Tunísia - Ligue 1", "Turquia - 1. Lig", "Turquia - Cup", "Turquia - Super Liga", "Ucrânia - Cup", "Ucrânia - Persha Liga", "Ucrânia - Premier League", "Uruguai - Primera División", "Uruguai - Segunda División", "Venezuela - Primera División", "Vietname - V.League 1", "África - CAF Champions League", "Índia - I-League", "Ásia - AFC Champions League", "Áustria - 1. Liga", "Áustria - Bundesliga", "Áustria - Cup", "África do Sul - 1st Division", "África do Sul - Cup", "África do Sul - PSL", "África do Sul - Taça da Liga"]

    filtered_competitions = ["Mundo - FIFA Club World Cup"]
    try:
        if 'Cancelado' in soup.find('td', class_='status').text:
            return matchesToBet

        matchUrl = soup.find('td', class_='score').find('a')["href"]

        matchDict = OrderedDict()
        homeTeam = soup.find('td', class_='team-a').text.strip()
        awayTeam = soup.find('td', class_='team-b').text.strip()
        matchScore = soup.find('td', class_='score').text
        matchScore = re.sub(r'\s+', ' ', matchScore).strip().replace(' ', '')
        competition = soup.find('td', class_='flag').find('a')["title"]

        if competition not in filtered_competitions:
            return matchesToBet

        if len(matchScore) < 3:
            homeScore = None
            awayScore = None
            totalGoals = None
        else:
            homeScore = matchScore[0:6].split('-')[0].strip()
            awayScore = matchScore[0:6].split('-')[1].strip()
            totalGoals = int(homeScore) + int(awayScore)

        date = soup.find('td', class_='hour')["timestamp"]

        htResult = getFinishedMatchFirstHalfGoalsFromAdA(matchUrl + "/live")
        gc.collect()

        matchDict['match_url'] = matchUrl
        matchDict['date'] = str(datetime.fromtimestamp(int(date)))
        matchDict['timestamp'] = (date)
        matchDict['home_team'] = homeTeam
        matchDict['away_team'] = awayTeam
        matchDict['ft_result'] = re.sub(r'\s+', ' ', matchScore).strip()
        matchDict['total_goals'] = totalGoals
        matchDict['home_score'] = homeScore
        matchDict['away_score'] = awayScore
        matchDict['ht_result'] = htResult
        matchDict['competition'] = competition
        matchStats = getMatchStatsFromAdA(matchUrl)
        matchDict.update(matchStats)
        matchesToBet.append(matchDict)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return matchesToBet

def getMatchStatsFromAdA(url):
    response = requests.get(url)
    matchStats = OrderedDict()
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("\ngetting match stats: " + str(url))

        try:

            ############## COMPETITION INFO
            competitionThisMatch = soup.find('div', class_='stats-game-head').find_all('li')[4].text.strip()
            season = soup.find('div', class_='stats-game-head').find_all('li')[5].text.strip()
            competitionPhase = soup.find('div', class_='stats-game-head').find_all('li')[6].text.strip()

            ############## GOALS STATS
            tables = soup.find_all('table', 'stat-seqs stat-half-padding')
            homeGoalsTable = tables[2]
            awayGoalsTable = tables[3]

            # then we can iterate through each row and extract either header or row values:
            header = []
            homeGoalsRows = []
            awayGoalsRows = []

            for i, row in enumerate(homeGoalsTable.find_all('tr')):
                if i == 0:
                    header = [el.text.strip() for el in row.find_all('th')]
                else:
                    homeGoalsRows.append([el.text.strip() for el in row.find_all('td')])

            for i, row in enumerate(awayGoalsTable.find_all('tr')):
                if i == 0:
                    header = [el.text.strip() for el in row.find_all('th')]
                else:
                    awayGoalsRows.append([el.text.strip() for el in row.find_all('td')])


            homeOverRateAtHome = 0 if homeGoalsRows[5][1][:-1] == '-' or homeGoalsRows[5][1][:-1] == '' else homeGoalsRows[5][1][:-1]
            homeOverRateAtAway = 0 if homeGoalsRows[5][2][:-1] == '-' or homeGoalsRows[5][2][:-1] == '' else homeGoalsRows[5][2][:-1]
            homeOverRateGlobal = 0 if homeGoalsRows[5][3][:-1] == '-' or homeGoalsRows[5][3][:-1] == '' else homeGoalsRows[5][3][:-1]
            awayOverRateAtHome = 0 if awayGoalsRows[5][1][:-1] == '-' or awayGoalsRows[5][1][:-1] == '' else awayGoalsRows[5][1][:-1]
            awayOverRateAtAway = 0 if awayGoalsRows[5][2][:-1] == '-' or awayGoalsRows[5][2][:-1] == '' else awayGoalsRows[5][2][:-1]
            awayOverRateGlobal = 0 if awayGoalsRows[5][3][:-1] == '-' or awayGoalsRows[5][3][:-1] == '' else awayGoalsRows[5][3][:-1]
            homeScoredGoalsAvgAtHome = 0 if homeGoalsRows[0][1] == '-' or homeGoalsRows[0][1] == '' else homeGoalsRows[0][1]
            homeScoredGoalsAvgAtAway = 0 if homeGoalsRows[0][2] == '-' or homeGoalsRows[0][2] == '' else homeGoalsRows[0][2]
            homeScoredGoalsAvgGlobal = 0 if homeGoalsRows[0][3] == '-' or homeGoalsRows[0][3] == '' else homeGoalsRows[0][3]
            awayScoredGoalsAvgAtHome = 0 if awayGoalsRows[0][1] == '-' or awayGoalsRows[0][1] == '' else awayGoalsRows[0][1]
            awayScoredGoalsAvgAtAway = 0 if awayGoalsRows[0][2] == '-' or awayGoalsRows[0][2] == '' else awayGoalsRows[0][2]
            awayScoredGoalsAvgGlobal = 0 if awayGoalsRows[0][3] == '-' or awayGoalsRows[0][3] == '' else awayGoalsRows[0][3]
            homeConcededGoalsAvgAtHome = 0 if homeGoalsRows[1][1] == '-' or homeGoalsRows[1][1] == '' else homeGoalsRows[1][1]
            homeConcededGoalsAvgAtAway = 0 if homeGoalsRows[1][2] == '-' or homeGoalsRows[1][2] == '' else homeGoalsRows[1][2]
            homeConcededGoalsAvgGlobal = 0 if homeGoalsRows[1][3] == '-' or homeGoalsRows[1][3] == '' else homeGoalsRows[1][3]
            awayConcededGoalsAvgAtHome = 0 if awayGoalsRows[1][1] == '-' or awayGoalsRows[1][1] == '' else awayGoalsRows[1][1]
            awayConcededGoalsAvgAtAway = 0 if awayGoalsRows[1][2] == '-' or awayGoalsRows[1][2] == '' else awayGoalsRows[1][2]
            awayConcededGoalsAvgGlobal = 0 if awayGoalsRows[1][3] == '-' or awayGoalsRows[1][3] == '' else awayGoalsRows[1][3]
            homeTotalGoalsAvgAtHome = 0 if homeGoalsRows[2][1] == '-' or homeGoalsRows[2][1] == '' else homeGoalsRows[2][1]
            homeTotalGoalsAvgAtAway = 0 if homeGoalsRows[2][2] == '-' or homeGoalsRows[2][2] == '' else homeGoalsRows[2][2]
            homeTotalGoalsAvgGlobal = 0 if homeGoalsRows[2][3] == '-' or homeGoalsRows[2][3] == '' else homeGoalsRows[2][3]
            awayTotalGoalsAvgAtHome = 0 if awayGoalsRows[2][1] == '-' or awayGoalsRows[2][1] == '' else awayGoalsRows[2][1]
            awayTotalGoalsAvgAtAway = 0 if awayGoalsRows[2][2] == '-' or awayGoalsRows[2][2] == '' else awayGoalsRows[2][2]
            awayTotalGoalsAvgGlobal = 0 if awayGoalsRows[2][3] == '-' or awayGoalsRows[2][3] == '' else awayGoalsRows[2][3]
            homeCleanSheetsRateAtHome = 0 if homeGoalsRows[3][1][:-1] == '-' or homeGoalsRows[3][1][:-1] == '' else homeGoalsRows[3][1][:-1]
            homeCleanSheetsRateAtAway = 0 if homeGoalsRows[3][2][:-1] == '-' or homeGoalsRows[3][2][:-1] == '' else homeGoalsRows[3][2][:-1]
            homeCleanSheetsRateGlobal = 0 if homeGoalsRows[3][3][:-1] == '-' or homeGoalsRows[3][3][:-1] == '' else homeGoalsRows[3][3][:-1]
            awayCleanSheetsRateAtHome = 0 if awayGoalsRows[3][1][:-1] == '-' or awayGoalsRows[3][1][:-1] == '' else awayGoalsRows[3][1][:-1]
            awayCleanSheetsRateAtAway = 0 if awayGoalsRows[3][2][:-1] == '-' or awayGoalsRows[3][2][:-1] == '' else awayGoalsRows[3][2][:-1]
            awayCleanSheetsRateGlobal = 0 if awayGoalsRows[3][3][:-1] == '-' or awayGoalsRows[3][3][:-1] == '' else awayGoalsRows[3][3][:-1]
            homeNoScoreRateAtHome = 0 if homeGoalsRows[4][1][:-1] == '-' or homeGoalsRows[4][1][:-1] == '' else homeGoalsRows[4][1][:-1]
            homeNoScoreRateAtAway = 0 if homeGoalsRows[4][2][:-1] == '-' or homeGoalsRows[4][2][:-1] == '' else homeGoalsRows[4][2][:-1]
            homeNoScoreRateGlobal = 0 if homeGoalsRows[4][3][:-1] == '-' or homeGoalsRows[4][3][:-1] == '' else homeGoalsRows[4][3][:-1]
            awayNoScoreRateAtHome = 0 if awayGoalsRows[4][1][:-1] == '-' or awayGoalsRows[4][1][:-1] == '' else awayGoalsRows[4][1][:-1]
            awayNoScoreRateAtAway = 0 if awayGoalsRows[4][2][:-1] == '-' or awayGoalsRows[4][2][:-1] == '' else awayGoalsRows[4][2][:-1]
            awayNoScoreRateGlobal = 0 if awayGoalsRows[4][3][:-1] == '-' or awayGoalsRows[4][3][:-1] == '' else awayGoalsRows[4][3][:-1]
            homeUnderRateAtHome = 0 if homeGoalsRows[6][1][:-1] == '-' or homeGoalsRows[6][1][:-1] == '' else homeGoalsRows[6][1][:-1]
            homeUnderRateAtAway = 0 if homeGoalsRows[6][2][:-1] == '-' or homeGoalsRows[6][2][:-1] == '' else homeGoalsRows[6][2][:-1]
            homeUnderRateGlobal = 0 if homeGoalsRows[6][3][:-1] == '-' or homeGoalsRows[6][3][:-1] == '' else homeGoalsRows[6][3][:-1]
            awayUnderRateAtHome = 0 if awayGoalsRows[6][1][:-1] == '-' or awayGoalsRows[6][1][:-1] == '' else awayGoalsRows[6][1][:-1]
            awayUnderRateAtAway = 0 if awayGoalsRows[6][2][:-1] == '-' or awayGoalsRows[6][2][:-1] == '' else awayGoalsRows[6][2][:-1]
            awayUnderRateGlobal = 0 if awayGoalsRows[6][3][:-1] == '-' or awayGoalsRows[6][3][:-1] == '' else awayGoalsRows[6][3][:-1]


            ############## LAST MATCHES
            lastMatchesTables = soup.find(id='ultimos_resultados') #.find_all("td", {"class" : regex})
            home_team_last_matches = []
            away_team_last_matches = []

            team_tables = soup.find_all('table', class_='stat-last10')

            for row in team_tables[0].find_all('tr'):
                # Skip the header row and "Proximos jogos" rows
                if row.find('th', class_='stats-wd-date') or row.find('td', class_='next_matches_title'):
                    continue

                cells = row.find_all('td')
                if len(cells) >= 5:
                    date = cells[0].text.strip()
                    competition = cells[1]['title']
                    home_team = cells[2].text.strip()
                    result = cells[3].text.strip()
                    away_team = cells[4].text.strip()

                    match_string = f"{date} | {competition} | {home_team} | {result} | {away_team}"
                    home_team_last_matches.append(match_string)

            for row in team_tables[1].find_all('tr'):
                # Skip the header row and "Proximos jogos" rows
                if row.find('th', class_='stats-wd-date') or row.find('td', class_='next_matches_title'):
                    continue

                cells = row.find_all('td')
                if len(cells) >= 5:
                    date = cells[0].text.strip()
                    competition = cells[1]['title']
                    home_team = cells[2].text.strip()
                    result = cells[3].text.strip()
                    away_team = cells[4].text.strip()

                    match_string = f"{date} | {competition} | {home_team} | {result} | {away_team}"
                    away_team_last_matches.append(match_string)
            
            
            ############## H2H MATCHES
            regex = re.compile('stat-.*')
            h2hMatches = soup.find(id='show_h2h').find('table') #.find_all("td", {"class" : regex})
            h2hMatchesList = []

            for row in h2hMatches.find_all('tr'):
                # Skip the header row and "Proximos jogos" rows
                if row.find('th', class_='stats-wd-date') or row.find('td', class_='next_matches_title'):
                    continue

                cells = row.find_all('td')
                if len(cells) >= 5:
                    date = cells[0].text.strip()
                    competition = cells[1]['title']
                    home_team = cells[2].text.strip()
                    result = cells[3].text.strip()
                    away_team = cells[4].text.strip()

                    match_string = f"{date} | {competition} | {home_team} | {result} | {away_team}"
                    h2hMatchesList.append(match_string)
    
            ############## ODDS
            if (soup.find(id='odds')):
                oddsDict = extractOddsValues(soup.find(id='odds')['href'])
                v1Odd = oddsDict['v1Odd']
                xOdd = oddsDict['xOdd']
                v2Odd = oddsDict['v2Odd']
                bttsYesOdd = oddsDict['bttsYesOdd']
                bttsNoOdd = oddsDict['bttsNoOdd']
                overOdd = oddsDict['over25Odd']
                underOdd = oddsDict['under25Odd']
            else:
                bttsYesOdd = 0
                bttsNoOdd = 0
                #over/under odds
                odds = soup.find_all('table', 'odds_2-5')
                if len(odds) > 0:
                    odds = odds[0].find_all("td", {"class" : "odd-B"})
                underOdd = 0
                overOdd = 0
                if len(odds) >= 2:
                    underOdd = odds[0].text.strip()
                    overOdd = odds[1].text.strip()

                #home win odds
                v1Odds = soup.find_all('table', 'odds_MO')
                v1Odd = 0
                xOdd = 0
                v2Odd = 0
                if len(odds) > 0:
                    v1Odd = v1Odds[0].find_all("td")[1].text.strip()
                    xOdd = v1Odds[0].find_all("td")[2].text.strip()
                    v2Odd = v1Odds[0].find_all("td")[3].text.strip()


            matchStats['season'] = season
            matchStats['competition_phase'] = re.sub(r'\s+', ' ', competitionPhase).strip()

            matchStats['home_scored_goals_avg_at_home_pre'] = homeScoredGoalsAvgAtHome
            matchStats['home_scored_goals_avg_at_away_pre'] = homeScoredGoalsAvgAtAway
            matchStats['home_scored_goals_avg_global_pre'] = homeScoredGoalsAvgGlobal
            matchStats['away_scored_goals_avg_at_home_pre'] = awayScoredGoalsAvgAtHome
            matchStats['away_scored_goals_avg_at_away_pre'] = awayScoredGoalsAvgAtAway
            matchStats['away_scored_goals_avg_global_pre'] = awayScoredGoalsAvgGlobal

            matchStats['home_conceded_goals_avg_at_home_pre'] = homeConcededGoalsAvgAtHome
            matchStats['home_conceded_goals_avg_at_away_pre'] = homeConcededGoalsAvgAtAway
            matchStats['home_conceded_goals_avg_global_pre'] = homeConcededGoalsAvgGlobal
            matchStats['away_conceded_goals_avg_at_home_pre'] = awayConcededGoalsAvgAtHome
            matchStats['away_conceded_goals_avg_at_away_pre'] = awayConcededGoalsAvgAtAway
            matchStats['away_conceded_goals_avg_global_pre'] = awayConcededGoalsAvgGlobal

            matchStats['home_total_goals_avg_at_home_pre'] = homeTotalGoalsAvgAtHome
            matchStats['home_total_goals_avg_at_away_pre'] = homeTotalGoalsAvgAtAway
            matchStats['home_total_goals_avg_global_pre'] = homeTotalGoalsAvgGlobal
            matchStats['away_total_goals_avg_at_home_pre'] = awayTotalGoalsAvgAtHome
            matchStats['away_total_goals_avg_at_away_pre'] = awayTotalGoalsAvgAtAway
            matchStats['away_total_goals_avg_global_pre'] = awayTotalGoalsAvgGlobal

            matchStats['home_clean_sheets_rate_at_home_pre'] = homeCleanSheetsRateAtHome
            matchStats['home_clean_sheets_rate_at_away_pre'] = homeCleanSheetsRateAtAway
            matchStats['home_clean_sheets_rate_global_pre'] = homeCleanSheetsRateGlobal
            matchStats['away_clean_sheets_rate_at_home_pre'] = awayCleanSheetsRateAtHome
            matchStats['away_clean_sheets_rate_at_away_pre'] = awayCleanSheetsRateAtAway
            matchStats['away_clean_sheets_rate_global_pre'] = awayCleanSheetsRateGlobal

            matchStats['home_no_score_rate_at_home_pre'] = homeNoScoreRateAtHome
            matchStats['home_no_score_rate_at_away_pre'] = homeNoScoreRateAtAway
            matchStats['home_no_score_rate_global_pre'] = homeNoScoreRateGlobal
            matchStats['away_no_score_rate_at_home_pre'] = awayNoScoreRateAtHome
            matchStats['away_no_score_rate_at_away_pre'] = awayNoScoreRateAtAway
            matchStats['away_no_score_rate_global_pre'] = awayNoScoreRateGlobal

            matchStats['home_over_rate_at_home_pre'] = homeOverRateAtHome
            matchStats['home_over_rate_at_away_pre'] = homeOverRateAtAway
            matchStats['home_over_rate_global_pre'] = homeOverRateGlobal
            matchStats['away_over_rate_at_home_pre'] = awayOverRateAtHome
            matchStats['away_over_rate_at_away_pre'] = awayOverRateAtAway
            matchStats['away_over_rate_global_pre'] = awayOverRateGlobal

            matchStats['home_under_rate_at_home_pre'] = homeUnderRateAtHome
            matchStats['home_under_rate_at_away_pre'] = homeUnderRateAtAway
            matchStats['home_under_rate_global_pre'] = homeUnderRateGlobal
            matchStats['away_under_rate_at_home_pre'] = awayUnderRateAtHome
            matchStats['away_under_rate_at_away_pre'] = awayUnderRateAtAway
            matchStats['away_under_rate_global_pre'] = awayUnderRateGlobal

            matchStats['last_home_team_matches'] = re.sub(r'\s+', ' ', str(home_team_last_matches)).strip()
            matchStats['last_away_team_matches'] = re.sub(r'\s+', ' ', str(away_team_last_matches)).strip()
            matchStats['h2h_matches'] = str(h2hMatchesList)

            matchStats['v1_odd'] = (v1Odd)
            matchStats['x_odd'] = (xOdd)
            matchStats['v2_odd'] = (v2Odd)
            matchStats['under25_odd'] = (underOdd)
            matchStats['over25_odd'] = (overOdd)
            matchStats['btts_yes_odd'] = (bttsYesOdd)
            matchStats['btts_no_odd'] = (bttsNoOdd)
            
            
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    
    return matchStats

def extractOddsValues(url):
    response = requests.get(url)
    try:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            oddsDiv = soup.find('div', class_='full_markets_odds')

            finalResultMarket = ''
            bttsMarket = ''
            over25Market = ''
            finalResultOdds = []
            bttsOdds = []
            over25Odds = []

            for li in oddsDiv.find_all('li'):
                if '1x2' in li.text:
                    finalResultMarket = li['market']
                    finalResultOdds = oddsDiv.find('div', class_=finalResultMarket).find('table').find_all('tr', class_='strong_text')
                if 'Ambas' in li.text:
                    bttsMarket = li['market']
                    bttsOdds = oddsDiv.find('div', class_=bttsMarket).find('table').find_all('tr', class_='strong_text')
                if '2.5' in li.text:
                    over25Market = li['market']
                    over25Odds = oddsDiv.find('div', class_=over25Market).find('table').find_all('tr', class_='strong_text')

            if (len(finalResultOdds) > 0):
                finalResultOdds = finalResultOdds[0].find_all('td', class_='align_odds')
                v1Odd = finalResultOdds[0].text.strip()
                xOdd = finalResultOdds[1].text.strip()
                v2Odd = finalResultOdds[2].text.strip()
            else:
                finalResultOdds = oddsDiv.find('div', class_=finalResultMarket).find('table').find_all('td', class_='align_odds')
                v1Odd = finalResultOdds[0].text.strip()
                xOdd = finalResultOdds[1].text.strip()
                v2Odd = finalResultOdds[2].text.strip()

            if (len(bttsOdds) > 0):
                bttsOdds = bttsOdds[0].find_all('td', class_='align_odds')
                bttsYesOdd = bttsOdds[0].text.strip()
                bttsNoOdd = bttsOdds[1].text.strip()
            else:
                bttsOdds = oddsDiv.find('div', class_=bttsMarket).find('table').find_all('td', class_='align_odds')
                bttsYesOdd = bttsOdds[0].text.strip()
                bttsNoOdd = bttsOdds[1].text.strip()

            if (len(over25Odds) > 0):
                over25Odds = over25Odds[0].find_all('td', class_='align_odds')
                over25 = over25Odds[1].text.strip()
                under25 = over25Odds[0].text.strip()
            else:
                over25Odds = oddsDiv.find('div', class_=over25Market).find('table').find_all('td', class_='align_odds')
                over25 = over25Odds[1].text.strip()
                under25 = over25Odds[0].text.strip()

            odds = {'v1Odd': v1Odd.split(' ')[0],
                    'xOdd': xOdd.split(' ')[0],
                    'v2Odd': v2Odd.split(' ')[0],
                    'bttsYesOdd': bttsYesOdd.split(' ')[0],
                    'bttsNoOdd': bttsNoOdd.split(' ')[0],
                    'over25Odd': over25.split(' ')[0],
                    'under25Odd': under25.split(' ')[0]}
            
            return odds        
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        odds = {'v1Odd': 0,
                    'xOdd': 0,
                    'v2Odd': 0,
                    'bttsYesOdd': 0,
                    'bttsNoOdd': 0,
                    'over25Odd': 0,
                    'under25Odd': 0}
        return odds        

def getFinishedMatchFirstHalfGoalsFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # print(url)

        table = soup.find(id='first-half-summary')
        
        return table.find_all('td', 'ht-score')[0].text.strip()        
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')