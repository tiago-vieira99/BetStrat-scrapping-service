import requests
from flask import jsonify
from bs4 import BeautifulSoup
from obj.match import Match
import re
from datetime import datetime, timedelta
import sys, os
import csv
from collections import OrderedDict
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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


def getNextMatchFromWF(url, team, season, allLeagues, source_code):
    logging.info("getting next match for " + team + ": " + str(url))
    matches = []
    
    if source_code is not None:
        soup = BeautifulSoup(source_code, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table', class_="standard_tabelle")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        match_urls = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])
            if len(row.find_all('a')) > 0:
                match_urls.append(row.find_all('a')[-1]['href'])
            else:
                match_urls.append('')

        flag = False
        competition = ''
        for i, r in enumerate(rows):
            if len(r) < 10:
                if ('Friendlies' in r[1]) or (season not in r[1]):
                    flag = False
                else:
                    flag = True
                    competition = r[1]
            if (len(r) > 15) and (flag is True):
                if allLeagues is False and r[1] != 'Round':
                    continue
                if len(r[13]) < 4 and r[13] == '-:-':
                    date = datetime.strptime(r[3], "%d/%m/%Y")
                    if r[7] == 'H':
                        matches.append(Match(date.strftime('%Y-%m-%d'), team, r[11], '', '', competition, "http://www.worlfootbal.net" + match_urls[i]).to_dict())
                    else:
                        matches.append(Match(date.strftime('%Y-%m-%d'), r[11], team, '', '', competition, "http://www.worlfootbal.net" + match_urls[i]).to_dict())            

        logging.info(str(len(matches)) + " matches scrapped for " + team)
        matches.sort(key=lambda match: datetime.strptime(match["date"], "%Y-%m-%d"))
        return matches[0]
    else:
        raise Exception(f'Failed to scrape data from {url}. ')


def getWFSourceHtmlCode(url, driver):
    try:
        driver.set_page_load_timeout(30)  # Increased timeout
        driver.delete_all_cookies()
        driver.get(url)
        logging.info(f"Navigated to {url}")

        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "cmpwelcomebtnyes"))
            )
            button.click()
            logging.info("Clicked the 'cmpwelcomebtnyes' button.")
        except Exception as e:
            logging.info("No 'cmpwelcomebtnyes' button found or failed to click.")

        source_code = driver.page_source
        logging.info("Successfully retrieved page source.")
        return source_code

    except Exception as e:
        logging.error(f"Error getting source code for {url}: {e}", exc_info=True) # Log with traceback
        return None


def getLastNMatchesFromWF(url, n, team, allLeagues, season, source_code):
    logging.info("getting last " + str(n) + " match stats: " + str(url))
    matches = []
    
    if source_code is not None:
        soup = BeautifulSoup(source_code, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table', class_="standard_tabelle")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        match_urls = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])
            if len(row.find_all('a')) > 0:
                match_urls.append(row.find_all('a')[-1]['href'])
            else:
                match_urls.append('')

        flag = False
        competition = ''
        for i, r in enumerate(rows):
            #logging.info(r)
            if len(r) < 10:
                if ('Friendlies' in r[1]) or (season not in r[1]):
                    flag = False
                else:
                    flag = True
                    competition = re.sub(r'(\d{4}(?:/\d{4})?)\s.*$', r'\1', r[1])
            if (len(r) > 15) and (flag is True) and bool(re.search(r'\b\d+:\d+\b', r[13])):# and '(' in r[13]:
                if allLeagues is False and r[1] != 'Round':
                    continue
                ftResult = ''
                htResult = ''
                if ('pso' in r[13] or 'aet' in r[13] or 'dec' in r[13]) and ',' in r[13]:
                    ftResult = r[13].split(',')[1].split(')')[0].strip()
                    htResult = r[13].split(',')[0].split('(')[1].strip().replace(',','')
                elif 'n.P.' in r[13]:
                    ftResult = r[13].split(',')[1].strip()
                    htResult = r[13].split(',')[0].split('(')[1].strip().replace(',','')
                else:
                    ftResult = r[13].split(' ')[0]
                    if (len(r[13].split(' ')) > 1):
                        htResult = r[13].split(' ')[1].replace('(','').replace(')','').replace(',','')

                if ':' in ftResult:
                    if r[7] == 'H':
                        matches.append(Match(r[3], team, r[11], ftResult, htResult, competition, "http://www.worlfootbal.net" + match_urls[i]).to_dict())
                    else:
                        ftResult = ftResult.split(':')[1] + ':' + ftResult.split(':')[0]
                        if ':' in htResult:
                            htResult = htResult.split(':')[1] + ':' + htResult.split(':')[0]
                        matches.append(Match(r[3], r[11], team, ftResult, htResult, competition, "http://www.worlfootbal.net" + match_urls[i]).to_dict())    
                else:
                    logging.info(r)            

        logging.info(str(len(matches)) + " matches scrapped for " + team)
        matches.sort(key=lambda match: datetime.strptime(match["date"], "%d/%m/%Y"))
        matches.reverse()
        count = 0
        lastMatches = []
        for r in matches:
            if count == n:
                break
            lastMatches.append(r)
            count = count + 1
        return lastMatches
    else:
        raise Exception(f'Failed to scrape data from {url}.')

def getLeagueTeamsFromWF(urlLeaguesList, driver):
    teams = {}

    for url in str(urlLeaguesList, 'utf-8').split('\n'):
        time.sleep(1)
        logging.info("getting league teams: " + str(url))
        source_code = getWFSourceHtmlCode(url, driver)

        try:
            if source_code is not None:
                soup = BeautifulSoup(source_code, 'html.parser')
                # Perform scraping operations using BeautifulSoup here
                tables = soup.find_all('table', class_="standard_tabelle")
            
                # then we can iterate through each row and extract either header or row values:
                header = []
                rows = []
                if len(tables) > 2:
                    totalNumTables = len(tables)-1
                else:
                    totalNumTables = len(tables)
                for j in range(1, totalNumTables):
                    table = tables[j]
                    for i, row in enumerate(table.find_all('tr')):
                        if i != 0:
                            rows.append([el.text.strip() for el in row])

                logging.info("Number of teams collected: " + str(len(rows)))
                for i, r in enumerate(rows):
                    teams[r[5].split('\n')[0]] = i+1;
                    # break
            else:
                logging.info(f'Failed to scrape data from {url}.')
        except Exception as e:
            logging.info(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, fname, exc_tb.tb_lineno)
            continue

    driver.close()
    return teams

def getLiveMatchStatsFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("\ngetting live match stats: " + str(url))
        
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

            logging.info('Scrapped stats: homeOverRate: '+ homeOverRate + '; awayOverRate: ' + awayOverRate + '; homeGoalsAvg: ' + homeGoalsAvg + '; awayGoalsAvg: ' + awayGoalsAvg + '; numOverh2h: ' + str(numOversh2h))

            h2hOverRate = 100*numOversh2h/len(h2hMatches)
            logging.info(h2hOverRate)
            if (int(homeOverRate) >= 70 or int(awayOverRate) >= 70) and ((int(homeGoalsAvg)+int(awayGoalsAvg))/2 >= 3) and float(h2hOverRate) >= 65:
                return True
            else:
                return False
        except:
            logging.info("An exception has occurred!\n")

    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    