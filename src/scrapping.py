import requests
from flask import jsonify
from bs4 import BeautifulSoup
from obj.match import Match
from selenium import webdriver

def getLastNMatchesFromAdA(url, n):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table', class_="next-games")
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            if i == 0:
                header = [el.text.strip() for el in row.find_all('th')]
            else:
                rows.append([el.text.strip() for el in row.find_all('td')])

        matches = []

        count = 0;
        for r in rows:
            if count == n:
                break
            if r[4] != 'vs':
                matches.append(Match(r[0], r[3], r[5], r[4].replace("-",":")).to_dict())
                count = count + 1

        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')


def getNextMatchFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table', class_="next-games")
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            if i == 0:
                header = [el.text.strip() for el in row.find_all('th')]
            else:
                rows.append([el.text.strip() for el in row.find_all('td')])

        matches = []

        for r in rows:
            if r[4] == 'vs':
                matches.append(Match(r[0], r[3], r[5], r[4]).to_dict())

        return matches[len(matches) - 1]
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    

def getLiveMatchStatsFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("checkpoint!")
        # Perform scraping operations using BeautifulSoup here
        # table = soup.find('table', class_="next-games")
        # # then we can iterate through each row and extract either header or row values:
        # header = []
        # rows = []
        # for i, row in enumerate(table.find_all('tr')):
        #     if i == 0:
        #         header = [el.text.strip() for el in row.find_all('th')]
        #     else:
        #         rows.append([el.text.strip() for el in row.find_all('td')])

        # matches = []

        # for r in rows:
        #     if r[4] == 'vs':
        #         matches.append(Match(r[0], r[3], r[5], r[4]).to_dict())

        # return matches[len(matches) - 1]
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')