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


def generateFileForNextMatchesEbookStrategy():
    matches = []

    # Get today's date
    today = datetime.now()

    comps = [ "AFC > AFC Champions League", "Albania > Kategoria Superiore", "Algeria > Ligue 1", "Argentina > Primera División", "Armenia > Premier League", "Australia > A-League", "Austria > 2. Liga", "Austria > Bundesliga", "Azerbaijan > I Liqa", "Belarus > Cempionat", "Belgium > Challenger Pro League", "Belgium > Pro League", "Bolivia > Liga Profesional", "Brazil > Copa do Brasil", "Brazil > Série A", "Brazil > Série B", "Bulgaria > Parva Liga", "Canada > Premier League", "Chile > Copa Chile", "Chile > Primera B", "Chile > Primera División", "China > League One", "China > Super League", "Colombia > Copa Colombia", "Colombia > Primera A", "Colombia > Primera B", "Costa Rica > Primera División", "Croatia > 1. HNL", "Cyprus > First Division", "Czech Republic > 1. fotbalová liga", "Czech Republic > 2. fotbalová liga", "Denmark > 1. Division", "Denmark > Superliga", "Ecuador > Serie A", "England > Championship", "England > Premier League", "FIFA > Friendlies", "Finland > Veikkausliiga Championship", "France > Ligue 1", "France > Ligue 2", "Germany > 2. Bundesliga", "Germany > Bundesliga", "Greece > Super League", "Hungary > NB I", "Ireland > Premier Division", "Israel > Liga Leumit", "Israel > Ligat ha'Al", "Italy > Serie A", "Italy > Serie B", "Japan > J1 League", "Mexico > Primera División", "Netherlands > Eerste Divisie", "Netherlands > Eredivisie", "Norway > Eliteserien", "Paraguay > Primera División", "Peru > Primera División", "Poland > I Liga", "Portugal > Primeira Liga", "Portugal > Segunda Liga", "Portugal > Taça", "Portugal > U23 Liga Revelação", "Romania > Liga 1", "Russia > Premier Liga", "Saudi Arabia > Saudi Pro League", "Scotland > Premiership", "Serbia > Prva Liga", "Serbia > Super Liga", "Slovakia > Super Liga", "Slovenia > PrvaLiga", "South Korea > K League 1", "Spain > Copa del Rey", "Spain > Primera División", "Spain > Segunda División", "Sweden > Allsvenskan", "Switzerland > Super League", "Turkey > SüperLig", "UEFA > Champions League", "UEFA > Conference League", "UEFA > Europa League", "UEFA > Youth Youth League", "Ukraine > Premyer Liga", "Uruguay > Primera División", "USA > Major League Soccer" ];
    
    teams = [ "07 Vestur", "1. BFK Frýdlant", "1. CfR Pforzheim", "1. FC 06 Erlensee", "1. FC Düren", "1. FC Heidenheim 1846", "1. FC Kaiserslautern", "1. FC Kaiserslautern II", "1. FC Köln", "1. FC Köln II", "1. FC Magdeburg", "1. FC Magdeburg II", "1. FC Nürnberg", "1. FC Nürnberg II", "1. FC Phönix Lübeck", "1. FC Saarbrücken", "1. FC Schweinfurt 05", "1. FC Slovácko", "1. FC Union Berlin", "1. FSV Mainz 05", "1. FSV Mainz 05 II", "1. SC Feucht", "1. SC Znojmo", "1899 Hoffenheim", "AB Argir", "AB Gladsaxe", "AC", "AC Ajaccio", "AC Amager Academy", "AC Carpi", "AC Horsens", "AC Libertas", "AC Locri 1909", "AC Nagano Parceiro", "AC Oulu", "AC Pavia", "AC Sparta Praha", "AC Sparta Praha B", "AC Sparta Praha II (U14)", "AC Taverne", "ACF Brescia", "ACV Assen", "AD Huracan", "ADO Den Haag", "AE Kifisias", "AE Lárissa", "AE Zakakiou", "AEK Athen", "AEL Limassol", "AF Virois", "AFA Olaine", "AFC Ajax", "AFC Bournemouth", "AFC Bournemouth U23", "AFC Eskilstuna", "AFC Fylde", "AGF Fodbold", "AIK Solna", "APIA Leichhardt FC", "AS Cittadella", "AS Monaco", "AS Montferrand", "AS Pagny-sur-Moselle", "AS Roma", "AS Saint-Priest", "ASC 09 Dortmund", "ASD Canicattì", "ASD Res Roma", "ASK Klagenfurt", "ASK Voitsberg", "ASPTT Marseille", "ASV Cham", "ASV Draßburg", "ASV Neumarkt", "ATSV Mutschelbach", "AZ Alkmaar", "AZ Alkmaar (J)", "Aalborg BK", "Aalesunds FK", "Aalesunds FK II", "Aarhus Fremad", "Aarhus GF", "Aberdeen FC", "Abha Club", "Accrington Stanley", "Achuapa", "Adamstown Rosebud", "Adelaide Comets", "Adelaide Croatia Raiders", "Adelaide Olympic", "Adelaide United", "Adelaide United Youth", "Afturelding", "Aguacateros de Peribán", "Ajman Club", "Akademiya Konopleva", "Al Ahli Doha", "Al Ain FC", "Al Arabi SC", "Al Bataeh", "Al Duhail SC", "Al Fahaheel", "Al Fateh", "Al Gharafa", "Al Hazem", "Al Hilal", "Al Ittihad", "Al Jahra SC", "Al Jazira Club", "Al Markhiya SC", "Al Muharraq", "Al Najma", "Al Nassr", "Al Sadd", "Al Shamal SC", "Al Wahda", "Al Wasl", "Al Wehda", "Alania-2 Vladikavkaz", "Alanyaspor", "Albacete", "Albania", "Albirex Niigata (S)", "Aldershot Town", "Alebrijes de Oaxaca", "Alemannia Aachen", "Algeria", "Alloa Athletic", "Almere City FC", "Alta IF", "Altona 93", "Always Ready", "American Samoa", "Amsterdamsche FC", "América - MG", "Annan Athletic", "Antalyaspor", "Aomori Yamada High School", "Arbroath FC", "Ards FC", "Argentina", "Ariana FC", "Armadale SC", "Arminia Bielefeld", "Arminia Ludwigshafen", "Arna-Bjørnar", "Arsenal FC", "Arsenal FC U21", "Arsenal WFC", "Arsenal Česká Lípa", "Aruba", "Arucas CF", "Assyriska FF", "Asteras Tripolis", "Aston Villa", "Aston Villa U21", "Aston Villa WFC", "Atalanta", "Atlanta United FC", "Atlanta United II", "Atlas Delmenhorst", "Atlétic Escaldes", "Atlético Chiriquí", "Atlético La Paz", "Atlético Mineiro", "Atlético Pachuca", "Atlético San Luis", "Aucas", "Austin FC II", "Australia", "Austria", "Austria Salzburg", "Aveley FC", "B.93 København", "B36 Tórshavn", "B68 Toftir", "BFC Dynamo", "BG Pathum United", "BK Häcken", "BSC Old Boys", "BSC Young Boys", "BSC Young Boys II", "BTS Neustadt", "BVV Barendrecht", "Balestier Khalsa", "Bali United", "Ballyclare Comrades", "Balma SC", "Bangladesh", "Bangor FC", "Banik Ostrava", "Barnet FC", "Barnsley FC", "Barnsley FC U23", "Barracas Central II", "Bayer Leverkusen", "Bayern Alzenau", "Bayern München", "Bayern München II", "Bayswater City SC", "Beitar Rīga", "Belgrano de Córdoba II", "Belize", "Belshina Bobruisk", "Benin", "Bergerac Périgord FC", "Bermuda", "Beşiktaş", "Birmingham City U23", "Bischofswerdaer FV", "Blackburn Rovers", "Blackburn Rovers U21", "Blacktown City FC", "Blau-Weiß Bornreihe", "Blauw Geel '38", "Blois Foot 41", "Blumenthaler SV", "Blyth Spartans", "Boavista", "Bodens BK", "Bohemians Praha 1905", "Bohemians Praha 1905 II (U14)", "Bologna FC", "Bolton Wanderers", "Bolívar", "Bor. Mönchengladbach", "Bor. Mönchengladbach II", "Boreham Wood", "Borgo San Donnino", "Borussia Dortmund", "Borussia Dortmund II", "Borussia Freialdenhoven", "Bosnia-Herzegovina", "Botafogo - RJ", "Boyacá Chicó", "Brattvåg IL", "Breiðablik", "Brentford FC", "Brighton & Hove Albion", "Brighton & Hove Albion U21", "Brighton & Hove Albion WFC", "Brinkumer SV", "Brisbane City FC", "Brisbane Roar", "Brisbane Roar Youth", "Bristol City U23", "Bristol City WFC", "Bristol Rovers", "Broadmeadow Magic", "Bruk-Bet Termalica Nieciecza", "Brusaporto", "Brøndby IF", "Burkina Faso", "Burnley FC", "Burnley FC U23", "Bursaspor", "Buxton FC", "Bærum SK", "Bình Định FC", "CD Castellón", "CD Covadonga", "CD Guadalajara", "CD Magallanes", "CD Nacional", "CD Revilla", "CD Roda", "CD San Francisco", "CD San Jose", "CD Vasconia", "CDM FC", "CE Carroi", "CF América", "CF Atlètic Amèrica", "CF Badalona", "CF Bansander", "CF Esperança d'Andorra", "CF Gazte Berriak", "CF Pachuca", "CF Platges de Calvià", "CF Unión Viera", "CS Chênois", "CS Petrocub", "CS Romontois", "CS Universitatea Craiova", "CSKA Moskva", "Caernarfon Town", "Cagliari Calcio", "Caja Oblatos", "Calavera CF", "Campbelltown City SC", "Canberra Croatia", "Canberra Olympic", "Canberra United", "Canet Roussillon", "Cangzhou Mighty Lions", "Cardiff City", "Cardiff City U23", "Cardiff Metropolitan", "Carlos Stein", "Carrick Rangers", "Castelnau Le Crès FC", "Cavigal Nice", "Celtic FC", "Central Coast Mariners Academy", "Cercle Brugge", "Cesena FC", "Chamois Niortais", "Charlestown Azzurri", "Charlton Athletic", "Charlton Athletic U23", "Chattanooga FC", "Chelsea FC", "Chelsea FC U21", "Chelsea FC Women", "Chengdu Rongcheng", "Chertanovo Football Academy", "Chesterfield FC", "Chicago Fire 2", "ChievoVerona Valpo", "Chilangos FC", "Chlumec nad Cidlinou", "Chongqing Tongliang Long", "Chorley FC", "Chur 97", "Churchill Brothers", "Cimarrones de Sonora", "Clarence Zebras", "Cliftonville FC", "Club Brugge KV", "Club Nacional", "Club Tijuana", "Club de Ciervos", "Clyde FC", "Cobh Ramblers", "Cobresal", "Colchester United", "Colchester United U23", "Coleraine FC", "College 1975 FC", "Colorado Rapids", "Colorado Rapids 2", "Colorado Springs Switchbacks", "Columbus Crew", "Columbus Crew 2", "Como 1907", "Comoros", "Connah's Quay Nomads", "Cook Islands", "Cooks Hill United", "Cooma FC", "Correcaminos UAT II", "Corticella", "Cosmos Koblenz", "Cove Rangers", "Coventry City", "Coventry City U23", "Crawley Town", "Crewe Alexandra", "Crewe Alexandra U23", "Croatia", "Crown Legacy FC", "Croydon Kings", "Crusaders FC", "Crvena Zvezda", "Crystal Palace", "Crystal Palace U21", "Curaçao", "Czech Republic", "Công An Hà Nội FC", "DJK Adler Union Frintrop", "DJK Ammerthal", "DJK Gebenbach", "DJK Vilzing", "DPMM FC", "Dacia Buiucani", "Dalian Pro", "Dalkurd FF", "Dalvík/Reynir", "Dandenong City SC", "Dandenong Thunder", "De Graafschap", "De Treffers", "Degerfors IF", "Delfino Pescara", "Delhi FC", "Denizlispor", "Denmark", "Deportes Iquique", "Deportivo Dongu", "Deportivo Garcilaso", "Deportivo Guadalajara", "Deportivo Ibarra", "Deportivo La Guaira", "Deportivo Malacateco", "Derby County U21", "Dergview FC", "Deutschlandsberger SC", "Devonport City FC", "Dewa United FC", "Dijon FCO", "Dinamo Barnaul", "Dinamo Brest", "Dinamo Moskva", "Dinamo Moskva 2", "Dinan Léhon", "Diósgyöri VTK", "Djurgårdens IF", "Dom. Republic", "Doncaster Rovers", "Dorados de Sinaloa", "Dornbirner SV", "Dragonas IDV", "Dukla Banská Bystrica", "Dundela FC", "Dunfermline Athletic", "Dungannon Swifts", "Dynamo Schwerin", "Dynamo České Budějovice", "Dynamo České Budějovice B", "Dynamo České Budějovice II (U14)", "Düneberger SV", "EA Guingamp (CFA)", "EB/Streymur", "EDF Logroño", "EF Gava", "EFB Miguelturra", "ES Saintes", "ES Wasquehal", "ESC Geestemünde", "ETSV Hamburg", "East Fife FC", "East Riffa Club", "Eastern SC", "Eastleigh FC", "Eckernförder SV", "Edgeworth FC", "Edinburgh City", "Egersunds IK", "Eidsvold TF", "Einheit Wernigerode", "Eintracht Frankfurt", "Eintracht Norderstedt", "Eintracht Stadtallendorf", "Eintracht Trier", "Ekenäs IF", "El Salvador", "Elgin City", "Emirates Club", "Energie Cottbus", "England", "Enisey Krasnoyarsk 2", "Esbjerg fB", "Espuce FC", "Estonia", "Ethnikos Achna", "Etoile Carouge FC", "Everton FC U21", "Excelsior Maassluis", "F91 Dudelange", "FBK Karlstad", "FC 08 Homburg", "FC 08 Villingen", "FC 93 Bobigny", "FC Aarau", "FC Ajoie-Monterri", "FC Alashkert", "FC Alsterbrüder", "FC Amical Saint-Prex", "FC Anker Wismar", "FC Annecy", "FC Arouca", "FC Augsburg", "FC Baden", "FC Baden 1897", "FC Balzers", "FC Barcelona", "FC Basel 1893", "FC Basel 1893 II", "FC Bassecourt", "FC Bavois", "FC Bazenheid", "FC Bergheim", "FC Besa Biel/Bienne", "FC Bitburg", "FC Black Stars Basel", "FC Borgo", "FC Bosporus", "FC Bourg-Péronnas", "FC Breitenrain Bern", "FC Brünninghausen", "FC Bubendorf", "FC Büderich 02", "FC Bülach", "FC Bălţi", "FC Carl Zeiss Jena", "FC Chamalières", "FC Châtel-Saint-Denis", "FC Cincinnati 2", "FC Coburg", "FC Coffrane", "FC Collex-Bossy", "FC Concordia Basel", "FC Concordia Lausanne", "FC Concordia/BSC Old Boys", "FC Courtételle", "FC Dardania Lausanne", "FC Deisenhofen", "FC Den Bosch", "FC Denzlingen", "FC Dietikon", "FC Differdange 03", "FC Dordrecht", "FC Dornbreite Lübeck", "FC Dübendorf", "FC Echallens", "FC Echichens", "FC Eddersheim", "FC Eindhoven", "FC Einheit Rudolstadt", "FC Emmen", "FC Emmenbrücke", "FC Farvagny/Ogoz", "FC Fiorentino", "FC Floreşti", "FC Frauenfeld", "FC Gießen", "FC Gleisdorf 09", "FC Gossau", "FC Grand-Saconnex", "FC Grimma", "FC Groningen", "FC Gütersloh", "FC Hanau 93", "FC Helsingør", "FC Hennef 05", "FC Hlučín", "FC Holzhausen", "FC Hradec Králové", "FC Hradec Králové B", "FC Hradec Králové II (U14)", "FC Iberia 1999", "FC Ingolstadt 04", "FC Ingolstadt 04 II", "FC Istres", "FC Karbach", "FC Kreuzlingen", "FC København", "FC La Chaux-de-Fonds", "FC La Sarraz-Eclépens", "FC La Tour/Le Pâquier", "FC Lachen/Altendorf", "FC Lahti", "FC Lausanne-Sport", "FC Libourne", "FC Liefering", "FC Liestal", "FC Linth 04", "FC Lisse", "FC Lorient", "FC Lugano II", "FC Luzern", "FC Luzern II", "FC Mantois", "FC Marmande 47", "FC Martigny Sports", "FC Mauerwerk", "FC Memmingen", "FC Mendrisio", "FC Meyrin", "FC Midtjylland", "FC Mondercange", "FC Muri", "FC Muri-Gümligen", "FC Münsingen", "FC Nantes", "FC Naters", "FC Nordsjælland", "FC Nöttingen", "FC Oberneuland", "FC Perlen-Buchrain", "FC Perly-Certoux", "FC Plan-les-Ouates", "FC Portalban/Gletterens", "FC Porto", "FC Porto B", "FC Praha", "FC Pratteln", "FC Prishtina Bern", "FC Písek", "FC Rapperswil-Jona", "FC Rapperswil-Jona II", "FC Rapperswil-Jona/GC", "FC Rijnvogels", "FC Rosengård", "FC Rosengård 1917", "FC Roskilde", "FC Rot-Weiß Rankweil", "FC Samtredia", "FC Santa Coloma", "FC Schaffhausen", "FC Schalke 04", "FC Schalke 04 II", "FC Schifflange 95", "FC Schötz", "FC Sheriff", "FC Sion", "FC Sion II", "FC Slovan Rosice", "FC Sochaux", "FC St. Gallen", "FC St. Gallen II", "FC St. Pauli", "FC St. Pauli II", "FC Stade Nyonnais", "FC Sursee", "FC Süderelbe", "FC Tavannes/Tramelan", "FC Thalwil", "FC Thun Berner Oberland", "FC Thun Berner Oberland II", "FC Tiamo Hirakata", "FC Trollhättan", "FC Tuggen", "FC Twente", "FC Tägerwilen", "FC Türkiye", "FC Ueberstorf", "FC Unterstrass", "FC Urartu", "FC Uster", "FC Utrecht", "FC Uzwil", "FC Vaduz", "FC Veyrier Sports", "FC Volendam", "FC Wacker Innsbruck", "FC Weesen", "FC Wegberg-Beeck", "FC Wettswil-Bonstetten", "FC Widnau", "FC Wil 1900", "FC Wil 1900 II", "FC Wiltz 71", "FC Winterthur", "FC Winterthur II", "FC Wolfurt", "FC Zbrojovka Brno", "FC Zlín", "FC Zürich", "FC Zürich Frauen", "FC Zürich Frauen (U21)", "FCB Magpies", "FCE Rheine", "FCM Aubervilliers", "FCM Traiskirchen", "FCO Rheintal/Bodensee", "FCO St. Gallen", "FCO Wil", "FCSR Haguenau", "FCV Dender EH II", "FF Jaro", "FFC Vorderland", "FH Hafnarfjörður", "FK Admira Praha", "FK Arendal", "FK Arsenal", "FK Beograd", "FK Blansko", "FK Bodø/Glimt", "FK Budućnost Podgorica", "FK Chertanovo", "FK Dinamo Rīga", "FK Dukla Praha", "FK Dukla Praha B", "FK Frýdek-Místek", "FK Jablonec", "FK Jablonec II (U14)", "FK Jerv", "FK Kolomna", "FK Kolín", "FK Krasnodar", "FK Králův Dvůr", "FK Liepāja", "FK Loko Vltavín", "FK MAS Táborsko B", "FK Mladá Boleslav", "FK Mladá Boleslav II (U14)", "FK Motorlet Praha", "FK Orenburg", "FK Pardubice", "FK Pardubice B", "FK Pardubice II (U14)", "FK Peresvet Domodedovo", "FK Pirmasens", "FK Přepeře", "FK Radnički 1923", "FK Robstav", "FK Rostov", "FK Rostov II", "FK Sakhalinets", "FK Saturn", "FK Smiltene", "FK Smorgon", "FK Sochi", "FK Strogino Moskva", "FK Teplice", "FK Teplice II (U14)", "FK Tukums 2000 II", "FK Tuzla City", "FK Třinec", "FK Ural", "FK Varnsdorf", "FK Voždovac", "FK Znamya Truda", "FK Ústí nad Labem", "FK Ústí nad Labem II (U14)", "FK Čukarički", "FK Žalgiris", "FK Železiarne Podbrezová", "FSV 08 Bietigheim-Bissingen", "FSV 63 Luckenwalde", "FSV Budissa Bautzen", "FSV Fernwald", "FSV Gütersloh 2009", "FSV Hollenbach", "FSV Motor Marienberg", "FSV Schöningen", "FSV Zwickau", "FShM Moskva", "FV 07 Diefflen", "FV Dudenhofen", "FV Engers 07", "FV Illertissen", "FV Ravensburg", "Falkenbergs FF", "Farnborough FC", "Farum BK", "Fatih Karagümrük", "Fenerbahçe", "Feralpisalò", "Feyenoord", "Fiji", "First Vienna FC", "Fleetwood Town", "Fleetwood Town U23", "Floreat Athena", "Floriana FC", "Football Talent Academy", "Football Talent Academy II (U14)", "Forest Green Rovers", "Forge FC", "Fortaleza - CE", "Fortuna Düsseldorf", "Fortuna Regensburg", "Fram Reykjavík", "Freedom FC", "Friska Viljor FC", "Frosinone Calcio", "Fulham FC", "Fulham FC U21", "Fylkir Reykjavík", "GAIS Göteborg", "GD Estoril", "GIF Sundsvall", "GV San José", "GVVV", "Gainare Tottori", "Galatasaray", "Gateshead FC", "Georgia", "Germania Halberstadt", "Germania Teveren", "Germany", "Geylang International", "Ghivizzano Borgo", "Gillingham FC", "Gimnasia de La Plata", "Glacis United FC", "Glenorchy Knights", "Gloucester City", "Go Ahead Eagles", "Gokulam Kerala", "Gold Coast United", "Gombe United", "Grasshopper Club Zürich", "Grasshopper Club Zürich II", "Green Gully SC", "Grimsby Town", "Grobiņas SC", "Grorud IL", "Grótta", "Gudja United", "Gungahlin United", "Górnik Zabrze", "Göppinger SV", "H&H Export Sébaco", "H&W Welders", "HB Køge", "HEBC Hamburg", "HJK Helsinki", "HK Kópavogur", "HK U23", "HNK O’Connor Knights", "HSC'21", "HSV Hoek", "Haka Valkeakoski", "Hamarkameratene", "Hamburger SV", "Hamburger SV II", "Hamilton Academical", "Hammarby IF", "Hamrun Spartans", "Hannover 96", "Hannover 96 II", "Hansa Rostock", "Hansa Rostock II", "Hapoel Haifa", "Harkemase Boys", "Hartford Athletic", "Hartlepool United", "Hassania US Agadir", "Havant & Waterlooville", "Havre AC", "Heeslinger SC", "Heider SV", "Hellerup IK", "Helsingfors IFK", "Hemel Hempstead Town", "Henan FC", "Heracles Almelo", "Herrera FC", "Hertha BSC", "Hertha BSC II", "Hertha Zehlendorf", "Hibernian FC", "Hills United", "Holstein Kiel", "Holstein Kiel II", "Honduras", "Hong Kong FC", "Hong Kong Rangers FC", "Hougang United", "Houston Dynamo 2", "Huddersfield Town", "Hull City", "Hull City U23", "Hume City FC", "Hungary", "Huntsville City FC", "Hvidovre IF", "Hyderabad FC", "Hà Nội FC", "Hünfelder SV", "Hảiphòng FC", "IF Brommapojkarna", "IF Elfsborg", "IF Lyseng", "IF Vestri", "IFK Stocksund", "IJsselmeervogels", "IK Junkeren", "IL Stjørdals-Blink", "Ichiritsu Funabashi High School", "Indonesia", "Inglewood United", "Inter", "Inter Club d'Escaldes", "Inter Kashi", "Inter Miami CF", "Inter Miami CF 2", "Inter Turku", "Inter Türkspor Kiel", "Inter de Querétaro", "Internacional de la Amistad", "Ipswich Town", "Ipswich Town U23", "Iraq", "JA Drancy", "JDFS Alberts", "JK Narva Trans", "JK Nõmme Kalju", "JK Tallinna Kalev", "JK Tammeka", "Jagiellonia Białystok", "Jahn Regensburg", "Jahn Regensburg II", "Japan", "Jeunesse Esch", "Jiangxi Lushan", "Johor Darul Ta’zim", "Jong Ajax", "Jong Almere City FC", "Jong PSV", "Jordan", "JäPS", "Jönköpings Södra IF", "KA Akureyri", "KAA Gent", "KAS Eupen II", "KF Dardania St. Gallen", "KPV Kokkola", "KR Reykjavík", "KRC Genk", "KRC Genk II", "KSV Baunatal", "KTP", "KV Kortrijk II", "KV Mechelen", "KV Oostende II", "KVC Westerlo", "KVC Westerlo II", "Kagoshima United", "Kalmar FF", "Kamimura Gakuen", "Kampong Utrecht", "Kapfenberger SV 1919", "Karlbergs BK", "Karlsruher SC", "Karmiotissa Polemidion", "Kashiwa Reysol", "Kasımpaşa SK", "Keflavík ÍF", "Kelty Hearts", "Kerry FC", "Khor Fakkan Club", "Kickers Emden", "Kickers Luzern", "Kickers Offenbach", "Kilia Kiel", "Kingborough Lions United", "Kitchee SC", "Knockbreda FC", "Kocaelispor", "Kolding IF", "Kolkheti Poti", "Kompozit Pavlovsky Posad", "Kongsvinger IL", "Koninklijke HFC", "Kosmos Dolgoprudny", "Kosovo", "Kozakken Boys", "Kremser SC", "Kristianstads DFF", "Kristiansund BK", "Krylia Sovetov", "Kuala Lumpur City FC", "Kuching City", "Kuopion PS", "Kuwait SC", "Kvant Obninsk", "Kvik Halden", "Kyrgyzstan", "KÍ Klaksvík", "KäPa", "Kırşehir Belediyespor", "LB Châteauroux", "LTS Bremerhaven", "La Roche VF", "Ladies FC Dornbirn", "Lake Macquarie City", "Lambton Jaffas", "Lamia", "Lamphun Warriors", "Lanús II", "Larne FC", "Las Vegas Lights FC", "Latvia", "Launceston United", "Le Mans FC", "Lee Man FC", "Leeds United U21", "Legia Warszawa", "Leicester City", "Leicester City U21", "Leiknir Reykjavík", "Leones FC", "Leones del Norte", "Levante Las Planas", "Liaoning Shenyang Urban FC", "Libertad", "Lierse Kempenzonen", "Lierse Kempenzonen II", "Lille OSC", "Lincoln Red Imps", "Linfield FC", "Linköpings FC", "Lion City Sailors", "Lions FC", "Lions Gibraltar", "Lithuania", "Liverpool FC", "Liverpool FC U21", "Lokomotiv Moskva", "Lokomotiv Plovdiv", "Lommel SK II", "Los Angeles FC", "Los Angeles FC 2", "Los Angeles Galaxy", "Los Chankas", "Loudoun United", "Loughgall FC", "Louisville City FC", "Ludwigsfelder FC", "Luis Ángel Firpo", "Lunds BK", "Luton Town", "Lyn Oslo", "Lyngby BK", "Lynx FC", "Lyon-La Duchère", "Lysekloster IL", "MFK Karviná", "MFK Karviná B", "MSV Duisburg", "MTK Budapest", "MTSV Hohenwestedt", "MTV Eintracht Celle", "MVV", "Macarthur FC", "Maccabi Petach-Tikva", "Maccabi Tel Aviv", "Madrid CFF", "Maebashi Ikuei High School", "Maitland FC", "Malaysia", "Malmö FF", "Managua FC", "Manchester 62 FC", "Manchester City", "Manchester City U21", "Manchester City WFC", "Manchester United", "Manchester United U21", "Manchester United WFC", "Manisa FK", "Manly United", "Manningham United", "Mansfield Town", "Mantova 1911 SSD", "Marconi Stallions", "Marisca Mersch", "Mazatlán FC", "Melbourne Victory", "Memphis 901", "Metalist 1925 Kharkiv", "Meteor Praha VIII", "Meteor Praha VIII II (U14)", "MetroStars FC", "Metropolitanos FC", "Mezőkövesdi SE", "Middlesbrough FC", "Middlesbrough FC U21", "Millwall FC U23", "Milton Keynes Dons", "Mineros de Zacatecas", "Minnesota United FC", "Minnesota United FC 2", "Mjällby AIF", "Mjøndalen IF", "Modbury Jets", "Mohammedan SC", "Mohun Bagan Super Giant", "Molde FK", "Moldova", "Molynes United", "Monagas", "Mons Calpe S.C.", "Montego Bay United FC", "Montenegro", "Montpellier HSC", "Morecambe FC", "Moreton City Excelsior", "Moss FK", "Motala AIF", "Motherwell FC", "Muaither SC", "Muangthong United", "Mumbai City FC", "MŠK Žilina", "NAC Breda", "NEC Nijmegen", "NEROCA FC", "NK Bravo", "NK Celje", "NK Domžale", "NK Dugopolje", "NK GOŠK Gabela", "NK Maribor", "NK Veres", "NK Vukovar 91", "NSÍ Runavík", "Naftan Novopolotsk", "Nakhon Pathom", "Namdhari FC", "Nantong Zhiyun", "Nart Cherkessk", "Nea Salamina", "Netherlands", "Neuchâtel Xamax", "Neuchâtel Xamax FCS", "New England Revolution 2", "New York City FC 2", "New York RB II", "Newcastle Olympic", "Newcastle United", "Newcastle United Jets", "Newcastle United U21", "Newington FC", "Newport County", "Newry City FC", "Newtown AFC", "Niendorfer TSV", "Nordic United FC", "Norrby IF", "North District FC", "North Macedonia", "North Texas SC", "NorthEast United FC", "Northampton Town", "Northern Ireland", "Norway", "Norwich City", "Norwich City U21", "Nottingham Forest", "Nottingham Forest U21", "Notts County", "Nykøbing FC", "Næsby BK", "Næstved BK", "Nõmme United", "NŠ Mura", "ODIN '59", "OFI Heraklion", "OSC Bremerhaven", "OSS '20", "Oakleigh Cannons", "Odds BK", "Odense BK", "Offenburger FV", "Oldenburger SV", "Oldham Athletic", "Olimpija Ljubljana", "Olympiakos Piraeus", "Olympic FC", "Olympique Lyonnais", "Olympique Marseille", "Olympique Rovenain", "Olympique Saint-Quentin", "Olympique Saumur", "Olympique de Valence", "Omonia Nikosia", "Onsala BK", "Optik Rathenow", "Orgánica Masachapa", "Orlando City", "Orlando City B", "Oskarshamns AIK", "Othellos Athienou", "Otsu High School", "Oud-Heverlee Leuven", "Oxford City", "Oxford United", "PAE Chania", "PAOK Saloniki", "PAS Giannina", "PDRM FA", "PEC Zwolle", "PFC Ludogorets Razgrad", "PS Barito Putera", "PSIS Semarang", "PSV Eindhoven", "PSV Union Neumünster", "Paksi SE", "Panama", "Panathinaikos", "Panserraikos", "Papua New Guinea", "Para Hills Knights SC", "Paris 13 Atletico", "Paris Saint-Germain", "Parma Calcio 1913", "Partick Thistle", "Partizan", "Patro Eisden MM II", "Pau FC", "Paços de Ferreira", "Pendikspor", "Peninsula Power", "Penya Encarnada", "Perak TBG", "Persib Bandung", "Persik Kediri", "Persikabo 1973", "Persis Solo (LI)", "Perth Glory", "Perth SC", "Peterborough United", "Peterborough United U23", "Peterhead FC", "Peña Deportiva", "Peñarol de Chimbas", "Pharco FC", "Philadelphia Union", "Philadelphia Union 2", "Piacenza Calcio", "Platense Zacatecoluca", "Plymouth Argyle", "Poland", "Police Tero FC", "Pomigliano CF", "Pontevedra CF", "Port FC", "Port Melbourne Sharks", "Portadown FC", "Portimonense SC", "Portland Timbers", "Portland Timbers 2", "Portsmouth FC", "Portugal", "Portuguesa FC", "Potencia", "Povltavská FA", "Prague Raptors FC", "Preston North End", "Preußen 09 Reinfeld", "Preußen Münster", "Preußen Münster II", "Progreso", "Progrès Niedercorn", "Puebla FC", "Pully Football", "Pyunik FC", "Qarabağ FK", "Qatar", "Qatar SC", "Queens Park Rangers", "Queens Park Rangers U23", "Quick Boys", "Quick Den Haag", "RB Leipzig", "RC Lens", "RC Strasbourg", "RC Épernay Champagne", "RFC Seraing", "RFC de Liège II", "RFCU Luxemburg", "RKAV Volendam", "RKVV DEM", "RMSK Nový Bydžov", "RMSK Nový Bydžov II (U14)", "RSC Anderlecht", "RSCA Futures", "RSV Eintracht 1949", "Racing Club", "Radomiak Radom", "Rajasthan United", "Randers SK Freja", "Rangers FC", "Rapid Wien (A)", "Reading FC", "Reading FC U21", "Real Casalnuovo", "Real Madrid", "Real Monarchs SLC", "Real Monterotondo Scalo", "Real Salt Lake", "Recoleta", "Red Star FC", "Reilac Shiga", "Resources Capital", "Resovia Rzeszów", "Riffa SC", "Riga FC", "Rijnsburgse Boys", "Riverside Olympic", "Rochdale AFC", "Rockdale Illinden FC", "Roda JC Kerkrade", "Rodez AF", "Rodina Moskva", "Rosenborg BK", "Rostocker FC", "Rot Weiss Ahlen", "Rot-Weiss Essen", "Rot-Weiß Koblenz", "Rot-Weiß Oberhausen", "Rot-Weiß Walldorf", "Rotenburger SV", "Rotherham United", "Royal Francs Borains", "Royal Francs Borains II", "Royal Pari", "Ruch Chorzów", "Rushall Olympic", "Russia", "Rēzeknes FA", "Rīgas Futbola skola II", "SA Mérignac", "SBV Excelsior", "SC 1960 Hanau", "SC Brühl", "SC Buochs", "SC Cambuur", "SC Cenaia", "SC Cham", "SC Dornach", "SC Eltersdorf", "SC Emmen", "SC Faetano", "SC Freiburg", "SC Freital", "SC Genemuiden", "SC Goldau", "SC Imst", "SC Kriens", "SC Lusitânia", "SC Neusiedl/See 1919", "SC Paderborn 07", "SC Paderborn 07 II", "SC Röthis", "SC Schwaz", "SC Spelle-Venhaus", "SC Staaken", "SC Trestina", "SC Vahr-Blockdiek", "SC Waldgirmes", "SC Weiz", "SC Wiener Viktoria", "SC YF/Juventus Zürich", "SCD Durango", "SD Leioa", "SF Hamborn 07", "SG 99 Andernach", "SG Aumund-Vegesack", "SG Finnentrop/Bamenohl", "SG Sonnenhof Großaspach", "SJK Akatemia", "SJK Seinäjoki", "SK Beveren II", "SK Bischofshofen", "SK Brann", "SK Brann II", "SK Deinze II", "SK Hranice", "SK Kladno", "SK Kladno II (U14)", "SK Træff", "SK Vard", "SK Zápy", "SKN St. Pölten", "SL Benfica", "SO Cholet", "SO Romorantin", "SP Tre Penne", "SPG Silz/Mötz", "SPG Union Kleinmünchen/BW Linz", "SR Delémont", "SR Donaufeld", "SS Pennarossa", "SS San Giovanni", "SSC Bari", "SSV Jeddeloh II", "SSV Reutlingen", "SSV Ulm 1846", "SSV Vorsfelde", "SSVg Velbert", "SShOR Zenit", "STK Eilvese", "SV 07 Elversberg", "SV 09 Arnstadt", "SV Auersmacher", "SV Donaustauf", "SV Drochtersen/Assel", "SV Eichede", "SV Gonsenheim", "SV Halstenbek-Rellingen", "SV Heimstetten", "SV Hemelingen", "SV Horn", "SV Höngg", "SV Lafnitz", "SV Lichtenberg 47", "SV Lippstadt 08", "SV Meerssen", "SV Meppen II", "SV Morlautern", "SV Muttenz", "SV Oberachern", "SV Oberwart", "SV Ramlingen/Ehlershausen", "SV Ried (A)", "SV Rugenbergen", "SV Sandhausen", "SV Schaffhausen", "SV Schalding-Heining", "SV Schermbeck", "SV Sonsbeck", "SV Spakenburg", "SV Steinbach", "SV Stripfing/Weiden", "SV Tasmania Berlin", "SV Todesfelde", "SV Urk", "SV Wallern", "SV Wals-Grünau", "SV Wehen Wiesbaden", "SV Weidenhausen", "SV Zulte Waregem", "SVG Reichenau", "SVV Scheveningen", "Sabah FA", "Sagan Tosu", "Saint Clément Montferrier", "SalPa", "Salford City", "Samoa", "Sampdoria", "Samsunspor", "San Diego Loyal", "San Jose Earthquakes", "San Marino", "San Marino Academy", "Sandnes Ulf", "Sanfrecce Hiroshima", "Santa Cruz", "Santos Laguna", "Sarpsborg 08", "Sassuolo Calcio", "Saudi Arabia", "Schwarz-Weiß Bregenz", "Schwarz-Weiß Rehden", "Scotland", "Seattle Sounders", "Serbia", "Servette FC", "Servette FC U21", "Servette FCCF", "Sevilla FC", "Seychelles", "SfB-Oure FA", "Shabab Al Ahli Club", "Shakhtar Donetsk", "Shanghai Port FC", "Sharjah FC", "Sheffield United", "Sheffield United U23", "Sheffield Wednesday U23", "Shillong Lajong FC", "Shizuoka Gakuen", "Shohei High School", "Shukura Kobuleti", "Sigma Olomouc", "Signal FC Bernex-Confignon", "Silkeborg IF", "Singapore", "Sint-Truidense VV", "Sirens FC", "Sitra Club", "Skála ÍF", "Slavia Karlovy Vary", "Slavia Praha", "Slavia Praha B", "Slavia Praha II (U14)", "Slough Town", "Slovan Bratislava", "Slovan Liberec", "Slovan Liberec B", "Slovan Liberec II (U14)", "Slovenia", "Sogndal IL", "Sokol Živanice", "Sol de Mayo de Viedma", "Solihull Moors", "Sony Sendai", "Sotra SK", "South Adelaide Panthers", "South Africa", "South Hobart FC", "Southampton FC", "Southampton FC U21", "Southend United", "SpVg Schonnebeck", "SpVg. Porz", "SpVgg Ansbach", "SpVgg Bayern Hof", "SpVgg Erkenschwick", "SpVgg Greuther Fürth II", "SpVgg Hankofen-Hailing", "SpVgg Quierschied", "SpVgg Vreden", "Spain", "Sparta Lichtenberg", "Sparta Nijkerk", "Sparta Rotterdam", "Sparta Rotterdam (J)", "Sparta Selemet", "Spartak Moskva", "Spartak Tambov", "Spennymoor Town", "Sportfreunde Lotte", "Sportfreunde Siegen", "Sporting Braga", "Sporting CP", "Sporting Kansas City", "Sporting Kansas City 2", "Sporting de Huelva", "Sreenidi Deccan", "St Albans Saints", "St George City FA", "St George FC", "St. Joseph's FC", "St. Louis City SC", "St. Vincent/Grenadines", "Stade Lausanne-Ouchy", "Stade Payerne", "Stade brestois 29", "Stade de Reims", "Stade-Lausanne-Ouchy", "Stal Rzeszow", "SteDoCo", "Stirling Macedonia", "Stockholm Internazionale", "Stockport County", "Stoke City U21", "Stroitel Kamensk-Shakhtinskiy", "Strømmen IF", "Strømsgodset IF II", "Sturm Graz (A)", "Sukhothai FC", "Sunderland AFC U21", "Sutton United", "Suzuka Point Getters", "Swansea City", "Swansea City U23", "Swift Hesperange", "Swindon Town", "Sydney FC Youth", "Sydney Olympic", "Sydney United 58", "SønderjyskE", "Səbail FK", "TA Rennes", "TEC VV", "TJ Jiskra Domažlice", "TJ Start Brno", "TPS Turku", "TRAU FC", "TS Woltmershausen", "TSC Bačka Topola", "TSG Backnang", "TSG Balingen", "TSG Neustrelitz", "TSG Pfeddersheim", "TSG Sprockhövel", "TSV 1860 München", "TSV 1860 München II", "TSV 1865 Dachau", "TSV 1896 Rain", "TSV Abtswind", "TSV Bordesholm", "TSV Buchholz 08", "TSV Essingen", "TSV Havelse", "TSV Kornburg", "TSV Kottern-St. Mang", "TSV Landsberg", "TSV Neudrossenfeld", "TSV Nordmark Satrup", "TSV Nördlingen", "TSV Sasel", "TSV Schott Mainz", "TSV St. Johann", "TSV Steinbach Haiger", "TVD Velbert", "Tacoma Defiance", "Tahiti", "Taiwan", "Tampines Rovers", "Tanjong Pagar United", "Tau Altopascio", "TeBe Berlin", "Team AFF-FFV Fribourg", "Team BEJUNE FA", "Team Basel Concordia", "Team FC Luzern/SC Kriens", "Team GC Limmattal/Stadt", "Team Jura", "Team Köniz", "Team Liechtenstein", "Team Oberaargau Emmental TOBE", "Team Servette/Etoile Carouge", "Team Südostschweiz", "Team Ticino", "Team Ticino Sopraceneri", "Team Ticino Sottoceneri", "Team Valais/Wallis-Sion", "Team Vaud La Côte", "Team Vaud Riviera-Chablais", "Team Vaud Yverdon Région et Broye", "Team Xamax-BEJUNE FA", "Team Zugerland", "Team Zürich-Oberland", "Team Zürich/Red-Star", "Tecnico Universitario", "Tecos Fútbol Club", "Telstar", "Tepatitlán", "Terengganu FC", "The New Saints", "Thep Xanh Nam Định FC", "Tochigi City", "Tokyo Musashino United", "Tonga", "Toronto FC", "Toronto FC 2", "Torpedo Vladimir", "Tottenham Hotspur", "Tottenham Hotspur U21", "Toulouse FC", "Toulouse FC (CFA)", "Trabzonspor", "Tranmere Rovers", "Trat FC", "Trelleborgs FF", "Tromsdalen UIL", "Trélissac FC", "TuRa Bremen", "TuRa Harksheide", "TuS Bad Gleichenberg", "TuS Bersenbrück", "TuS Bövinghausen", "TuS Dassendorf", "TuS Dietkirchen", "TuS Ennepetal", "TuS Koblenz", "TuS Komet Arsten", "TuS Königsdorf", "TuS Mechtersheim", "Tuggeranong United", "Turan Tovuz", "Turkey", "Tuzlaspor", "Twente/Heracles", "Täby FK", "Türk Gücü Friedberg", "Türkgücü München", "Türkspor Dortmund", "U.S.I. Lupo-Martini", "UD La Cruz", "UD Tomares", "UDC Txantrea", "UF Mâconnais", "UJS Toulouse", "UMF Grindavík", "UMF Njarðvík", "UMF Selfoss", "UMF Stjarnan", "UNA Strassen", "UNAN Managua", "UPC Tavagnacco", "US Colomiers", "US Fiorenzuola", "US Lesquin", "US Mondorf", "US Quevilly-Rouen", "US Souf", "US Vigor Senigallia", "USA", "USJA Carquefou", "USM Saran", "USSA Vertou", "USV Allerheiligen", "USV Eschen/Mauren", "USV Hercules", "Udinese Calcio", "Uhlenhorster SC Paloma", "Ukraine", "Ullensaker/Kisa IL", "Ullern IF", "Umeå FC", "Umm-Salal", "Union 60 Bremen", "Union Fürstenwalde", "Union Saint-Gilloise", "Union Schafhausen", "Union Titus Pétange", "Union Tornesch", "Union Vöcklamarkt", "Unitas Gorinchem", "Universidad Técnica", "Universidad de Concepción", "Universitario FC", "Unión Comercio", "Uor-5 Egorievsk", "Urania Genéve Sport", "Uthai Thani FC", "VSG Altglienicke", "VV Baronie", "VV DOVO Veenendaal", "VV Eemdijk", "VV Gemert", "VV Hoogeveen", "VV Katwijk", "VV Kloetinge", "VV OJC Rosmalen", "VV Sint Bavo", "VV Staphorst", "VVV-Venlo", "Vaasan PS", "Val Miñor Nigrán", "Valenciennes FC", "Valentine FC", "Valmiera FC II", "Valour FC", "Valur Reykjavík", "Vancouver FC", "Vancouver Whitecaps", "Vanspor FK", "Varesina Calcio", "Vatan Spor Bremen", "Vendée Les Herbiers", "Ventforet Kofu", "Veraguas United", "Veriña CF", "Vevey-Sports", "VfB Auerbach", "VfB Eichstätt", "VfB Homberg", "VfB Lübeck II", "VfB Marburg", "VfB Oldenburg", "VfB Stuttgart", "VfB Stuttgart II", "VfB Waltrop", "VfL 08 Vichttal", "VfL Bochum", "VfL Halle 96", "VfL Oldenburg", "VfL Osnabrück", "VfL Wolfsburg", "VfR Baumholder", "VfR Garching", "VfR Mannheim", "VfV Hildesheim", "Viborg FF", "Victoria Hamburg", "Viking FK", "Viktoria Clarholz", "Viktoria Griesheim", "Viktoria Köln", "Viktoria Plzeň", "Viktoria Plzeň B", "Viktoria Plzeň II (U14)", "Viktoria Žižkov", "Vilaverdense FC", "Villarreal CF", "Virtus Bolzano", "Virtus CiseranoBergamo", "Vitesse", "Vitória Setúbal", "Vojvodina", "Volos NFC", "Vysočina Jihlava", "Växjö DFF", "Vålerenga IF", "Vålerenga IF II", "Víkingur", "Víkingur Reykjavík", "WTSV Concordia", "Waldhof Mannheim", "Wales", "Walsall FC", "Warrington Town FC", "Watford FC U23", "Weiche Flensburg 08 II", "Werder Bremen", "West Bromwich Albion", "West Bromwich Albion U21", "West Ham United", "West Ham United U21", "West Ham United WFC", "Western Sydney Wanderers", "Western Sydney Wanderers Youth", "Western United", "Westfalia Rhynern", "Weston Workers FC", "Wexford FC", "Wiener Sport-Club", "Wigan Athletic U23", "Willem II", "Wisła Kraków", "Wisła Płock", "Wolfsberger AC (A)", "Wollongong Wolves", "Wolverhampton Wanderers", "Wolverhampton Wanderers U21", "Wormatia Worms", "Worthing FC", "Wrexham AFC", "Wuppertaler SV", "Wynnum Wolves FC", "Würzburger FV", "Xerez Deportivo FC", "Yeni Malatyaspor", "Yokogawa Musashino FC", "Yokohama F. Marinos", "York United", "Young Lions", "Yunnan Yukun", "Yverdon Sport FC", "Yverdon Sport FC II", "Zagłębie Lubin", "Zalaegerszegi TE", "Zenit St. Petersburg", "Zhejiang Professional", "Zlaté Moravce", "Zug 94", "Zvezda St. Petersburg", "Zvijezda 09 Bijeljina", "sc Heerenveen", "Ängelholms FF", "Åtvidabergs FF", "Ægir", "Çorum FK", "ÍA Akranes", "ÍBV Vestmannaeyjar", "ÍR Reykjavík", "Ñañas", "Örebro SK", "Örebro Syrianska IF", "Örgryte IS", "Östers IF", "Újpest FC", "Þróttur Reykjavík", "ČSK Uherský Brod", "Đông Á Thanh Hóa", "İstanbulspor AŞ", "ŁKS Łódź", "Železničar Pančevo" ];

    #csv file header
    matches.append("datetime ; competition ; match ; h2h matches ; h2h goals")
    for k in range(0, 15):
        print(datetime.now())
        current_date = today + timedelta(days=k)
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
        year = "2024"
        month = "12"
        response = requests.get("https://www.over25tips.com/soccer-predictions/?date=" + year + "-" + month + "-" + str("%02d" % day))
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
                        statsUrl = (row.find('td', class_="COL-4").find('a')['href'])
                        nextDay = day+1
                        ftResult = getFTFromO25Tips(statsUrl, str("%02d" % day) + "." + month + "." + year, str("%02d" % nextDay) + "." + month + "." + year)
                        gfg = [('1. datetime', str(day) + "-" + month + "-" + year), ('2. competition', competition), ('3. match', str(homeTeam + " Vs " + awayTeam)), ('4. ftResult', ftResult)]
                        json_data = OrderedDict(gfg)
                        matches.append(json_data)

            response2 = requests.get("https://www.over25tips.com/soccer-predictions/?date=" + year + "-" + month + "-" + str("%02d" % day) +"&page=2")
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
                            statsUrl = (row.find('td', class_="COL-4").find('a')['href'])
                            nextDay = day+1
                            ftResult = getFTFromO25Tips(statsUrl, str("%02d" % day) + "." + month + "." + year, str("%02d" % nextDay) + "." + month + "." + year)
                            gfg = [('1. datetime', str(day) + "-" + month + "-" + year), ('2. competition', competition), ('3. match', str(homeTeam + " Vs " + awayTeam)), ('4. ftResult', ftResult)]
                            gfg = [('1. datetime', str(day) + "-" + month + "-" + year), ('2. competition', competition), ('3. match', str(homeTeam + " Vs " + awayTeam))]
                            json_data = OrderedDict(gfg)
                            matches.append(json_data)
        else:
            raise Exception(f'Failed to scrape data from {url}. Error: {response.status_code}')
        #break
    return matches


def getFTFromO25Tips(statsUrl, date1, date2):
    response = requests.get("https://www.over25tips.com/" + statsUrl)
    if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Perform scraping operations using BeautifulSoup here
            table = soup.find('table', class_="table-bordered")
            if table is not None:
                for i, row in enumerate(table.find_all('tr')):
                    if len(row.find_all('td', class_="tac")) > 0:
                        realDate = row.find_all('td', class_="tac")[1].text.strip()
                        if realDate == date1 or realDate == date2:
                            return (row.find_all('td', class_="tac")[0].text.strip()).replace(' ', '')


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
    #formatted_tomorrow = tomorrow.strftime("%Y/%b/%d/").lower()
    
    matches = []
    #code to get all matches for all months of a year
    for year in [season]:
        #for m in [ "jan", "feb", "mar", "apr", "may", "jun"]:
        #for m in [ "jul", "aug", "sep", "oct", "nov", "dec"]:
        #for m in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec" ]:
        for m in ["jan"]:
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
                    competition = re.sub(r'(\d{4}(?:/\d{4})?)\s.*$', r'\1', r[1])
            if (len(r) > 15) and (flag is True) and bool(re.search(r'\b\d+:\d+\b', r[13])):# and '(' in r[13]:
                if allLeagues is False and r[1] != 'Round':
                    continue
                ftResult = ''
                htResult = ''
                if ('pso' in r[13] or 'aet' in r[13] or 'dec' in r[13]) and ',' in r[13]:
                    ftResult = r[13].split(',')[1].split(')')[0].strip()
                    htResult = r[13].split(',')[0].split('(')[1].strip().replace(',','')
                elif 'n.P.' in r[13]:
                    ftResult = r[13].split(',')[1].strip()
                    htResult = r[13].split(',')[0].split('(')[1].strip().replace(',','')
                else:
                    ftResult = r[13].split(' ')[0]
                    if (len(r[13].split(' ')) > 1):
                        htResult = r[13].split(' ')[1].replace('(','').replace(')','').replace(',','')
                print(ftResult)
                if ':' in ftResult:
                    if r[7] == 'H':
                        matches.append(Match(r[3], team, r[11], ftResult, htResult, competition).to_dict())
                    else:
                        ftResult = ftResult.split(':')[1] + ':' + ftResult.split(':')[0]
                        if ':' in htResult:
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
        tables = soup.find_all('table', class_="standard_tabelle")
    
        # then we can iterate through each row and extract either header or row values:
        header = []
        rows = []
        for j in range(1, len(tables)-1):
            table = tables[j]
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