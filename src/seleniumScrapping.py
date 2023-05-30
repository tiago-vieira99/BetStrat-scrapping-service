from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import scrapping

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
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
    print("oiiio oiii ")

    for match in liveMatches:
        print(match.find_element(By.CLASS_NAME, "team-a").text)
        if len(match.find_elements(By.CLASS_NAME, "gameinlive")) == 0:
            continue
        matchTime = match.find_element(By.CLASS_NAME, "game_running").text
        matchScore = match.find_element(By.CLASS_NAME, "score").text
        print(matchScore)
        if (matchScore == '0 - 0') and ((matchTime == 'Intervalo') or (int(matchTime) > 39 and int(matchTime) < 61)):
            print("hey hey")
        print(match.find_element(By.CLASS_NAME, "team-a").text)
        matchUrl = match.find_elements(By.CLASS_NAME, "gameinlive")[1].find_element(By.TAG_NAME, "a").get_attribute("href")
        scrapping.getLiveMatchStatsFromAdA(matchUrl)

    driver.close()