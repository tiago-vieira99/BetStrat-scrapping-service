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
from urllib.parse import urlparse, parse_qs


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

def scrappNBAStatsBulk(url, season):

    matches = []

    hasNextDay = True
    #url = "https://www.covers.com/sports/nba/matchups?selectedDate=2024-06-17"
    driver = webdriver.Remote("http://172.17.0.3:4444", options=webdriver.ChromeOptions())

    while(hasNextDay):
        print(url)
        date = url.split('selectedDate=')[1]
        response = requests.get(url)
        if response.status_code == 200:
            try:
                soup = BeautifulSoup(response.content, 'html.parser')

                if (soup.find('a', class_='isDailySport').find_next('a', class_='navigation-anchor') is None):
                    print('last day!')
                    hasNextDay = False
                else:
                    url = "https://www.covers.com/" + soup.find('a', class_='isDailySport').find_next('a', class_='navigation-anchor')['href']

                matches_boxes = soup.find_all('article', class_='gamebox')
                for match_box in matches_boxes:
                    thisMatch = {}
                    match_url = "http://www.covers.com" + match_box.find('a', attrs={'data-linkcont': 'nba-scoreboard-page-postgame-matchup-click'})['href']

                    away_team_short = match_box.find_all('span', class_='text-nowrap')[0].text.strip()
                    home_team_short = match_box.find_all('span', class_='text-nowrap')[1].text.strip()

                    if len(match_box.find('p', id='gamebox-header').find_all('span')) > 0:
                        competition_phase = match_box.find('p', id='gamebox-header').find_all('span')[0].text.strip()
                    else:
                        competition_phase = 'Regular'

                    # QUARTER RESULTs
                    first_q_result = match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[2].find_all('td')[0].text.strip() + '-' + match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[1].find_all('td')[0].text.strip()
                    second_q_result = match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[2].find_all('td')[1].text.strip() + '-' + match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[1].find_all('td')[1].text.strip()  
                    third_q_result = match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[2].find_all('td')[2].text.strip() + '-' + match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[1].find_all('td')[2].text.strip()
                    fourth_q_result = match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[2].find_all('td')[3].text.strip() + '-' + match_box.find('table', class_='d-none d-xl-table w-100 fs-8 text-center').find_all('tr')[1].find_all('td')[3].text.strip() 
                    ht_result = str(int(first_q_result.split('-')[0]) + int(second_q_result.split('-')[0])) + '-' + str(int(first_q_result.split('-')[1]) + int(second_q_result.split('-')[1])) 
                    ft_result = str(int(first_q_result.split('-')[0]) + int(second_q_result.split('-')[0]) + int(third_q_result.split('-')[0]) + int(fourth_q_result.split('-')[0])) + '-' + str(int(first_q_result.split('-')[1]) + int(second_q_result.split('-')[1]) + int(third_q_result.split('-')[1]) + int(fourth_q_result.split('-')[1])) 
                    
                    thisMatch['date'] = date
                    thisMatch['season'] = season
                    thisMatch['home_team_short'] = home_team_short
                    thisMatch['away_team_short'] = away_team_short
                    thisMatch['ft_result'] = ft_result
                    thisMatch['ht_result'] = ht_result
                    thisMatch['first_quarter_result'] = first_q_result
                    thisMatch['second_quarter_result'] = second_q_result
                    thisMatch['third_quarter_result'] = third_q_result
                    thisMatch['fourth_quarter_result'] = fourth_q_result
                    thisMatch['competition_phase'] = competition_phase
                    thisMatch['match_url'] = match_url
                    thisMatch['total_points'] = int(ft_result.split('-')[0]) + int(ft_result.split('-')[1])

                    driver.maximize_window()
                    driver.get(match_url)
                    #delete the cookies  
                    driver.delete_all_cookies() 

                    time.sleep(1.5)
 
                    oddsHtml = driver.find_elements(By.ID, "sponsoredOdds-table")[0].get_attribute('outerHTML')
                    recentFormHtml = driver.find_elements(By.ID, "sponsored-odds")[0].find_element(By.XPATH, "./..").find_elements(By.CLASS_NAME, "table-container")[0].get_attribute('outerHTML')
                    h2hSection = driver.find_elements(By.CLASS_NAME, "both-team-section")[0].get_attribute('outerHTML')
                    awaySection = driver.find_elements(By.CLASS_NAME, "away-team-section")[0].get_attribute('outerHTML')
                    homeSection = driver.find_elements(By.CLASS_NAME, "home-team-section")[0].get_attribute('outerHTML')

                    response2 = requests.get(match_url)
                    if response2.status_code == 200:
                        soup2 = BeautifulSoup(response2.content, 'html.parser')

                        away_team = soup2.find_all('span', class_='matchup-team-name')[0].find('a')['href'].split('main/')[1].replace('-', ' ')
                        home_team = soup2.find_all('span', class_='matchup-team-name')[1].find('a')['href'].split('main/')[1].replace('-', ' ')

                        away_team_conference = soup2.find_all('span', class_='matchup-team-confStats')[0].text.strip().split('CONFERENCE')[0].split(' ')[1].title()
                        home_team_conference = soup2.find_all('span', class_='matchup-team-confStats')[1].text.strip().split('CONFERENCE')[0].split(' ')[1].title()
                        
                        thisMatch['home_team'] = ' '.join(word.capitalize() for word in home_team.split())
                        thisMatch['away_team'] = ' '.join(word.capitalize() for word in away_team.split())
                        thisMatch['home_team_conference'] = home_team_conference
                        thisMatch['away_team_conference'] = away_team_conference

                        # RECENT FORM
                        recentFormSoup = BeautifulSoup(recentFormHtml, 'html.parser')
                        if len(recentFormSoup.find_all('table')) > 0:
                            thisMatch['away_num_wins_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[1].text.strip().split('-')[0]
                            thisMatch['away_num_losses_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[1].text.strip().split('-')[1]
                            thisMatch['away_ats_wins_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[2].text.strip().split('-')[0]
                            thisMatch['away_ats_losses_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[2].text.strip().split('-')[1]
                            thisMatch['away_ats_ties_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[2].text.strip().split('-')[2]
                            thisMatch['away_overs_wins_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[3].text.strip().split('-')[0]
                            thisMatch['away_overs_losses_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[3].text.strip().split('-')[1]
                            thisMatch['away_overs_ties_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[3].text.strip().split('-')[2]
                            thisMatch['away_num_wins_at_away_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[4].text.strip().split('-')[0]
                            thisMatch['away_num_losses_at_away_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[4].text.strip().split('-')[1]
                            thisMatch['away_num_wins_at_home_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[5].text.strip().split('-')[0]
                            thisMatch['away_num_losses_at_home_pre'] = recentFormSoup.find_all('tr')[1].find_all('td')[5].text.strip().split('-')[1]
                            thisMatch['home_num_wins_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[1].text.strip().split('-')[0]
                            thisMatch['home_num_losses_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[1].text.strip().split('-')[1]
                            thisMatch['home_ats_wins_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[2].text.strip().split('-')[0]
                            thisMatch['home_ats_losses_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[2].text.strip().split('-')[1]
                            thisMatch['home_ats_ties_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[2].text.strip().split('-')[2]
                            thisMatch['home_overs_wins_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[3].text.strip().split('-')[0]
                            thisMatch['home_overs_losses_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[3].text.strip().split('-')[1]
                            thisMatch['home_overs_ties_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[3].text.strip().split('-')[2]
                            thisMatch['home_num_wins_at_away_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[4].text.strip().split('-')[0]
                            thisMatch['home_num_losses_at_away_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[4].text.strip().split('-')[1]
                            thisMatch['home_num_wins_at_home_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[5].text.strip().split('-')[0]
                            thisMatch['home_num_losses_at_home_pre'] = recentFormSoup.find_all('tr')[2].find_all('td')[5].text.strip().split('-')[1]

                        # ODDS
                        response3 = requests.get(match_url + "/odds")
                        if response3.status_code == 200:
                            oddsSoup = BeautifulSoup(response3.content, 'html.parser')

                            if (len(oddsSoup.find_all('a', class_='oddsLink')) > 0):
                                away_spread = oddsSoup.find_all('table', class_='teamsPage')[0].find_all('a', class_='oddsLink')[0].find('b').text.strip() + ' ' + oddsSoup.find_all('table', class_='teamsPage')[0].find_all('a', class_='oddsLink')[0].find('span').text.strip()
                                home_spread = oddsSoup.find_all('table', class_='teamsPage')[0].find_all('a', class_='oddsLink')[1].find('b').text.strip() + ' ' + oddsSoup.find_all('table', class_='teamsPage')[0].find_all('a', class_='oddsLink')[1].find('span').text.strip()
                                over_spread = oddsSoup.find_all('table', class_='teamsPage')[1].find_all('a', class_='oddsLink')[0].find('b').text.strip() + ' ' + oddsSoup.find_all('table', class_='teamsPage')[1].find_all('a', class_='oddsLink')[0].find('span').text.strip()
                                under_spread = oddsSoup.find_all('table', class_='teamsPage')[1].find_all('a', class_='oddsLink')[1].find('b').text.strip() + ' ' + oddsSoup.find_all('table', class_='teamsPage')[1].find_all('a', class_='oddsLink')[1].find('span').text.strip()
                                away_money_line = oddsSoup.find_all('table', class_='teamsPage')[2].find_all('a', class_='oddsLink')[0].text.strip()
                                home_money_line = oddsSoup.find_all('table', class_='teamsPage')[2].find_all('a', class_='oddsLink')[1].text.strip()

                                thisMatch['home_spread'] = home_spread.split(' ')[0]
                                thisMatch['away_spread'] = away_spread.split(' ')[0]
                                thisMatch['points_spread'] = over_spread.split(' ')[0].replace('o','')
                                thisMatch['home_win_odd'] = convertToDecimalOdds(home_money_line)
                                thisMatch['away_win_odd'] = convertToDecimalOdds(away_money_line)
                                thisMatch['away_spread_odd'] = convertToDecimalOdds(away_spread.split(' ')[1])
                                thisMatch['home_spread_odd'] = convertToDecimalOdds(home_spread.split(' ')[1])
                                thisMatch['over_spread_odd'] = convertToDecimalOdds(over_spread.split(' ')[1])
                                thisMatch['under_spread_odd'] = convertToDecimalOdds(under_spread.split(' ')[1])

                        # H2H LAST 10
                        h2hSoup = BeautifulSoup(h2hSection, 'html.parser')
                        if (away_team_short.lower() + '.svg' in str(h2hSoup.find_all('div', class_='record-value')[0])):
                            thisMatch['h2h_last10_away_wins_pre'] = h2hSoup.find_all('div', class_='record-value')[0].text.strip().split('-')[0]
                            thisMatch['h2h_last10_home_wins_pre'] = h2hSoup.find_all('div', class_='record-value')[0].text.strip().split('-')[1]
                        elif (home_team_short.lower() + '.svg' in str(h2hSoup.find_all('div', class_='record-value')[0])):
                            thisMatch['h2h_last10_away_wins_pre'] = h2hSoup.find_all('div', class_='record-value')[0].text.strip().split('-')[1]
                            thisMatch['h2h_last10_home_wins_pre'] = h2hSoup.find_all('div', class_='record-value')[0].text.strip().split('-')[0]
                        else:
                            thisMatch['h2h_last10_away_wins_pre'] = "5"
                            thisMatch['h2h_last10_home_wins_pre'] = "5"

                        thisMatch['h2h_last10_away_ats_wins_pre'] = h2hSoup.find_all('div', class_='record-value')[1].text.strip().split('-')[0]
                        thisMatch['h2h_last10_home_ats_wins_pre'] = h2hSoup.find_all('div', class_='record-value')[1].text.strip().split('-')[1]

                        h2hLast10 = []
                        for h2hMatch in h2hSoup.find('table', class_='last-10-table').find_all('tr')[1:]:
                            h2hLast10.append(str(h2hMatch.find_all('td')[0].text.strip() + ';' + h2hMatch.find_all('td')[1].text.strip() + ';' + h2hMatch.find_all('td')[2].text.strip() + ';' + h2hMatch.find_all('td')[3].text.strip() + ';' + h2hMatch.find_all('td')[4].text.strip()))

                        thisMatch['h2h_last10'] = str(h2hLast10)
                        thisMatch['h2h_last10_overs_wins_pre'] = h2hSoup.find_all('div', class_='record-value')[2].text.strip().split('-')[0]
                        thisMatch['h2h_last10_overs_losses_pre'] = h2hSoup.find_all('div', class_='record-value')[2].text.strip().split('-')[1]
                        thisMatch['h2h_last10_overs_draws_pre'] = h2hSoup.find_all('div', class_='record-value')[2].text.strip().split('-')[2]

                        # AWAY LAST 10
                        awaySoup = BeautifulSoup(awaySection, 'html.parser')
                        awayLast10 = []
                        for match in awaySoup.find('table', class_='last-10-table').find_all('tr')[1:]:
                            awayLast10.append(str(match.find_all('td')[0].text.strip() + ';' + match.find_all('td')[1].text.strip() + ';' + match.find_all('td')[2].text.strip() + ';' + match.find_all('td')[3].text.strip() + ';' + match.find_all('td')[4].text.strip()))

                        thisMatch['away_last10'] = str(awayLast10)
                        thisMatch['last10_away_wins_pre'] = awaySoup.find_all('div', class_='record-value')[0].text.strip().split('-')[0]
                        thisMatch['last10_away_losses_pre'] = awaySoup.find_all('div', class_='record-value')[0].text.strip().split('-')[1]
                        thisMatch['last10_away_draws_pre'] = awaySoup.find_all('div', class_='record-value')[0].text.strip().split('-')[2]
                        thisMatch['last10_away_ats_wins_pre'] = awaySoup.find_all('div', class_='record-value')[1].text.strip().split('-')[0]
                        thisMatch['last10_away_ats_losses_pre'] = awaySoup.find_all('div', class_='record-value')[1].text.strip().split('-')[1]
                        thisMatch['last10_away_ats_draws_pre'] = awaySoup.find_all('div', class_='record-value')[1].text.strip().split('-')[2]
                        thisMatch['last10_away_overs_wins_pre'] = awaySoup.find_all('div', class_='record-value')[2].text.strip().split('-')[0]
                        thisMatch['last10_away_overs_losses_pre'] = awaySoup.find_all('div', class_='record-value')[2].text.strip().split('-')[1]
                        thisMatch['last10_away_overs_draws_pre'] = awaySoup.find_all('div', class_='record-value')[2].text.strip().split('-')[2]

                        # HOME LAST 10
                        homeSoup = BeautifulSoup(homeSection, 'html.parser')
                        homeLast10 = []
                        for match in homeSoup.find('table', class_='last-10-table').find_all('tr')[1:]:
                            homeLast10.append(str(match.find_all('td')[0].text.strip() + ';' + match.find_all('td')[1].text.strip() + ';' + match.find_all('td')[2].text.strip() + ';' + match.find_all('td')[3].text.strip() + ';' + match.find_all('td')[4].text.strip()))

                        thisMatch['home_last10'] = str(homeLast10)
                        thisMatch['last10_home_wins_pre'] = homeSoup.find_all('div', class_='record-value')[0].text.strip().split('-')[0]
                        thisMatch['last10_home_losses_pre'] = homeSoup.find_all('div', class_='record-value')[0].text.strip().split('-')[1]
                        thisMatch['last10_home_draws_pre'] = homeSoup.find_all('div', class_='record-value')[0].text.strip().split('-')[2]
                        thisMatch['last10_home_ats_wins_pre'] = homeSoup.find_all('div', class_='record-value')[1].text.strip().split('-')[0]
                        thisMatch['last10_home_ats_losses_pre'] = homeSoup.find_all('div', class_='record-value')[1].text.strip().split('-')[1]
                        thisMatch['last10_home_ats_draws_pre'] = homeSoup.find_all('div', class_='record-value')[1].text.strip().split('-')[2]
                        thisMatch['last10_home_overs_wins_pre'] = homeSoup.find_all('div', class_='record-value')[2].text.strip().split('-')[0]
                        thisMatch['last10_home_overs_losses_pre'] = homeSoup.find_all('div', class_='record-value')[2].text.strip().split('-')[1]
                        thisMatch['last10_home_overs_draws_pre'] = homeSoup.find_all('div', class_='record-value')[2].text.strip().split('-')[2]

                    #matches.append(thisMatch)
                    insertMatchInDB(thisMatch)
                    # hasNextDay = False
                    # break 

            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

    driver.close()
    return matches

def convertToDecimalOdds(americanOdd):
    if americanOdd == '--':
        return 0
    if(float(americanOdd) < 0):
        return round(1 + (100 / (-1 * float(americanOdd))), 2)
    else:
        return round(1 + (float(americanOdd) / 100), 2)


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

        query = f"INSERT INTO backtesting.nba ({columns}) VALUES ({placeholders})"

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

