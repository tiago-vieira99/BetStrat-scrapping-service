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
    
    #teams = filterTeamsBySeason("23-24")
    #teams for 24-25:
    teams = ["1. FC Heidenheim 1846", "1. FC Kaiserslautern", "1. FC Köln", "1. FC Nürnberg", "1. FSV Mainz 05", "1899 Hoffenheim", "2 de Mayo", "Aalborg BK", "Aberdeen FC", "Abha Club", "AC Sparta Praha", "AC Sparta Praha B", "Adelaide United", "ADO Den Haag", "AE Kifisias", "AE Zakakiou", "AEK Athen", "AEL Limassol", "AFC Ajax", "AFC Bournemouth", "AIK Solna", "Al Fateh", "Al Hazem", "Al Hilal", "Al Ittihad", "Al Nassr", "Al Wehda", "Alanyaspor", "Almere City FC", "Arsenal FC", "Arsenal FC U21", "AS Monaco", "Aston Villa", "Aston Villa U21", "Atalanta", "Athletic Club", "Athletico Paranaense", "Atlanta United FC", "Atlético San Luis", "Aucas", "AZ Alkmaar", "AZ Alkmaar (J)", "Bayer Leverkusen", "Bayern München", "Beşiktaş", "BK Häcken", "Blackburn Rovers U21", "Boavista", "Bolívar", "Bor. Mönchengladbach", "Borussia Dortmund", "Boyacá Chicó", "Brentford FC", "Brighton & Hove Albion", "Brighton & Hove Albion U21", "Brisbane Roar", "Brøndby IF", "Bruk-Bet Termalica Nieciecza", "Burnley FC", "Cagliari Calcio", "Cangzhou Mighty Lions", "CD Magallanes", "CD Nacional", "Celtic FC", "Cercle Brugge", "Cerro Porteño", "CF Monterrey", "CF Pachuca", "Chelsea FC", "Chelsea FC U21", "Club Brugge KV", "Club Necaxa", "Club Tijuana", "Cobresal", "Colorado Rapids", "Columbus Crew", "Coventry City", "Crvena Zvezda", "Crystal Palace U21", "CS Universitatea Craiova", "CSKA Moskva", "De Graafschap", "Defensor Sporting", "Deportes Iquique", "Derby County U21", "Dinamo Brest", "Dinamo Moskva", "Diósgyöri VTK", "Dukla Banská Bystrica", "Dynamo České Budějovice", "Eintracht Frankfurt", "Ethnikos Achna", "Everton FC U21", "FC Alashkert", "FC Ararat-Armenia", "FC Arouca", "FC Augsburg", "FC Dordrecht", "FC Eindhoven", "FC Emmen", "FC København", "FC Liefering", "FC Lorient", "FC Luzern", "FC Midtjylland", "FC Mynai", "FC Porto", "FC Porto B", "FC Schalke 04", "FC St. Gallen", "FC Urartu", "FC Volendam", "FC Winterthur", "Fenerbahçe", "Feyenoord", "FK Bodø/Glimt", "FK Čukarički", "FK Orenburg", "FK Radnički 1923", "FK Smorgon", "FK Varnsdorf", "FK Voždovac", "FK Železiarne Podbrezová", "Forge FC", "Fortuna Düsseldorf", "Fulham FC", "Fulham FC U21", "Galatasaray", "Gallos Blancos", "Gaziantep FK", "GD Chaves", "GD Estoril", "Girona FC", "Go Ahead Eagles", "Hamburger SV", "Hannover 96", "Hapoel Haifa", "HB Køge", "Henan FC", "Heracles Almelo", "Hertha BSC", "Hibernian FC", "HJK Helsinki", "Huddersfield Town", "IF Brommapojkarna", "IFK Norrköping", "Inter", "Inter Miami CF", "Jeonbuk FC", "Jiangxi Lushan", "Jong Ajax", "Jong PSV", "Júbilo Iwata", "KAA Gent", "Kalmar FF", "Kapfenberger SV 1919", "Karlsruher SC", "Karmiotissa Polemidion", "Kashiwa Reysol", "Kasımpaşa SK", "KF Tiranë", "Konyaspor", "KRC Genk II", "Krylia Sovetov", "KVC Westerlo", "Lamia", "Leeds United U21", "Legia Warszawa", "Leicester City U21", "Leones FC", "Lierse Kempenzonen", "Lille OSC", "Liverpool FC", "Liverpool FC U21", "Lokomotiv Moskva", "Lokomotiv Plovdiv", "Los Angeles FC", "Los Angeles Galaxy", "Luton Town", "Macarthur FC", "Maccabi Petach-Tikva", "Manchester City", "Manchester City U21", "Manchester United U21", "Mazatlán FC", "Metalist 1925 Kharkiv", "Mezőkövesdi SE", "MG", "Middlesbrough FC", "Middlesbrough FC U21", "Minnesota United FC", "Mjällby AIF", "MKE Ankaragücü", "Molde FK", "Montpellier HSC", "Motherwell FC", "MŠK Žilina", "MTK Budapest", "MVV", "NAC Breda", "Naftan Novopolotsk", "Nea Salamina", "NEC Nijmegen", "New York City FC", "Newcastle United", "Newcastle United Jets", "Newcastle United U21", "NK Bravo", "NK Celje", "NK Domžale", "NK Maribor", "NK Veres", "Norwich City U21", "Nottingham Forest", "Nottingham Forest U21", "Odds BK", "OFI Heraklion", "Olimpija Ljubljana", "Olympiakos Piraeus", "Omonia Nikosia", "Othellos Athienou", "PAE Chania", "Panathinaikos", "Panserraikos", "PAOK Saloniki", "Paris Saint-Germain", "Parma Calcio 1913", "Partizan", "PAS Giannina", "Pau FC", "PEC Zwolle", "Pendikspor", "Perth Glory", "Philadelphia Union", "Pisa SC", "Portimonense SC", "Portland Timbers", "PSV Eindhoven", "Puebla FC", "Pyunik FC", "Rangers FC", "Rapid Bucureşti", "RB Leipzig", "RC Strasbourg", "Reading FC U21", "Real Madrid", "Real Salt Lake", "Recoleta", "Resovia Rzeszów", "RFC Seraing", "Rio Ave FC", "Roda JC Kerkrade", "Rodez AF", "Rosenborg BK", "Royal Francs Borains", "Royal Pari", "RSC Anderlecht", "RSCA Futures", "RWDM Brussels FC", "Sagan Tosu", "Samsunspor", "San Jose Earthquakes", "Santa Cruz", "Santos Laguna", "Sarpsborg 08", "SBV Excelsior", "SC Cambuur", "SC Farense", "sc Heerenveen", "SC Paderborn 07", "Schwarz-Weiß Bregenz", "Shakhtar Donetsk", "Shanghai Port FC", "Shanghai Shenhua", "Sheffield United", "Sigma Olomouc", "Silkeborg IF", "Sint-Truidense VV", "SK Brann", "SKN St. Pölten", "SL Benfica", "Slavia Praha", "Slovan Bratislava", "Slovan Liberec", "SønderjyskE", "Southampton FC", "Southampton FC U21", "Sparta Rotterdam", "Sporting Braga", "Sporting CP", "Sporting Kansas City", "Sportivo Trinidense", "St. Louis City SC", "Stade de Reims", "Stade Rennais", "Stade-Lausanne-Ouchy", "Stal Rzeszow", "Stoke City U21", "Sturm Graz (A)", "Sunderland AFC U21", "SV 07 Elversberg", "SV Horn", "SV Lafnitz", "SV Stripfing/Weiden", "Sydney FC", "Telstar", "The Strongest", "Tottenham Hotspur", "Tottenham Hotspur U21", "Toulouse FC", "TSC Bačka Topola", "TSV Hartberg", "UANL Tigres", "Udinese Calcio", "Újpest FC", "Unión Comercio", "Unión La Calera", "Universidad de Concepción", "Universidad Técnica", "US Catanzaro", "US Salernitana 1919", "US Souf", "Vålerenga IF", "Valour FC", "Vancouver FC", "Vancouver Whitecaps", "VfB Stuttgart", "VfL Bochum", "VfL Wolfsburg", "Viking FK", "Viktoria Žižkov", "Vilaverdense FC", "Villarreal CF", "Vitesse", "Vojvodina", "Volos NFC", "VVV-Venlo", "Werder Bremen", "West Bromwich Albion U21", "West Ham United", "West Ham United U21", "Willem II", "Wisła Kraków", "Wisła Płock", "Wolverhampton Wanderers U21", "Yokohama F. Marinos", "York United", "Yverdon Sport FC", "Zalaegerszegi TE", "Železničar Pančevo", "Zenit St. Petersburg", "Zhejiang Professional"]

    #csv file header
    matches.append("datetime ; competition ; match ; h2h matches ; h2h goals")
    for k in range(0, 4):
        current_date = today + timedelta(days=k)
        print(current_date)
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
    f_teams = filterTeamsBySeason(previousSeason)

    #f_teams = ["Incheon United", "Kauno Zalgiris", "Angers SCO", "FC Hradec Králové", "Eintracht Braunschweig", "Hvidovre IF", "Viktoria Plzeň", "Degerfors", "Degerfors IF", "FC DAC 1904", "Levadia Tallin", "1. FC Heidenheim 1846", "Kayserispor", "Spartak Subotica", "Sarpsborg 08", "JK Narva Trans", "FBC Melgar", "Crystal Palace", "Athletic Bilbao", "Rubin Kazan", "Piast Gliwice", "NK Istra 1961", "Curicó Unido", "Konyaspor", "Lyngby BK", "Nea Salamina", "Portuguesa FC", "Montevideo Wanderers", "Libertad", "Lazio Roma", "RSC Anderlecht", "Cumbayá", "2 de Mayo", "FC Blau Weiß Linz", "Daegu", "AS Roma", "MFK Zemplín Michalovce", "Golden Arrows", "Kalmar", "Brentford FC", "FC Famalicão", "Paris Saint-Germain", "Patronato Paraná", "Lille OSC", "Always Ready", "Pescara Calcio", "FKS Stal Mielec", "Suwon Bluewings", "1. FC Union Berlin", "CD Santa Clara", "Tromso", "SSC Napoli", "Liverpool", "Boavista", "Lechia Gdańsk", "Emelec", "FK Jablonec", "Odense BK", "CD Nacional", "Göteborg", "PEC Zwolle", "LASK", "Zagłębie Lubin", "NEC Nijmegen", "Granada CF", "OGC Nice", "BATE Borisov", "Lanús", "Göztepe", "VfL Osnabruck", "Sint-Truidense VV", "Paris FC", "AS Monaco", "Defensor Sporting", "LDU de Quito", "Jagiellonia Białystok", "Union Saint-Gilloise", "Austria Lustenau", "Go Ahead Eagles", "Sparta Rotterdam", "Atlético de Rafaela", "FK Oleksandriya", "Manchester United", "Sampdoria", "Atlético Palmaflor", "Beşiktaş", "Stade Brestois 29", "Hellas Verona", "The Strongest", "Ümraniyespor", "Pendikspor", "Vejle BK", "Strømsgodset IF", "Çaykur Rizespor", "Zorya Lugansk", "Colo-Colo", "Sporting Charleroi", "Brighton & Hove Albion", "FC Tokyo", "Livingston FC", "Greenock Morton", "Universitario de Vinto", "CSKA Moskva", "GD Estoril", "AZ Alkmaar", "Nacional Potosí", "Bala Town FC", "Cerezo Osaka", "1. FC Köln", "Trabzonspor", "FC Barcelona", "1. FSV Mainz 05", "FK Rostov", "Estudiantes de Mérida FC", "Bohemians Praha 1905", "IK Sirius", "Motherwell FC", "Venezia FC", "Aucas", "Club Olimpia", "İstanbul Başakşehir", "Werder Bremen", "Sporting CP", "Brann", "Flamengo RJ", "Real Betis", "Bodrum FK", "Heracles Almelo", "UD Almería", "Unión La Calera", "AS Trenčín", "AJ Auxerre", "RC Lens", "BSC Young Boys", "Rosenborg", "AEK Larnaca", "Fehérvár FC", "Atalanta", "FK Haugesund", "Sandefjord Fotball", "AFC Bournemouth", "Kjelsas", "Newcastle United", "Atlético Junior", "River Plate", "Cagliari Calcio", "Bologna FC", "Jeonbuk Motors", "FC Basel 1893", "HNK Rijeka", "GD Chaves", "1. FC Nurnberg", "Olympique Marseille", "VfB Stuttgart", "CD Guabirá", "Valencia CF", "Djurgårdens IF", "Audax Italiano", "Metropolitanos FC", "Orense SC", "Doxa Katokopias", "HJK Helsinki", "Academia Puerto Cabello", "Millonarios", "Mansfield Town", "RB Salzburg", "FC Twente", "Leicester City", "Karlsruher SC", "Brøndby IF", "CD Hermanos Colmenarez", "Antofagasta", "Cartaginés", "O'Higgins", "Club Aurora", "Sporting Braga", "AC Sparta Praha", "VfL Wolfsburg", "1. FC Slovácko", "AS Saint-Étienne", "1. FC Magdeburg", "FK Mladá Boleslav", "Montpellier HSC", "ŁKS Łódź", "Grazer AK", "Hatayspor", "PFC Ludogorets Razgrad", "Flora Tallin", "Universidad Católica", "Tottenham Hotspur", "Stade Rennais", "VfL Bochum", "Moreirense FC", "FC Schalke 04", "West Ham United", "Delfín SC", "St. Pauli", "FC St. Pauli", "SønderjyskE", "Zenit St. Petersburg", "Slovan Bratislava", "Mezőkövesdi SE", "İstanbulspor AŞ", "Sportivo Luqueño", "Pogoń Szczecin", "Defensa y Justicia", "El Nacional", "B36 Tórshavn", "River Plate Montevideo", "SC Freiburg", "Eintracht Frankfurt", "Sivasspor", "Southampthon FC", "Ulsan Horang-i", "Jorge Wilstermann", "Fatih Karagümrük SK", "Fortuna Sittard", "SV Darmstadt 98", "Dynamo České Budějovice", "Hacken", "Norrkoping", "SV Wehen Wiesbaden", "SS Monopoli", "FK Khimki", "CA Cerro", "FC Volendam", "Mineros de Guayana", "SpVgg Greuther Furth", "Sporting Cristal", "Górnik Zabrze", "FC Nordsjælland", "Royal Pari", "RB Leipzig", "Palestino", "Ismaily SC", "Spezia Calcio", "Kasımpaşa SK", "Aalborg BK", "Zamalek SC", "Lokomotiv Moskva", "Lokomotiva Zagreb", "Gaziantep FK", "Al Ahli Jeddah", "FK Dukla Praha", "Újpest FC", "Universidad de Chile", "MFK Karviná", "Melbourne Heart", "Vicenza", "Sassuolo Calcio", "FC Luzern", "Odds BK", "Santiago Morning", "FK Teplice", "Universidad Catolica", "Tokyo Verdy", "FK Sochi", "FC Lausanne-Sport", "Hamburger SV", "FK Orenburg", "SBV Excelsior", "Club América", "Randers FC", "Aktobe", "Legia Warszawa", "Monagas", "HamKam", "Hamarkameratene", "Bayer Leverkusen", "Willem II", "FC Sion", "Wolfsberger AC", "Alanyaspor", "RKC Waalwijk", "Jeju United", "KV Kortrijk", "sc Heerenveen", "Adana Demirspor", "Almere City FC", "Olympique Lyonnais", "FC St. Gallen", "NK Maribor", "Astana", "Borussia Dortmund", "FC Winterthur", "Dundee FC", "FC Zlín", "ESTAC Troyes", "Bayern München", "Varbergs BoIS", "US Lecce", "FC Zürich", "Universitario de Deportes", "SC Paderborn 07", "Godoy Cruz", "Grasshopper Club Zürich", "Paksi SE", "Fenerbahçe", "Baník Ostrava", "KVC Westerlo", "Unión Española", "Spartak Moskva", "MKE Ankaragücü", "Austria Wien", "Zweigen Kanazawa", "Hertha BSC", "Galatasaray", "KAS Eupen", "Holstein Kiel", "Fortuna Dusseldorf", "Paide Linnameeskond", "FC Augsburg", "NorthEast United", "Stjarnan", "Sydney FC", "JK Tammeka", "PSV Eindhoven", "NAC Breda", "Rapid Wien", "IF Elfsborg", "KRC Genk", "Vitesse", "Servette FC", "KV Mechelen", "MŠK Žilina", "Bor. Mönchengladbach", "Oud-Heverlee Leuven", "Zilina", "Aalesunds FK", "TSV Hartberg", "Bodø/Glimt", "Mannucci", "Lillestrøm", "Cercle Brugge", "FC Utrecht", "Víkingur Gøta", "Hammarby", "Kerala Blasters", "Viking", "Molde", "1899 Hoffenheim", "SK Austria Klagenfurt", "Real Santa Cruz"]

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