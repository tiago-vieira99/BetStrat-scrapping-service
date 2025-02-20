import csv
from collections import Counter
import pandas as pd
from datetime import datetime, timedelta
import requests
import sys, os
from bs4 import BeautifulSoup

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
        print("\n" + str(current_date) + "\n")
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
                        print(r[3] + " - " + r[7])
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
                            print("MATCH ADDED!\n")
                            matches.append(formatted_date + " " + r[1] + " ; " + competition + " ; " + r[3] + " - " + r[7] + " ; " + h2hmatches + " ; " + str(h2hgoals))       
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)                        
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
    csv_file = "/scrapper/newData/matches" + season + ".csv"  # Replace with your actual file path
    
    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];

    data = pd.read_csv(csv_file, sep=',', dtype='unicode')
    results = []
    #f_teams = filterTeamsBySeason(previousSeason)

    #2025 teams:
    f_teams = ["RB Leipzig", "1. FC Köln", "FC Zlín", "SL Benfica", "Montpellier HSC", "Atlético Bucaramanga", "FK Ural", "Aswan FC", "Fénix", "Göteborg", "AJ Auxerre", "Monagas", "FK Jablonec", "FK Sochi", "Zenit St. Petersburg", "Sigma Olomouc", "West Ham United", "Manchester United", "Libertad", "Sarpsborg 08", "Mineros de Guayana", "Villarreal CF", "RSC Anderlecht", "FC København", "FK Krasnodar", "NK Osijek", "FC Lausanne-Sport", "Queen's Park", "Sheffield United", "Frosinone Calcio", "FC Zürich", "Sparta Rotterdam", "FKS Stal Mielec", "Varbergs BoIS", "Górnik Zabrze", "Belgrano de Córdoba", "AS Roma", "Malmö FF", "MKE Ankaragücü", "Çaykur Rizespor", "Emelec", "AC Milan", "Santa Fe", "Fehérvár FC", "Carabobo FC", "Olimpija Ljubljana", "JK Narva Trans", "Bologna FC", "Motherwell FC", "FC DAC 1904", "CD Nacional", "Zorya Lugansk", "1. FSV Mainz 05", "Bnei Sachnin FC", "Gil Vicente", "Fortuna Sittard", "Palestino", "Nea Salamina", "FC Barcelona", "Shakhtar Donetsk", "Austria Wien", "Stade de Reims", "Atlético de Rafaela", "Sturm Graz", "Always Ready", "Zalgiris", "MFK Zemplín Michalovce", "Korona Kielce", "Shamrock Rovers", "Fortaleza FC", "Slavia Praha", "Stabæk IF", "Crystal Palace", "Palmeiras", "Halmstad", "Piast Gliwice", "O'Higgins", "FK Pardubice", "Sport Huancayo", "Havre AC", "Dundee United", "Getafe CF", "Atromitos", "The Strongest", "Amiens SC", "Sint-Truidense VV", "FBC Melgar", "Ebro", "Baroka", "Dinamo Tbilisi", "Cherno More Varna", "Envigado FC", "Maccabi Tel Aviv", "Udinese Calcio", "Akhmat Grozny", "Baník Ostrava", "IK Sirius", "K Beerschot VA", "ACF Fiorentina", "Cartaginés", "FC Basel 1893", "Almere City FC", "Arsenal de Sarandí", "RC Lens", "Real Betis", "Vejle BK", "Royal Pari", "ESTAC Troyes", "Hvidovre IF", "Unión La Calera", "FC Luzern", "Leicester City", "Sandefjord Fotball", "FC Midtjylland", "WSG Tirol", "FC Lugano", "FC Metz", "FC Lorient", "RKC Waalwijk", "CA Cerro", "Lokomotiv Plovdiv", "Sivasspor", "Liverpool FC", "Mushuc Runa", "Lyngby BK", "Melbourne Heart", "St. Pauli", "Delfín SC", "RC Strasbourg", "Cerezo Osaka", "Tottenham Hotspur", "Cruz Azul", "Zweigen Kanazawa", "Flamengo RJ", "Paris Saint-Germain", "Legia Warszawa", "Norrkoping", "Jeju United", "Lokomotiva Zagreb", "Randers FC", "Feyenoord", "Slovan Bratislava", "Ulsan Horang-i", "Willem II", "Sol de América", "Anorthosis Famagusta", "Suwon Bluewings", "AEK Athen", "CD Santa Clara", "Barcelona", "AS Trenčín", "Defensor Sporting", "GD Chaves", "FC Twente", "Orense SC", "Patronato Paraná", "Metropolitanos FC", "AFC Bournemouth", "Olympiakos Piraeus", "Astana", "CSKA Moskva", "Shkupi", "Atlético Madrid", "RB Salzburg", "Torino FC", "River Plate", "Paris FC", "Incheon United", "Universidad Católica", "VfB Stuttgart", "Werder Bremen", "Aalesunds FK", "FK Haugesund", "Trabzonspor", "Vorskla Poltava", "B36 Tórshavn", "Bor. Mönchengladbach", "Aktobe", "Galatasaray", "SS Monopoli", "Aberdeen FC", "VfL Wolfsburg", "SC Freiburg", "VfL Bochum", "FK Teplice", "Fulham FC", "Ross County FC", "Śląsk Wrocław", "ŁKS Łódź", "Grazer AK", "FC Groningen", "Eyüpspor", "Jorge Wilstermann", "1. FC Magdeburg", "sc Heerenveen", "Degerfors", "Hatayspor", "Angers SCO", "NK Domžale", "Lanús", "Molde", "LDU de Quito", "Olympique Lyonnais", "Krylia Sovetov", "Fatih Karagümrük SK", "Grasshopper Club Zürich", "Atalanta", "Hammarby", "Degerfors IF", "Diriangén", "Hellas Verona", "NAC Breda", "Vojvodina", "Eintracht Frankfurt", "SV Darmstadt 98", "Godoy Cruz", "Greenock Morton", "Odense BK", "FC St. Pauli", "Vitória Guimarães", "Sevilla FC", "İstanbulspor AŞ", "CD Guabirá", "Wolfsberger AC", "Cumbayá", "Unión Española", "Pogoń Szczecin", "FC Sion", "FK Orenburg", "Servette FC", "SK Austria Klagenfurt", "Bohemians Praha 1905", "PEC Zwolle", "Newcastle United", "NEC Nijmegen", "Boavista", "Alanyaspor", "MFK Karviná", "Vitesse", "Academia Puerto Cabello", "El Nacional", "Virtus Francavilla", "Club América", "FCSB", "Bayer Leverkusen", "SønderjyskE", "Universitario de Deportes", "Panetolikos", "Flora Tallin", "Atlético Junior", "Olympique Marseille", "Crvena Zvezda", "Viborg FF", "FK Mladá Boleslav", "Luton Town", "FC Hradec Králové", "KV Kortrijk", "Celtic FC", "Rosenborg", "Valerenga", "Millonarios", "IF Elfsborg", "Real Madrid", "Defensa y Justicia", "TSV Hartberg", "Lokomotiv Moskva", "Valencia CF", "River Plate Montevideo", "Dundee FC", "Curicó Unido", "San Lorenzo", "Real Santa Cruz", "Union Saint-Gilloise", "AC Sparta Praha", "Manchester City", "NK Maribor", "Royal AM", "HJK Helsinki", "Sassuolo Calcio", "Dynamo České Budějovice", "PAS Giannina", "Rosario Central", "1. FC Heidenheim 1846", "Deportivo Cuenca", "PFC Ludogorets Razgrad", "Kauno Zalgiris", "Jagiellonia Białystok", "Nacional Potosí", "Odds BK", "FC Schalke 04", "Brann", "FK Rostov", "Adana Demirspor", "MŠK Žilina", "Kjelsas", "Paksi SE", "FC Augsburg", "Aston Villa", "Southampthon FC", "Stjarnan", "Cercle Brugge", "Universidad Catolica", "FK Dukla Praha", "Toulouse FC", "Hibernian FC", "Mansfield Town", "Aalborg BK", "Brentford FC", "SC Paderborn 07", "Oud-Heverlee Leuven", "Vicenza", "Hertha BSC", "Hamarkameratene", "JK Tammeka", "KRC Genk", "HamKam", "Tokyo Verdy", "Pendikspor", "Fenerbahçe", "Spezia Calcio", "FC Ashdod", "Espanyol Barcelona", "Lillestrøm", "OFI Heraklion", "Slovan Liberec", "Santiago Morning", "PSV Eindhoven", "Bayern München", "Paide Linnameeskond", "Fortuna Dusseldorf", "Víkingur Gøta", "Újpest FC", "Kasımpaşa SK", "Tromso", "Viking", "FC Volendam", "AS Monaco", "FC St. Gallen", "Zilina", "FK Khimki", "Hacken", "Colón de Santa Fe", "SBV Excelsior", "Borussia Dortmund", "FC Winterthur", "Mannucci", "FC Utrecht", "SpVgg Greuther Furth", "Al Ahli Jeddah", "Bodø/Glimt", "Holstein Kiel", "KVC Westerlo", "1899 Hoffenheim"]

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
    csv_file = "/scrapper/newData/matches" + season + ".csv"  # Replace with your actual file path
    
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
            #print(f"{team} ; {x} ; {y} ; {x/y}")

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