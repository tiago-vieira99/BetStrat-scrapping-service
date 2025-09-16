from flask import Flask, jsonify, request
import scrapping
import bttsOneHalf
import aDaScrappings
import difflib
import json
import time
from collections import OrderedDict
import sys, os
import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import time
import logging
import threading

def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
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

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/last-matches/<int:n>', methods=['POST'])
def get_last_n_matches(n):
    data = request.get_json()
    thread = threading.Thread(target=scrape_last_n_matches, args=(data,n))
    thread.start()
    return jsonify({"status": "started"}), 202


def scrape_last_n_matches(data, n):
    allLeagues = True #used only for historic-data, so always true

    for key, value in data.items():
        lastMatchesList = {}
        driver = webdriver.Remote("http://selenium:4444", options=webdriver.ChromeOptions(), keep_alive=True)
        driver.maximize_window()
        #time.sleep(1)
        source_code = scrapping.getWFSourceHtmlCode(value['url'], driver)
        driver.quit() #very important
        try:
            lastMatches = scrapping.getLastNMatchesFromWF(value['url'], n, key, allLeagues, value['season'], source_code)
            lastMatchesList[key] = {}
            lastMatchesList[key]['lastMatches'] = lastMatches
            bttsOneHalf.publish_match(lastMatchesList, "historic_last_matches")
        except Exception as e:
            logging.error("ERROR getting last matches for " + key)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, fname, exc_tb.tb_lineno)
            continue

    return "done."

@app.route('/last-match', methods=['POST'])
def get_last_margin_wins_matches():
    allLeagues = True #used only for historic-data, so always true
    lastMatchesList = {}
    data = request.get_json()

    for key, value in data.items():
        driver = webdriver.Remote("http://selenium:4444", options=webdriver.ChromeOptions(), keep_alive=True)
        driver.maximize_window()
        #time.sleep(1)
        source_code = scrapping.getWFSourceHtmlCode(value['url'], driver)
        driver.quit() #very important
        try:
            lastMatches = scrapping.getLastNMatchesFromWF(value['url'], 1, key, allLeagues, value['season'], source_code)
            lastMatchesList[key] = {}
            lastMatchesList[key]['lastMatches'] = lastMatches
            bttsOneHalf.publish_match(lastMatchesList, "margin_wins_last_matches")
        except Exception as e:
            logging.error("ERROR getting last matches for " + key)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, fname, exc_tb.tb_lineno)
            continue

    return jsonify(lastMatchesList)

@app.route('/next-matches', methods=['POST'])
def get_next_match():
    allLeagues = False
    if request.args.get("allleagues") == 'true':
        allLeagues = True

    nextMatchesList = {}
    data = request.get_json()

    for key, value in data.items():
        driver = webdriver.Remote("http://selenium:4444", options=webdriver.ChromeOptions(), keep_alive=True)
        driver.maximize_window()
        source_code = scrapping.getWFSourceHtmlCode(value['url'], driver)
        driver.quit() #very important
        try:
            nextMatches = scrapping.getNextMatchFromWF(value['url'], key, value['season'], allLeagues, source_code)
            nextMatchesList[key] = {}
            nextMatchesList[key]['nextMatches'] = nextMatches
        except Exception as e:
            logging.error("ERROR getting next match for " + key)
            continue

    
    return jsonify(nextMatchesList)


@app.route('/league-teams', methods=['POST'])
def get_all_league_teams():
    try:
        driver = webdriver.Remote("http://selenium:4444", options=webdriver.ChromeOptions(), keep_alive=True)
        driver.maximize_window()
        
        if "worldfootball" in request.data.decode("utf-8"):
            return jsonify(scrapping.getLeagueTeamsFromWF(request.data, driver))
        else:
            return 'url not supported'
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        driver.quit() #very important


@app.route('/kelly-strats/next-matches-links', methods=['GET'])
def over25_get_next_matches_links():
    today = datetime.date.today()

    # Calculate tomorrow and the day after tomorrow
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = today + datetime.timedelta(days=2)

    # Format the dates as mm/dd
    tomorrow_formatted = tomorrow.strftime("%d")
    day_after_tomorrow_formatted = day_after_tomorrow.strftime("%d")
    tomorrow_month = tomorrow.strftime("%m")
    after_tomorrow_month = day_after_tomorrow.strftime("%m")

    tomorrow_link = "https://www.academiadasapostas.com/stats/livescores/2025/" + tomorrow_month + "/" + tomorrow_formatted
    after_tomorrow_link = "https://www.academiadasapostas.com/stats/livescores/2025/" + after_tomorrow_month + "/" + day_after_tomorrow_formatted
    adaLinks = []
    adaLinks.append(tomorrow_link)
    adaLinks.append(after_tomorrow_link)
    #adaLinks.append("https://www.academiadasapostas.com/stats/livescores/2025/09/04")
    #adaLinks.append("https://www.academiadasapostas.com/stats/livescores/2025/08/17")
    matchesLinks = []

    for link in adaLinks:
        logging.info("getting matches links for: " + link)
        matchesLinks += aDaScrappings.getAdaMatchesLinks(link);#aDaScrappings.getAdaMatchesLinks("https://www.academiadasapostas.com/stats/livescores/2025/06/" + str("%02d" % d))#
            
    return matchesLinks


@app.route('/kelly-strats/matches-results-over25', methods=['POST'])
def kelly_over25_matches_results():
    data = request.get_json()
    thread = threading.Thread(target=scrapeMatchesResultsInBackground, args=(data, "over25-results"))
    thread.start()
    return jsonify({"status": "started"}), 202


@app.route('/kelly-strats/matches-results-btts-one-half', methods=['POST'])
def kelly_btts_one_half_matches_results():
    data = request.get_json()
    thread = threading.Thread(target=scrapeMatchesResultsInBackground, args=(data, "btts-one-half-results"))
    thread.start()
    return jsonify({"status": "started"}), 202


def scrapeMatchesResultsInBackground(data, strategy):
    print(data)
    try:
        for element in data:
            try:
                match = aDaScrappings.getMatchFinalResultFromAdA(element)
                logging.info(match)
                bttsOneHalf.publish_match(match, strategy)
                time.sleep(2)
            except Exception as e:
                logging.info(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.info(exc_type, fname, exc_tb.tb_lineno)
                continue
    except Exception as e:
        logging.info(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.info(exc_type, fname, exc_tb.tb_lineno)
        return ({'error': str(e)})


@app.route('/kelly-strats/next-matches', methods=['POST'])
def over25_get_next_matches():
    data = request.get_json()
    thread = threading.Thread(target=scrapeMatchesInBackground, args=(data,))
    thread.start()
    return jsonify({"status": "started"}), 202


def scrapeMatchesInBackground(data):
    try:
        matchesToBet = {}
        over25Matches = []
        bttsOneHalfMatches = []
        for element in data:
            try:
                match = aDaScrappings.getAdaMatchesStats(element)
                if filter_criteria_over25_match(match[0]):
                    logging.info(match[0])
                    over25Matches.append(match[0])
                    bttsOneHalf.publish_match(match[0], "Over25")
                if filter_criteria_btts_match(match[0]):
                    logging.info(match[0])
                    bttsOneHalfMatches.append(match[0])
                    bttsOneHalf.publish_match(match[0], "BTTSOneHalf")
                time.sleep(2)
            except Exception as e:
                logging.info(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.info(exc_type, fname, exc_tb.tb_lineno)
                continue
        matchesToBet['over25'] = over25Matches
        matchesToBet['bttsOneHalf'] = bttsOneHalfMatches
        print(len(over25Matches))
        print(len(bttsOneHalfMatches))
        return matchesToBet
    except Exception as e:
        logging.info(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.info(exc_type, fname, exc_tb.tb_lineno)
        return ({'error': str(e)})

def filter_criteria_over25_match(match):
    last_home_team_matches = match['last_home_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
    last_away_team_matches = match['last_away_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
    home_total_goals_avg_at_home_pre = float(match['home_total_goals_avg_at_home_pre'])
    away_total_goals_avg_at_away_pre = float(match['away_total_goals_avg_at_away_pre'])
    
    last_home_data = json.loads(last_home_team_matches)  # Parse the JSON string
    last_away_data = json.loads(last_away_team_matches)  # Parse the JSON string

    #filtered_comps = ["República da Irlanda - FAI Cup", "Catar - Play-offs 1/2", "Canadá - Canadian Championship", "Croácia - Cup", "África do Sul - Cup", "Ucrânia - Persha Liga", "Estónia - Super Cup", "Albânia - Cup", "Arménia - Cup", "Emirados Árabes Unidos - League Cup", "Catar - QSL Cup", "Estados Unidos da América - US Open Cup", "África - CAF Champions League", "Portugal - Taça da Liga", "Turquia - Cup", "Bielorrússia - Cup", "Japão - Emperor Cup", "Malta - FA Trophy", "Itália - Coppa Italia", "Índia - I-League", "Rússia - Cup", "Islândia - 1. Deild", "Suíça - Schweizer Pokal", "Israel - State Cup", "Escócia - FA Cup", "Argentina - Primera División", "Portugal - Taça de Portugal", "Hungria - Magyar Kupa", "Rússia - FNL", "Singapura - Premier League", "França - Coupe de France", "Israel - Toto Cup Ligat Al", "Islândia - Cup", "Bósnia-Herzegovina - Cup", "Irlanda do Norte - Taça da Liga", "República da Coreia - FA Cup", "Suíça - Challenge League", "Europa - UEFA Champions League", "Eslováquia - 2. liga", "Países Baixos - KNVB Beker", "Perú - Segunda División", "Austrália - A-League", "Eslováquia - Cup", "Áustria - Cup", "Cazaquistão - Premier League", "Bélgica - First Division B", "Ásia - AFC Champions League", "Polónia - Cup", "Noruega - NM Cupen", "Países Baixos - Eerste Divisie", "Bélgica - Cup", "Malásia - Super League", "Arménia - Premier League", "Chile - Copa Chile", "Inglaterra - FA Cup", "Espanha - Copa del Rey", "Estónia - Cup", "Eslovénia - Cup", "Albânia - Superliga", "Finlândia - Ykkönen", "Islândia - Úrvalsdeild", "Inglaterra - Premier League", "Europa - UEFA Europa League", "Áustria - 1. Liga", "Itália - Serie A", "República Checa - Czech Liga", "RP China - CSL", "Gales - Premier League", "Portugal - Liga Portugal Betclic", "Suécia - Svenska Cupen", "Alemanha - Bundesliga", "América do Sul - CONMEBOL Libertadores", "Polónia - I Liga", "Escócia - Taça da Liga", "Brasil - Serie A", "Alemanha - Regionalliga", "Bélgica - Pro League", "Luxemburgo - National Division", "Finlândia - Veikkausliiga", "Lituânia - A Lyga", "Irlanda do Norte - Premiership", "Croácia - 1. HNL", "Noruega - 1. Division", "Catar - Stars League", "Alemanha - DFB Pokal", "Roménia - Cupa României", "Noruega - Eliteserien", "Japão - J1 League", "Chile - Primera División", "Alemanha - 2. Bundesliga", "Inglaterra - League Two", "Estados Unidos da América - MLS", "México - Liga MX", "Inglaterra - League One"]
    filtered_comps = ["Alemanha - Bundesliga", "Argentina - Primera División", "Argentina - Primera Nacional", "Arménia - Premier League", "Ásia - AFC Champions League", "Austrália - A-League", "Áustria - 1. Liga", "Áustria - Cup", "Bélgica - Cup", "Bélgica - First Division B", "Brasil - Serie A", "Catar - QSL Cup", "Cazaquistão - Premier League", "Chile - Copa Chile", "Chile - Primera División", "Croácia - 1. HNL", "Equador - Primera B", "Escócia - FA Cup", "Eslováquia - 2. liga", "Eslováquia - Cup", "Estónia - Cup", "Europa - UEFA Champions League", "Europa - UEFA Europa League", "Finlândia - Veikkausliiga", "Finlândia - Ykkönen", "França - Coupe de France", "Gales - Premier League", "Húngria - Magyar Kupa", "Índia - I-League", "Inglaterra - FA Cup", "Inglaterra - Premier League", "Islândia - 1. Deild", "Islândia - Cup", "Islândia - Úrvalsdeild", "Israel - State Cup", "Israel - Toto Cup Ligat Al", "Itália - Coppa Italia", "Itália - Serie A", "Itália - Serie B", "Japão - Emperor Cup", "Japão - J1 League", "Lituânia - A Lyga", "Malásia - Super League", "Noruega - Eliteserien", "Noruega - NM Cupen", "Países Baixos - Eerste Divisie", "Países Baixos - KNVB Beker", "Perú - Segunda División", "Polónia - Cup", "Polónia - I Liga", "Portugal - Liga Portugal Betclic", "Portugal - Taça da Liga", "Portugal - Taça de Portugal", "República Checa - Czech Liga", "República da Irlanda - FAI Cup", "RP China - CSL", "Rússia - Cup", "Rússia - FNL", "Suíça - Challenge League", "Suíça - Schweizer Pokal", "Turquia - Cup"]

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


    if home_team_eligle and away_team_eligle and str(match['competition']) in filtered_comps:
        logging.info(str(match['home_team']) + ' - '  + str(match['away_team']))
        # logging.info('total_goals_last_home_team_matches' + str(total_goals_last_home_team_matches))
        # logging.info('last_home_team_matches_overs' + str(last_home_team_matches_overs))
        # logging.info('total_goals_last_away_team_matches' + str(total_goals_last_away_team_matches))
        # logging.info('last_away_team_matches_overs' + str(last_away_team_matches_overs))
        # logging.info('total_goals_previous_away_team_match' + str(total_goals_previous_away_team_match))
        # logging.info('last_away_team_matches_scored' + str(last_away_team_matches_scored))
        return True
    return False


@app.route('/database/insert-new-matches', methods=['POST'])
def btts_get_next_matches():
    try:
        matchesToBet = []
        for d in range(1,32):
            matchesLinks = aDaScrappings.getAdaMatchesLinks("https://www.academiadasapostas.com/stats/livescores/2025/08/" + str("%02d" % d))
            for element in matchesLinks:
                try:
                    match = aDaScrappings.getAdaMatchesStats(element)
                    if len(match) > 0:
                        aDaScrappings.insertMatchInDB(match[0])
                    # if filter_criteria_btts_match(match[0]):
                    #     logging.info(match[0])
                    #     matchesToBet.append(match[0])
                except Exception as e:
                    logging.info(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    logging.info(exc_type, fname, exc_tb.tb_lineno)
                    continue
        return matchesToBet
    except Exception as e:
        logging.info(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.info(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({'error': str(e)})

def filter_criteria_btts_match(match):
    h2h_matches_json = match['h2h_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
    last_home_team_matches = match['last_home_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
    last_away_team_matches = match['last_away_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
    home_total_goals_avg_at_home_pre = float(match['home_total_goals_avg_at_home_pre'])
    away_total_goals_avg_at_away_pre = float(match['away_total_goals_avg_at_away_pre'])
    if h2h_matches_json:  # Check if the JSON string is not empty/None
        h2h_data = json.loads(h2h_matches_json)  # Parse the JSON string
        last_home_data = json.loads(last_home_team_matches)  # Parse the JSON string
        last_away_data = json.loads(last_away_team_matches)  # Parse the JSON string

        bttsLastStreak = bttsOneHalf.filterMatchesByBttsCondition(h2h_data)
        btts_streak_length = int(bttsLastStreak.split('/')[1])
        btts_streak_value = int(bttsLastStreak.split('/')[0])

        overLastStreak = bttsOneHalf.filterMatchesByOverCondition(h2h_data)
        over_streak_length = int(overLastStreak.split('/')[1])
        over_streak_value = int(overLastStreak.split('/')[0])

        home_bttsLastStreak = bttsOneHalf.filterMatchesByBttsCondition(last_home_data)
        home_btts_streak_length = int(home_bttsLastStreak.split('/')[1])
        home_btts_streak_value = int(home_bttsLastStreak.split('/')[0])

        home_overLastStreak = bttsOneHalf.filterMatchesByOverCondition(last_home_data)
        home_over_streak_length = int(home_overLastStreak.split('/')[1])
        home_over_streak_value = int(home_overLastStreak.split('/')[0])

        away_bttsLastStreak = bttsOneHalf.filterMatchesByBttsCondition(last_away_data)
        away_btts_streak_length = int(away_bttsLastStreak.split('/')[1])
        away_btts_streak_value = int(away_bttsLastStreak.split('/')[0])

        away_overLastStreak = bttsOneHalf.filterMatchesByOverCondition(last_away_data)
        away_over_streak_length = int(away_overLastStreak.split('/')[1])
        away_over_streak_value = int(away_overLastStreak.split('/')[0])

        teams_goals_avg = float((home_total_goals_avg_at_home_pre + away_total_goals_avg_at_away_pre) / 2)

        if teams_goals_avg >= 3.5 and (btts_streak_length >= 5 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 5 and float(over_streak_value/over_streak_length) >= 0.75) and ( (home_btts_streak_length >= 5 and float(home_btts_streak_value/home_btts_streak_length) >= 0.75) and (home_over_streak_length >= 5 and float(home_over_streak_value/home_over_streak_length) >= 0.75) or (away_btts_streak_length >= 5 and float(away_btts_streak_value/away_btts_streak_length) >= 0.75) and (away_over_streak_length >= 5 and float(away_over_streak_value/away_over_streak_length) >= 0.75) ):
            return True
    return False
            

@app.route('/btts-one-half/matches-from-database', methods=['GET'])
def btts_get_matches_from_database():
    return_list = []
    results = []
    for j in range(7, 8):
        try:
            for i in range(1, 32):
                date = "2025-" + str("%02d" % j) + "-" + str("%02d" % i)
                results += (bttsOneHalf.getBTTSMatchesByDateFromDB(date))

            # num_greens_over25 = 0
            # num_greens_btts1h = 0
            # for m in results:
            #     if ((int(m['05. ft_result'].split('-')[0]) + int(m['05. ft_result'].split('-')[1])) > 2):
            #         num_greens_over25 += 1
            #     if len(m['06. ht_result']) > 0 and bttsOneHalf.evalute_btts_one_half_result(m):
            #         num_greens_btts1h += 1

            # simulation = {}
            # #simulation['matches'] = results
            # simulation['month'] = j
            # simulation['num_greens_over25'] = num_greens_over25
            # simulation['num_greens_btts1h'] = num_greens_btts1h
            # simulation['num_bets'] = len(results)
            # if len(results) > 0:
            #     simulation['success_o25'] = float(num_greens_over25/len(results))
            #     simulation['success_btts1h'] = float(num_greens_btts1h/len(results))
            # return_list.append(simulation)

        except Exception as e:
            logging.info(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, fname, exc_tb.tb_lineno)
            continue

    return results


@app.route('/over-25/matches-from-database', methods=['GET'])
def over25_get_matches_from_database():
    return_list = []
    results = []
    for j in range(8, 9):
        try:
            for i in range(1, 32):
                date = "2025-" + str("%02d" % j) + "-" + str("%02d" % i)
                results += (bttsOneHalf.getOVERMatchesByDateFromDB(date))

            # num_greens_over25 = 0
            # num_greens_btts1h = 0
            # for m in results:
            #     if ((int(m['05. ft_result'].split('-')[0]) + int(m['05. ft_result'].split('-')[1])) > 2):
            #         num_greens_over25 += 1
            #     if len(m['06. ht_result']) > 0 and bttsOneHalf.evalute_btts_one_half_result(m):
            #         num_greens_btts1h += 1

            # simulation = {}
            # #simulation['matches'] = results
            # simulation['month'] = j
            # simulation['num_greens_over25'] = num_greens_over25
            # simulation['num_greens_btts1h'] = num_greens_btts1h
            # simulation['num_bets'] = len(results)
            # if len(results) > 0:
            #     simulation['success_o25'] = float(num_greens_over25/len(results))
            #     simulation['success_btts1h'] = float(num_greens_btts1h/len(results))
            # return_list.append(simulation)

        except Exception as e:
            logging.info(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, fname, exc_tb.tb_lineno)
            continue

    return results



if __name__ == '__main__':
    logging.info("scrapper service is running...")
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)
