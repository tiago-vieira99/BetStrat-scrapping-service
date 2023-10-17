from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import scrapping
from obj.match import Match

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

def getLiveResultsFromAdA():
    driver = webdriver.Chrome(options=set_chrome_options())
    driver.get("http://www.academiadasapostas.com/stats/livescores/")
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

    liveMatches = driver.find_elements(By.CLASS_NAME, "live-subscription")

    matchesToBet = []

    for match in liveMatches:
        if len(match.find_elements(By.CLASS_NAME, "gameinlive")) == 0:
            continue

        matchTime = match.find_element(By.CLASS_NAME, "game_running").text
        matchScore = match.find_element(By.CLASS_NAME, "score").text

        if (matchScore == '0 - 0') and ((matchTime == 'Intervalo') or (int(matchTime) > 39 and int(matchTime) < 61)):
            matchUrl = match.find_elements(By.CLASS_NAME, "gameinlive")[1].find_element(By.TAG_NAME, "a").get_attribute("href")
            if scrapping.getLiveMatchStatsFromAdA(matchUrl):
                matchesToBet.append(Match('', match.find_element(By.CLASS_NAME, "team-a").text, match.find_element(By.CLASS_NAME, "team-b").text, '', '').to_dict())

    driver.close()
    return matchesToBet

def getLeagueNextMatchFromAdA(url):
    print("\ngetting next match: " + str(url))
    driver = webdriver.Chrome(options=set_chrome_options())
    driver.get(url.decode("utf-8"))
    #delete the cookies  
    driver.delete_all_cookies()
    leagueButton = driver.find_elements(By.CLASS_NAME, "competition")[1]

    print(leagueButton.text)

    # actions = ActionChains(driver)
    # actions.move_to_element(moreButton[0])
    # actions.click(moreButton[0])
    # actions.perform()
    # time.sleep(1)  

def getLateGoalsMatchesCandidatesFromAdA():
    driver = webdriver.Chrome(options=set_chrome_options())
    matchesToBet = []
    driver.get("http://www.academiadasapostas.com/stats/livescores/2023/10/07")
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

    # driver.close()

    for match in todayMatches:
        if len(match.find_elements(By.CLASS_NAME, "gameinlive")) != 0:
            continue

        matchTime = match.find_element(By.CLASS_NAME, "game_running").text
        matchScore = match.find_element(By.CLASS_NAME, "score").text

        matchUrl = match.find_element(By.CLASS_NAME, "score").find_element(By.TAG_NAME, "a").get_attribute("href")
        firstHalfGoals = ''
        allowedLeagues = ["psl", "1st-division", "superliga", "bundesliga", "2-bundesliga", "3-liga", "ligue-1", "girabola", "pro-league", "primera-division", "primera-nacional", "premier-league", "a-league", "1-liga", "premyer-liqa", "first-division-b", "1-division", "premier-liga", "serie-a", "serie-b", "serie-c", "a-pfg", "b-pfg", "canadian-championship", "stars-league", "primera-b", "primera-a", "1-hnl", "2-hnl", "arabian-gulf-league", "liga-pro", "premiership", "championship", "super-liga", "2-liga", "1-snl", "2-snl", "segunda-division", "segunda-b", "mls", "meistriliiga", "esiliiga-a", "veikkausliiga", "ligue-2", "national", "super-league", "football-league", "liga-nacional", "nb-i", "i-league", "liga-1", "persion-gulf-pro-league", "iraqi-league", "urvalsdeild", "ligat-haal", "liga-leumit", "j1-league", "j2-league", "virsliga", "a-lyga", "national-division", "liga-mx", "mocambola", "divizia-nationala", "npfl", "eliteserien", "national-league", "eredivisie", "eerste-divisie", "lpf", "division-profesional", "ekstraklasa", "i-liga", "liga-portugal-bwin", "segunda-liga", "czech-liga", "k-league-1", "k-league-2", "premier-division", "liga-i", "liga-ii", "csl", "super-liga", "allsvenskan", "superettan", "challenge-league", "thai-league-1", "vleague-1", "campeonato-nacional"]

        # if matchUrl.split('/')[6] not in allowedLeagues:
        #     continue

        if matchTime == 'Terminado':
            continue
        
        try:
            score = getLateGoalsMatchFromAdA(matchUrl)
            date = match.find_element(By.CLASS_NAME, "hour").get_attribute("timestamp")
            matchesToBet.append(Match(date, match.find_element(By.CLASS_NAME, "team-a").text, match.find_element(By.CLASS_NAME, "team-b").text, score, '').to_dict())
        except Exception as e:
            print("An exception has occurred: " + repr(e))
        # break
    # driver.close()
    return matchesToBet

def getLateGoalsMatchFromAdA(url):
    print("\ngetting next match: " + str(url))
    driver = webdriver.Chrome(options=set_chrome_options())
    driver.get(url)
    #delete the cookies  
    driver.delete_all_cookies()  

    button = driver.find_elements(By.CLASS_NAME, "marketselector")[5]

    # button = driver.find_elements(By.CSS_SELECTOR, '[data-id="last_10g"]')[1]

    actions = ActionChains(driver)
    actions.move_to_element(button)
    time.sleep(1.5)
    actions.click(button)
    actions.perform()
    time.sleep(3)  

    goalsTableIdx = 0
    if(len(driver.find_elements(By.CLASS_NAME, "stat-quarts-padding")) > 6):
        goalsTableIdx = 2 
    
    homeGoalsTables = driver.find_elements(By.CLASS_NAME, "stat-quarts-padding")[goalsTableIdx].find_elements(By.TAG_NAME, "tr")[:-1]

    lastMinutesFlag = False
    totalHomeGoals = 0
    totalLateHomeGoals = 0
    for goalsRow in homeGoalsTables:
        # print(goalsRow.get_attribute('innerHTML'))
        # print(" - ")
        goalsRowElems = goalsRow.find_elements(By.TAG_NAME, "td")
        if '90' in goalsRowElems[0].text:
            lastMinutesFlag = True
        if (goalsRowElems[len(goalsRowElems)-2].text != ''):
            totalHomeGoals += int(goalsRowElems[len(goalsRowElems)-2].text)
            if lastMinutesFlag:
                totalLateHomeGoals += int(goalsRowElems[len(goalsRowElems)-2].text)

    awayGoalsTables = driver.find_elements(By.CLASS_NAME, "stat-quarts-padding")[goalsTableIdx + 1].find_elements(By.TAG_NAME, "tr")[:-1]

    lastMinutesFlag = False
    totalAwayGoals = 0
    totalLateAwayGoals = 0
    for goalsRow in awayGoalsTables:
        # print(goalsRow.get_attribute('innerHTML'))
        # print(" - ")
        goalsRowElems = goalsRow.find_elements(By.TAG_NAME, "td")
        if '90' in goalsRowElems[0].text:
            lastMinutesFlag = True
        if (goalsRowElems[len(goalsRowElems)-2].text != ''):
            totalAwayGoals += int(goalsRowElems[len(goalsRowElems)-2].text)
            if lastMinutesFlag:
                totalLateAwayGoals += int(goalsRowElems[len(goalsRowElems)-2].text)

    if (totalHomeGoals == 0) or (totalLateHomeGoals == 0) or (totalAwayGoals == 0) or (totalLateAwayGoals == 0):
        return 0
    print((totalLateHomeGoals / totalHomeGoals) + (totalLateAwayGoals / totalAwayGoals) / 2)  
    return str(((totalLateHomeGoals / totalHomeGoals) + (totalLateAwayGoals / totalAwayGoals)) / 2)
    # if float(((totalLateHomeGoals / totalHomeGoals) + (totalLateAwayGoals / totalAwayGoals)) / 2) >= float(0.40):
    #     return True
