import requests
from flask import jsonify
from bs4 import BeautifulSoup
from obj.match import Match
import re

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
        print("\ngetting live match stats: " + url)
        
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

            print('Scrapped stats: homeOverRate: '+ homeOverRate + '; awayOverRate: ' + awayOverRate + '; homeGoalsAvg: ' + homeGoalsAvg + '; awayGoalsAvg: ' + awayGoalsAvg + '; numOverh2h: ' + str(numOversh2h))

            h2hOverRate = 100*numOversh2h/len(h2hMatches)
            print(h2hOverRate)
            if (int(homeOverRate) >= 70 or int(awayOverRate) >= 70) and ((int(homeGoalsAvg)+int(awayGoalsAvg))/2 >= 3) and float(h2hOverRate) >= 65:
                return True
            else:
                return False
        except:
            print("An exception has occurred!\n")

    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')