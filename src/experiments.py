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

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

def scrappAdAStatsBulk():
    driver = webdriver.Chrome(options=set_chrome_options())
    matches = []
    for i in range(29,32):
        print("########## step: " + str(i))
        matches += getOver25GoalCandidatesFromAdA("https://www.academiadasapostas.com/stats/livescores/2023/05/" + str(i), driver)
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
            numOversh2h = 0

            i=0
            while i<len(h2hMatches):
                h2hMatchResult = h2hMatches[i].text.strip()
                if h2hMatchResult.split('-')[0] != '':
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
            homePosition = soup.find("table", {"class" : "competition-rounds"}).find_all("tr", {"style" : "background-color: #CDDFF0"})[0].find_all('td')[0].text.strip()
            awayPosition = soup.find("table", {"class" : "competition-rounds"}).find_all("tr", {"style" : "background-color: #FFE0A6"})[0].find_all('td')[0].text.strip()

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
            matchStats['21. h2hOverRate'] = round(float(h2hOverRate),2)
            matchStats['22. underOdd'] = (underOdd)
            matchStats['23. overOdd'] = (overOdd)
            matchStats['24. v1Odd'] = (v1Odd)
            matchStats['25. v2Odd'] = (v2Odd)
            matchStats['26. last5HomeMatchesForm'] = str(last5HomeMatchesForm)
            matchStats['27. last5AwayMatchesForm'] = str(last5AwayMatchesForm)
            
        except Exception as e:
            print("An exception has occurred!\n" + str(e))

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
        matchStats = getMatchStatsFromAdA(matchUrl)
        matchDict.update(matchStats)
        matchesToBet.append(matchDict)
        # break
    # driver.close()
    return matchesToBet

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
            matchUrl = "http://www.betexplorer.com" + match.find('a', class_='in-match')['href'] + "#ou"
            # matchUrl = "https://www.betexplorer.com/football/luxembourg/national-division-2021-2022/progres-niedercorn-luxembourg-city/EBSy8Oud/#ou"
            # matchUrl = "https://www.betexplorer.com/football/netherlands/eerste-divisie-2019-2020/jong-ajax-helmond-sport/h2qvuVWk/#ou"
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
            for table in overTables:
                # print(table.text)
                if "2.5" in table.find_elements(By.TAG_NAME, "tr")[1].text.split('\n')[1].split(' ')[0]:
                    over25Odd = table.find_elements(By.TAG_NAME, "td")[5].get_attribute("data-odd").strip()
                if "1.5" in table.find_elements(By.TAG_NAME, "tr")[1].text.split('\n')[1].split(' ')[0]:
                    over15Odd = table.find_elements(By.TAG_NAME, "td")[5].get_attribute("data-odd").strip()
            import datetime
            matchStats['01. date'] = (matchDate)
            matchStats['02. timestamp'] = str(time.mktime(datetime.datetime.strptime(matchDate, "%d.%m.%Y - %H:%M").timetuple()))
            matchStats['03. homeTeam'] = (homeTeam)
            matchStats['04. awayTeam'] = (awayTeam)
            matchStats['05. matchScore'] = (matchScore)
            matchStats['06. homeGoals'] = matchScore.split(':')[0]
            matchStats['07. awayGoals'] = matchScore.split(':')[1]
            matchStats['08. under25Odd'] = (over25Odd).replace('.', ',')
            matchStats['09. under15Odd'] = (over15Odd).replace('.', ',')
           
            matchesToBet.append(matchStats)
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