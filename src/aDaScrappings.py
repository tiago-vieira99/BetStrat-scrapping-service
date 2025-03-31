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

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
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

# docker run -d -p 4444:4444 -p 7900:7900  --shm-size="2g" --platform linux/x86_64 -e SE_NODE_SESSION_TIMEOUT='20' selenium/standalone-chrome:latest
def scrappAdAStatsBulk(month):
    #driver = webdriver.Chrome(options=set_chrome_options())
    driver = webdriver.Remote("http://172.17.0.2:4444", options=webdriver.ChromeOptions())
    driver.maximize_window()

    matches = []
    for i in range(1,32):
        print("########## DATE: " + str(i) + '/' + month)
        try:
            matches += getOver25GoalCandidatesFromAdA("https://www.academiadasapostas.com/stats/livescores/2024/"+ month + "/" + str(i), driver)
            with open("scrapper/newData/allMatchesByAda_2024_" + str(i) + ".json", 'a', encoding='utf-8') as file:
                json.dump(matches, file, ensure_ascii=False, indent=4)
                matches = []
            
            #time.sleep(2)
        except Exception as e:
            print("WILL SKIP THE DAY: " + + str(i) + '/' + month)
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            matches = []
            continue
    driver.close()
    return matches

def getOver25GoalCandidatesFromAdA(url, driver):
    matchesToBet = []
    
    driver.get(url)
    #delete the cookies  
    driver.delete_all_cookies()  

    table = driver.find_element(By.ID, "fh_main_tab")
    moreButton = table.find_elements(By.CLASS_NAME, "footer")

    while len(moreButton) > 0:
        actions = ActionChains(driver)
        actions.move_to_element(moreButton[0])
        actions.click(moreButton[0])
        actions.perform()
        time.sleep(3)  
        table = driver.find_element(By.ID, "fh_main_tab")
        moreButton = table.find_elements(By.CLASS_NAME, "footer")

    todayMatches = driver.find_elements(By.CLASS_NAME, "live-subscription")
    print(len(todayMatches))

    try:
        for match in todayMatches:
            if 'Cancelado' in match.find_element(By.CLASS_NAME, "status").text:
                continue

            matchUrl = match.find_element(By.CLASS_NAME, "score").find_element(By.TAG_NAME, "a").get_attribute("href")

            matchDict = OrderedDict()
            homeTeam = match.find_element(By.CLASS_NAME, "team-a").text
            awayTeam = match.find_element(By.CLASS_NAME, "team-b").text
            matchScore = match.find_element(By.CLASS_NAME, "score").text
            competition = match.find_element(By.CLASS_NAME, "flag").get_attribute("original-title")
            if len(matchScore) < 4:
                homeScore = '-'
                awayScore = '-'
                totalGoals = '-'
            else:
                homeScore = matchScore[0:6].split('-')[0].strip()
                awayScore = matchScore[0:6].split('-')[1].strip()
                totalGoals = int(homeScore) + int(awayScore)

            date = match.find_element(By.CLASS_NAME, "hour").get_attribute("timestamp")

            htResult = getFinishedMatchFirstHalfGoalsFromAdA(matchUrl + "/live")

            matchDict['01. date'] = str(datetime.fromtimestamp(int(date)))
            matchDict['02. timestamp'] = (date)
            matchDict['03. home_team'] = homeTeam
            matchDict['04. away_team'] = awayTeam
            matchDict['05. ft_result'] = re.sub(r'\s+', ' ', matchScore).strip()
            matchDict['06. total_goals'] = totalGoals
            matchDict['07. home_score'] = homeScore
            matchDict['08. away_score'] = awayScore
            matchDict['09. ht_result'] = htResult
            matchDict['11. competition'] = competition
            matchStats = getMatchStatsFromAdA(matchUrl)
            matchDict.update(matchStats)
            matchesToBet.append(matchDict)
            #break
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    # driver.close()
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


            homeOverRateAtHome = homeGoalsRows[5][1][:-1]
            homeOverRateAtAway = homeGoalsRows[5][2][:-1]
            homeOverRateGlobal = homeGoalsRows[5][3][:-1]
            awayOverRateAtHome = awayGoalsRows[5][1][:-1]
            awayOverRateAtAway = awayGoalsRows[5][2][:-1]
            awayOverRateGlobal = awayGoalsRows[5][3][:-1]
            homeScoredGoalsAvgAtHome = homeGoalsRows[0][1]
            homeScoredGoalsAvgAtAway = homeGoalsRows[0][2]
            homeScoredGoalsAvgGlobal = homeGoalsRows[0][3]
            awayScoredGoalsAvgAtHome = awayGoalsRows[0][1]
            awayScoredGoalsAvgAtAway = awayGoalsRows[0][2]
            awayScoredGoalsAvgGlobal = awayGoalsRows[0][3]
            homeConcededGoalsAvgAtHome = homeGoalsRows[1][1]
            homeConcededGoalsAvgAtAway = homeGoalsRows[1][2]
            homeConcededGoalsAvgGlobal = homeGoalsRows[1][3]
            awayConcededGoalsAvgAtHome = awayGoalsRows[1][1]
            awayConcededGoalsAvgAtAway = awayGoalsRows[1][2]
            awayConcededGoalsAvgGlobal = awayGoalsRows[1][3]
            homeTotalGoalsAvgAtHome = homeGoalsRows[2][1]
            homeTotalGoalsAvgAtAway = homeGoalsRows[2][2]
            homeTotalGoalsAvgGlobal = homeGoalsRows[2][3]
            awayTotalGoalsAvgAtHome = awayGoalsRows[2][1]
            awayTotalGoalsAvgAtAway = awayGoalsRows[2][2]
            awayTotalGoalsAvgGlobal = awayGoalsRows[2][3]
            homeCleanSheetsRateAtHome = homeGoalsRows[3][1][:-1]
            homeCleanSheetsRateAtAway = homeGoalsRows[3][2][:-1]
            homeCleanSheetsRateGlobal = homeGoalsRows[3][3][:-1]
            awayCleanSheetsRateAtHome = awayGoalsRows[3][1][:-1]
            awayCleanSheetsRateAtAway = awayGoalsRows[3][2][:-1]
            awayCleanSheetsRateGlobal = awayGoalsRows[3][3][:-1]
            homeNoScoreRateAtHome = homeGoalsRows[4][1][:-1]
            homeNoScoreRateAtAway = homeGoalsRows[4][2][:-1]
            homeNoScoreRateGlobal = homeGoalsRows[4][3][:-1]
            awayNoScoreRateAtHome = awayGoalsRows[4][1][:-1]
            awayNoScoreRateAtAway = awayGoalsRows[4][2][:-1]
            awayNoScoreRateGlobal = awayGoalsRows[4][3][:-1]
            homeUnderRateAtHome = homeGoalsRows[6][1][:-1]
            homeUnderRateAtAway = homeGoalsRows[6][2][:-1]
            homeUnderRateGlobal = homeGoalsRows[6][3][:-1]
            awayUnderRateAtHome = awayGoalsRows[6][1][:-1]
            awayUnderRateAtAway = awayGoalsRows[6][2][:-1]
            awayUnderRateGlobal = awayGoalsRows[6][3][:-1]


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


            matchStats['10. season'] = season
            matchStats['12. competition_phase'] = re.sub(r'\s+', ' ', competitionPhase).strip()

            matchStats['13. home_scored_goals_avg_at_home_pre'] = homeScoredGoalsAvgAtHome
            matchStats['14. home_scored_goals_avg_at_away_pre'] = homeScoredGoalsAvgAtAway
            matchStats['15. home_scored_goals_avg_global_pre'] = homeScoredGoalsAvgGlobal
            matchStats['16. away_scored_goals_avg_at_home_pre'] = awayScoredGoalsAvgAtHome
            matchStats['17. away_scored_goals_avg_at_away_pre'] = awayScoredGoalsAvgAtAway
            matchStats['18. away_scored_goals_avg_global_pre'] = awayScoredGoalsAvgGlobal

            matchStats['19. home_conceded_goals_avg_at_home_pre'] = homeConcededGoalsAvgAtHome
            matchStats['20. home_conceded_goals_avg_at_away_pre'] = homeConcededGoalsAvgAtAway
            matchStats['21. home_conceded_goals_avg_global_pre'] = homeConcededGoalsAvgGlobal
            matchStats['22. away_conceded_goals_avg_at_home_pre'] = awayConcededGoalsAvgAtHome
            matchStats['23. away_conceded_goals_avg_at_away_pre'] = awayConcededGoalsAvgAtAway
            matchStats['24. away_conceded_goals_avg_global_pre'] = awayConcededGoalsAvgGlobal

            matchStats['25. home_total_goals_avg_at_home_pre'] = homeTotalGoalsAvgAtHome
            matchStats['26. home_total_goals_avg_at_away_pre'] = homeTotalGoalsAvgAtAway
            matchStats['27. home_total_goals_avg_global_pre'] = homeTotalGoalsAvgGlobal
            matchStats['28. away_total_goals_avg_at_home_pre'] = awayTotalGoalsAvgAtHome
            matchStats['29. away_total_goals_avg_at_away_pre'] = awayTotalGoalsAvgAtAway
            matchStats['30. away_total_goals_avg_global_pre'] = awayTotalGoalsAvgGlobal

            matchStats['31. home_clean_sheets_rate_at_home_pre'] = homeCleanSheetsRateAtHome
            matchStats['32. home_clean_sheets_rate_at_away_pre'] = homeCleanSheetsRateAtAway
            matchStats['33. home_clean_sheets_rate_global_pre'] = homeCleanSheetsRateGlobal
            matchStats['34. away_clean_sheets_rate_at_home_pre'] = awayCleanSheetsRateAtHome
            matchStats['35. away_clean_sheets_rate_at_away_pre'] = awayCleanSheetsRateAtAway
            matchStats['36. away_clean_sheets_rate_global_pre'] = awayCleanSheetsRateGlobal

            matchStats['37. home_no_score_rate_at_home_pre'] = homeNoScoreRateAtHome
            matchStats['38. home_no_score_rate_at_away_pre'] = homeNoScoreRateAtAway
            matchStats['39. home_no_score_rate_global_pre'] = homeNoScoreRateGlobal
            matchStats['40. away_no_score_rate_at_home_pre'] = awayNoScoreRateAtHome
            matchStats['41. away_no_score_rate_at_away_pre'] = awayNoScoreRateAtAway
            matchStats['42. away_no_score_rate_global_pre'] = awayNoScoreRateGlobal

            matchStats['43. home_over_rate_at_home_pre'] = homeOverRateAtHome
            matchStats['44. home_over_rate_at_away_pre'] = homeOverRateAtAway
            matchStats['45. home_over_rate_global_pre'] = homeOverRateGlobal
            matchStats['46. away_over_rate_at_home_pre'] = awayOverRateAtHome
            matchStats['47. away_over_rate_at_away_pre'] = awayOverRateAtAway
            matchStats['48. away_over_rate_global_pre'] = awayOverRateGlobal

            matchStats['49. home_under_rate_at_home_pre'] = homeUnderRateAtHome
            matchStats['50. home_under_rate_at_away_pre'] = homeUnderRateAtAway
            matchStats['51. home_under_rate_global_pre'] = homeUnderRateGlobal
            matchStats['52. away_under_rate_at_home_pre'] = awayUnderRateAtHome
            matchStats['53. away_under_rate_at_away_pre'] = awayUnderRateAtAway
            matchStats['54. away_under_rate_global_pre'] = awayUnderRateGlobal

            matchStats['55. last_home_team_matches'] = re.sub(r'\s+', ' ', str(home_team_last_matches)).strip()
            matchStats['56. last_away_team_matches'] = re.sub(r'\s+', ' ', str(away_team_last_matches)).strip()
            matchStats['57. h2h_matches'] = str(h2hMatchesList)

            matchStats['58. v1Odd'] = (v1Odd)
            matchStats['59. xOdd'] = (xOdd)
            matchStats['60. v2Odd'] = (v2Odd)
            matchStats['61. underOdd'] = (underOdd)
            matchStats['62. overOdd'] = (overOdd)
            matchStats['63. bttsYesOdds'] = (bttsYesOdd)
            matchStats['64. bttsNoOdds'] = (bttsNoOdd)
            
            
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

            for li in oddsDiv.find_all('li'):
                if '1x2' in li.text:
                    finalResultMarket = li['market']
                if 'Ambas' in li.text:
                    bttsMarket = li['market']
                if '2.5' in li.text:
                    over25Market = li['market']

            finalResultOdds = oddsDiv.find('div', class_=finalResultMarket).find('table').find_all('tr', class_='strong_text')
            if (len(finalResultOdds) > 0):
                finalResultOdds = finalResultOdds[0].find_all('td', class_='align_odds')
                v1Odd = finalResultOdds[0].text
                xOdd = finalResultOdds[1].text
                v2Odd = finalResultOdds[2].text
            else:
                finalResultOdds = oddsDiv.find('div', class_=finalResultMarket).find('table').find_all('td', class_='align_odds')
                v1Odd = finalResultOdds[0].text
                xOdd = finalResultOdds[1].text
                v2Odd = finalResultOdds[2].text

            bttsOdds = oddsDiv.find('div', class_=bttsMarket).find('table').find_all('tr', class_='strong_text')
            if (len(bttsOdds) > 0):
                bttsOdds = bttsOdds[0].find_all('td', class_='align_odds')
                bttsYesOdd = bttsOdds[0].text
                bttsNoOdd = bttsOdds[1].text
            else:
                bttsOdds = oddsDiv.find('div', class_=bttsMarket).find('table').find_all('td', class_='align_odds')
                bttsYesOdd = bttsOdds[0].text
                bttsNoOdd = bttsOdds[1].text

            over25Odds = oddsDiv.find('div', class_=over25Market).find('table').find_all('tr', class_='strong_text')
            if (len(over25Odds) > 0):
                over25Odds = over25Odds[0].find_all('td', class_='align_odds')
                over25 = over25Odds[1].text
                under25 = over25Odds[0].text
            else:
                over25Odds = oddsDiv.find('div', class_=over25Market).find('table').find_all('td', class_='align_odds')
                over25 = over25Odds[1].text
                under25 = over25Odds[0].text

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