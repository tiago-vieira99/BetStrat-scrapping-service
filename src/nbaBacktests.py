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

def scrappNBAStatsBulk(firstDayUrl):

    matches = []

    url = "https://sportsdata.usatoday.com/basketball/nba/scores?date=2022-10-02&season=2022"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            #print(soup.find_all('div', class_='react-multi-carousel-list')[0].find_all('ul', class_='react-multi-carousel-track')[0])
            matches_links = soup.find_all('div', class_='class-1ne55WF')[0].find_all('a')
            for match in matches_links:
                print(match['href'])
                response2 = requests.get("https://sportsdata.usatoday.com" + match['href'])
                if response2.status_code == 200:
                    thisMatch = {}
                    soup2 = BeautifulSoup(response2.content, 'html.parser')
                    home_team = soup2.find_all('div', class_='class-B7unWiD')[0].find('a').find_all('div')[0].text.strip()
                    home_team_short = soup2.find_all('div', class_='class-B7unWiD')[0].find('a').find_all('div')[1].text.strip()
                    away_team = soup2.find_all('div', class_='class-B7unWiD')[1].find('a').find_all('div')[0].text.strip()
                    away_team_short = soup2.find_all('div', class_='class-B7unWiD')[1].find('a').find_all('div')[1].text.strip()

                    ft_result = soup2.find_all('div', class_='class-MPFG1-M')[0].text.strip() + '-' + soup2.find_all('div', class_='class-MPFG1-M')[1].text.strip()

                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)

                    date = query_params.get('date', [None])[0]  # Get the value associated with 'date'
                    season = query_params.get('season', [None])[0] # Get the value associated with 'season'

                    home_score_by_quarter = soup2.find('table', class_='class-c7k6WPY').find('tbody').find_all('tr')[0]
                    away_score_by_quarter = soup2.find('table', class_='class-c7k6WPY').find('tbody').find_all('tr')[1]

                    first_quarter_result = home_score_by_quarter.find_all('td')[1].text.strip() + '-' + away_score_by_quarter.find_all('td')[1].text.strip()
                    second_quarter_result = home_score_by_quarter.find_all('td')[2].text.strip() + '-' + away_score_by_quarter.find_all('td')[2].text.strip()
                    third_quarter_result = home_score_by_quarter.find_all('td')[3].text.strip() + '-' + away_score_by_quarter.find_all('td')[3].text.strip()
                    fourth_quarter_result = home_score_by_quarter.find_all('td')[4].text.strip() + '-' + away_score_by_quarter.find_all('td')[4].text.strip()


                    thisMatch['date'] = date
                    thisMatch['season'] = season
                    thisMatch['home_team'] = home_team
                    thisMatch['home_team_short'] = home_team_short
                    thisMatch['away_team'] = away_team
                    thisMatch['away_team_short'] = away_team_short
                    thisMatch['ft_result'] = ft_result
                    thisMatch['ht_result'] = 0
                    thisMatch['first_quarter_result'] = first_quarter_result
                    thisMatch['second_quarter_result'] = second_quarter_result
                    thisMatch['third_quarter_result'] = third_quarter_result
                    thisMatch['fourth_quarter_result'] = fourth_quarter_result

                    print(soup2.find_all('span', class_='class-ewsk9ur'))

                    break

                    matches.append(thisMatch)    

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    return matches



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

def getNBAMatchesByDay(url, driver):
    matchesToBet = []
    try:
        print("342")

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    return matchesToBet
