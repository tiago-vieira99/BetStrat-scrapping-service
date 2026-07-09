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
import psycopg2
import psycopg2.extras


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
                if len(r[7]) < 4 and r[7] == '-:-':
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

def getSpecificMatchFromWF(url, team, season, source_code):
    logging.info("getting match for " + str(team) + ", season " + str(season) + " : " + str(url))
    match_dict = {}
    
    if source_code is not None:
        soup = BeautifulSoup(source_code, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        match = soup.find('div', class_='match')

        if match:
            # Check if match status is "Ended"
            status = match.find('div', class_='match-status')
            
            if status and 'Ended' in status.get_text():
                # Get final result (match-result-0)
                final_result = match.find('div', class_='match-result match-result-0')
                
                # Get halftime result (match-result-1 inside match-result-intermediate)
                ht_result_span = match.find('span', class_='match-result match-result-1')

                # Extract datetime from data-datetime attribute
                datetime_str = match.get('data-datetime')

                # Parse and format
                match_date = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = match_date.strftime('%d/%m/%Y')
                
                if final_result and ht_result_span:
                    match_dict['ft_result'] = final_result.get_text()
                    match_dict['ht_result'] = ht_result_span.get_text()
                    match_dict['date'] = formatted_date
                    logging.info(f"Scraped match data: {match_dict}")
        
        return match_dict
    else:
        raise Exception(f'Failed to scrape data from {url}.')


# also includes next match!!
def getLastNMatchesFromWF(url, n, team, allLeagues, season, source_code):
    logging.info("getting last " + str(n) + " match stats: " + str(url))
    matches = []
    
    if source_code is not None:
        soup = BeautifulSoup(source_code, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table')
        current_competition_name = None
        first_upcoming_match_added = False  # Track if we've added the first upcoming match
        
        for row in table.find_all('tr'):
            if 'hs-head--competition' in row.get('class', []):
                # This is a competition header row
                title_tag = row.find('th')
                if title_tag:
                    current_competition_name = title_tag.text.strip()
            elif row.get('data-match_id') and current_competition_name:
                is_finished = 'finished' in row.get('class', [])

                if 'Friendlies' in current_competition_name:
                    continue  # Skip friendly matches
                
                # Process finished matches OR the first upcoming match
                if is_finished or (not first_upcoming_match_added and not is_finished):
                    cols = row.find_all('td')
                    
                    if len(cols) >= 8:
                        # Check if match is rescheduled - skip if it is
                        match_incident = cols[7].find('span', class_='match-incident')
                        if match_incident and 'resch' in match_incident.text.lower():
                            continue  # Skip rescheduled matches

                        date = cols[0].text.strip()
                        home_away_indicator = cols[3].text.strip()
                        opponent_name = cols[5].find('a').text.strip() if cols[5].find('a') else None
                        teamUrl = (cols[5].find('a').get('href').rsplit('/', 2)[0] + '/')
                        opponentNormalizedName = getTeamByUrlFromDB(teamUrl)
                        if opponentNormalizedName is not None:
                            opponent_name = opponentNormalizedName

                        ft_result = None
                        ht_result = None
                        match_url_suffix = None
                        # Extract FT Result (match-result-0) and HT Result (match-result-1)
                        ft_result_span = cols[7].find('span', class_='match-result-0')
                        if ft_result_span:
                            ft_result = ft_result_span.find('a').text.strip() if ft_result_span.find('a') else None
                            match_url_suffix = ft_result_span.find('a').get('href') if ft_result_span.find('a') else None
                        ht_result_span = cols[7].find('span', class_='match-result-1')
                        if ht_result_span:
                            ht_result = ht_result_span.find('a').text.strip() if ht_result_span.find('a') else None
                        
                        # Determine home_team and away_team based on 'H/A' indicator for MY_TEAM
                        home_team = None
                        away_team = None
                        if home_away_indicator == 'H':
                            home_team = team
                            away_team = opponent_name
                        elif home_away_indicator == 'A':
                            home_team = opponent_name
                            away_team = team
                            ft_result = ft_result.split(':')[1] + ':' + ft_result.split(':')[0] if ft_result else None
                            ht_result = ht_result.split(':')[1] + ':' + ht_result.split(':')[0] if ht_result else None
                        # If results are like "0:0", indicating an upcoming match or rescheduled, treat as None or specific placeholder
                        if ft_result == '-:-' or ft_result is None:
                            ft_result = None
                        if ht_result == '-:-' or ht_result is None:
                            ht_result = None
                        # Create Match object and append to list
                        if home_team and away_team and current_competition_name and match_url_suffix:
                            matches.append(Match(
                                date.replace('.', '/'),
                                home_team,
                                away_team,
                                ft_result,
                                ht_result,
                                current_competition_name,
                                match_url_suffix
                            ).to_dict())
                            
                            # Mark that we've added the first upcoming match
                            if not is_finished:
                                first_upcoming_match_added = True


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

def getTeamByUrlFromDB(teamUrl):
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
        logging.info(f"Connected to database !")
        logging.info("Getting data for " + teamUrl)

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = "SELECT name FROM historic_data.teams WHERE sport = 'Football' AND url LIKE %s "
        like_pattern = f"%{teamUrl}%"  # Construct the LIKE pattern
        cursor.execute(query, (like_pattern,))

        teamName = cursor.fetchall()  # Fetch all results

        return teamName[0]['name'] if teamName else None  # Return the name if found, else None

    except psycopg2.Error as e:
        logging.info(f"PostgreSQL error: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            cursor = conn.cursor()  # Create a cursor before closing it
            cursor.close()
            conn.close()

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
                tables = soup.find('div', class_="module-standing").find_all('table')
            
                # then we can iterate through each row and extract either header or row values:
                header = []
                rows = []
                # if len(tables) > 2:
                #     totalNumTables = len(tables)-1
                # else:
                #     totalNumTables = len(tables)
                # for j in range(1, totalNumTables):
                #     table = tables[j]
                for i, row in enumerate(tables[0].find_all('tr')):
                    if i != 0:
                        rows.append([el.text.strip() for el in row])

                logging.info("Number of teams collected: " + str(len(rows)))
                for i, r in enumerate(rows):
                    teams[r[2].split('\n')[0]] = i+1;
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
    