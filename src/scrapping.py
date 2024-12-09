import requests
from flask import jsonify
from bs4 import BeautifulSoup
from obj.match import Match
import re
import Levenshtein
from datetime import datetime, timedelta
import sys, os
import csv
from collections import OrderedDict

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
                matches.append(Match(r[0], r[3], r[5], r[4].replace("-",":"), '', '', '').to_dict())
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


def getTipsFromO25Tips():
    matches = []
    for day in range(1,32):
        response = requests.get("https://www.over25tips.com/soccer-predictions/?date=2024-10-" + str("%02d" % day))
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Perform scraping operations using BeautifulSoup here
            table = soup.find('table', class_="predictionsTable")

            if table is not None:
                for i, row in enumerate(table.find_all('tr', class_="main-row")):
                    prediction = row.find('td', class_="soccerPredictions").text
                    competition = row.find('div', class_="h2prediction_info").find_all('span')[1].text.strip()
                    homeTeam = row.find('td', class_="new-home").text.strip()
                    awayTeam = row.find('td', class_="COL-5 left-align").text.strip()
                    if 'BTTS & Over' in prediction and competition != "" and len(row.find_all('td', class_="system-WIN")) >= 5:
                        gfg = [('1. datetime', str(day) + "-10-2024"), ('2. competition', competition), ('3. match', str(homeTeam + " Vs " + awayTeam))]
                        json_data = OrderedDict(gfg)
                        matches.append(json_data)

            response2 = requests.get("https://www.over25tips.com/soccer-predictions/?date=2024-10-"+ str("%02d" % day) +"&page=2")
            if response2.status_code == 200:
                soup = BeautifulSoup(response2.content, 'html.parser')
                # Perform scraping operations using BeautifulSoup here
                table2 = soup.find('table', class_="predictionsTable")

                if table2 is not None:
                    for i, row in enumerate(table2.find_all('tr', class_="main-row")):
                        prediction = row.find('td', class_="soccerPredictions").text
                        competition = row.find('div', class_="h2prediction_info").find_all('span')[1].text.strip()
                        homeTeam = row.find('td', class_="new-home").text.strip()
                        awayTeam = row.find('td', class_="COL-5 left-align").text.strip()
                        if 'BTTS & Over' in prediction and competition != "" and len(row.find_all('td', class_="system-WIN")) >= 5:
                            gfg = [('1. datetime', str(day) + "-10-2024"), ('2. competition', competition), ('3. match', str(homeTeam + " Vs " + awayTeam))]
                            json_data = OrderedDict(gfg)
                            matches.append(json_data)
        else:
            raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    return matches


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
                matches.append(Match(r[0], team, r[header.index("Opponent")], r[header.index("GF")].split(' ')[0]+':'+r[header.index("GA")].split(' ')[0], '', '', competition).to_dict())
            else:
                matches.append(Match(r[0], r[header.index("Opponent")], team, r[header.index("GA")].split(' ')[0]+':'+r[header.index("GF")].split(' ')[0], '', '', competition).to_dict())

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
                matches.append(Match(r[1], team, r[4], result, '', r[6]).to_dict())
            else:
                matches.append(Match(r[1], r[4], team, result, '', r[6]).to_dict())

        matches.reverse()
        print(str(len(matches)) + " matches scrapped for " + team)
        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getTomorrowMatchesFromWF(season):
    #2024-25: 
    #teams = ["1. FC Heidenheim 1846", "1. FC Kaiserslautern", "1. FC Köln", "1. FC Magdeburg", "1. FC Nurnberg", "1. FSV Mainz 05", "1899 Hoffenheim", "Aalborg BK", "Aalesunds FK", "AC Milan", "AC Sparta Praha", "ACF Fiorentina", "Adana Demirspor", "AEK Athen", "AFC Ajax", "Akhmat Grozny", "Al Ahli Jeddah", "Alanyaspor", "Albirex Niigata S", "Almere City FC", "Always Ready", "Arsenal FC", "AS Monaco", "AS Trenčín", "Aston Villa", "Atalanta", "Atletico Torque", "Atromitos", "Austria Lustenau", "Austria Wien", "AZ Alkmaar", "B36 Tórshavn", "Baník Ostrava", "Barcelona SC", "BATE Borisov", "Bayer Leverkusen", "Bayern München", "Beşiktaş", "Bodø/Glimt", "Bohemians Praha 1905", "Bolívar", "Bor. Mönchengladbach", "Borussia Dortmund", "Brann", "Brentford FC", "Brighton & Hove Albion", "Brøndby IF", "BSC Young Boys", "Cartaginés", "Çaykur Rizespor", "CD Hermanos Colmenarez", "CD Nacional", "Celtic FC", "Cercle Brugge", "Cliftonville", "Club América", "Club Brugge KV", "Colón de Santa Fe", "Copiapó", "Crvena Zvezda", "Crystal Palace", "Degerfors", "Degerfors IF", "Dinamo Kiev", "Dinamo Moskva", "Diriangén", "Eintracht Braunschweig", "Eintracht Frankfurt", "Emelec", "Espanyol Barcelona", "Estudiantes de Merida FC", "Eyüpspor", "Fatih Karagümrük SK", "FC Augsburg", "FC Basel 1893", "FC Blau Weiß Linz", "FC Hradec Králové", "FC København", "FC Lausanne-Sport", "FC Lorient", "FC Lugano", "FC Luzern", "FC Nordsjælland", "FC Porto", "FC Schalke 04", "FC Sion", "FC St. Gallen", "FC St. Pauli", "FC Twente", "FC Utrecht", "FC Volendam", "FC Zürich", "Fehérvár FC", "Fenerbahçe", "Ferencvárosi TC", "Feyenoord", "FK Krasnodar", "FK Mladá Boleslav", "FK Orenburg", "FK Sochi", "Flora Tallin", "Fortuna Dusseldorf", "Fortuna Sittard", "Fulham FC", "Galatasaray", "Gaziantep FK", "Gent", "Górnik Zabrze", "Göteborg", "Grasshopper Club Zürich", "Grazer AK", "Hacken", "Hamarkameratene", "Hamburger SV", "HamKam", "Hammarby", "Hannover 96", "Hellas Verona", "Heracles Almelo", "Hertha BSC", "HNK Rijeka", "Holstein Kiel", "Hvidovre IF", "IF Brommapojkarna", "IK Sirius", "Inter", "İstanbulspor AŞ", "Jagiellonia Białystok", "Jeonbuk Motors", "JK Tallinna Kalev", "JK Tammeka", "K Beerschot VA", "KAA Gent", "KAS Eupen", "Kayserispor", "KRC Genk", "Kuressaare", "KV Mechelen", "KVC Westerlo", "LASK", "LDU de Quito", "Leicester City", "Levadia Tallin", "Lille OSC", "Lillestrøm", "Linfield", "Lion City", "Liverpool FC", "Livingston FC", "Lokomotiv Moskva", "Lyngby BK", "Maccabi Haifa", "Maccabi Tel Aviv", "Malmö FF", "Manchester City", "Mansfield Town", "Melbourne Heart", "MFK Karviná", "Mineros de Guayana", "MKE Ankaragücü", "Molde", "Montpellier HSC", "Motherwell FC", "MŠK Žilina", "NAC Breda", "Nacional Potosí", "Newcastle United", "NK Domžale", "Norrkoping", "NorthEast United", "Nottingham Forest", "Odds BK", "Odense BK", "Olimpia", "Olympiakos Piraeus", "Olympique Lyonnais", "Olympique Marseille", "Oud-Heverlee Leuven", "Paksi SE", "PAOK Saloniki", "Paris Saint-Germain", "PEC Zwolle", "Pendikspor", "Pescara Calcio", "PFC Ludogorets Razgrad", "PSV Eindhoven", "Rangers FC", "Rapid Wien", "RB Leipzig", "RB Salzburg", "RC Lens", "RC Strasbourg", "Real Madrid", "Real Valladollid", "RKC Waalwijk", "Rosenborg", "Royal Pari", "RSC Anderlecht", "RWDM Brussels FC", "Sampdoria", "Samsunspor", "Sandefjord Fotball", "Santa Cruz", "Sarpsborg 08", "Sassuolo Calcio", "SBV Excelsior", "SC Freiburg", "sc Heerenveen", "SC Paderborn 07", "Servette FC", "Shakhtar Donetsk", "Silkeborg IF", "SK Austria Klagenfurt", "SK Dnipro-1", "SL Benfica", "Slavia Praha", "Slovan Bratislava", "SønderjyskE", "Southampthon FC", "Sparta Rotterdam", "Spartak Moskva", "Spartak Trnava", "Spezia Calcio", "Sporting Braga", "Sporting CP", "Sportivo Ameliano", "Sportivo Trinidense", "SpVgg Greuther Furth", "SSC Napoli", "St Patrick's Athletic", "St. Pauli", "Stade Lausanne-Ouchy", "Stade Rennais", "Stjarnan", "Strømsgodset IF", "Sturm Graz", "Sutjeska", "SV 07 Elversberg", "SV Darmstadt 98", "Sydney FC", "Tottenham Hotspur", "Trabzonspor", "TSC Bačka Topola", "TSV Hartberg", "UD Almería", "Újpest FC", "Unión La Calera", "Union Saint-Gilloise", "Universidad Catolica", "Universidad Católica", "US Salernitana 1919", "Valerenga", "Venezia FC", "VfB Stuttgart", "VfL Bochum", "VfL Wolfsburg", "Viborg FF", "Viking", "Víkingur Gøta", "Villarreal CF", "Vitesse", "Vojvodina", "Volos NFC", "Werder Bremen", "West Ham United", "Willem II", "Wolfsberger AC", "WSG Tirol", "Yverdon Sport FC", "Zagłębie Lubin", "Zalaegerszegi TE", "Zenit St. Petersburg", "Zilina" ];
    #2023-24: 
    #teams = ["Aalesunds FK", "Aktobe", "Always Ready", "Audax Italiano", "B36 Tórshavn", "Barcelona SC", "Bodø/Glimt", "Bolívar", "Brann", "CD Hermanos Colmenarez", "Colón de Santa Fe", "Curicó Unido", "Daegu", "Degerfors", "Degerfors IF", "Dinamo Tbilisi", "Emelec", "Flamengo RJ", "Flora Tallin", "Göteborg", "Guabirá", "Hacken", "Hamarkameratene", "HamKam", "Hammarby", "IK Sirius", "Jeonbuk Motors", "JK Tallinna Kalev", "JK Tammeka", "LDU de Quito", "Levadia Tallin", "Libertad Asuncion", "Lillestrøm", "Lion City", "Malmö FF", "Mineros de Guayana", "Molde", "Nacional Potosí", "Norrkoping", "Odds BK", "Olimpia", "Paide Linnameeskond", "Rosenborg", "Royal Pari", "Sandefjord Fotball", "Santa Cruz", "Sarpsborg 08", "Sporting Cristal", "Stabæk IF", "Stjarnan", "Strømsgodset IF", "The Strongest", "Tigre", "Tokyo Verdy", "Tromso", "Universidad Catolica", "Valerenga", "Viking", "Víkingur Gøta", "Zalgiris", "1899 Hoffenheim", "1. FC Kaiserslautern", "1. FC Köln", "1. FC Nurnberg", "1. FC Union Berlin", "1. FSV Mainz 05", "Aalborg BK", "ACF Fiorentina", "AC Monza", "AC Sparta Praha", "Adana Demirspor", "AEK Athen", "AFC Ajax", "Akhmat Grozny", "Al Ahli Jeddah", "Alanyaspor", "Almere City FC", "Arsenal FC", "AS Monaco", "Aston Villa", "AS Trenčín", "Atalanta", "Austria Lustenau", "Austria Wien", "AZ Alkmaar", "Bala Town FC", "Baník Ostrava", "Bayer Leverkusen", "Bayern München", "Beşiktaş", "Bohemians Praha 1905", "Bologna FC", "Bor. Mönchengladbach", "Borussia Dortmund", "Brentford FC", "Brescia", "Brighton & Hove Albion", "Brøndby IF", "BSC Young Boys", "Cartaginés", "Çaykur Rizespor", "Celtic FC", "Club Brugge KV", "Crvena Zvezda", "Dinamo Kiev", "Dinamo Moskva", "Eintracht Braunschweig", "Eintracht Frankfurt", "Elche", "Empoli FC", "Fatih Karagümrük SK", "FC Ashdod", "FC Augsburg", "FC Basel 1893", "FC Blau Weiß Linz", "FC Hradec Králové", "FC Lausanne-Sport", "FC Luzern", "FC Nordsjælland", "FC Porto", "FC Schalke 04", "FC Sion", "FC St. Gallen", "FC St. Pauli", "FC Twente", "FC Utrecht", "FC Volendam", "FC Zürich", "Fehérvár FC", "Fenerbahçe", "Ferencvárosi TC", "Feyenoord", "FK Jablonec", "FK Krasnodar", "FK Mladá Boleslav", "FK Oleksandriya", "FK Orenburg", "FK Rostov", "FK Sochi", "FK Teplice", "Fortuna Dusseldorf", "Fortuna Sittard", "Galatasaray", "Gaziantep FK", "Gent", "Göztepe", "Grasshopper Club Zürich", "Grazer AK", "Hajduk Split", "Hamburger SV", "Hannover 96", "Hellas Verona", "Heracles Almelo", "Hertha BSC", "HNK Gorica", "HNK Rijeka", "Holstein Kiel", "Inter", "İstanbulspor AŞ", "Jagiellonia Białystok", "Juventus", "KAA Gent", "Karlsruher SC", "KAS Eupen", "Kayserispor", "KRC Genk", "KVC Westerlo", "KV Kortrijk", "KV Mechelen", "LASK", "Lazio Roma", "Leicester City", "Lille OSC", "Linfield", "Liverpool FC", "Livingston FC", "Lokomotiv Moskva", "Lyngby BK", "Maccabi Haifa", "Manchester City", "Melbourne Heart", "MFK Karviná", "Motherwell FC", "MŠK Žilina", "NAC Breda", "NK Domžale", "NorthEast United", "Odense BK", "Olympique Lyonnais", "Olympique Marseille", "Oud-Heverlee Leuven", "Paksi SE", "Paphos FC", "Paris Saint-Germain", "PEC Zwolle", "Pendikspor", "Pescara Calcio", "PFC Beroe", "PFC Ludogorets Razgrad", "PSV Eindhoven", "Randers FC", "Rangers FC", "Rapid Wien", "RB Leipzig", "RB Salzburg", "Real Betis", "RKC Waalwijk", "Sampdoria", "Samsunspor", "Sassuolo Calcio", "SBV Excelsior", "SC Freiburg", "sc Heerenveen", "SC Paderborn 07", "Servette FC", "Shakhtar Donetsk", "Silkeborg IF", "SK Austria Klagenfurt", "SK Dnipro-1", "Śląsk Wrocław", "Slavia Praha", "SL Benfica", "Slovan Bratislava", "SønderjyskE", "Southampthon FC", "Spartak Moskva", "Sparta Rotterdam", "Spezia Calcio", "Sporting Charleroi", "Sporting CP", "SpVgg Greuther Furth", "SSC Napoli", "Stade Lausanne-Ouchy", "Standard Liège", "St. Pauli", "Sturm Graz", "Sutjeska", "SV 07 Elversberg", "SV Darmstadt 98", "Sydney FC", "Tottenham Hotspur", "Trabzonspor", "TSC Bačka Topola", "TSV Hartberg", "Újpest FC", "Ümraniyespor", "Union Saint-Gilloise", "US Salernitana 1919", "Valencia CF", "Venezia FC", "VfB Stuttgart", "VfL Bochum", "VfL Wolfsburg", "Viborg FF", "Villarreal CF", "Vitesse", "Werder Bremen", "West Ham United", "Willem II", "Wolfsberger AC", "WSG Tirol", "Yverdon Sport FC", "Zagłębie Lubin", "Zalaegerszegi TE", "Zenit St. Petersburg", "Zilina" ];
    #2022-23: 
    #teams = [ "1899 Hoffenheim", "1. FC Kaiserslautern", "1. FC Köln", "1. FC Nurnberg", "1. FC Union Berlin", "1. FSV Mainz 05", "Aalborg BK", "ACF Fiorentina", "AC Sparta Praha", "Adana Demirspor", "AEK Athen", "AFC Ajax", "Al Ahli Jeddah", "Almere City FC", "Apollon Limassol", "Arsenal FC", "AS Monaco", "AS Roma", "Aston Villa", "AS Trenčín", "Atalanta", "Austria Lustenau", "Austria Wien", "AZ Alkmaar", "Bala Town FC", "Baník Ostrava", "Bayer Leverkusen", "Bayern München", "Beşiktaş", "Bodrum FK", "Bologna FC", "Bor. Mönchengladbach", "Borussia Dortmund", "Brentford FC", "Brescia", "Brøndby IF", "BSC Young Boys", "Cagliari Calcio", "Cartaginés", "Çaykur Rizespor", "Celtic FC", "Chelsea FC", "Club Brugge KV", "Crvena Zvezda", "Dinamo Kiev", "Eintracht Braunschweig", "Eintracht Frankfurt", "Empoli FC", "FC Augsburg", "FC Barcelona", "FC Basel 1893", "FC Blau Weiß Linz", "FC Hradec Králové", "FC København", "FC Lausanne-Sport", "FC Luzern", "FC Nordsjælland", "FC Porto", "FC Schalke 04", "FC Sion", "FC St. Gallen", "FC St. Pauli", "FC Twente", "FC Utrecht", "FC Volendam", "FC Winterthur", "FC Zürich", "Fenerbahçe", "Ferencvárosi TC", "Feyenoord", "FK Krasnodar", "FK Mladá Boleslav", "FK Oleksandriya", "FK Orenburg", "FK Teplice", "Fortuna Dusseldorf", "Fortuna Sittard", "Galatasaray", "Gaziantep FK", "Genoa CFC", "Gent", "Göztepe", "Grasshopper Club Zürich", "Grazer AK", "Hajduk Split", "Hamburger SV", "Hannover 96", "Hapoel Haifa", "Hellas Verona", "Heracles Almelo", "Hertha BSC", "HNK Gorica", "HNK Rijeka", "Holstein Kiel", "Inter", "İstanbulspor AŞ", "Juventus", "KAA Gent", "Karlsruher SC", "KAS Eupen", "Kasımpaşa SK", "Kayserispor", "Kerala Blasters", "KRC Genk", "KVC Westerlo", "KV Kortrijk", "KV Mechelen", "LASK", "Lazio Roma", "Leicester City", "Linfield", "Liverpool FC", "ŁKS Łódź", "Lokomotiva Zagreb", "Lyngby BK", "Maccabi Haifa", "Manchester City", "Manchester United", "Melbourne Heart", "MFK Karviná", "MFK Zemplín Michalovce", "MŠK Žilina", "NAC Breda", "NEC Nijmegen", "Newcastle United", "NK Aluminij", "NK Domžale", "NK Istra 1961", "NK Maribor", "NK Rudeš", "Odense BK", "Olympique Lyonnais", "Olympique Marseille", "Oud-Heverlee Leuven", "Paksi SE", "Paphos FC", "Paris Saint-Germain", "PEC Zwolle", "Pendikspor", "Pescara Calcio", "PSV Eindhoven", "Puskás FC", "Randers FC", "Rapid Wien", "RB Leipzig", "RB Salzburg", "Real Betis", "RKC Waalwijk", "Ross County FC", "RSC Anderlecht", "Sampdoria", "Sassuolo Calcio", "SBV Excelsior", "SC Freiburg", "sc Heerenveen", "SC Paderborn 07", "SCR Altach", "Servette FC", "Shakhtar Donetsk", "Silkeborg IF", "SK Austria Klagenfurt", "SK Dnipro-1", "Śląsk Wrocław", "Slavia Praha", "SL Benfica", "Slovan Bratislava", "SønderjyskE", "Southampthon FC", "Sparta Rotterdam", "Spezia Calcio", "Sporting Charleroi", "Sporting CP", "SpVgg Greuther Furth", "SSC Napoli", "Stade Brestois 29", "Stade Lausanne-Ouchy", "Standard Liège", "St. Pauli", "Sturm Graz", "Sutjeska", "SV Darmstadt 98", "Sydney FC", "Trabzonspor", "TSC Bačka Topola", "TSV Hartberg", "Union Saint-Gilloise", "US Lecce", "Valencia CF", "Vejle BK", "VfB Stuttgart", "VfL Bochum", "VfL Wolfsburg", "Viborg FF", "Villarreal CF", "Vitesse", "Werder Bremen", "West Ham United", "Willem II", "Wolfsberger AC", "WSG Tirol", "Yverdon Sport FC", "Zagłębie Lubin", "Zalaegerszegi TE", "Zenit St. Petersburg", "Zilina", "Aalesunds FK", "Aktobe", "Always Ready", "Atletico Torque", "B36 Tórshavn", "Barcelona SC", "BATE Borisov", "Blooming", "Bodø/Glimt", "Bolívar", "Brann", "CD Hermanos Colmenarez", "Club Guarani", "Daegu", "Defensor Sporting", "Degerfors", "Degerfors IF", "Delfin SC", "Deportivo Cuenca", "Dinamo Tbilisi", "Emelec", "Fenix", "Flamengo RJ", "Flora Tallin", "Göteborg", "Guabirá", "Hacken", "Hamarkameratene", "HamKam", "Hammarby", "IK Sirius", "Independiente del Valle", "Jeonbuk Motors", "JK Tallinna Kalev", "Jorge Wilstermann", "Kjelsas", "Kuressaare", "Levadia Tallin", "Libertad Asuncion", "Lillestrøm", "Lion City", "Liverpool Montevideo", "Malmö FF", "Molde", "Nacional Potosí", "Nõmme Kalju", "Norrkoping", "Odds BK", "Olimpia", "Paide Linnameeskond", "Palestino", "Rosenborg", "Royal Pari", "Sandefjord Fotball", "Sarpsborg 08", "Sporting Cristal", "Stabæk IF", "Stjarnan", "Strømsgodset IF", "The Strongest", "Unión Española", "Universidad Catolica", "Valerenga", "Viking", "Víkingur Gøta", "Wanderers" ];
    #2021-22: 
    #teams = ["Aalesunds FK", "Arsenal de Sarandí", "Astana", "Audax Italiano", "B36 Tórshavn", "Barcelona SC", "Blooming", "Bodø/Glimt", "Bolívar", "Brann", "CD Hermanos Colmenarez", "Club Guarani", "Daegu", "Defensor Sporting", "Degerfors", "Degerfors IF", "Deportivo Cuenca", "Dinamo Tbilisi", "Djurgårdens IF", "Fenix", "Flamengo RJ", "Flora Tallin", "Göteborg", "Guabirá", "Hacken", "Hamarkameratene", "HamKam", "Hammarby", "HJK Helsinki", "Huachipato", "IK Sirius", "Independiente del Valle", "Jeju United", "Jeonbuk Motors", "JK Tallinna Kalev", "Levadia Tallin", "Lillestrøm", "Lion City", "Liverpool Montevideo", "Malmö FF", "Mjällby AIF", "Molde", "Nagoya Grampus", "Nõmme Kalju", "Norrkoping", "Olimpia", "Paide Linnameeskond", "Rosenborg", "Sandefjord Fotball", "Sarpsborg 08", "Sport Huancayo", "Sporting Cristal", "Stabæk IF", "Stjarnan", "Strømsgodset IF", "The Strongest", "Tigre", "Unión Española", "Universidad de Chile", "Universitario", "Valerenga", "Viking", "Víkingur Gøta", "Wanderers", "1899 Hoffenheim", "1. FC Kaiserslautern", "1. FC Nurnberg", "1. FC Union Berlin", "1. FSV Mainz 05", "Aberdeen FC", "ACF Fiorentina", "Adana Demirspor", "AFC Ajax", "Al Ahli Jeddah", "Al Ahly Cairo", "Almere City FC", "Apollon Limassol", "Arsenal FC", "AS Monaco", "AS Roma", "AS Trenčín", "Atalanta", "Austria Lustenau", "Austria Wien", "AZ Alkmaar", "Bala Town FC", "Baník Ostrava", "Bayer Leverkusen", "Bayern München", "Beşiktaş", "Bodrum FK", "Bologna FC", "Bor. Mönchengladbach", "Borussia Dortmund", "Brescia", "Brøndby IF", "BSC Young Boys", "Çaykur Rizespor", "Celtic FC", "Cliftonville", "Club Brugge KV", "Crvena Zvezda", "Debreceni VSC", "Diósgyöri VTK", "Doxa Katokopias", "Dundee United", "Eintracht Braunschweig", "Eintracht Frankfurt", "Empoli FC", "Ethnikos Achna", "FC Ashdod", "FC Augsburg", "FC Barcelona", "FC Basel 1893", "FC Blau Weiß Linz", "FC Hradec Králové", "FC Lausanne-Sport", "FC Luzern", "FC Nordsjælland", "FC Porto", "FCSB", "FC Schalke 04", "FC Sion", "FC St. Gallen", "FC St. Pauli", "FC Twente", "FC Utrecht", "FC Volendam", "FC Winterthur", "FC Zürich", "Fenerbahçe", "Ferencvárosi TC", "Feyenoord", "FK Dukla Praha", "FK Jablonec", "FK Krasnodar", "FK Mladá Boleslav", "FK Napredak", "FK Oleksandriya", "FK Teplice", "Fortuna Dusseldorf", "Fortuna Sittard", "Galatasaray", "Genoa CFC", "Gent", "Go Ahead Eagles", "Göztepe", "Grasshopper Club Zürich", "Grazer AK", "Greenock Morton", "Hajduk Split", "Hannover 96", "Hapoel Haifa", "Hellas Verona", "Heracles Almelo", "Hertha BSC", "HNK Gorica", "HNK Rijeka", "Holstein Kiel", "Hvidovre IF", "İstanbul Başakşehir", "İstanbulspor AŞ", "Juventus", "KAA Gent", "KAS Eupen", "Kasımpaşa SK", "Kayserispor", "KRC Genk", "KVC Westerlo", "KV Kortrijk", "KV Mechelen", "LASK", "Lazio Roma", "Leicester City", "Lille OSC", "Linfield", "Liverpool FC", "ŁKS Łódź", "Luton Town", "Lyngby BK", "Maccabi Haifa", "Manchester City", "Melbourne Heart", "Meuselwitz", "MFK Zemplín Michalovce", "MŠK Žilina", "NEC Nijmegen", "NK Aluminij", "NK Celje", "NK Domžale", "NK Maribor", "NK Osijek", "NK Rudeš", "Odense BK", "OGC Nice", "Olympiakos Piraeus", "Olympique Lyonnais", "Olympique Marseille", "Oud-Heverlee Leuven", "Paksi SE", "PAOK Saloniki", "Paris Saint-Germain", "PEC Zwolle", "Pendikspor", "Pescara Calcio", "PFC Ludogorets Razgrad", "PSV Eindhoven", "Puskás FC", "Queen's Park", "Randers FC", "Rapid Wien", "RB Leipzig", "RB Salzburg", "RC Celta", "RC Strasbourg", "Real Betis", "Real Madrid", "RKC Waalwijk", "Ross County FC", "Royal Antwerp FC", "Sampdoria", "Sassuolo Calcio", "SBV Excelsior", "SC Freiburg", "sc Heerenveen", "SC Paderborn 07", "Servette FC", "Shakhtar Donetsk", "Silkeborg IF", "SK Austria Klagenfurt", "Śląsk Wrocław", "SL Benfica", "Slovan Bratislava", "Southampthon FC", "Spartak Subotica", "Sparta Rotterdam", "Sporting Charleroi", "Sporting CP", "SpVgg Greuther Furth", "SSC Napoli", "Stade Lausanne-Ouchy", "Standard Liège", "St. Pauli", "Sturm Graz", "SV Darmstadt 98", "Sydney FC", "Torino FC", "Tottenham Hotspur", "Trabzonspor", "TSV Hartberg", "Union Saint-Gilloise", "US Lecce", "Valencia CF", "VfB Stuttgart", "VfL Bochum", "VfL Wolfsburg", "Viborg FF", "Villarreal CF", "Vitesse", "Werder Bremen", "West Ham United", "Willem II", "Wolfsberger AC", "WSG Tirol", "Yverdon Sport FC", "Zagłębie Lubin", "Zenit St. Petersburg", "Zilina" ];
    #2020-21: 
    #teams = [ "1899 Hoffenheim", "1. FC Heidenheim 1846", "1. FC Kaiserslautern", "1. FC Köln", "1. FC Nurnberg", "1. FC Union Berlin", "1. FSV Mainz 05", "Aberdeen FC", "Adana Demirspor", "AFC Ajax", "AFC Bournemouth", "Al Ahli Jeddah", "Almere City FC", "Apollon Limassol", "Arsenal FC", "AS Monaco", "AS Roma", "AS Trenčín", "Atalanta", "Austria Lustenau", "Austria Wien", "AZ Alkmaar", "Bala Town FC", "Bayer Leverkusen", "Bayern München", "Beşiktaş", "Bodrum FK", "Bor. Mönchengladbach", "Borussia Dortmund", "Brescia", "Brøndby IF", "BSC Young Boys", "Cagliari Calcio", "Çaykur Rizespor", "Celtic FC", "Chelsea FC", "Club Brugge KV", "Crvena Zvezda", "Debreceni VSC", "Diósgyöri VTK", "Doxa Katokopias", "Dundee United", "Eintracht Braunschweig", "Empoli FC", "Ethnikos Achna", "Everton FC", "FC Augsburg", "FC Barcelona", "FC Basel 1893", "FC Blau Weiß Linz", "FC Lausanne-Sport", "FC Luzern", "FC Midtjylland", "FC Nordsjælland", "FC Schalke 04", "FC Sion", "FC St. Gallen", "FC St. Pauli", "FC Twente", "FC Utrecht", "FC Volendam", "FC Winterthur", "FC Zlín", "FC Zürich", "Ferencvárosi TC", "Feyenoord", "FK Dukla Praha", "FK Jablonec", "FK Krasnodar", "FK Mladá Boleslav", "FK Teplice", "Fortuna Dusseldorf", "Fortuna Sittard", "Fulham FC", "Galatasaray", "Go Ahead Eagles", "Górnik Zabrze", "Göztepe", "Grasshopper Club Zürich", "Greenock Morton", "Hajduk Split", "Hannover 96", "Hellas Verona", "Heracles Almelo", "Hertha BSC", "Hibernian FC", "HNK Rijeka", "Holstein Kiel", "Juventus", "KAS Eupen", "Kasımpaşa SK", "Kayserispor", "KRC Genk", "KS Cracovia", "KVC Westerlo", "KV Kortrijk", "KV Mechelen", "LASK", "Lazio Roma", "Leicester City", "Liverpool FC", "Luton Town", "Lyngby BK", "Manchester City", "Manchester United", "Melbourne Heart", "Meuselwitz", "MFK Zemplín Michalovce", "Motherwell FC", "MŠK Žilina", "NEC Nijmegen", "NK Aluminij", "NK Celje", "NK Domžale", "Olympique Lyonnais", "Olympique Marseille", "Oud-Heverlee Leuven", "Paris Saint-Germain", "PEC Zwolle", "Pescara Calcio", "PFC Ludogorets Razgrad", "PSV Eindhoven", "Queen's Park", "Randers FC", "Rapid Wien", "RB Leipzig", "RC Celta", "RC Strasbourg", "Real Madrid", "Real Sociedad", "RKC Waalwijk", "Ross County FC", "Royal Antwerp FC", "Sampdoria", "Sassuolo Calcio", "SBV Excelsior", "SC Freiburg", "sc Heerenveen", "SC Paderborn 07", "Servette FC", "Sevilla FC", "Shakhtar Donetsk", "Silkeborg IF", "SK Austria Klagenfurt", "Śląsk Wrocław", "SL Benfica", "Sparta Rotterdam", "SSC Napoli", "Stade Lausanne-Ouchy", "St. Mirren FC", "St. Pauli", "Sturm Graz", "SV Darmstadt 98", "Sydney FC", "Torino FC", "Tottenham Hotspur", "Trabzonspor", "TSV Hartberg", "Union Saint-Gilloise", "US Lecce", "Valencia CF", "VfB Stuttgart", "VfL Bochum", "Vitesse", "Werder Bremen", "West Ham United", "Willem II", "Wolfsberger AC", "WSG Tirol", "Zenit St. Petersburg", "Zilina", "Albirex Niigata S", "Audax Italiano", "Barcelona SC", "Bodø/Glimt", "Club Guarani", "Cobresal", "Daegu", "Degerfors", "Degerfors IF", "Dinamo Tbilisi", "Djurgårdens IF", "Flora Tallin", "Göteborg", "Hacken", "Hamarkameratene", "HamKam", "Hammarby", "Huachipato", "IK Sirius", "Independiente Medellin", "Jeonbuk Motors", "JK Narva Trans", "JK Tammeka", "Levadia Tallin", "Lillestrøm", "Lion City", "Malmö FF", "Molde", "Nacional Asuncion", "Nagoya Grampus", "Nõmme Kalju", "Norrkoping", "Olimpia", "Paide Linnameeskond", "Palestino", "Racing Montevideo", "Rosenborg", "Sandefjord Fotball", "Sarpsborg 08", "Sport Huancayo", "Sporting Cristal", "Sportivo Luqueno", "Stabæk IF", "Stjarnan", "Strømsgodset IF", "Suwon Bluewings", "Tromso", "Unión Española", "Universidad de Chile", "Universitario", "Valerenga", "Viking", "Víkingur Gøta", "Wanderers" ];

    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    # Get today's date
    today = datetime.now()

    # Calculate tomorrow's date
    tomorrow = today + timedelta(days=1)

    # Format the date as 2024/oct/22/
    formatted_tomorrow = tomorrow.strftime("%Y/%b/%d/").lower()
    matches = []
    
    for year in [season]:
        #for m in [ "jan", "feb", "mar", "apr", "may", "jun"]:
        #for m in [ "jul", "aug", "sep", "oct", "nov", "dec"]:
        for m in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec" ]:
        #for m in ["jan"]:
            matches.append(m)
            for j in range(1, 32):
                print(datetime.now())
                print(year + "-" + m + "-" + str(j))
                response = requests.get("https://www.worldfootball.net/matches_today/" + year + "/" + m + "/" + str(j))
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Perform scraping operations using BeautifulSoup here
                    table = soup.find('table', class_="standard_tabelle")
                
                    # then we can iterate through each row and extract either header or row values:
                    header = []
                    rows = []
                    competition = ''
                    for i, row in enumerate(table.find_all('tr')):
                        rows.append([el.text.strip() for el in row])

                        first_goal = ''
                        second_goal = ''
                        h2hmatches = ''
                        h2hgoals = ''
                        
                        try:
                            r = [el.text.strip() for el in row]
                            if len(r) <= 7:
                                competition = r[3]

                            if (len(r) > 7):
                            #if (len(r) > 7) and any(item.lower().replace(' ', '') not in competition.lower().replace(' ', '') for item in comps):
                            #if (len(r) > 7 and r[3] in teams and r[7] in teams ):
                                if len(row.find_all('a')) > 2:
                                    response3 = requests.get("https://www.worldfootball.net/" + row.find_all('a')[2]['href'])
                                    
                                    if response3.status_code == 200:
                                        soup3 = BeautifulSoup(response3.content, 'html.parser')
                                        table3 = soup3.find_all('table', class_="standard_tabelle")[1]
                                        
                                        # Extract goal minutes
                                        goal_minutes = []

                                        # Loop through each table row after the header row
                                        for row3 in table3.find_all('tr')[1:]:  # Skip header row
                                            # Find the second <td> element which contains the player and goal minute
                                            if len(row3.find_all('td')) > 1:
                                                goal_cell = row3.find_all('td')[1].text
                                                
                                                # Use regex to find the goal minute (number before a period, like "8." or "17.")
                                                match = re.search(r'\b\d{1,2}\b(?=\.)', goal_cell)
                                                if match:
                                                    goal_minutes.append(match.group())

                                        if len(goal_minutes) > 1:
                                            second_goal = goal_minutes[1]
                                        if len(goal_minutes) > 0:
                                            first_goal = goal_minutes[0]


                                        h2hurl = soup3.find_all('table', class_="auswahlbox")[1].find_all('a')[-1]['href']
                                        response4 = requests.get("https://www.worldfootball.net" + h2hurl)
                                    
                                        if response4.status_code == 200:
                                            soup4 = BeautifulSoup(response4.content, 'html.parser')
                                            table4 = soup4.find_all('table', class_="standard_tabelle")[0]
                                            h2hmatches = table4.find_all('tr')[-1].find_all('td')[2].text
                                            h2hgoals = int(table4.find_all('tr')[-1].find_all('td')[-3].text) + int(table4.find_all('tr')[-1].find_all('td')[-1].text)
                                
                                matches.append(str(f"{j:02}") + "-99-" + year + " " + r[1] + " ; " + competition + " ; " + r[3] + " - " + r[7] + " ; " + r[9] + " ; " + first_goal + " ; " + second_goal + " ; " + h2hmatches + " ; " + str(h2hgoals))         
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)                        
                else:
                    raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
                # Open file in write mode
                with open("/home/data.csv", "a", newline='') as file:
                    writer = csv.writer(file)
                    # Write each element as a row
                    for item in matches:
                        writer.writerow([item])
                matches = []
                
    return matches


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
            if (len(r) > 15) and (flag is True) and '(' in r[13]:
                if allLeagues is False and r[1] != 'Round':
                    continue
                ftResult = ''
                if 'pso' in r[13] or 'aet' in r[13]:
                    ftResult = r[13].split(',')[1].split(')')[0].strip()
                    htResult = r[13].split(',')[0].split('(')[1].strip()
                else:
                    ftResult = r[13].split(' ')[0]
                    htResult = r[13].split(' ')[1].replace('(','').replace(')','')
                    print(htResult)
                if ':' in ftResult:
                    if r[7] == 'H':
                        matches.append(Match(r[3], team, r[11], ftResult, htResult, competition).to_dict())
                    else:
                        ftResult = ftResult.split(':')[1] + ':' + ftResult.split(':')[0]
                        htResult = htResult.split(':')[1] + ':' + htResult.split(':')[0]
                        matches.append(Match(r[3], r[11], team, ftResult, htResult, competition).to_dict())            

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
                    matches.append(Match(r[1], team, r[4], result, '', r[6]).to_dict())
                else:
                    matches.append(Match(r[1], r[4], team, result, '', r[6]).to_dict())

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
                    matches.append(Match(r[1], team, r[4], result, '', r[6]).to_dict())
                else:
                    matches.append(Match(r[1], r[4], team, result, '', r[6]).to_dict())

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
                        matches.append(Match(date.strftime('%Y-%m-%d'), team, r[11], '', '', competition).to_dict())
                    else:
                        matches.append(Match(date.strftime('%Y-%m-%d'), r[11], team, '', '', competition).to_dict())            

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
            print(r)
            if len(r) < 10:
                if ('Friendlies' in r[1]) or (season not in r[1]):
                    flag = False
                else:
                    flag = True
                    competition = r[1]
            if (len(r) > 15) and (flag is True) and '(' in r[13]:
                if allLeagues is False and r[1] != 'Round':
                    continue
                ftResult = ''
                if ('pso' in r[13] or 'aet' in r[13] or 'dec' in r[13]) and ',' in r[13]:
                    ftResult = r[13].split(',')[1].split(')')[0].strip()
                    htResult = r[13].split(',')[0].split('(')[1].strip().replace(',','')
                elif 'n.P.' in r[13]:
                    ftResult = r[13].split(',')[1].strip()
                    htResult = r[13].split(',')[0].split('(')[1].strip().replace(',','')
                else:
                    ftResult = r[13].split(' ')[0]
                    htResult = r[13].split(' ')[1].replace('(','').replace(')','').replace(',','')
                if ':' in ftResult:
                    if r[7] == 'H':
                        matches.append(Match(r[3], team, r[11], ftResult, htResult, competition).to_dict())
                    else:
                        ftResult = ftResult.split(':')[1] + ':' + ftResult.split(':')[0]
                        htResult = htResult.split(':')[1] + ':' + htResult.split(':')[0]
                        matches.append(Match(r[3], r[11], team, ftResult, htResult, competition).to_dict())    
                else:
                    print(r)            

        print(str(len(matches)) + " matches scrapped for " + team)
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
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')

def getLeagueTeamsFromWF(url):
    print("\ngetting league teams: " + str(url))
    teams = {}
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Perform scraping operations using BeautifulSoup here
        table = soup.find_all('table', class_="standard_tabelle")[1]
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            if i != 0:
                rows.append([el.text.strip() for el in row])

        for i, r in enumerate(rows):
            teams[r[5].split('\n')[0]] = i+1;
            # break
        return teams
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
            try:
                if '@' in match.find_all('td')[1].text:
                    awayTeam = team
                    homeTeam = match.find_all('td')[1].text[2:]
                    if ftResult == 'W':
                        ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[1] + ':' + match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[0]
                    else:
                        ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':')
                else:
                    homeTeam = team
                    awayTeam = match.find_all('td')[1].text[2:]
                    if ftResult == 'L':
                        ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[1] + ':' + match.find_all('td')[2].text[1:].strip().replace('-',':').split(':')[0]
                    else:
                        ftScore = match.find_all('td')[2].text[1:].strip().replace('-',':')
                    
                if ' OT' in ftScore:
                    ftScore = ftScore.replace(' OT', '') + ' OT'

                matches.append(Match(match.find_all('td')[0].text, homeTeam.strip(), awayTeam.strip(), htResult + ';' + ftScore, '', 'NBA').to_dict())    
            except Exception as e:
                print(str(e))
        return matches
    else:
        raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')