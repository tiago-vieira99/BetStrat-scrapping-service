import csv
from collections import Counter
import pandas as pd
from datetime import datetime, timedelta
import requests
import sys, os
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generateFileForNextMatchesEbookStrategy():
    matches = []

    # Get today's date
    today = datetime.now()

    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];
    
    #2025 teams:
    teams = ["Göztepe", "Dinamo Kiev", "FK Voždovac", "Asteras Tripolis", "Rubin Kazan", "St Patrick's Athletic", "Vélez Sarsfield", "Zalgiris", "Real Zaragoza", "Real Valladollid", "Vasco da Gama - RJ", "Botafogo - RJ", "CFR Cluj", "FK Ural", "Empoli FC", "Wolverhampton Wanderers", "Shamrock Rovers", "Granada CF", "Radnik Surdulica", "PFC Beroe", "La Equidad", "Deportivo Pereira", "Independiente", "Independiente del Valle", "Club Brugge KV", "Paris FC", "Santa Fe", "FK Napredak", "Racing", "Lech Poznań", "Konyaspor", "CD Leganés", "Tigre", "Caracas FC", "Bahia - BA", "Juventus", "Kilmarnock FC", "Heart of Midlothian", "Machida Zelvia", "Hajduk Split", "Partizan", "Bohemian FC", "Livingston FC", "FK Nizhny Novgorod", "FC Nantes", "JK Narva Trans", "Zorya Lugansk", "Gil Vicente", "MFK Zemplín Michalovce", "Reggina Calcio", "Instituto de Córdoba", "Aarhus GF", "Inter", "GS Kallithea", "Mezőkövesdi SE", "FC Blau Weiß Linz", "AFC Wimbledon", "AmaZulu", "AE Kifisias", "Tenerife", "Arsenal de Sarandí", "Sarmiento de Junín", "Newell's Old Boys", "Crvena Zvezda", "Atlético Palmaflor", "Club Olimpia", "AC Milan", "CD Santa Clara", "Real Tomayapo", "Atlético Bucaramanga", "América - MG", "Atlético Mineiro", "Olimpija Ljubljana", "RC Lens", "Once Caldas", "Busan I'Park", "Fénix", "FC Voluntari", "Patriotas FC", "Omonia Nikosia", "Baltika Kaliningrad", "Tigres FC", "FC Famalicão", "Standard Liège", "FK Čukarički", "Kauno Zalgiris", "Racing Club", "Oriente Petrolero", "KAA Gent", "FK Haugesund", "Nõmme Kalju", "Deportes Tolima", "1. FC Union Berlin", "Everton", "Apollon Limassol", "Montevideo Wanderers", "OGC Nice", "Academia Puerto Cabello", "Paphos FC", "Ipswich Town", "Newcastle United", "K Beerschot VA", "América de Cali", "FC Porto", "Olympiakos Piraeus", "Talleres de Córdoba", "Aberdeen FC", "KS Cracovia", "AS Saint-Étienne", "AS Roma", "Club Nacional", "Plaza Colonia", "Doxa Katokopias", "Sol de América", "GD Estoril", "Sheffield United", "Vojvodina", "AC Ajaccio", "SSC Napoli", "FC Twente", "Daegu", "Gamba Osaka", "Lille OSC", "Levadia Tallin", "Mushuc Runa", "Austria Wien", "Lamia", "Aucas", "Austria Lustenau", "Maccabi Tel Aviv", "Hvidovre IF", "Unión La Calera", "KAS Eupen", "Sporting Charleroi", "Dynamo České Budějovice", "Gualaceo SC", "WSG Tirol", "Alianza FC", "Libertad", "Cerezo Osaka", "Celtic FC", "Gent", "Royal Antwerp FC", "CS Universitatea Craiova", "Deportivo Pasto", "Jaguares de Córdoba", "Sturm Graz", "Sigma Olomouc", "1. FC Slovácko", "Korona Kielce", "Banfield", "PAOK Saloniki", "Peñarol", "Flora Tallin", "Estudiantes de Mérida FC", "Hapoel Haifa", "Moreirense FC", "AEK Athen", "APOEL Nikosia", "FC Botoşani", "Patronato Paraná", "Racing Santander", "Dundee FC", "Hapoel Be'er Sheva", "UD Las Palmas", "San Lorenzo", "FC Tokyo", "Nacional", "Bolívar", "Ferencvárosi TC", "Lazio Roma", "Arsenal FC", "FC Barcelona", "Millonarios", "NK Istra 1961", "MFK Ružomberok", "Kalmar", "Zamora FC", "Slavia Sofia", "Werder Bremen", "Piast Gliwice", "Radnički Niš", "Belgrano de Córdoba", "Lokomotiv Plovdiv", "Carabobo FC", "Dinamo Tbilisi", "Paços de Ferreira", "Aswan FC", "Fehérvár FC", "SønderjyskE", "AEK Larnaca", "Barcelona", "Defensor Sporting", "Rayo Vallecano", "Genoa CFC", "Always Ready", "Universidad Católica", "Halmstad", "Eyüpspor", "Lechia Gdańsk", "Beitar Jerusalem", "Volos NFC", "Huachipato", "FC DAC 1904", "Dundee United", "Cumbayá", "Frosinone Calcio", "Rayo Zuliano", "Hansa Rostock", "FK Pardubice", "Sport Huancayo", "Zlaté Moravce", "Amiens SC", "Pontedera", "Baroka", "Royal AM", "Sutjeska", "São Paulo FC", "Malmö FF", "Brann", "Sportivo Luqueño", "FBC Melgar", "Ebro", "Odense BK", "Vitória Guimarães", "FCSB", "BATE Borisov", "Metropolitanos FC", "Dundalk", "Villarreal CF", "Leicester City", "Liverpool FC", "Sporting Braga", "Real Madrid", "Union Saint-Gilloise", "Sporting CP", "Slovan Bratislava", "ŁKS Łódź", "Anorthosis Famagusta", "FK Orenburg", "Clermont Foot 63", "FC Hradec Králové", "Boston River", "Viktoria Plzeň", "Incheon United", "AFC Ajax", "RB Leipzig", "Ross County FC", "Parma Calcio 1913", "Jorge Wilstermann", "ACF Fiorentina", "Rapid Wien", "Nacional Potosí", "Silkeborg IF", "Gaziantep FK", "LASK", "RC Celta", "RSC Anderlecht", "Liverpool", "Stade Rennais", "AZ Alkmaar", "CD Guabirá", "KV Mechelen", "FC Zürich", "Kayserispor", "NK Celje", "CD Nacional", "Tottenham Hotspur", "River Plate Montevideo", "Spartak Moskva", "Águilas Doradas", "Nottingham Forest", "Beşiktaş", "US Lecce", "VfL Bochum", "FK Teplice", "1. FC Magdeburg", "Montpellier HSC", "Stade Brestois 29", "LDU de Quito", "Göteborg", "FK Jablonec", "Rio Ave FC", "SV Darmstadt 98", "Sarpsborg 08", "Strømsgodset IF", "Sandefjord Fotball", "Sparta Rotterdam", "Go Ahead Eagles", "1. FSV Mainz 05", "Fortaleza FC", "Queen's Park", "Atromitos", "OFI Heraklion", "FK Oleksandriya", "IK Sirius", "Chelsea FC", "Palmeiras", "Rangers FC", "Curicó Unido", "Slavia Praha", "PFC Ludogorets Razgrad", "1. FC Köln", "sc Heerenveen", "FC Midtjylland", "US Salernitana 1919", "CA Cerro", "Colo-Colo", "NK Osijek", "Pisa Calcio", "FC Lorient", "Nea Salamina", "Athletic Bilbao", "CSKA Moskva", "1. FC Kaiserslautern", "Sporting Cristal", "HJK Helsinki", "Havre AC", "Slaven Belupo", "Djurgårdens IF", "Portuguesa FC", "Spartak Subotica", "Cherno More Varna", "Bologna FC", "İstanbul Başakşehir", "FC Nordsjælland", "VfB Stuttgart", "Vejle BK", "Torino FC", "Técnico Universitario", "Diriangén", "Boavista", "Virtus Francavilla", "Astana", "Shkupi", "Maccabi Haifa", "Lanús", "Deportivo Cali", "Brighton & Hove Albion", "Atlético Junior", "Flamengo RJ", "Legia Warszawa", "Manchester City", "Envigado FC", "Crystal Palace", "Bala Town FC", "Independiente Medellín", "FC Schalke 04", "Godoy Cruz", "Samsunspor", "Pescara Calcio", "Lokomotiva Zagreb", "Rosario Central", "Aston Villa", "Manchester United", "FC København", "FC Lugano", "Galatasaray", "Hatayspor", "FC Metz", "Club Aurora", "Stade de Reims", "AFC Bournemouth", "Universidad Catolica", "FC Basel 1893", "Zenit St. Petersburg", "Real Betis", "El Nacional", "Jeonbuk Motors", "PSV Eindhoven", "IF Elfsborg", "Atlético Madrid", "RB Salzburg", "Feyenoord", "Zagłębie Lubin", "Bodrum FK", "AS Trenčín", "KV Kortrijk", "Udinese Calcio", "Akhmat Grozny", "Aalborg BK", "Fatih Karagümrük SK", "Pendikspor", "FK Mladá Boleslav", "RC Strasbourg", "TSV Hartberg", "Brøndby IF", "1. FC Heidenheim 1846", "Elche", "Universidad Central", "Varbergs BoIS", "Vorskla Poltava", "2 de Mayo", "Vicenza", "West Ham United", "Mineros de Guayana", "Servette FC", "Cruz Azul", "BSC Young Boys", "Sampdoria", "SC Freiburg", "Fulham FC", "FC Groningen", "Cercle Brugge", "Royal Pari", "FC Sion", "Lillestrøm", "Alanyaspor", "Valencia CF", "Ulsan Horang-i", "Willem II", "FK Sochi", "Universitario de Vinto", "PEC Zwolle", "RKC Waalwijk", "Vitesse", "Çaykur Rizespor", "Santiago Morning", "Jeju United", "Baník Ostrava", "Delfín SC", "Bnei Sachnin FC", "Hammarby", "FK Dukla Praha", "Krylia Sovetov", "Mladost Lučani", "FC Luzern", "SL Benfica", "Colón de Santa Fe", "River Plate", "Olympique Lyonnais", "FC St. Gallen", "Víkingur Gøta", "1. FC Nurnberg", "Hertha BSC", "Getafe CF", "St. Johnstone FC", "Stabæk IF", "Barracas Central", "VfL Wolfsburg", "FK Khimki", "FC Ashdod", "Espanyol Barcelona", "Sint-Truidense VV", "Tromso", "Heracles Almelo", "Dinamo Moskva", "Kasımpaşa SK", "Angers SCO", "The Strongest", "SK Austria Klagenfurt", "Defensa y Justicia", "Kjelsas", "Burnley FC", "SpVgg Greuther Furth", "Sevilla FC", "Spezia Calcio", "Universitario de Deportes", "Shakhtar Donetsk", "Guaraní", "KRC Genk", "Borussia Dortmund", "Olympique Marseille", "AC Sparta Praha", "Bohemians Praha 1905", "Slovan Liberec", "Panetolikos", "UD Almería", "Brown de Adrogué", "Atlético de Rafaela", "Toulouse FC", "Brentford FC", "Tokyo Verdy", "NEC Nijmegen", "MKE Ankaragücü", "Antalyaspor", "Trabzonspor", "Luton Town", "Antofagasta", "NK Maribor", "Suwon Bluewings", "PAS Giannina", "Śląsk Wrocław", "Odds BK", "Monagas", "Hamarkameratene", "JK Tammeka", "AS Monaco", "HamKam", "İstanbulspor AŞ", "GD Chaves", "MFK Karviná", "Emelec", "Audax Italiano", "Paide Linnameeskond", "Randers FC", "SS Monopoli", "Mannucci", "Grazer AK", "NK Domžale", "Sportivo Trinidense", "Orense SC", "Motherwell FC", "Hibernian FC", "Atalanta", "Cremonese", "Club América", "B36 Tórshavn", "Aktobe", "Southampthon FC", "FKS Stal Mielec", "Paris Saint-Germain", "Cagliari Calcio", "Pogoń Szczecin", "FC Lausanne-Sport", "Bayern München", "FK Rostov", "Unión Española", "Rosenborg", "Universidad de Chile", "FK Krasnodar", "Wolfsberger AC", "Lyngby BK", "FC Utrecht", "Jagiellonia Białystok", "FC Zlín", "Hacken", "Hellas Verona", "Aalesunds FK", "Guayaquil City", "KVC Westerlo", "Viborg FF", "Lokomotiv Moskva", "MŠK Žilina", "Bor. Mönchengladbach", "Norrkoping", "SBV Excelsior", "Eintracht Frankfurt", "Sassuolo Calcio", "Paksi SE", "FC Volendam", "Mansfield Town", "Fortuna Dusseldorf", "AJ Auxerre", "SC Paderborn 07", "ESTAC Troyes", "Bodø/Glimt", "Zilina", "Hamburger SV", "O'Higgins", "NAC Breda", "Viking", "Zweigen Kanazawa", "Újpest FC", "FC St. Pauli", "Fenerbahçe", "Bayer Leverkusen", "Valerenga", "Grasshopper Club Zürich", "Oud-Heverlee Leuven", "Sivasspor", "Almere City FC", "Górnik Zabrze", "Fortuna Sittard", "Cartaginés", "Greenock Morton", "St. Pauli", "Degerfors", "Degerfors IF", "Palestino", "Deportivo Cuenca", "Stjarnan", "Al Ahli Jeddah", "Molde", "FC Winterthur", "FC Augsburg", "CD Hermanos Colmenarez", "Adana Demirspor", "1899 Hoffenheim", "Holstein Kiel", "Real Santa Cruz"]

    #csv file header
    matches.append("datetime ; competition ; match ; h2h matches ; h2h goals")
    for k in range(0, 4):
        current_date = today + timedelta(days=k)
        logging.info("\n" + str(current_date) + "\n")
        month = current_date.strftime("%b").lower()
        day = current_date.day
        formatted_date = f"{current_date.year}/{month}/{day}/"
        response = requests.get("https://www.worldfootball.net/matches_today/" + formatted_date)
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

                h2hmatches = ''
                h2hgoals = ''
                
                try:
                    r = [el.text.strip() for el in row]
                    if len(r) <= 7:
                        competition = r[3]

                    if (len(r) > 7) and any(item.lower().replace(' ', '') in competition.lower().replace(' ', '') for item in comps) and r[3] in teams and r[7] in teams:
                        logging.info(competition + ": \t" + r[3] + " - " + r[7])
                        if len(row.find_all('a')) > 2:
                            response3 = requests.get("https://www.worldfootball.net/" + row.find_all('a')[2]['href'])
                            
                            if response3.status_code == 200:
                                soup3 = BeautifulSoup(response3.content, 'html.parser')
                                table3 = soup3.find_all('table', class_="standard_tabelle")[1]
                                
                                h2hurl = soup3.find_all('table', class_="auswahlbox")[1].find_all('a')[-1]['href']
                                response4 = requests.get("https://www.worldfootball.net" + h2hurl)
                            
                                if response4.status_code == 200:
                                    soup4 = BeautifulSoup(response4.content, 'html.parser')
                                    table4 = soup4.find_all('table', class_="standard_tabelle")[0]
                                    h2hmatches = table4.find_all('tr')[-1].find_all('td')[2].text
                                    h2hgoals = int(table4.find_all('tr')[-1].find_all('td')[-3].text) + int(table4.find_all('tr')[-1].find_all('td')[-1].text)
                        
                        if (float(h2hgoals)/float(h2hmatches) >= 3.5):
                            logging.info("MATCH ADDED!\n")
                            matches.append(formatted_date + " " + r[1] + " ; " + competition + " ; " + r[3] + " - " + r[7] + " ; " + h2hmatches + " ; " + str(h2hgoals))       
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    logging.info(exc_type, fname, exc_tb.tb_lineno)                        
        else:
            raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
    # Open file in write mode
    # with open("/home/data.csv", "a", newline='') as file:
    #     writer = csv.writer(file)
    #     # Write each element as a row
    #     for item in matches:
    #         writer.writerow([item])

    return matches

def compile_matches_by_team(previousSeason, season):
    matches = getMatchesBetweenFilteredTeams(previousSeason, season)
    team_matches = {}
    
    for match in matches:
        parts = match.split(";")
        if len(parts) < 4:
            continue  # Skip invalid match entries

        if (float(parts[5]) / float(parts[4]) < 3.5) or parts[5] == "nan":
            continue
        
        teams = parts[2].split(" - ")
        if len(teams) != 2:
            continue  # Skip invalid team entries
        
        team1, team2 = teams
        
        # Add match to team1
        if team1 not in team_matches:
            team_matches[team1] = []
        team_matches[team1].append(match)
        
        # Add match to team2
        if team2 not in team_matches:
            team_matches[team2] = []
        team_matches[team2].append(match)
    
    return team_matches

def getAllMatchesByTeam(season, team):
    # Input array of matches
    # Load the CSV file
    csv_file = "/home/newData/matches" + season + ".csv"  # Replace with your actual file path
    
    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    data = pd.read_csv(csv_file, sep=',', dtype='unicode')
    results = []

    # Iterate over each row in filtered_matches
    for _, row in data.iterrows():
        if team_in_match(row['match'], team) == True and comp_in_comps_list(row['competition'], comps) == True:
            results.append(';'.join(map(str, row[:4].values.tolist() + row[6:8].values.tolist())))  # Take the first 8 columns as a string
            # Append the filtered matches as a list of values (or a specific column, depending on what you need)
            # If you want to append rows as lists of column values:
            #results.append(filtered_matches.values.tolist())

    return (results)

def getMatchesBetweenFilteredTeams(previousSeason, season):
    # Input array of matches
    # Load the CSV file
    csv_file = "/scrapper/newData/with_real_h2h/matches" + season + ".csv"  # Replace with your actual file path
    
    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    data = pd.read_csv(csv_file, sep=',', dtype='unicode')
    results = []
    f_teams = filterTeamsBySeason(previousSeason)

    #f_teams = ["SS Reyes", "FK Voždovac", "FK Ufa", "St Patrick's Athletic", "Vélez Sarsfield", "Spartak Trnava", "AmaZulu", "Linense", "Orlando Pirates", "MC Alger", "Kaizer Chiefs", "Zalgiris", "Vasco da Gama - RJ", "Botafogo - RJ", "Real Sociedad", "Ipswich Town", "Diriangén", "Racing Santander", "FC Voluntari", "Shamrock Rovers", "KS Cracovia", "La Equidad", "Lamia", "Olympiakos Piraeus", "Liverpool FC", "FC Porto", "AEL Larissa", "Heart of Midlothian", "Bnei Sachnin FC", "Crvena Zvezda", "Deportivo Pereira", "Independiente del Valle", "Independiente", "FCSB", "Santa Fe", "Sigma Olomouc", "Vorskla Poltava", "Racing", "Doxa Katokopias", "FC Lorient", "Kilmarnock FC", "Standard Liège", "Gil Vicente", "Millwall", "AS Lucchese Libertas", "FC Midtjylland", "Bahia - BA", "Machida Zelvia", "Tigre", "PAOK Saloniki", "Caracas FC", "FK Čukarički", "Bohemian FC", "Vojvodina", "Hannover 96", "Aarhus GF", "Hansa Rostock", "FK Pardubice", "JK Narva Trans", "Zlaté Moravce", "Frosinone Calcio", "Reggina Calcio", "Shakhtar Donetsk", "Clermont Foot 63", "CS Marítimo", "Instituto de Córdoba", "Hajduk Split", "Arsenal FC", "AFC Ajax", "Everton FC", "Tudelano", "OFI Heraklion", "Eyüpspor", "Zorya Lugansk", "FC Nantes", "Newell's Old Boys", "Viktoria Plzeň", "Sarmiento de Junín", "Arsenal de Sarandí", "Toulouse FC", "Atlético Palmaflor", "AFC Wimbledon", "AC Milan", "Club Olimpia", "CD Santa Clara", "Real Tomayapo", "Atlético Mineiro", "Atlético Bucaramanga", "AEK Larnaca", "América - MG", "Brescia", "Once Caldas", "AS Monaco", "Espanyol Barcelona", "FC Famalicão", "Busan I'Park", "Sturm Graz", "Radnik Surdulica", "Patriotas FC", "Real Valladollid", "Ümraniyespor", "Real Zaragoza", "Kauno Zalgiris", "Queen's Park", "Vitória Guimarães", "UD Las Palmas", "Tigres FC", "Fénix", "FK Ural", "Oriente Petrolero", "Tottenham Hotspur", "Racing Club", "KAA Gent", "Gent", "Lokomotiv Plovdiv", "Virtus Francavilla", "PFC Beroe", "Baltika Kaliningrad", "Shkupi", "FK Haugesund", "Nõmme Kalju", "VfL Wolfsburg", "Volos NFC", "Botev Plovdiv", "Deportes Tolima", "Maccabi Tel Aviv", "Sutjeska", "Ross County FC", "Everton", "Montevideo Wanderers", "Tala'ea Al Jaish Cairo", "FK Napredak", "Ittihad Alexandria", "Academia Puerto Cabello", "1. FC Heidenheim 1846", "Giresunspor", "FC Metz", "Široki Brijeg", "SCR Altach", "Celtic FC", "SL Benfica", "América de Cali", "Juventus", "Talleres de Córdoba", "Newcastle United", "Club Nacional", "Villarreal CF", "Real Madrid", "NK Osijek", "Krylia Sovetov", "Dundee United", "Sol de América", "NK Celje", "Plaza Colonia", "Mushuc Runa", "Piast Gliwice", "Slovan Liberec", "Sakaryaspor", "Lille OSC", "Leicester City", "SSC Napoli", "Daegu", "Feyenoord", "1. FC Union Berlin", "Levadia Tallin", "Gamba Osaka", "GD Estoril", "Akhmat Grozny", "Konyaspor", "WSG Tirol", "Austria Lustenau", "Aucas", "Unión La Calera", "1. FC Köln", "Pisa Calcio", "Gualaceo SC", "AEK Athen", "K Beerschot VA", "FUS de Rabat", "Alianza FC", "Libertad", "Cerezo Osaka", "SV 07 Elversberg", "CSKA Moskva", "AZ Alkmaar", "Paphos FC", "Deportivo Pasto", "1. FC Slovácko", "Inter", "Paris FC", "Jaguares de Córdoba", "Atlético Madrid", "ŁKS Łódź", "Burnley FC", "Omonia Nikosia", "Flora Tallin", "FC Barcelona", "Luton Town", "Rangers FC", "Chelsea FC", "Peñarol", "Sevilla FC", "Sporting CP", "Banfield", "Manchester City", "Estudiantes de Mérida FC", "FC DAC 1904", "Mamelodi Sundowns", "Hapoel Be'er Sheva", "VfL Bochum", "SønderjyskE", "Nottingham Forest", "MFK Ružomberok", "CD Leganés", "Patronato Paraná", "Getafe CF", "FC Tokyo", "Amiens SC", "FC Botoşani", "St. Johnstone FC", "APOEL Nikosia", "Olimpija Ljubljana", "Granada CF", "Lokomotiva Zagreb", "Livingston FC", "San Lorenzo", "Radnički Niš", "Nacional", "OGC Nice", "Sporting Braga", "Bolívar", "Millonarios", "Dinamo Tbilisi", "Zamora FC", "Legia Warszawa", "Carabobo FC", "AC Ajaccio", "Hapoel Haifa", "Nuova Cosenza", "Werder Bremen", "1. FC Kaiserslautern", "Rio Ave FC", "Kalmar", "Paços de Ferreira", "Belgrano de Córdoba", "Aswan FC", "Al Mokawloon Al Arab", "Barcelona", "Genoa CFC", "Pontedera", "Defensor Sporting", "Always Ready", "Universidad Católica", "PAS Giannina", "Halmstad", "Panetolikos", "Lechia Gdańsk", "Go Ahead Eagles", "Cruz Azul", "Sparta Rotterdam", "Huachipato", "Cumbayá", "MC Oran", "Rayo Zuliano", "Slaven Belupo", "Atromitos", "Sport Huancayo", "Havre AC", "Baroka", "FC Ashdod", "Rubin Kazan", "Malmö FF", "São Paulo FC", "Dinamo Moskva", "Brann", "FBC Melgar", "RC Lens", "Sportivo Luqueño", "Ebro", "Metropolitanos FC", "Angers SCO", "Dundalk", "BATE Borisov", "FC Blau Weiß Linz", "Anorthosis Famagusta", "Lazio Roma", "Union Saint-Gilloise", "RSC Anderlecht", "İstanbul Başakşehir", "Slovan Bratislava", "Ferencvárosi TC", "AS Roma", "Spartak Subotica", "FK Orenburg", "FC Hradec Králové", "Boston River", "Ironi Kiryat Shmona", "Incheon United", "Lugo", "CD Nacional", "Nacional Potosí", "Olympique Marseille", "ACF Fiorentina", "RC Celta", "River Plate Montevideo", "Águilas Doradas", "RB Leipzig", "Parma Calcio 1913", "Southampthon FC", "Pescara Calcio", "Stade Rennais", "Jorge Wilstermann", "FC Lugano", "Viborg FF", "CD Guabirá", "Liverpool", "Apollon Limassol", "HNK Rijeka", "Stade Brestois 29", "Göztepe", "FC Schalke 04", "Sarpsborg 08", "Göteborg", "Kayserispor", "Empoli FC", "LDU de Quito", "Sandefjord Fotball", "RC Strasbourg", "Strømsgodset IF", "FK Jablonec", "Fortaleza FC", "Boavista", "FC Zlín", "MFK Zemplín Michalovce", "Chippa United", "Slavia Praha", "IK Sirius", "Sporting Charleroi", "Curicó Unido", "Palmeiras", "sc Heerenveen", "CA Cerro", "Zamalek SC", "HJK Helsinki", "Hapoel Be'er Sheva", "Colo-Colo", "Sporting Cristal", "CD Leganés", "FC DAC 1904", "FK Čukarički", "Piast Gliwice", "Arenas de Getxo", "Portuguesa FC", "Djurgårdens IF", "Ebro", "Pendikspor", "FUS de Rabat", "Göztepe", "Brentford FC", "Rio Ave FC", "Heracles Almelo", "VfB Stuttgart", "Técnico Universitario", "Sutjeska", "Lazio Roma", "Astana", "FC Luzern", "FC St. Gallen", "Deportivo Cali", "Atlético Junior", "Lanús", "Manchester United", "Flamengo RJ", "FC Volendam", "Sassuolo Calcio", "FC St. Gallen", "Hatayspor", "Envigado FC", "Nea Salamina", "Godoy Cruz", "Rosario Central", "Paris Saint-Germain", "Independiente Medellín", "Vicenza", "Royal Antwerp FC", "PFC Ludogorets Razgrad", "Club Aurora", "FK Rostov", "AFC Bournemouth", "Bodrum FK", "Elche", "Fulham FC", "Hibernian FC", "Aston Villa", "Bologna FC", "Bala Town FC", "FC København", "Jeonbuk Motors", "Universidad Catolica", "Cremonese", "Trabzonspor", "IF Elfsborg", "El Nacional", "AS Trenčín", "Zagłębie Lubin", "Brøndby IF", "AS Saint-Étienne", "SC Paderborn 07", "Udinese Calcio", "Zenit St. Petersburg", "1. FC Magdeburg", "Eintracht Braunschweig", "VfL Osnabruck", "İstanbulspor AŞ", "Aalborg BK", "Universidad Central", "Semouha Club", "Varbergs BoIS", "TSV Hartberg", "ENPPI Cairo", "2 de Mayo", "Dundee FC", "West Ham United", "Mansfield Town", "Mineros de Guayana", "Dynamo České Budějovice", "Royal Pari", "NAC Breda", "Lillestrøm", "Willem II", "FC Twente", "Cagliari Calcio", "Sampdoria", "Ulsan Horang-i", "Valencia CF", "Rayo Vallecano", "BSC Young Boys", "Borussia Dortmund", "Santiago Morning", "1. FC Nurnberg", "Alanyaspor", "PEC Zwolle", "Universitario de Vinto", "LASK", "Venezia FC", "Jeju United", "FC Lausanne-Sport", "US Lecce", "Mezőkövesdi SE", "Çaykur Rizespor", "Fatih Karagümrük SK", "Karlsruher SC", "Delfín SC", "AJ Auxerre", "Pisa Calcio", "Kasımpaşa SK", "Hammarby", "SuperSport United", "Valencia CF", "Beşiktaş", "Sydney FC", "FK Voždovac", "Colón de Santa Fe", "River Plate", "NK Maribor", "Víkingur Gøta", "Fehérvár FC", "Stabæk IF", "NorthEast United", "Sporting CP", "Barracas Central", "Hapoel Haifa", "MFK Ružomberok", "FC Metz", "Gaziantep FK", "Bayern München", "Antalyaspor", "Athletic Bilbao", "Tromso", "Grazer AK", "SBV Excelsior", "The Strongest", "Oud-Heverlee Leuven", "Defensa y Justicia", "FC Utrecht", "Kjelsas", "Brighton & Hove Albion", "AEK Athen", "FC Botoşani", "FC Nordsjælland", "Universidad de Deportes", "FK Teplice", "Guaraní", "Pogoń Szczecin", "Tudelano", "NK Istra 1961", "Atlético de Rafaela", "Lokomotiv Moskva", "Austria Lustenau", "Brown de Adrogué", "SV Wehen Wiesbaden", "Śląsk Wrocław", "RC Lens", "Montpellier HSC", "Antofagasta", "Tokyo Verdy", "MC Oran", "Suwon Bluewings", "JK Tammeka", "Moreirense FC", "Audax Italiano", "Pontedera", "FK Mladá Boleslav", "Spezia Calcio", "Monagas", "Parma Calcio 1913", "Emelec", "1. FC Kaiserslautern", "Pendikspor", "FKS Stal Mielec", "Hamburger SV", "HamKam", "Apollon Limassol", "Sint-Truidense VV", "Odds BK", "Paide Linnameeskond", "Hamarkameratene", "Mannucci", "Orense SC", "Sportivo Trinidense", "B36 Tórshavn", "Aktobe", "Cartaginés", "BSC Young Boys", "PSV Eindhoven", "KRC Genk", "Kayserispor", "Servette FC", "AS Trenčín", "Greenock Morton", "FK Jablonec", "KV Mechelen", "Unión Española", "MŠK Žilina", "Rosenborg", "Zilina", "Empoli FC", "Royal Antwerp FC", "Hamburger SV", "1. FC Nurnberg", "Hertha BSC", "KAS Eupen", "FC Groningen", "KV Kortrijk", "Diósgyöri VTK", "FKS Stal Mielec", "Austria Wien", "Mezőkövesdi SE", "Universidad de Chile", "Fortuna Dusseldorf", "Hellas Verona", "Bor. Mönchengladbach", "Hacken", "Norrkoping", "Aalesunds FK", "Guayaquil City", "Eintracht Frankfurt", "FC Blau Weiß Linz", "NK Domžale", "Olympique Lyonnais", "Silkeborg IF", "Melbourne Heart", "FK Krasnodar", "FK Dukla Praha", "Bodø/Glimt", "Atalanta", "Rapid Wien", "O'Higgins", "Viking", "US Lecce", "Servette FC", "Zweigen Kanazawa", "Grasshopper Club Zürich", "Valerenga", "AS Roma", "Cartaginés", "Lugo", "Bayer Leverkusen", "Sivasspor", "Real Zaragoza", "Elche", "Çaykur Rizespor", "Fenerbahçe", "Al Ahli Jeddah", "SK Austria Klagenfurt", "Vitesse", "CD Nacional", "Fortuna Sittard", "RKC Waalwijk", "Cercle Brugge", "Górnik Zabrze", "Volos NFC", "FC Winterthur", "1. FC Union Berlin", "Spartak Moskva", "Degerfors", "Górnik Zabrze", "Degerfors IF", "FK Ural", "Ittihad Alexandria", "Almere City FC", "Austria Lustenau", "Adana Demirspor", "Palestino", "Deportivo Cuenca", "Stjarnan", "Karpaty Lviv", "Golden Arrows", "Fenerbahçe", "Molde", "CD Hermanos Colmenarez", "SC Freiburg", "FC Sion", "1899 Hoffenheim", "Holstein Kiel", "Kerala Blasters", "Real Santa Cruz"]

    #2025 teams:
    #f_teams = ["RB Leipzig", "1. FC Köln", "FC Zlín", "SL Benfica", "Montpellier HSC", "Atlético Bucaramanga", "FK Ural", "Aswan FC", "Fénix", "Göteborg", "AJ Auxerre", "Monagas", "FK Jablonec", "FK Sochi", "Zenit St. Petersburg", "Sigma Olomouc", "West Ham United", "Manchester United", "Libertad", "Sarpsborg 08", "Mineros de Guayana", "Villarreal CF", "RSC Anderlecht", "FC København", "FK Krasnodar", "NK Osijek", "FC Lausanne-Sport", "Queen's Park", "Sheffield United", "Frosinone Calcio", "FC Zürich", "Sparta Rotterdam", "FKS Stal Mielec", "Varbergs BoIS", "Górnik Zabrze", "Belgrano de Córdoba", "AS Roma", "Malmö FF", "MKE Ankaragücü", "Çaykur Rizespor", "Emelec", "AC Milan", "Santa Fe", "Fehérvár FC", "Carabobo FC", "Olimpija Ljubljana", "JK Narva Trans", "Bologna FC", "Motherwell FC", "FC DAC 1904", "CD Nacional", "Zorya Lugansk", "1. FSV Mainz 05", "Bnei Sachnin FC", "Gil Vicente", "Fortuna Sittard", "Palestino", "Nea Salamina", "FC Barcelona", "Shakhtar Donetsk", "Austria Wien", "Stade de Reims", "Atlético de Rafaela", "Sturm Graz", "Always Ready", "Zalgiris", "MFK Zemplín Michalovce", "Korona Kielce", "Shamrock Rovers", "Fortaleza FC", "Slavia Praha", "Stabæk IF", "Crystal Palace", "Palmeiras", "Halmstad", "Piast Gliwice", "O'Higgins", "FK Pardubice", "Sport Huancayo", "Havre AC", "Dundee United", "Getafe CF", "Atromitos", "The Strongest", "Amiens SC", "Sint-Truidense VV", "FBC Melgar", "Ebro", "Baroka", "Dinamo Tbilisi", "Cherno More Varna", "Envigado FC", "Maccabi Tel Aviv", "Udinese Calcio", "Akhmat Grozny", "Baník Ostrava", "IK Sirius", "K Beerschot VA", "ACF Fiorentina", "Cartaginés", "FC Basel 1893", "Almere City FC", "Arsenal de Sarandí", "RC Lens", "Real Betis", "Vejle BK", "Royal Pari", "ESTAC Troyes", "Hvidovre IF", "Unión La Calera", "FC Luzern", "Leicester City", "Sandefjord Fotball", "FC Midtjylland", "WSG Tirol", "FC Lugano", "FC Metz", "FC Lorient", "RKC Waalwijk", "CA Cerro", "Lokomotiv Plovdiv", "Sivasspor", "Liverpool FC", "Mushuc Runa", "Lyngby BK", "Melbourne Heart", "St. Pauli", "Delfín SC", "RC Strasbourg", "Cerezo Osaka", "Tottenham Hotspur", "Cruz Azul", "Zweigen Kanazawa", "Flamengo RJ", "Paris Saint-Germain", "Legia Warszawa", "Norrkoping", "Jeju United", "Lokomotiva Zagreb", "Randers FC", "Feyenoord", "Slovan Bratislava", "Ulsan Horang-i", "Willem II", "Sol de América", "Anorthosis Famagusta", "Suwon Bluewings", "AEK Athen", "CD Santa Clara", "Barcelona", "AS Trenčín", "Defensor Sporting", "GD Chaves", "FC Twente", "Orense SC", "Patronato Paraná", "Metropolitanos FC", "AFC Bournemouth", "Olympiakos Piraeus", "Astana", "CSKA Moskva", "Shkupi", "Atlético Madrid", "RB Salzburg", "Torino FC", "River Plate", "Paris FC", "Incheon United", "Universidad Católica", "VfB Stuttgart", "Werder Bremen", "Aalesunds FK", "FK Haugesund", "Trabzonspor", "Vorskla Poltava", "B36 Tórshavn", "Bor. Mönchengladbach", "Aktobe", "Galatasaray", "SS Monopoli", "Aberdeen FC", "VfL Wolfsburg", "SC Freiburg", "VfL Bochum", "FK Teplice", "Fulham FC", "Ross County FC", "Śląsk Wrocław", "ŁKS Łódź", "Grazer AK", "FC Groningen", "Eyüpspor", "Jorge Wilstermann", "1. FC Magdeburg", "sc Heerenveen", "Degerfors", "Hatayspor", "Angers SCO", "NK Domžale", "Lanús", "Molde", "LDU de Quito", "Olympique Lyonnais", "Krylia Sovetov", "Fatih Karagümrük SK", "Grasshopper Club Zürich", "Atalanta", "Hammarby", "Degerfors IF", "Diriangén", "Hellas Verona", "NAC Breda", "Vojvodina", "Eintracht Frankfurt", "SV Darmstadt 98", "Godoy Cruz", "Greenock Morton", "Odense BK", "FC St. Pauli", "Vitória Guimarães", "Sevilla FC", "İstanbulspor AŞ", "CD Guabirá", "Wolfsberger AC", "Cumbayá", "Unión Española", "Pogoń Szczecin", "FC Sion", "FK Orenburg", "Servette FC", "SK Austria Klagenfurt", "Bohemians Praha 1905", "PEC Zwolle", "Newcastle United", "NEC Nijmegen", "Boavista", "Alanyaspor", "MFK Karviná", "Vitesse", "Academia Puerto Cabello", "El Nacional", "Virtus Francavilla", "Club América", "FCSB", "Bayer Leverkusen", "SønderjyskE", "Universitario de Deportes", "Panetolikos", "Flora Tallin", "Atlético Junior", "Olympique Marseille", "Crvena Zvezda", "Viborg FF", "FK Mladá Boleslav", "Luton Town", "FC Hradec Králové", "KV Kortrijk", "Celtic FC", "Rosenborg", "Valerenga", "Millonarios", "IF Elfsborg", "Real Madrid", "Defensa y Justicia", "TSV Hartberg", "Lokomotiv Moskva", "Valencia CF", "River Plate Montevideo", "Dundee FC", "Curicó Unido", "San Lorenzo", "Real Santa Cruz", "Union Saint-Gilloise", "AC Sparta Praha", "Manchester City", "NK Maribor", "Royal AM", "HJK Helsinki", "Sassuolo Calcio", "Dynamo České Budějovice", "PAS Giannina", "Rosario Central", "1. FC Heidenheim 1846", "Deportivo Cuenca", "PFC Ludogorets Razgrad", "Kauno Zalgiris", "Jagiellonia Białystok", "Nacional Potosí", "Odds BK", "FC Schalke 04", "Brann", "FK Rostov", "Adana Demirspor", "MŠK Žilina", "Kjelsas", "Paksi SE", "FC Augsburg", "Aston Villa", "Southampthon FC", "Stjarnan", "Cercle Brugge", "Universidad Catolica", "FK Dukla Praha", "Toulouse FC", "Hibernian FC", "Mansfield Town", "Aalborg BK", "Brentford FC", "SC Paderborn 07", "Oud-Heverlee Leuven", "Vicenza", "Hertha BSC", "Hamarkameratene", "JK Tammeka", "KRC Genk", "HamKam", "Tokyo Verdy", "Pendikspor", "Fenerbahçe", "Spezia Calcio", "FC Ashdod", "Espanyol Barcelona", "Lillestrøm", "OFI Heraklion", "Slovan Liberec", "Santiago Morning", "PSV Eindhoven", "Bayern München", "Paide Linnameeskond", "Fortuna Dusseldorf", "Víkingur Gøta", "Újpest FC", "Kasımpaşa SK", "Tromso", "Viking", "FC Volendam", "AS Monaco", "FC St. Gallen", "Zilina", "FK Khimki", "Hacken", "Colón de Santa Fe", "SBV Excelsior", "Borussia Dortmund", "FC Winterthur", "Mannucci", "FC Utrecht", "SpVgg Greuther Furth", "Al Ahli Jeddah", "Bodø/Glimt", "Holstein Kiel", "KVC Westerlo", "1899 Hoffenheim"]

    # Iterate over each row in filtered_matches
    for _, row in data.iterrows():
        if match_in_teams_list(row['match'], f_teams) == True and comp_in_comps_list(row['competition'], comps) == True:
            results.append(';'.join(map(str, row[:4].values.tolist() + row[6:8].values.tolist())))  # Take the first 8 columns as a string
            # Append the filtered matches as a list of values (or a specific column, depending on what you need)
            # If you want to append rows as lists of column values:
            #results.append(filtered_matches.values.tolist())

    return (results)

def filterTeamsBySeason(season):
    # Input array of matches
    # Load the CSV file
    csv_file = "/scrapper/newData/with_real_h2h/matches" + season + ".csv"  # Replace with your actual file path
    
    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    data = pd.read_csv(csv_file, sep=',', dtype='unicode')
    rows_to_keep = []
    for _, row in data.iterrows():
        if comp_in_comps_list(row['competition'], comps) == True:
            rows_to_keep.append(row)

    data = pd.DataFrame(rows_to_keep)

    # Extract the total matches from the relevant column
    data['match'] = data['match'].fillna('').astype(str)  # Replace 'matches_column' with the actual column name
    total_matches = data['match'].tolist()  # Replace 'matches_column' with the actual column name

    # Filter matches where the "2nd goal" column is <= 60
    #filtered_data = data[data['2nd goal "'] <= 60]  # Replace '2nd goal' with the exact column name
    filtered_data = data[
        pd.to_numeric(
            data['total goals'].fillna('').str.replace(',', '.').str.replace('#VALUE', '', regex=False),
            errors='coerce'  # Invalid entries (e.g., '#VALUE') will become NaN
        ) >= 2
    ]

    matches = filtered_data['match'].tolist()

    # Flatten the lists into individual teams
    teams_from_matches = []
    teams_from_total_matches = []

    for match in matches:
        teams_from_matches.extend(split_match(match))

    for match in total_matches:
        teams_from_total_matches.extend(split_match(match))

    # Count occurrences in both arrays
    matches_count = Counter(teams_from_matches)
    total_matches_count = Counter(teams_from_total_matches)

    # Combine results into a unified list
    all_teams = set(matches_count.keys()).union(set(total_matches_count.keys()))

    f_teams =[]
    for team in sorted(all_teams):
        x = matches_count[team]  # Count from the filtered matches
        y = total_matches_count[team]  # Count from the total matches array
        if y != 0 and y >= 20 and (x / y) >= 0.8:
            ratio = str(x / y).replace(".", ",")
            #f_teams.append(f"{team} ; {x} ; {y} ; {ratio}")
            f_teams.append(f"{team}")
            #logging.info(f"{team} ; {x} ; {y} ; {x/y}")

    return f_teams

# Function to check if both teams in a match are in the teams_list
def comp_in_comps_list(comp, comps_list):
    try:
        for c in comps_list:
            if c.replace(" ", "") in comp.replace(" ", ""):
                return True
    except (ValueError, AttributeError):
        # If the match is not a valid string or can't be split into two parts, skip it
        return False

# Function to split match into exactly two teams
def split_match(match):
    # Split by ' - ' and assume the last ' - ' divides the two teams
    parts = match.rsplit(" - ", 1)
    if len(parts) == 2:
        return parts  # Two teams found
    else:
        return [match]  # Handle any malformed cases gracefully

# Function to check if both teams in a match are in the teams_list
def match_in_teams_list(match, teams_list):
    try:
        # Ensure the match is treated as a string
        match = str(match)
        # Split match into two teams using the last occurrence of " - "
        team1, team2 = match.rsplit(' - ', 1)  # Safely split by the last ' - '
        # Check if both teams are in the teams_list
        return team1.strip() in teams_list and team2.strip() in teams_list
    except (ValueError, AttributeError):
        # If the match is not a valid string or can't be split into two parts, skip it
        return False

# Function to check if team is in a match
def team_in_match(match, team):
    try:
        # Ensure the match is treated as a string
        match = str(match)
        # Split match into two teams using the last occurrence of " - "
        team1, team2 = match.rsplit(' - ', 1)  # Safely split by the last ' - '
        # Check if both teams are in the teams_list
        return team1.strip() == team.strip() or team2.strip() == team.strip()
    except (ValueError, AttributeError):
        # If the match is not a valid string or can't be split into two parts, skip it
        return False

# tetsing strategy: https://www.financial-spread-betting.com/sports/Goals-betting-system.html#respond
def getMatchesByDateFromDB2(date_str):
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
        logging.info("Getting data for " + date_str)

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = "SELECT date,season,timestamp,competition,home_team,away_team,ht_result,ft_result,last_home_team_matches,last_away_team_matches,home_total_goals_avg_at_home_pre,away_total_goals_avg_at_away_pre,over25_odd FROM backtesting.matches_stats ms WHERE date LIKE %s and last_home_team_matches != '[]' order by timestamp"
        #query = "SELECT date,timestamp,competition,home_team,away_team,ht_result,ft_result,h2h_matches,last_home_team_matches,last_away_team_matches,home_total_goals_avg_at_home_pre,away_total_goals_avg_at_away_pre FROM backtesting.matches_stats ms WHERE date LIKE %s and h2h_matches != '[]' and competition in ('Ásia - AFC Champions League', 'Austrália - A-League', 'Áustria - 1. Liga', 'Bélgica - First Division B', 'Bélgica - Pro League', 'Bolívia - Primera División', 'Chile - Primera División', 'Costa Rica - Primera División', 'Dinamarca - 1st Division', 'Dinamarca - Superliga', 'Inglaterra - FA Cup', 'Inglaterra - Taça da Liga', 'Alemanha - Bundesliga', 'Estónia - Meistriliiga', 'Alemanha - DFB Pokal' , 'Alemanha - 2. Bundesliga', 'Islândia - Úrvalsdeild', 'Índia - I-League', 'Indonésia - Liga 1', 'Itália - Coppa Italia', 'Luxemburgo - National Division','Malta - Premier League','México - Liga de Expansión MX','México - Liga MX','Países Baixos - Eerste Divisie', 'Países Baixos - Eredivisie', 'Irlanda do Norte - Premiership', 'Noruega - Eliteserien', 'Noruega - 1. Division','Paraguai - Division Profesional', 'Polónia - Cup', 'Arábia Saudita - Pro League', 'Singapura - Premier League', 'Suécia - Superettan','Suíça - Challenge League', 'Suíça - Super League','Emirados Árabes Unidos - Arabian Gulf League','Estados Unidos da América - MLS','Estados Unidos da América - USL Championship','Estados Unidos da América - US Open Cup')"
        like_pattern = f"%{date_str}%"  # Construct the LIKE pattern
        cursor.execute(query, (like_pattern,))

        matches = cursor.fetchall()  # Fetch all results
        matches_to_bet = []

        for match in matches:
            try:
                last_home_team_matches = match['last_home_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
                last_away_team_matches = match['last_away_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
                home_total_goals_avg_at_home_pre = float(match['home_total_goals_avg_at_home_pre'])
                away_total_goals_avg_at_away_pre = float(match['away_total_goals_avg_at_away_pre'])
                
                last_home_data = json.loads(last_home_team_matches)  # Parse the JSON string
                last_away_data = json.loads(last_away_team_matches)  # Parse the JSON string

                ### HOME conditions
                total_goals_last_home_team_matches = 0
                last_home_team_matches_iterated = 0
                last_home_team_matches_overs = 0
                for i in range(0, len(last_home_data)):
                    match_result = ''
                    
                    if str(last_home_data[i].split('|')[2].strip()) == str(match['home_team']) and last_home_team_matches_iterated < 3:
                        last_home_team_matches_iterated += 1
                        if 'ET' in last_home_data[i].split('|')[3].strip():
                            match_result = last_home_data[i].split('|')[3].split('ET')[0].strip()
                        elif 'PG' in last_home_data[i].split('|')[3].strip():
                            match_result = last_home_data[i].split('|')[3].split('PG')[0].strip()
                        elif last_home_data[i].split('|')[3].strip() == '-':
                            continue
                        else:
                            match_result = last_home_data[i].split('|')[3].strip()
                        if len(match_result) > 1:
                            total_goals_last_home_team_matches = total_goals_last_home_team_matches + int(match_result.split('-')[0]) + int(match_result.split('-')[1])
                            if (int(match_result.split('-')[0]) + int(match_result.split('-')[1])) > 2:
                                last_home_team_matches_overs += 1

    
                ## HOME Team eligibility evaluation
                home_team_eligle = False
                if total_goals_last_home_team_matches >= 7 and last_home_team_matches_overs >= 2:
                    home_team_eligle = True

                ### AWAY conditions
                total_goals_last_away_team_matches = 0
                total_goals_previous_away_team_match = 0
                last_away_team_matches_iterated = 0
                last_away_team_matches_overs = 0
                last_away_team_matches_scored = 0
                for i in range(0, len(last_away_data)):
                    match_result = ''
                    
                    if str(last_away_data[i].split('|')[4].strip()) == str(match['away_team']) and last_away_team_matches_iterated < 3:
                        last_away_team_matches_iterated += 1
                        if 'ET' in last_away_data[i].split('|')[3].strip():
                            match_result = last_away_data[i].split('|')[3].split('ET')[0].strip()
                        elif 'PG' in last_away_data[i].split('|')[3].strip():
                            match_result = last_away_data[i].split('|')[3].split('PG')[0].strip()
                        elif last_away_data[i].split('|')[3].strip() == '-':
                            continue
                        else:
                            match_result = last_away_data[i].split('|')[3].strip()
                        if len(match_result) > 1:
                            total_goals_last_away_team_matches = total_goals_last_away_team_matches + int(match_result.split('-')[0]) + int(match_result.split('-')[1])
                            if (int(match_result.split('-')[0]) + int(match_result.split('-')[1])) > 2:
                                last_away_team_matches_overs += 1
                            if int(match_result.split('-')[1]) > 0:
                                last_away_team_matches_scored += 1
                            if last_away_team_matches_iterated == 1:
                                total_goals_previous_away_team_match = int(match_result.split('-')[0]) + int(match_result.split('-')[1])

                ## AWAY Team eligibility evaluation
                away_team_eligle = False
                if total_goals_last_away_team_matches >= 7 and last_away_team_matches_overs >= 2 and total_goals_previous_away_team_match >= 2 and last_away_team_matches_scored >= 2:
                    away_team_eligle = True

                if home_team_eligle and away_team_eligle and float(match['over25_odd'] >= 1.6) and float(match['over25_odd'] <= 2.2):
                    home__ft_score, away__ft_score = map(int, match['ft_result'].split('-'))
                    home__ht_score, away__ht_score = map(int, match['ht_result'].split('-'))
                    home_2ht_score = home__ft_score - home__ht_score
                    away_2ht_score = away__ft_score - away__ht_score
                    match['2ht_result'] = str(home_2ht_score) + '-' + str(away_2ht_score)
                    backtestingMatch = {}
                    backtestingMatch['01. timestamp'] = match['timestamp']
                    backtestingMatch['02. date'] = match['date']
                    backtestingMatch['03. competition'] = match['competition']
                    backtestingMatch['04. match'] = match['home_team'] + " - " + match['away_team']
                    backtestingMatch['05. ft_result'] = match['ft_result']
                    backtestingMatch['06. ht_result'] = match['ht_result']
                    backtestingMatch['07. 2ht_result'] = match['2ht_result']
                    backtestingMatch['08. over25_odd'] = match['over25_odd']
                    backtestingMatch['09. season'] = match['season']
                    backtestingMatch['10. home_total_goals_avg_at_home_pre'] = home_total_goals_avg_at_home_pre
                    backtestingMatch['11. away_total_goals_avg_at_away_pre'] = away_total_goals_avg_at_away_pre
                    matches_to_bet.append(backtestingMatch)
            except Exception as e:
                logging.info(f"Error decoding JSON for match ID {match.get('id', 'Unknown')}: {e}")
                logging.info(match['competition'] + " ## " + match['home_team'] + " - " + match['away_team'] +  " ## " + match['ft_result'])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.info(exc_type, fname, exc_tb.tb_lineno)
                continue
            #break

        #logging.info(len(matches_to_bet))
        return matches_to_bet

    except psycopg2.Error as e:
        logging.info(f"PostgreSQL error: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            cursor = conn.cursor()  # Create a cursor before closing it
            cursor.close()
            conn.close()

def getMatchesByDateFromDB(date_str):
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
        logging.info("Getting data for " + date_str)

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = "SELECT date,timestamp,competition,home_team,away_team,ht_result,ft_result,h2h_matches,last_home_team_matches,last_away_team_matches,home_total_goals_avg_at_home_pre,away_total_goals_avg_at_away_pre FROM backtesting.matches_stats ms WHERE date LIKE %s and h2h_matches != '[]'"
        #query = "SELECT date,timestamp,competition,home_team,away_team,ht_result,ft_result,h2h_matches,last_home_team_matches,last_away_team_matches,home_total_goals_avg_at_home_pre,away_total_goals_avg_at_away_pre FROM backtesting.matches_stats ms WHERE date LIKE %s and h2h_matches != '[]' and competition in ('Ásia - AFC Champions League', 'Austrália - A-League', 'Áustria - 1. Liga', 'Bélgica - First Division B', 'Bélgica - Pro League', 'Bolívia - Primera División', 'Chile - Primera División', 'Costa Rica - Primera División', 'Dinamarca - 1st Division', 'Dinamarca - Superliga', 'Inglaterra - FA Cup', 'Inglaterra - Taça da Liga', 'Alemanha - Bundesliga', 'Estónia - Meistriliiga', 'Alemanha - DFB Pokal' , 'Alemanha - 2. Bundesliga', 'Islândia - Úrvalsdeild', 'Índia - I-League', 'Indonésia - Liga 1', 'Itália - Coppa Italia', 'Luxemburgo - National Division','Malta - Premier League','México - Liga de Expansión MX','México - Liga MX','Países Baixos - Eerste Divisie', 'Países Baixos - Eredivisie', 'Irlanda do Norte - Premiership', 'Noruega - Eliteserien', 'Noruega - 1. Division','Paraguai - Division Profesional', 'Polónia - Cup', 'Arábia Saudita - Pro League', 'Singapura - Premier League', 'Suécia - Superettan','Suíça - Challenge League', 'Suíça - Super League','Emirados Árabes Unidos - Arabian Gulf League','Estados Unidos da América - MLS','Estados Unidos da América - USL Championship','Estados Unidos da América - US Open Cup')"
        like_pattern = f"%{date_str}%"  # Construct the LIKE pattern
        cursor.execute(query, (like_pattern,))

        matches = cursor.fetchall()  # Fetch all results
        matches_to_bet = []

        for match in matches:
            try:
                h2h_matches_json = match['h2h_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
                last_home_team_matches = match['last_home_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
                last_away_team_matches = match['last_away_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
                home_total_goals_avg_at_home_pre = float(match['home_total_goals_avg_at_home_pre'])
                away_total_goals_avg_at_away_pre = float(match['away_total_goals_avg_at_away_pre'])
                if h2h_matches_json:  # Check if the JSON string is not empty/None
                    h2h_data = json.loads(h2h_matches_json)  # Parse the JSON string
                    last_home_data = json.loads(last_home_team_matches)  # Parse the JSON string
                    last_away_data = json.loads(last_away_team_matches)  # Parse the JSON string

                    bttsLastStreak = filterMatchesByBttsCondition(h2h_data)
                    btts_streak_length = int(bttsLastStreak.split('/')[1])
                    btts_streak_value = int(bttsLastStreak.split('/')[0])

                    overLastStreak = filterMatchesByOverCondition(h2h_data)
                    over_streak_length = int(overLastStreak.split('/')[1])
                    over_streak_value = int(overLastStreak.split('/')[0])

                    home_bttsLastStreak = filterMatchesByBttsCondition(last_home_data)
                    home_btts_streak_length = int(home_bttsLastStreak.split('/')[1])
                    home_btts_streak_value = int(home_bttsLastStreak.split('/')[0])

                    home_overLastStreak = filterMatchesByOverCondition(last_home_data)
                    home_over_streak_length = int(home_overLastStreak.split('/')[1])
                    home_over_streak_value = int(home_overLastStreak.split('/')[0])

                    away_bttsLastStreak = filterMatchesByBttsCondition(last_away_data)
                    away_btts_streak_length = int(away_bttsLastStreak.split('/')[1])
                    away_btts_streak_value = int(away_bttsLastStreak.split('/')[0])

                    away_overLastStreak = filterMatchesByOverCondition(last_away_data)
                    away_over_streak_length = int(away_overLastStreak.split('/')[1])
                    away_over_streak_value = int(away_overLastStreak.split('/')[0])


                    #if (btts_streak_length >= 6 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 6 and float(over_streak_value/over_streak_length) >= 0.75) and home_total_goals_avg_at_home_pre >= 2 and away_total_goals_avg_at_away_pre >= 2:
                    ##working: if home_total_goals_avg_at_home_pre >= 3 and away_total_goals_avg_at_away_pre >= 3 and (btts_streak_length >= 5 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 5 and float(over_streak_value/over_streak_length) >= 0.75) and ( (home_btts_streak_length >= 5 and float(home_btts_streak_value/home_btts_streak_length) >= 0.75) and (home_over_streak_length >= 5 and float(home_over_streak_value/home_over_streak_length) >= 0.75) or (away_btts_streak_length >= 5 and float(away_btts_streak_value/away_btts_streak_length) >= 0.75) and (away_over_streak_length >= 5 and float(away_over_streak_value/away_over_streak_length) >= 0.75) ):
                    if (btts_streak_length >= 5 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 5 and float(over_streak_value/over_streak_length) >= 0.75) and ( (home_btts_streak_length >= 5 and float(home_btts_streak_value/home_btts_streak_length) >= 0.75) and (home_over_streak_length >= 5 and float(home_over_streak_value/home_over_streak_length) >= 0.75) or (away_btts_streak_length >= 5 and float(away_btts_streak_value/away_btts_streak_length) >= 0.75) and (away_over_streak_length >= 5 and float(away_over_streak_value/away_over_streak_length) >= 0.75) ):
                        # logging.info("BTTS streak: " + bttsLastStreak)
                        # logging.info("OVER streak: " + overLastStreak)
                        # logging.info("\n\n")
                        home__ft_score, away__ft_score = map(int, match['ft_result'].split('-'))
                        home__ht_score, away__ht_score = map(int, match['ht_result'].split('-'))
                        home_2ht_score = home__ft_score - home__ht_score
                        away_2ht_score = away__ft_score - away__ht_score
                        match['2ht_result'] = str(home_2ht_score) + '-' + str(away_2ht_score)
                        backtestingMatch = {}
                        backtestingMatch['01. timestamp'] = match['timestamp']
                        backtestingMatch['02. date'] = match['date']
                        backtestingMatch['03. competition'] = match['competition']
                        backtestingMatch['04. match'] = match['home_team'] + " - " + match['away_team']
                        backtestingMatch['05. ft_result'] = match['ft_result']
                        backtestingMatch['06. ht_result'] = match['ht_result']
                        backtestingMatch['07. 2ht_result'] = match['2ht_result']
                        backtestingMatch['08. home_total_goals_avg_at_home_pre'] = home_total_goals_avg_at_home_pre
                        backtestingMatch['09. away_total_goals_avg_at_away_pre'] = away_total_goals_avg_at_away_pre
                        matches_to_bet.append(backtestingMatch)
            except Exception as e:
                logging.info(f"Error decoding JSON for match ID {match.get('id', 'Unknown')}: {e}")
                logging.info(match['competition'] + " ## " + match['home_team'] + " - " + match['away_team'] +  " ## " + match['ft_result'])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.info(exc_type, fname, exc_tb.tb_lineno)
                continue
            #break

        logging.info(len(matches_to_bet))
        return matches_to_bet

    except psycopg2.Error as e:
        logging.info(f"PostgreSQL error: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            cursor = conn.cursor()  # Create a cursor before closing it
            cursor.close()
            conn.close()

def evalute_btts_one_half_result(match):
    if (int(match['06. ht_result'].split('-')[0]) > 0 and int(match['06. ht_result'].split('-')[1]) > 0) or (int(match['07. 2ht_result'].split('-')[0]) > 0 and int(match['07. 2ht_result'].split('-')[1]) > 0):
        return True
    return False

def filterMatchesByBttsCondition(h2h_matches):
    results = []
    #logging.info("\n".join(h2h_matches))
    for match in h2h_matches:
        match_result = ''
        
        if 'ET' in match.split('|')[3].strip():
            match_result = match.split('|')[3].split('ET')[0].strip()
        elif 'PG' in match.split('|')[3].strip():
            match_result = match.split('|')[3].split('PG')[0].strip()
        elif match.split('|')[3].strip() == '-':
            continue
        else:
            match_result = match.split('|')[3].strip()
        results.append(match_result)

    best_scored = 0
    best_total = 0
    best_percentage = 0.0

    if not results:
        return "0/0"

    for streak_length in range(min(5,len(results)), len(results) + 1):
        # The streak starts at the beginning of the list (most recent)
        streak = results[:streak_length]  # Get the first 'streak_length' elements

        scored_count = 0
        for result in streak:
            home_score, away_score = map(int, result.split('-'))
            if home_score > 0 and away_score > 0:
                scored_count += 1

        percentage = (scored_count / streak_length) if streak_length > 0 else 0.0

        if percentage > best_percentage:
            best_percentage = percentage
            best_scored = scored_count
            best_total = streak_length

    return f"{best_scored}/{best_total}"


def filterMatchesByOverCondition(h2h_matches):
    results = []
    #logging.info(h2h_matches)
    for match in h2h_matches:
        match_result = ''
        
        if 'ET' in match.split('|')[3].strip():
            match_result = match.split('|')[3].split('ET')[0].strip()
        elif 'PG' in match.split('|')[3].strip():
            match_result = match.split('|')[3].split('PG')[0].strip()
        elif match.split('|')[3].strip() == '-':
            continue
        else:
            match_result = match.split('|')[3].strip()
        results.append(match_result)

    best_scored = 0
    best_total = 0
    best_percentage = 0.0

    if not results:
        return "0/0"

    for streak_length in range(min(5,len(results)), len(results) + 1):
        # The streak starts at the beginning of the list (most recent)
        streak = results[:streak_length]  # Get the first 'streak_length' elements

        scored_count = 0
        for result in streak:
            home_score, away_score = map(int, result.split('-'))
            if home_score+away_score > 2:
                scored_count += 1

        percentage = (scored_count / streak_length) if streak_length > 0 else 0.0

        if percentage > best_percentage:
            best_percentage = percentage
            best_scored = scored_count
            best_total = streak_length

    return f"{best_scored}/{best_total}"