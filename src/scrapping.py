import requests
from flask import jsonify
from bs4 import BeautifulSoup
from obj.match import Match
import re
import Levenshtein
from datetime import datetime

def getLastNMatchesFromAdA(url, n):
    response = requests.get(url)
    print("\ngetting last " + str(n) + " match stats: " + str(url))
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
            if 'Adiado' in r[4]:
                continue
            if r[4] != 'vs':
                matches.append(Match(r[0], r[3], r[5], r[4].replace("-",":"), '').to_dict())
                count = count + 1

        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')


def getNextMatchFromAdA(url):
    print("\ngetting next match: " + str(url))
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
                matches.append(Match(r[0], r[3], r[5], r[4], '').to_dict())

        return matches[len(matches) - 1]
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')


def getSeasonMatchesFromFBRef(url, team, allLeagues):
    print("\ngetting all season matches: " + str(url))
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')   
        if allLeagues is False:
            matchLogsUrl = "http://www.fbref.com" + soup.find_all('p', class_="listhead")[2].find_next_siblings("ul")[0].find_all('a')[0]['href']
            response = requests.get(matchLogsUrl)
            soup = BeautifulSoup(response.content, 'html.parser')               

        table = soup.find('table', id="matchlogs_for")
        competition = soup.find_all('div', class_="current")[0].text.strip()
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            if i == 0:
                header = [el.text.strip() for el in row.find_all('th')]
            else:
                rows.append([el.text.strip() for el in row])

        matches = []

        for r in rows:
            print(r)
            if r[0] == '':
                continue
            if r[header.index("Venue")] == 'Home':
                matches.append(Match(r[0], team, r[header.index("Opponent")], r[header.index("GF")].split(' ')[0]+':'+r[header.index("GA")].split(' ')[0], competition).to_dict())
            else:
                matches.append(Match(r[0], r[header.index("Opponent")], team, r[header.index("GA")].split(' ')[0]+':'+r[header.index("GF")].split(' ')[0], competition).to_dict())

        print(str(len(matches)) + " matches scrapped for " + team)
        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    

def getSeasonMatchesFromZZ(url, team, allLeagues):
    print("\ngetting all season matches: " + str(url))
    matches = []
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        compsData = soup.find_all('div', id="team_games")[0].find_all('tr')
        compNumMatches = 0
        mainCompName = ''
        for i, comp in enumerate(compsData):
            if len(comp.find_all('td', class_='double')) > 0:
                if compNumMatches < int(comp.find_all('td', class_='double')[1].text.strip()):
                    compNumMatches = int(comp.find_all('td', class_='double')[1].text.strip())
                    mainCompName = comp.find('div', class_='text').text.strip()

        div_table = soup.find_all('div', id="team_games")[1]
        table = div_table.find('table', class_="zztable")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])

        response2 = requests.get(url.decode("utf-8")+"&page=2")
        if response2.status_code == 200:
            soup2 = BeautifulSoup(response2.content, 'html.parser')
            # Perform scraping operations using BeautifulSoup here
            div_table2 = soup2.find_all('div', id="team_games")[0]
            table2 = div_table2.find('table', class_="zztable")
            
            if len(table2.find_all('tr')) > 0:
                rows = rows[:-1]
            for i, row in enumerate(table2.find_all('tr')):
                rows.append([el.text.strip() for el in row])

            if len(table2.find_all('tr')) > 0:
                rows = rows[:-1]
        else:
            raise Exception(f'Failed to scrape data from {url}. Error: {response2.status_code}')
        
        for r in rows:
            result = ""
            if allLeagues is False and 'compet_id_jogos=0' in str(url) and Levenshtein.distance(r[6], mainCompName) > 9:
                continue    

            if "-" in r[5]:
                result = r[5].split('-')[0] + ":" + r[5].split('-')[1]
            else:
                continue

            if r[3] == '(C)':
                matches.append(Match(r[1], team, r[4], result, r[6]).to_dict())
            else:
                matches.append(Match(r[1], r[4], team, result, r[6]).to_dict())

        matches.reverse()
        print(str(len(matches)) + " matches scrapped for " + team)
        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')


def getSeasonMatchesFromWF(url, team, season, allLeagues):
    print("\ngetting all season matches: " + str(url, 'utf-8'))
    matches = []
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table', class_="standard_tabelle")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])

        flag = False
        competition = ''
        for r in rows:
            if len(r) < 10:
                if ('Friendlies' in r[1]) or (season not in r[1]):
                    flag = False
                else:
                    flag = True
                    competition = r[1]
            if (len(r) > 15) and (flag is True):
                if allLeagues is False and r[1] != 'Round':
                    continue
                result = ''
                if 'pso' in r[13] or 'aet' in r[13]:
                    result = r[13].split(',')[1].split(')')[0].strip()
                else:
                    result = r[13].split(' ')[0]
                if ':' in result:
                    if r[7] == 'H':
                        matches.append(Match(r[3], team, r[11], result, competition).to_dict())
                    else:
                        result = result.split(':')[1] + ':' + result.split(':')[0]
                        matches.append(Match(r[3], r[11], team, result, competition).to_dict())            

        print(str(len(matches)) + " matches scrapped for " + team)
        matches.sort(key=lambda match: datetime.strptime(match["date"], "%d/%m/%Y"))
        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getNextMatchFromZZ(url, team):
    print("\ngetting next match for " + team + ": " + str(url, 'utf-8'))
    matches = []
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        compsData = soup.find_all('div', id="team_games")[0].find_all('tr')
        compNumMatches = 0
        mainCompName = ''
        for i, comp in enumerate(compsData):
            if len(comp.find_all('td', class_='double')) > 0:
                if compNumMatches < int(comp.find_all('td', class_='double')[1].text.strip()):
                    compNumMatches = int(comp.find_all('td', class_='double')[1].text.strip())
                    mainCompName = comp.find('div', class_='text').text.strip()

        div_table = soup.find_all('div', id="team_games")[1]
        table = div_table.find('table', class_="zztable")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])

        # response2 = requests.get(url.decode("utf-8")+"&page=2")
        # if response2.status_code == 200:
        #     soup2 = BeautifulSoup(response2.content, 'html.parser')
        #     # Perform scraping operations using BeautifulSoup here
        #     div_table2 = soup2.find_all('div', id="team_games")[0]
        #     table2 = div_table2.find('table', class_="zztable")
            
        #     if len(table2.find_all('tr')) > 0:
        #         rows = rows[:-1]
        #     for i, row in enumerate(table2.find_all('tr')):
        #         rows.append([el.text.strip() for el in row])

        #     if len(table2.find_all('tr')) > 0:
        #         rows = rows[:-1]
        # else:
        #     raise Exception(f'Failed to scrape data from {url}. Error: {response2.status_code}')
        
        for r in rows:
            result = ""

            if r[5] == '-':
                if r[3] == '(C)':
                    matches.append(Match(r[1], team, r[4], result, r[6]).to_dict())
                else:
                    matches.append(Match(r[1], r[4], team, result, r[6]).to_dict())

        matches.reverse()
        print(str(len(matches)) + " matches scrapped for " + team)
        return matches[0]
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getLastNMatchesFromZZ(url, n, team):
    print("\ngetting last " + str(n) + " match stats: " + str(url))
    matches = []
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        compsData = soup.find_all('div', id="team_games")[0].find_all('tr')
        compNumMatches = 0
        mainCompName = ''
        for i, comp in enumerate(compsData):
            if len(comp.find_all('td', class_='double')) > 0:
                if compNumMatches < int(comp.find_all('td', class_='double')[1].text.strip()):
                    compNumMatches = int(comp.find_all('td', class_='double')[1].text.strip())
                    mainCompName = comp.find('div', class_='text').text.strip()

        div_table = soup.find_all('div', id="team_games")[1]
        table = div_table.find('table', class_="zztable")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])

        # response2 = requests.get(url.decode("utf-8")+"&page=2")
        # if response2.status_code == 200:
        #     soup2 = BeautifulSoup(response2.content, 'html.parser')
        #     # Perform scraping operations using BeautifulSoup here
        #     div_table2 = soup2.find_all('div', id="team_games")[0]
        #     table2 = div_table2.find('table', class_="zztable")
            
        #     if len(table2.find_all('tr')) > 0:
        #         rows = rows[:-1]
        #     for i, row in enumerate(table2.find_all('tr')):
        #         rows.append([el.text.strip() for el in row])

        #     if len(table2.find_all('tr')) > 0:
        #         rows = rows[:-1]
        # else:
        #     raise Exception(f'Failed to scrape data from {url}. Error: {response2.status_code}')
        
        for r in rows:
            result = ""
            print(r)

            if r[5] != '-' and '-' in r[5]:
                result = r[5].split('-')[0] + ":" + r[5].split('-')[1][0]
                if r[3] == '(C)':
                    matches.append(Match(r[1], team, r[4], result, r[6]).to_dict())
                else:
                    matches.append(Match(r[1], r[4], team, result, r[6]).to_dict())

        # matches.reverse()
        print(str(len(matches)) + " matches scrapped for " + team)
        count = 0
        lastMatches = []
        for r in matches:
            if count == n:
                break
            lastMatches.append(r)
            count = count + 1
        return lastMatches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getNextMatchFromWF(url, team, season, allLeagues):
    print("\ngetting next match for " + team + ": " + str(url, 'utf-8'))
    matches = []
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table', class_="standard_tabelle")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])

        flag = False
        competition = ''
        for r in rows:
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
                        matches.append(Match(date.strftime('%Y-%m-%d'), team, r[11], '', competition).to_dict())
                    else:
                        matches.append(Match(date.strftime('%Y-%m-%d'), r[11], team, '', competition).to_dict())            

        print(str(len(matches)) + " matches scrapped for " + team)
        matches.sort(key=lambda match: datetime.strptime(match["date"], "%Y-%m-%d"))
        return matches[0]
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getLastNMatchesFromWF(url, n, team, allLeagues, season):
    print("\ngetting last " + str(n) + " match stats: " + str(url))
    matches = []
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find('table', class_="standard_tabelle")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            rows.append([el.text.strip() for el in row])

        flag = False
        competition = ''
        for r in rows:
            if len(r) < 10:
                if ('Friendlies' in r[1]) or (season not in r[1]):
                    flag = False
                else:
                    flag = True
                    competition = r[1]
            if (len(r) > 15) and (flag is True):
                if allLeagues is False and r[1] != 'Round':
                    continue
                result = ''
                if 'abor' in r[13] or 'resch' in r[13]:
                    continue
                if 'pso' in r[13] or 'aet' in r[13]:
                    result = r[13].replace('pso','').replace('aet','')
                else:
                    result = r[13].split(' ')[0]
                if len(r[13]) > 4 or r[13] != '-:-':
                    date = datetime.strptime(r[3], "%d/%m/%Y")
                    if r[7] == 'H':
                        matches.append(Match(date.strftime('%Y-%m-%d'), team, r[11], result, competition).to_dict())
                    else:
                        result = result.split(':')[1] + ':' + result.split(':')[0]
                        matches.append(Match(date.strftime('%Y-%m-%d'), r[11], team, result, competition).to_dict())        

        print(str(len(matches)) + " matches scrapped for " + team)
        matches.sort(key=lambda match: datetime.strptime(match["date"], "%Y-%m-%d"))
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
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getLiveMatchStatsFromAdA(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print("\ngetting live match stats: " + str(url))
        
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
    
def getLMPprgnosticos():
    response = requests.get('https://apostaslmp.pt/prognosticos/')
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        items = soup.find_all('div', class_="portfolio-item")

        prognosticos = []
        
        for i, item in enumerate(items):
            itemUrl = item.find('a', class_='-unlink')['href']  
            match = itemUrl.split('/')[5][12:]
            response2 = requests.get(itemUrl)
            if response.status_code == 200: 
                soup2 = BeautifulSoup(response2.content, 'html.parser')
                date = soup2.find_all('div', class_='elementor-widget-ohio_heading')[1].find('div', class_='subtitle').text.strip()
                homeAnalise = soup2.find_all('div', class_='elementor-widget-text-editor')[4].text.strip()
                awayAnalise = soup2.find_all('div', class_='elementor-widget-text-editor')[6].text.strip()
                prognostico = soup2.find_all('div', class_="elementor-col-14")[2].text.strip()
                odd = soup2.find_all('div', class_="elementor-col-14")[6].text.strip().replace('.',',')
                prognosticos.append(date + ';' + match + ' -> ' + prognostico + ';' + odd + ';' + homeAnalise + ';' + awayAnalise)
            else:
                raise Exception(f'Failed to scrape data from LMP Apostas. Error: {response.status_code}') 

        return prognosticos
    else:
        raise Exception(f'Failed to scrape data from LMP Apostas. Error: {response.status_code}')
    
def getNBASeasonMatchesFromESPN(url, team):
    print("\ngetting all season matches: " + str(url, 'utf-8'))
    matches = []

    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        allMatches = soup.find_all('tr', class_="Table__even")
        allMatches = allMatches[1:]

        # add playoff matches to allMatches list if there is any

        for match in allMatches:
            if "Post" in match.text:
                continue

            matchStatsUrl = match.find_all('a')[2]['href']
            response2 = requests.get(matchStatsUrl, headers=HEADERS)
            soup2 = BeautifulSoup(response2.content, 'html.parser')
            awayHTPoints = int(soup2.find_all('tbody', class_="Table__TBODY")[0].find_all('tr', class_="Table__TR--sm")[0].find_all('td')[1].text) + int(soup2.find_all('tbody', class_="Table__TBODY")[0].find_all('tr', class_="Table__TR--sm")[0].find_all('td')[2].text)
            homeHTPoints = int(soup2.find_all('tbody', class_="Table__TBODY")[0].find_all('tr', class_="Table__TR--sm")[1].find_all('td')[1].text) + int(soup2.find_all('tbody', class_="Table__TBODY")[0].find_all('tr', class_="Table__TR--sm")[1].find_all('td')[2].text)

            htResult = str(homeHTPoints) + ':' + str(awayHTPoints)

            ftResult = match.find_all('td')[2].text[0:1].strip()
            awayTeam = ''
            homeTeam = ''
            ftScore = ''
            if '@' in match.find_all('td')[1].text:
                awayTeam = team
                homeTeam = match.find_all('td')[1].text[2:]
                if ftResult is 'W':
                    ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[1] + ':' + match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[0]
                else:
                    ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':')
            else:
                homeTeam = team
                awayTeam = match.find_all('td')[1].text[2:]
                if ftResult is 'L':
                    ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[1] + ':' + match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[0]
                else:
                    ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':')
                
            if ' OT' in ftScore:
                ftScore = ftScore.replace(' OT', '') + ' OT'

            matches.append(Match(match.find_all('td')[0].text, homeTeam.strip(), awayTeam.strip(), htResult + ';' + ftScore, 'NBA').to_dict())    
            # break
        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')