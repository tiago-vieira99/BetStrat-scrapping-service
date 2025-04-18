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

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

# docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" --platform linux/x86_64 selenium/standalone-chrome:latest
def scrappAdAStatsBulk(month):
    #driver = webdriver.Chrome(options=set_chrome_options())
    driver = webdriver.Remote("http://172.17.0.3:4444", options=webdriver.ChromeOptions())

    matches = []
    for i in range(1,3):
        print("########## step: " + str(i))
        matches += getOver25GoalCandidatesFromAdA("https://www.academiadasapostas.com/stats/livescores/2024/"+ month + "/" + str(i), driver)
        time.sleep(2)
    driver.close()
    return matches

def scrappBTTSAdAStatsBulk():
    driver = webdriver.Chrome(options=set_chrome_options())
    matches = []
    for i in range(1,13):
        print("########## step: " + str(i))
        matches += getBTTSCandidatesFromAdA("https://www.academiadasapostas.com/stats/livescores/2023/05/" + str(i), driver)
        time.sleep(2)
    driver.close()
    return matches

def scrappCornerAdAStatsBulk():
    driver = webdriver.Chrome(options=set_chrome_options())
    matches = []
    for i in range(6,15):
        print("########## step: " + str(i))
        matches += getCornerStrategyCandidatesFromAdA("https://www.academiadasapostas.com/stats/livescores/2023/09/" + str(i), driver)
        time.sleep(2)
    driver.close()
    return matches

def getFirstHalfGoalCandidatesFromAdA(url, driver):
    
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
        time.sleep(1)  
        table = driver.find_element(By.ID, "fh_main_tab")
        moreButton = table.find_elements(By.CLASS_NAME, "footer")

    todayMatches = driver.find_elements(By.CLASS_NAME, "live-subscription")

    for match in todayMatches:
        if len(match.find_elements(By.CLASS_NAME, "gameinlive")) != 0:
            continue

        matchTime = match.find_element(By.CLASS_NAME, "game_running").text
        matchScore = match.find_element(By.CLASS_NAME, "score").text

        matchUrl = match.find_element(By.CLASS_NAME, "score").find_element(By.TAG_NAME, "a").get_attribute("href")
        firstHalfGoals = ''
        allowedLeagues = ["psl", "1st-division", "superliga", "bundesliga", "2-bundesliga", "3-liga", "ligue-1", "girabola", "pro-league", "primera-division", "primera-nacional", "premier-league", "a-league", "1-liga", "premyer-liqa", "first-division-b", "1-division", "premier-liga", "serie-a", "serie-b", "serie-c", "a-pfg", "b-pfg", "canadian-championship", "stars-league", "primera-b", "primera-a", "1-hnl", "2-hnl", "arabian-gulf-league", "liga-pro", "premiership", "championship", "super-liga", "2-liga", "1-snl", "2-snl", "segunda-division", "segunda-b", "mls", "meistriliiga", "esiliiga-a", "veikkausliiga", "ligue-2", "national", "super-league", "football-league", "liga-nacional", "nb-i", "i-league", "liga-1", "persion-gulf-pro-league", "iraqi-league", "urvalsdeild", "ligat-haal", "liga-leumit", "j1-league", "j2-league", "virsliga", "a-lyga", "national-division", "liga-mx", "mocambola", "divizia-nationala", "npfl", "eliteserien", "national-league", "eredivisie", "eerste-divisie", "lpf", "division-profesional", "ekstraklasa", "i-liga", "liga-portugal-bwin", "segunda-liga", "czech-liga", "k-league-1", "k-league-2", "premier-division", "liga-i", "liga-ii", "csl", "super-liga", "allsvenskan", "superettan", "challenge-league", "thai-league-1", "vleague-1", "campeonato-nacional"]

        if matchUrl.split('/')[6] not in allowedLeagues:
            continue

        if matchTime == 'Terminado':
            firstHalfGoals = getFinishedMatchFirstHalfGoalsFromAdA(matchUrl + "/live")
            
        if validateFirstHalfGoalCandidateFromAdA(matchUrl):
            date = match.find_element(By.CLASS_NAME, "hour").get_attribute("timestamp")
            matchesToBet.append(Match(date, match.find_element(By.CLASS_NAME, "team-a").text, match.find_element(By.CLASS_NAME, "team-b").text, firstHalfGoals, '').to_dict())
        # break
    # driver.close()
    return matchesToBet

def validateFirstHalfGoalCandidateFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # print("\ngetting match stats: " + str(url))
        
        tables = soup.find_all('table', 'stat-seqs stat-half-padding')
        homeGoalsTable = tables[2]
        awayGoalsTable = tables[3]

        htScoresTables = tables = soup.find_all('table', 'stat-correctscore')

        # then we can iterate through each row and extract either header or row values:
        header = []
        homeGoalsRows = []
        awayGoalsRows = []
        homeHTscores = []
        awayHTscores = []
        try:
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

            for i, row in enumerate(htScoresTables[0].find_all('tr')):
                if i == 0:
                    header = [el.text.strip() for el in row.find_all('th')]
                else:
                    homeHTscores.append([el.text.strip() for el in row.find_all('td')])

            for i, row in enumerate(htScoresTables[2].find_all('tr')):
                if i == 0:
                    header = [el.text.strip() for el in row.find_all('th')]
                else:
                    awayHTscores.append([el.text.strip() for el in row.find_all('td')])

            homeHTNilRate = 0
            for hht in homeHTscores:
                if '0-0' in hht[0]:
                    homeHTNilRate = hht[1].split('%')[0]

            awayHTNilRate = 0
            for aht in awayHTscores:
                if '0-0' in aht[0]:
                    awayHTNilRate = aht[1].split('%')[0]

            homeOverRate = homeGoalsRows[5][1].replace('%', '')
            awayOverRate = awayGoalsRows[5][2].replace('%', '')
            homeGoalsAvg = homeGoalsRows[2][1]
            awayGoalsAvg = awayGoalsRows[2][2]

            regex = re.compile('stat-.*')
            h2hMatches = soup.find(id='show_h2h').find_all("td", {"class" : regex})
            numOversh2h = 0

            i=0
            while i<len(h2hMatches):
                h2hMatchResult = h2hMatches[i].text.strip()
                if h2hMatchResult.split('-')[0] != '':
                    if int(h2hMatchResult.split('-')[0]) + int(h2hMatchResult.split('-')[1]) > 2:
                        numOversh2h += 1
                i+=1

            # print('Scrapped stats: homeOverRate: '+ str(homeOverRate) + '; awayOverRate: ' + str(awayOverRate) + '; homeGoalsAvg: ' + str(homeGoalsAvg) + '; awayGoalsAvg: ' + str(awayGoalsAvg) + '; numOverh2h: ' + str(numOversh2h))

            h2hOverRate = 0
            if numOversh2h > 0:
                h2hOverRate = 100*numOversh2h/len(h2hMatches)

            if ((float(homeOverRate) + float(awayOverRate))/2 >= 60) and ((float(homeGoalsAvg)+float(awayGoalsAvg))/2 >= 3) and float(h2hOverRate) >= 50 and int(homeHTNilRate) < 30 and int(awayHTNilRate) < 30:
                return True
            else:
                return False
        except Exception as error:
            print("An error occurred:", error)
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    
def getFinishedMatchFirstHalfGoalsFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # print(url)

        table = soup.find(id='first-half-summary')
        
        return table.find_all('td', 'ht-score')[0].text.strip()        
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getFirstGoalMinuteFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all 'tr' rows that contain a goal event
        goal_event = soup.find('span', title="Goal")

        # Initialize variable for the first goal minute
        first_goal_minute = None

        # Navigate to the parent 'tr'
        parent_tr = goal_event.find_parent('tr')

        # Find the 'td' element that contains the minute (ignore empty ones)
        goal_minute_tds = parent_tr.find_all('td', class_='match-sum-wd-minute')

        # Loop through the goal events and find the first valid minute
        for goal in goal_minute_tds:
            print(goal.text.strip())
            if "'" in goal.text.strip():  # Ensure it's not empty
                first_goal_minute = goal.text.strip().replace("'", "")  # Remove the apostrophe
                break
            
        return first_goal_minute
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    

################## test Over 1.5 strategy #######################
# +1.5 Goals % by Both Teams played Overall is between 75 and 100
# Total Goals (AVG) by Both Teams played Overall is between 2 and 15
# Total Goals (AVG) by Away Team played Away is between 2 and 15
# +2.5 Goals % by Both Teams played Overall is between 50 and 100
# So if we get that strategy and see how it would have performed in last 6 months:
# 🎯 Over 1.5 Total Goals (21277/24982) 85.17%
# 🎯 Summary
# 85.17% Won desired outcome
# 14.83% Lost desired outcome
# 1.19 Average odds for the outcome

def getMatchStatsFromAdA(url):
    response = requests.get(url)
    matchStats = OrderedDict()
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("\ngetting match stats: " + str(url))
        
        tables = soup.find_all('table', 'stat-seqs stat-half-padding')
        homeGoalsTable = tables[2]
        awayGoalsTable = tables[3]

        # then we can iterate through each row and extract either header or row values:
        header = []
        homeGoalsRows = []
        awayGoalsRows = []
        try:
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


            homeOverRate = '0' + homeGoalsRows[5][1][:-1]
            awayOverRate = '0' + awayGoalsRows[5][2][:-1]
            homeGoalsAvg = homeGoalsRows[2][1]
            awayGoalsAvg = awayGoalsRows[2][2]
            homeCleanSheetsRate = '0' + homeGoalsRows[3][1][:-1]
            awayCleanSheetsRate = '0' + awayGoalsRows[3][2][:-1]
            homeNoGoalsRate = '0' + homeGoalsRows[4][1][:-1]
            awayNoGoalsRate = '0' + awayGoalsRows[4][2][:-1]

            regex = re.compile('stat-.*')
            h2hMatches = soup.find(id='show_h2h').find_all("td", {"class" : regex})
            h2hTotalGoals = 0
            numOversh2h = 0

            i=0
            while i<len(h2hMatches):
                h2hMatchResult = h2hMatches[i].text.strip()
                if h2hMatchResult.split('-')[0] != '':
                    h2hTotalGoals += int(h2hMatchResult.split('-')[0]) + int(h2hMatchResult.split('-')[1][0])
                    if int(h2hMatchResult.split('-')[0]) + int(h2hMatchResult.split('-')[1][0]) > 2:
                        numOversh2h += 1
                i+=1

            if len(h2hMatches) > 0:
                h2hOverRate = 100*numOversh2h/len(h2hMatches)
            else:
                h2hOverRate = 0

            last3HomeMatchesTotalGoals = 0
            last3AwayMatchesTotalGoals = 0
            lastMatchesTables = soup.find(id='ultimos_resultados').find_all("td", {"class" : regex})

            if len(lastMatchesTables) > 18:
                last3HomeMatches = lastMatchesTables[0:6]
                last3AwayMatches = lastMatchesTables[12:18]
            
                j = 0
                for i in range(0,3):
                    if (len(last3HomeMatches[j].text.strip()) < 3 or len(last3AwayMatches[j].text.strip()) < 3):
                        j+=1
                    last3HomeMatchesTotalGoals += int(last3HomeMatches[j].text.strip().split('-')[0]) + int(last3HomeMatches[j].text.strip().split('-')[1][0])
                    last3AwayMatchesTotalGoals += int(last3AwayMatches[j].text.strip().split('-')[0]) + int(last3AwayMatches[j].text.strip().split('-')[1][0])
                    j+=1

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
            v2Odd = 0
            if len(odds) > 0:
                v1Odd = v1Odds[0].find_all("td")[1].text.strip()
                v2Odd = v1Odds[0].find_all("td")[3].text.strip()

            #teams league position

            if soup.find("table", {"class" : "competition-rounds"}).find_all("tr", {"style" : "background-color: #CDDFF0"}):
                homePosition = soup.find("table", {"class" : "competition-rounds"}).find_all("tr", {"style" : "background-color: #CDDFF0"})[0].find_all('td')[0].text.strip()
                awayPosition = soup.find("table", {"class" : "competition-rounds"}).find_all("tr", {"style" : "background-color: #FFE0A6"})[0].find_all('td')[0].text.strip()
            else:
                homePosition = ''
                awayPosition = ''

            #last 5 matches form
            last5HomeMatchesForm = []
            last5AwayMatchesForm = []
            if len(lastMatchesTables) > 21:
                last5HomeMatches = lastMatchesTables[0:9]
                last5AwayMatches = lastMatchesTables[12:21]
                for i in range(0,5):
                    if 'win' in str(last5HomeMatches[i]):
                        last5HomeMatchesForm.append('W')
                    if 'draw' in str(last5HomeMatches[i]):
                        last5HomeMatchesForm.append('D')
                    if 'lose' in str(last5HomeMatches[i]):
                        last5HomeMatchesForm.append('L')
                    if 'win' in str(last5AwayMatches[i]):
                        last5AwayMatchesForm.append('W')
                    if 'draw' in str(last5AwayMatches[i]):
                        last5AwayMatchesForm.append('D')
                    if 'lose' in str(last5AwayMatches[i]):
                        last5AwayMatchesForm.append('L')
            
            matchStats['09. homePosition'] = (homePosition)
            matchStats['10. awayPosition'] = (awayPosition)
            matchStats['11. homeOverRate'] = (homeOverRate)
            matchStats['12. awayOverRate'] = (awayOverRate)
            matchStats['13. homeGoalsAvg'] = (homeGoalsAvg)
            matchStats['14. awayGoalsAvg'] = (awayGoalsAvg)
            matchStats['15. homeCleanSheetsRate'] = (homeCleanSheetsRate)
            matchStats['16. awayCleanSheetsRate'] = (awayCleanSheetsRate)
            matchStats['17. homeNoGoalsRate'] = (homeNoGoalsRate)
            matchStats['18. awayNoGoalsRate'] = (awayNoGoalsRate)
            matchStats['19. last3HomeMatchesTotalGoals'] = last3HomeMatchesTotalGoals
            matchStats['20. last3AwayMatchesTotalGoals'] = last3AwayMatchesTotalGoals
            matchStats['211. h2hmatches'] = (h2hMatches)
            matchStats['212. h2hgoals'] = (h2hTotalGoals)
            matchStats['22. underOdd'] = (underOdd)
            matchStats['23. overOdd'] = (overOdd)
            matchStats['24. v1Odd'] = (v1Odd)
            matchStats['25. v2Odd'] = (v2Odd)
            matchStats['26. last5HomeMatchesForm'] = str(last5HomeMatchesForm)
            matchStats['27. last5AwayMatchesForm'] = str(last5AwayMatchesForm)
            matchStats['28. first goal minute'] = getFirstGoalMinuteFromAdA(url + '/live')
            
        except Exception as e:
            print("An exception has occurred: \t\t" + str(e))
            print(traceback.format_exc()) 

    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    
    return matchStats

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

    for match in todayMatches:
        if 'Cancelado' in match.find_element(By.CLASS_NAME, "status").text:
            continue

        matchUrl = match.find_element(By.CLASS_NAME, "score").find_element(By.TAG_NAME, "a").get_attribute("href")
        #allowedLeagues = ["psl", "1st-division", "superliga", "bundesliga", "2-bundesliga", "3-liga", "ligue-1", "girabola", "pro-league", "primera-division", "primera-nacional", "premier-league", "a-league", "1-liga", "premyer-liqa", "first-division-b", "1-division", "premier-liga", "serie-a", "serie-b", "serie-c", "a-pfg", "b-pfg", "canadian-championship", "stars-league", "primera-b", "primera-a", "1-hnl", "2-hnl", "arabian-gulf-league", "liga-pro", "premiership", "championship", "super-liga", "2-liga", "1-snl", "2-snl", "segunda-division", "segunda-b", "mls", "meistriliiga", "esiliiga-a", "veikkausliiga", "ligue-2", "national", "super-league", "football-league", "liga-nacional", "nb-i", "i-league", "liga-1", "persion-gulf-pro-league", "iraqi-league", "urvalsdeild", "ligat-haal", "liga-leumit", "j1-league", "j2-league", "virsliga", "a-lyga", "national-division", "liga-mx", "mocambola", "divizia-nationala", "npfl", "eliteserien", "national-league", "eredivisie", "eerste-divisie", "lpf", "division-profesional", "ekstraklasa", "i-liga", "liga-portugal-bwin", "liga-portugal-betclic", "segunda-liga", "czech-liga", "k-league-1", "k-league-2", "premier-division", "liga-i", "liga-ii", "csl", "super-liga", "allsvenskan", "superettan", "challenge-league", "thai-league-1", "vleague-1", "campeonato-nacional"]

        # allowedLeagues = ["psl", "superliga", "cup", "bundesliga", "dfb-pokal", "2-bundesliga", "ligue-1", "girabola", "pro-league", "primera-division", "copa-argentina",
        #  "primera-nacional", "premier-league", "a-league", "1-liga", "premyer-liqa", "pro-league", "first-division-b", "1-division", "premier-liga", "serie-a", "serie-b", 
        #  "a-pfg", "b-pfg", "canadian-championship", "stars-league", "primera-b", "primera-a", "1-hnl", "2-hnl", "arabian-gulf-league", "liga-pro", "premiership", "championship", 
        #  "super-liga", "2-liga", "1-snl", "2-snl", "segunda-division", "copa-del-rey", "mls", "meistriliiga", "esiliiga-a", "veikkausliiga", "ligue-2", "super-league", "football-league", 
        #  "liga-nacional", "nb-i", "i-league", "liga-1", "persion-gulf-pro-league", "iraqi-league", "urvalsdeild", "ligat-haal", "liga-leumit", "coppa-italia", "fa-cup", "j1-league", "j2-league", 
        #  "virsliga", "a-lyga", "national-division", "liga-mx", "copa-mx" "mocambola", "divizia-nationala", "npfl", "eliteserien", "national-league", "eredivisie", "eerste-divisie", 
        #  "lpf", "division-profesional", "ekstraklasa", "i-liga", "liga-portugal-bwin", "liga-portugal-betclic", "segunda-liga", "czech-liga", "k-league-1", "k-league-2", "premier-division", 
        #  "liga-i", "liga-ii", "csl", "super-liga", "allsvenskan", "superettan", "challenge-league", "thai-league-1", "vleague-1", "knvb-beker", "taca-de-portugal", "taca-da-liga", 
        #   "conmebol-libertadores", "caf-champions-league", "concacaf-champions-league", "afc-champions-league", "uefa-champions-league", "uefa-europa-league", "europa-conference-league"]

        # if matchUrl.split('/')[6] not in allowedLeagues:
        #     continue

        matchDict = OrderedDict()
        homeTeam = match.find_element(By.CLASS_NAME, "team-a").text
        awayTeam = match.find_element(By.CLASS_NAME, "team-b").text
        matchScore = match.find_element(By.CLASS_NAME, "score").text
        if len(matchScore) < 4:
            homeScore = '-'
            awayScore = '-'
            totalGoals = '-'
        else:
            homeScore = matchScore[0:6].split('-')[0].strip()
            awayScore = matchScore[0:6].split('-')[1].strip()
            totalGoals = int(homeScore) + int(awayScore)

        date = match.find_element(By.CLASS_NAME, "hour").get_attribute("timestamp")

        matchDict['01. date'] = str(datetime.fromtimestamp(int(date)))
        matchDict['02. timestamp'] = (date)
        matchDict['03. homeTeam'] = homeTeam
        matchDict['04. awayTeam'] = awayTeam
        matchDict['05. matchScore'] = matchScore
        matchDict['06. totalGoals'] = totalGoals
        matchDict['07. homeScore'] = homeScore
        matchDict['08. awayScore'] = awayScore
        matchStats = getMatchStatsFromAdA(matchUrl)
        matchDict.update(matchStats)
        matchesToBet.append(matchDict)
        break
    # driver.close()
    return matchesToBet

def getBTTSCandidatesFromAdA(url, driver):
    
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

    try:
        for match in todayMatches:
            if 'Cancelado' in match.find_element(By.CLASS_NAME, "status").text:
                continue

            matchUrl = match.find_element(By.CLASS_NAME, "score").find_element(By.TAG_NAME, "a").get_attribute("href")
            allowedLeagues = ["psl", "1st-division", "superliga", "bundesliga", "2-bundesliga", "3-liga", "ligue-1", "girabola", "pro-league", "primera-division", "primera-nacional", "premier-league", "a-league", "1-liga", "premyer-liqa", "first-division-b", "1-division", "premier-liga", "serie-a", "serie-b", "serie-c", "a-pfg", "b-pfg", "canadian-championship", "stars-league", "primera-b", "primera-a", "1-hnl", "2-hnl", "arabian-gulf-league", "liga-pro", "premiership", "championship", "super-liga", "2-liga", "1-snl", "2-snl", "segunda-division", "segunda-b", "mls", "meistriliiga", "esiliiga-a", "veikkausliiga", "ligue-2", "national", "super-league", "football-league", "liga-nacional", "nb-i", "i-league", "liga-1", "persion-gulf-pro-league", "iraqi-league", "urvalsdeild", "ligat-haal", "liga-leumit", "j1-league", "j2-league", "virsliga", "a-lyga", "national-division", "liga-mx", "mocambola", "divizia-nationala", "npfl", "eliteserien", "national-league", "eredivisie", "eerste-divisie", "lpf", "division-profesional", "ekstraklasa", "i-liga", "liga-portugal-bwin", "segunda-liga", "czech-liga", "k-league-1", "k-league-2", "premier-division", "liga-i", "liga-ii", "csl", "super-liga", "allsvenskan", "superettan", "challenge-league", "thai-league-1", "vleague-1", "campeonato-nacional"]

            if matchUrl.split('/')[6] not in allowedLeagues:
                continue

            matchDict = OrderedDict()
            homeTeam = match.find_element(By.CLASS_NAME, "team-a").text
            awayTeam = match.find_element(By.CLASS_NAME, "team-b").text
            matchScore = match.find_element(By.CLASS_NAME, "score").text
            if len(matchScore) < 4:
                homeScore = '-'
                awayScore = '-'
                totalGoals = '-'
            else:
                homeScore = matchScore[0:6].split('-')[0].strip()
                awayScore = matchScore[0:6].split('-')[1].strip()
                totalGoals = int(homeScore) + int(awayScore)

            date = match.find_element(By.CLASS_NAME, "hour").get_attribute("timestamp")

            matchDict['01. date'] = str(datetime.fromtimestamp(int(date)))
            matchDict['02. timestamp'] = (date)
            matchDict['03. homeTeam'] = homeTeam
            matchDict['04. awayTeam'] = awayTeam
            matchDict['05. matchScore'] = matchScore
            matchDict['06. totalGoals'] = totalGoals
            matchDict['07. homeScore'] = homeScore
            matchDict['08. awayScore'] = awayScore
            matchDict['09. competition'] = matchUrl.split('/')[6]
            matchStats = getBTTSMatchStatsFromAdA(matchUrl, matchUrl.split('/')[6])
            matchDict.update(matchStats)
            matchesToBet.append(matchDict)
            break
    except Exception as e:
            print("An exception has occurred!\n" + str(e))
    # driver.close()
    return matchesToBet

def getBTTSMatchStatsFromAdA(url, competition):
    response = requests.get(url)
    matchStats = OrderedDict()
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("\ngetting match stats: " + str(url))
        
        try:
            regex = re.compile('stat-.*')
            h2hMatches = soup.find(id='show_h2h').find_all("td", {"class" : regex})
            numBttsh2h = 0

            i=0
            while i<len(h2hMatches):
                h2hMatchResult = h2hMatches[i].text.strip()
                if h2hMatchResult.split('-')[0] != '':
                    if int(h2hMatchResult.split('-')[0]) > 0 and int(h2hMatchResult.split('-')[1][0]) > 0:
                        numBttsh2h += 1
                i+=1

            h2hBttsRate = 0
            if len(h2hMatches) > 0:
                h2hBttsRate = 100*numBttsh2h/len(h2hMatches)
            else:
                h2hBttsRate = 0

            #teams league position
            homePosition = soup.find("table", {"class" : "competition-rounds"}).find_all("tr", {"style" : "background-color: #CDDFF0"})[0].find_all('td')[0].text.strip()
            awayPosition = soup.find("table", {"class" : "competition-rounds"}).find_all("tr", {"style" : "background-color: #FFE0A6"})[0].find_all('td')[0].text.strip()

            #find last league game for home and away team
            lastHomeTeamMatchResult = ''
            lastAwayTeamMatchResult = ''
            lastMatchesTables = soup.find(id='ultimos_resultados').find_all("td", {"class" : regex})
            urlHomeTeam = url.split('/')[7]
            urlAwayTeam = url.split('/')[8]
        
            #analyse last 6 matches of each team
            lastHomeResults = {}
            lastAwayResults = {}
            if len(lastMatchesTables) > 18:
                lastHomeMatches = lastMatchesTables[0:10]
                lastAwayMatches = lastMatchesTables[12:22]
                
                for i in range(0,len(lastHomeMatches)):
                    if competition in lastHomeMatches[i].find('a')['href']:
                        if urlHomeTeam == lastHomeMatches[i].find('a')['href'].split('/')[7]:
                            lastHomeResults[str(i) + 'home'] = (lastHomeMatches[i].text.strip())
                        else:
                            lastHomeResults[str(i) + 'away'] = (lastHomeMatches[i].text.strip().split('-')[1] + '-' + lastHomeMatches[i].text.strip().split('-')[0])
                
                for i in range(0,len(lastAwayMatches)):
                    if competition in lastAwayMatches[i].find('a')['href']:
                        if urlAwayTeam == lastAwayMatches[i].find('a')['href'].split('/')[7]:
                            lastAwayResults[str(i) + 'home'] = (lastAwayMatches[i].text.strip())
                        else:
                            lastAwayResults[str(i) + 'away'] = (lastAwayMatches[i].text.strip().split('-')[1] + '-' + lastAwayMatches[i].text.strip().split('-')[0])

            else:
                return None

            totalPoints = 0
            #calculate points
            if len(lastHomeResults) >= 6 and len(lastAwayResults) >= 6: 
                for i in range(0,(len(lastHomeResults)-6)):
                    lastHomeResults.popitem()

                for i in range(0,(len(lastAwayResults)-6)):
                    lastAwayResults.popitem()

                homeTeamPoints = 0 
                awayTeamPoints = 0
                #homeTeamPoints
                for key, value in lastHomeResults.items():
                    homeScore = value.split('-')[0]
                    awayScore = value.split('-')[1]
                    
                    if int(homeScore) == 0 and int(awayScore) == 0:
                        homeTeamPoints -= 2

                    if int(homeScore) > 0 and int(awayScore) > 0:
                        homeTeamPoints += 1
                    
                    if int(homeScore) > 0 and int(awayScore) > 0 and 'home' in key:
                        homeTeamPoints += 1

                    if int(homeScore) > 2:
                        homeTeamPoints += (int(homeScore)-2) * 0.5
                    
                    if int(awayScore) > 2:
                        homeTeamPoints += (int(awayScore)-2) * 0.5

                #awayTeamPoints
                for key, value in lastAwayResults.items():
                    homeScore = value.split('-')[0]
                    awayScore = value.split('-')[1]
                    
                    if int(homeScore) == 0 and int(awayScore) == 0:
                        awayTeamPoints -= 2

                    if int(homeScore) > 0 and int(awayScore) > 0:
                        awayTeamPoints += 1
                    
                    if int(homeScore) > 0 and int(awayScore) > 0 and 'away' in key:
                        awayTeamPoints += 1

                    if int(homeScore) > 2:
                        awayTeamPoints += (int(homeScore)-2) * 0.5
                    
                    if int(awayScore) > 2:
                        awayTeamPoints += (int(awayScore)-2) * 0.5
                
                totalPoints = homeTeamPoints + awayTeamPoints

            print(totalPoints)
            matchStats['11. homePosition'] = (homePosition)
            matchStats['12. awayPosition'] = (awayPosition)

            matchStats['13. BTTS h2h rate'] = h2hBttsRate

            matchStats['14. BTTS points'] = totalPoints
            
            #home win odds
            v1Odds = soup.find_all('table', 'odds_MO')
            v1Odd = 0
            v2Odd = 0
            if len(v1Odds) > 0:
                v1Odd = float(v1Odds[0].find_all("td")[1].text.strip())
                v2Odd = float(v1Odds[0].find_all("td")[3].text.strip())
            matchStats['15. v1Odd'] = (v1Odd)
            matchStats['16. v2Odd'] = (v2Odd)
            
            #btts odd
            response = requests.get(url + '/odds')
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                bttsOdds = soup.find('div', {"class" : "odds_graph_20"}).find('tr', {"class" : "strong_text light"}).find_all('td', {"class" : "align_odds"})[0].text.strip()
                matchStats['17. bttsOdds'] = (bttsOdds)
            
        except Exception as e:
            print("An exception has occurred!\n" + str(e))

    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    
    return matchStats

def getCornerStrategyCandidatesFromAdA(url, driver):
    
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

    for match in todayMatches:
        if 'Cancelado' in match.find_element(By.CLASS_NAME, "status").text:
            continue

        matchUrl = match.find_element(By.CLASS_NAME, "score").find_element(By.TAG_NAME, "a").get_attribute("href")
        # allowedLeagues = ["psl", "1st-division", "superliga", "bundesliga", "2-bundesliga", "3-liga", "ligue-1", "girabola", "pro-league", "primera-division", "primera-nacional", "premier-league", "a-league", "1-liga", "premyer-liqa", "first-division-b", "1-division", "premier-liga", "serie-a", "serie-b", "serie-c", "a-pfg", "b-pfg", "canadian-championship", "stars-league", "primera-b", "primera-a", "1-hnl", "2-hnl", "arabian-gulf-league", "liga-pro", "premiership", "championship", "super-liga", "2-liga", "1-snl", "2-snl", "segunda-division", "segunda-b", "mls", "meistriliiga", "esiliiga-a", "veikkausliiga", "ligue-2", "national", "super-league", "football-league", "liga-nacional", "nb-i", "i-league", "liga-1", "persion-gulf-pro-league", "iraqi-league", "urvalsdeild", "ligat-haal", "liga-leumit", "j1-league", "j2-league", "virsliga", "a-lyga", "national-division", "liga-mx", "mocambola", "divizia-nationala", "npfl", "eliteserien", "national-league", "eredivisie", "eerste-divisie", "lpf", "division-profesional", "ekstraklasa", "i-liga", "liga-portugal-bwin", "segunda-liga", "czech-liga", "k-league-1", "k-league-2", "premier-division", "liga-i", "liga-ii", "csl", "super-liga", "allsvenskan", "superettan", "challenge-league", "thai-league-1", "vleague-1", "campeonato-nacional"]

        # if matchUrl.split('/')[6] not in allowedLeagues:
        #     continue

        matchDict = OrderedDict()
        homeTeam = match.find_element(By.CLASS_NAME, "team-a").text
        awayTeam = match.find_element(By.CLASS_NAME, "team-b").text
        matchScore = match.find_element(By.CLASS_NAME, "score").text
        if len(matchScore) < 4:
            homeScore = '-'
            awayScore = '-'
            totalGoals = '-'
        else:
            homeScore = matchScore[0:6].split('-')[0].strip()
            awayScore = matchScore[0:6].split('-')[1].strip()
            totalGoals = int(homeScore) + int(awayScore)

        date = match.find_element(By.CLASS_NAME, "hour").get_attribute("timestamp")

        matchDict['01. date'] = str(datetime.fromtimestamp(int(date)))
        matchDict['02. timestamp'] = (date)
        matchDict['03. homeTeam'] = homeTeam
        matchDict['04. awayTeam'] = awayTeam
        matchDict['05. matchScore'] = matchScore
        matchDict['06. totalGoals'] = totalGoals
        matchDict['07. homeScore'] = homeScore
        matchDict['08. awayScore'] = awayScore
        matchDict['09. competition'] = matchUrl.split('/')[5] + ' - ' + matchUrl.split('/')[6]
        matchStats = getCornersMatchStatsFromAdA(matchUrl)
        matchDict.update(matchStats)
        matchesToBet.append(matchDict)
        # break
    # driver.close()
    return matchesToBet


def getCornersMatchStatsFromAdA(url):
    response = requests.get(url)
    matchStats = OrderedDict()
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("\ngetting match stats: " + str(url))
        
        try:
            #home win odds
            v1Odds = soup.find_all('table', 'odds_MO')
            v1Odd = 0
            v2Odd = 0
            if len(v1Odds) > 0:
                v1Odd = float(v1Odds[0].find_all("td")[1].text.strip())
                v2Odd = float(v1Odds[0].find_all("td")[3].text.strip())
            matchStats['10. v1Odd'] = (v1Odd)
            matchStats['11. v2Odd'] = (v2Odd)
                        
            if (v1Odd > 0 and v2Odd > 0) and (v1Odd <= 1.3 or v2Odd <= 1.3):
                response = requests.get(url + '/live')
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    cornerStats = soup.find_all('table', {"class" : "match_stats_center"})[0].find('tr', {"class" : "corners"})
                    homeCorners = int(cornerStats.find('td', {"class" : "stat_value_number_team_A"}).text.strip())
                    awayCorners = int(cornerStats.find('td', {"class" : "stat_value_number_team_B"}).text.strip())
                    if homeCorners != None and awayCorners != None:
                        matchStats['12. isApt'] = True
                    else:
                        matchStats['12. isApt'] = False

                    matchStats['13. homeCorners'] = homeCorners
                    matchStats['14. awayCorners'] = awayCorners

                    if homeCorners >= 7 and awayCorners >= 7:
                        matchStats['15. result'] = "check"
                        return matchStats

                    if (v1Odd > v2Odd and homeCorners < awayCorners and awayCorners >= 7 and homeCorners < 7) or (v1Odd < v2Odd and homeCorners > awayCorners and homeCorners >= 7 and awayCorners < 7):
                        matchStats['15. result'] = "GREEN"
                    else:
                        matchStats['15. result'] = "red"
            
            
        except Exception as e:
            print("An exception has occurred!\n" + str(e))

    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    
    return matchStats

def getMatchStatsFromBetExplorer(url):
    response = requests.get(url)
    matchesToBet = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        driver = webdriver.Chrome(options=set_chrome_options())
        matchesList = soup.find_all("table", {"class" : "table-main"})[0].find_all("td", {"class" : "h-text-left"})

        for match in matchesList:
            matchStats = OrderedDict()
            homeTeam = match.text.strip().split('-')[0].strip()
            awayTeam = match.text.strip().split('-')[1].strip()
            matchUrl = "http://www.betexplorer.com" + match.find('a', class_='in-match')['href'] + "#bts"
            # matchUrl = "https://www.betexplorer.com/football/albania/superliga-2022-2023/vllaznia-teuta/pYZh6WOS/#bts"
            print(matchUrl)
            driver.get(matchUrl)
            #delete the cookies  
            driver.delete_all_cookies()
            time.sleep(1)  
            matchDate = driver.find_element(By.ID, "match-date").text.strip()
            if len(driver.find_elements(By.ID, "js-score")) < 1:
                continue
            matchScore = driver.find_element(By.ID, "js-score").text.strip()
            overTables = driver.find_elements(By.CLASS_NAME, "sortable")
            over25Odd = ""
            over15Odd = ""
            bttsOdd = ""
            if len(overTables) > 0:
                bttsOdd = overTables[0].find_elements(By.TAG_NAME, "td")[3].get_attribute("data-odd").strip()
            # for table in overTables:
            #     # print(table.text)
            #     if "2.5" in table.find_elements(By.TAG_NAME, "tr")[1].text.split('\n')[1].split(' ')[0]:
            #         over25Odd = table.find_elements(By.TAG_NAME, "td")[5].get_attribute("data-odd").strip()
            #     if "1.5" in table.find_elements(By.TAG_NAME, "tr")[1].text.split('\n')[1].split(' ')[0]:
            #         over15Odd = table.find_elements(By.TAG_NAME, "td")[5].get_attribute("data-odd").strip()
            import datetime
            try:
                matchStats['01. date'] = (matchDate)
                matchStats['02. timestamp'] = str(time.mktime(datetime.datetime.strptime(matchDate, "%d.%m.%Y - %H:%M").timetuple()))
                matchStats['03. homeTeam'] = (homeTeam)
                matchStats['04. awayTeam'] = (awayTeam)
                matchStats['05. matchScore'] = (matchScore)
                matchStats['06. homeGoals'] = matchScore.split(':')[0]
                matchStats['07. awayGoals'] = matchScore.split(':')[1]
                matchStats['08. bttsOdd'] = (bttsOdd).replace('.', ',')
                # matchStats['08. under25Odd'] = (over25Odd).replace('.', ',')
                # matchStats['09. under15Odd'] = (over15Odd).replace('.', ',')
            
                matchesToBet.append(matchStats)
            except Exception as e:
                print("The error is: ",e)
            # break

        driver.close()
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

    return matchesToBet

def getLeagueOverStatsFromBetExplorer(body):
    seasons = ["2022-2023", "2021-2022", "2020-2021", "2019-2020", "2018-2019", "2017-2018"]
    returnObj = []
    for url in body.decode("utf-8").split('\r\n'):
        overStats = {}
        for s in seasons:
            print(url[0:url.rfind("/")]+"-"+s+"/stats/")
            try:
                response = requests.get(url[0:url.rfind("/")]+"-"+s+"/stats/")
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if len(soup.find_all('li', string='Main')) > 0:
                        stage = soup.find_all('li', string='Main')[0].find('a')['href']
                        response = requests.get(url[0:url.rfind("/")]+"-"+s+"/stats/"+stage)
                        soup = BeautifulSoup(response.content, 'html.parser')
                    
                    over25Stat = soup.find_all('table', 'leaguestats')[0].find_all('tr')[-2:][0].find_all('td')[2].text.strip()
                    overStats[s] = over25Stat
                    overStats["00 country"] = str(url).split('/')[4]
                    overStats["01 league"] = str(url).split('/')[5]
                    # time.sleep(1)
                else:
                    raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
            except Exception as error:
                print("An error occurred:", error)
        returnObj.append(overStats)

    return returnObj

#TODO
# Tatuki system