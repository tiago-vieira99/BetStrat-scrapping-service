from flask import Flask, jsonify, request
import scrapping
import seleniumScrapping
import experiments
import goalsFest
import bttsOneHalf
import footystats
import aDaScrappings
import nbaBacktests
import telegramScraps
import sofascore as ss
import difflib
import json
import test
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
    allLeagues = True #used only for historic-data, so always true
    lastMatchesList = {}
    data = request.get_json()

    driver = webdriver.Remote("http://selenium:4444", options=webdriver.ChromeOptions(), keep_alive=True)
    driver.maximize_window()

    logging.info(data)

    for key, value in data.items():
        source_code = scrapping.getWFSourceHtmlCode(value['url'], driver)
        try:
            lastMatches = scrapping.getLastNMatchesFromWF(value['url'], n, key, allLeagues, value['season'], source_code)
            lastMatchesList[key] = {}
            lastMatchesList[key]['lastMatches'] = lastMatches
        except Exception as e:
            logging.error("ERROR getting last matches for " + key)
            continue

    driver.quit() #very important
    return jsonify(lastMatchesList)

@app.route('/next-matches', methods=['POST'])
def get_next_match():
    allLeagues = False
    if request.args.get("allleagues") == 'true':
        allLeagues = True

    nextMatchesList = {}
    data = request.get_json()

    driver = webdriver.Remote("http://selenium:4444", options=webdriver.ChromeOptions(), keep_alive=True)
    driver.maximize_window()

    for key, value in data.items():
        source_code = scrapping.getWFSourceHtmlCode(value['url'], driver)
        try:
            nextMatches = scrapping.getNextMatchFromWF(value['url'], key, value['season'], allLeagues, source_code)
            nextMatchesList[key] = {}
            nextMatchesList[key]['nextMatches'] = nextMatches
        except Exception as e:
            logging.error("ERROR getting next match for " + key)
            continue

    driver.quit() #very important
    return jsonify(nextMatchesList)

@app.route('/next-league-match', methods=['POST'])
def get_next_league_match():
    try:
        return jsonify(seleniumScrapping.getLeagueNextMatchFromAdA(request.data))
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/football-stats/all-season-matches', methods=['POST'])
def get_all_season_matches():
    try:
        allLeagues = False
        if request.args.get("allleagues") == 'true':
            allLeagues = True

        if "worldfootball" in request.data.decode("utf-8"):
            return jsonify(scrapping.getSeasonMatchesFromWF(request.data, request.args.get("team"), request.args.get("season"), allLeagues))
        elif "fbref" in request.data.decode("utf-8"):
            return jsonify(scrapping.getSeasonMatchesFromFBRef(request.data, request.args.get("team"), allLeagues))
        elif "zerozero" in request.data.decode("utf-8"):
            return jsonify(scrapping.getSeasonMatchesFromZZ(request.data, request.args.get("team"), allLeagues))
        elif "espn" in request.data.decode("utf-8"):
            return jsonify(scrapping.getNBASeasonMatchesFromESPN(request.data, request.args.get("team")))
        else:
            return 'url not supported'
    except Exception as e:
        return jsonify({'error': str(e)})


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


@app.route('/lmp-prognosticos', methods=['GET'])
def get_lmp_prognosticos():
    try:
        return jsonify(scrapping.getLMPprgnosticos())
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/live-matches', methods=['GET'])
def get_live_matches():
    try:
        return jsonify(seleniumScrapping.getLiveResultsFromAdA())
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/first-half-goal-candidates', methods=['GET'])
def get_first_half_goal_candidates():
    try:
        return jsonify(experiments.scrappAdAStatsBulk('1'))
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/over25-candidates', methods=['GET'])
def get_over25_candidates():
    try:
        for i in range(1,2):
            data = (experiments.scrappAdAStatsBulk(str(i)))
            f = open(str(i) + "-data.json", "x")
            f.write(json.dumps(data, indent=4))
            f.close()
        return "ok"
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/friendly-matches', methods=['POST'])
def friendly_matches():
    try:
        data = request.get_json()
        for element in data:
            #logging.info(element['3. match'])
            element['4. ft_result'] = test.get_goals_mins(element)
            #break
            # time.sleep(2)
            # #logging.info(str(len(mins))+ " !! " + str(int(element['total goals'][0])))
            # #if len(mins) == int(element['total goals'][0]):
            # element['4. goals_mins'] = ''.join(mins)
            # if len(mins) > 1 and int(mins[1].replace("'","").strip()) <= 60:
            #     element['5. <60m'] = "GREEN"
            # if len(mins) > 1:
            #     element['6. +1.5'] = True
            # if len(mins) > 2:
            #     element['7. +2.5'] = True
        return data
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/simulate/wins-margin-v2', methods=['POST'])
def sofascore():
    try:
        result = []
        initial_target = 2
        data = request.get_json()
        #return test.simulate_sequence_w_recovery(list(map(int, data['sequence'].replace(" ","").split(","))), float(data['odd'].replace(",", ".")) * 0.9, initial_target)
        for element in data:
            sequence = element['negative sequence']
            odd = element['odd']
            result.append({
                    "Equipa": element['Equipa'],
                    "score": element['score'],
                    "sequence": element['negative sequence'],
                    "balance": test.ternary_progression(list(map(int, sequence.replace(" ","").split(","))), float(odd.replace(",", ".")) * 0.95, initial_target)
                })

        return result
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/simulate/ternary', methods=['POST'])
def ternary():
    try:
        result = []
        initial_target = 2
        data = request.get_json()
        return test.ternary_progression(list(map(int, data['sequence'].replace(" ","").split(","))), float(data['odd'].replace(",", ".")) * 0.95, initial_target)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/o25tips', methods=['GET'])
def o25tips():
    try:
        return scrapping.getTipsFromO25Tips()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/btts-candidates', methods=['GET'])
def get_btts_candidates():
    try:
        return jsonify(experiments.scrappBTTSAdAStatsBulk())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/tomorrow-matches', methods=['GET'])
def get_tomorrow_matches():
    try:
        data = request.get_json()
        return jsonify(scrapping.getTomorrowMatchesFromWF(data['season']))
        #return test.testTeamsCount()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/goals-fest/filtered-teams', methods=['GET'])
def gf_get_filtered_teams():
    try:
        data = request.get_json()
        return goalsFest.filterTeamsBySeason(data['season'])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/goals-fest/matches-between-teams', methods=['GET'])
def gf_get_matches_between_teams():
    try:
        data = request.get_json()
        return goalsFest.getMatchesBetweenFilteredTeams(data['previousSeason'], data['season'])
    except Exception as e:
        logging.info(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.info(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({'error': str(e)})

@app.route('/btts-one-half/matches-between-teams', methods=['GET'])
def btts_get_matches_between_teams():
    try:
        data = request.get_json()
        return bttsOneHalf.getMatchesBetweenFilteredTeams(data['previousSeason'], data['season'])
    except Exception as e:
        logging.info(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.info(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({'error': str(e)})

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
    matchesLinks = []

    for link in adaLinks:
        logging.info("getting matches links for: " + link)
        matchesLinks += aDaScrappings.getAdaMatchesLinks(link);#aDaScrappings.getAdaMatchesLinks("https://www.academiadasapostas.com/stats/livescores/2025/06/" + str("%02d" % d))#
            
    return matchesLinks


@app.route('/kelly-strats/next-matches', methods=['POST'])
def over25_get_next_matches():
    data = request.get_json()
    try:
        matchesToBet = {}
        over25Matches = []
        bttsOneHalfMatches = []
        for element in data:
            try:
                match = aDaScrappings.getAdaMatchesStats(element)
                # if len(match) > 0:
                #     aDaScrappings.insertMatchInDB(match[0])
                if filter_criteria_over25_match(match[0]):
                    logging.info(match[0])
                    over25Matches.append(match[0])
                if filter_criteria_btts_match(match[0]):
                    logging.info(match[0])
                    bttsOneHalfMatches.append(match[0])
                time.sleep(2)
            except Exception as e:
                logging.info(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.info(exc_type, fname, exc_tb.tb_lineno)
                continue
        matchesToBet['over25'] = over25Matches
        matchesToBet['bttsOneHalf'] = bttsOneHalfMatches
        return matchesToBet
    except Exception as e:
        logging.info(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.info(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({'error': str(e)})

def filter_criteria_over25_match(match):
    last_home_team_matches = match['last_home_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
    last_away_team_matches = match['last_away_team_matches'].replace("', '", "\", \"").replace("', ", "\", ").replace(", '", ", \"").replace("']", "\"]").replace("['", "[\"")
    home_total_goals_avg_at_home_pre = float(match['home_total_goals_avg_at_home_pre'])
    away_total_goals_avg_at_away_pre = float(match['away_total_goals_avg_at_away_pre'])
    
    last_home_data = json.loads(last_home_team_matches)  # Parse the JSON string
    last_away_data = json.loads(last_away_team_matches)  # Parse the JSON string

    filtered_comps = ["República da Irlanda - FAI Cup", "Catar - Play-offs 1/2", "Canadá - Canadian Championship", "Croácia - Cup", "África do Sul - Cup", "Ucrânia - Persha Liga", "Estónia - Super Cup", "Albânia - Cup", "Arménia - Cup", "Emirados Árabes Unidos - League Cup", "Catar - QSL Cup", "Estados Unidos da América - US Open Cup", "África - CAF Champions League", "Portugal - Taça da Liga", "Turquia - Cup", "Bielorrússia - Cup", "Japão - Emperor Cup", "Malta - FA Trophy", "Itália - Coppa Italia", "Índia - I-League", "Rússia - Cup", "Islândia - 1. Deild", "Suíça - Schweizer Pokal", "Israel - State Cup", "Escócia - FA Cup", "Argentina - Primera División", "Portugal - Taça de Portugal", "Hungria - Magyar Kupa", "Rússia - FNL", "Singapura - Premier League", "França - Coupe de France", "Israel - Toto Cup Ligat Al", "Islândia - Cup", "Bósnia-Herzegovina - Cup", "Irlanda do Norte - Taça da Liga", "República da Coreia - FA Cup", "Suíça - Challenge League", "Europa - UEFA Champions League", "Eslováquia - 2. liga", "Países Baixos - KNVB Beker", "Perú - Segunda División", "Austrália - A-League", "Eslováquia - Cup", "Áustria - Cup", "Cazaquistão - Premier League", "Bélgica - First Division B", "Ásia - AFC Champions League", "Polónia - Cup", "Noruega - NM Cupen", "Países Baixos - Eerste Divisie", "Bélgica - Cup", "Malásia - Super League", "Arménia - Premier League", "Chile - Copa Chile", "Inglaterra - FA Cup", "Espanha - Copa del Rey", "Estónia - Cup", "Eslovénia - Cup", "Albânia - Superliga", "Finlândia - Ykkönen", "Islândia - Úrvalsdeild", "Inglaterra - Premier League", "Europa - UEFA Europa League", "Áustria - 1. Liga", "Itália - Serie A", "República Checa - Czech Liga", "RP China - CSL", "Gales - Premier League", "Portugal - Liga Portugal Betclic", "Suécia - Svenska Cupen", "Alemanha - Bundesliga", "América do Sul - CONMEBOL Libertadores", "Polónia - I Liga", "Escócia - Taça da Liga", "Brasil - Serie A", "Alemanha - Regionalliga", "Bélgica - Pro League", "Luxemburgo - National Division", "Finlândia - Veikkausliiga", "Lituânia - A Lyga", "Irlanda do Norte - Premiership", "Croácia - 1. HNL", "Noruega - 1. Division", "Catar - Stars League", "Alemanha - DFB Pokal", "Roménia - Cupa României", "Noruega - Eliteserien", "Japão - J1 League", "Chile - Primera División", "Alemanha - 2. Bundesliga", "Inglaterra - League Two", "Estados Unidos da América - MLS", "México - Liga MX", "Inglaterra - League One"]

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

@app.route('/database/insert-new-matches', methods=['GET'])
def btts_get_next_matches():
    try:
        matchesToBet = []
        for d in range(21,31):
            matchesLinks = aDaScrappings.getAdaMatchesLinks("https://www.academiadasapostas.com/stats/livescores/2025/06/" + str("%02d" % d))
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
    for j in range(6,7):
        try:
            for i in range(1, 31):
                date = "2025-" + str("%02d" % j) + "-" + str("%02d" % i)
                results += (bttsOneHalf.getMatchesByDateFromDB2(date))

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

@app.route('/footy-stats/merge-csv', methods=['POST'])
def merge_csv():
    try:
        #data = request.get_json()
        return jsonify(footystats.merge_csv_files())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/footy-stats/add-new-columns', methods=['POST'])
def add_new_columns():
    try:
        #data = request.get_json()
        return jsonify(footystats.add_new_match_columns())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/footy-stats/test-strategy', methods=['POST'])
def test_strategies():
    try:
        #data = request.get_json()
        return jsonify(footystats.identify_teams_with_high_goal_percentage())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/footy-stats/leagues-stats-rates', methods=['GET'])
def get_leagues_stats_rates():
    try:
        #data = request.get_json()
        return jsonify(footystats.get_leagues_stats_rates())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/footy-stats/teams-stats-rates', methods=['POST'])
def get_teams_draws_info():
    try:
        data = request.data
        return jsonify(footystats.get_team_draw_stats_by_league(data))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/footy-stats/team-neg-seq', methods=['POST'])
def get_neg_seq():
    try:
        data = request.data
        return jsonify(footystats.get_neg_sequence_by_team(data))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/goals-fest/arrange-matches-by-season', methods=['POST'])
def arrange_matches_by_season():
    try:
        return goalsFest.filter_matches_by_competition()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/goals-fest/test', methods=['GET'])
def test_o25_strategy():
    try:
        return goalsFest.test_strategy_with_last_3_matches()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/ada/scrap-all-stats', methods=['POST'])
def ada_scrap_all_stats():
    try:
        data = request.get_json()
        return aDaScrappings.scrappAdAStatsBulk(data['month'], data['day'])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/ada/json-to-csv', methods=['POST'])
def ada_json_to_csv():
    try:
        return aDaScrappings.json_to_csv("scrapper/newData/allMatchesByAda_2024.json", "scrapper/newData/allMatchesByAda_2024.csv")
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/goals-fest/generate-csv', methods=['POST'])
def generate_csv():
    try:
        #data = request.get_json()
        return jsonify(goalsFest.generateFileForNextMatchesEbookStrategy())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/nba/scrap-data', methods=['POST'])
def nba_scrap_data():
    try:
        data = request.get_json()
        return jsonify(nbaBacktests.scrappNBAStatsBulk(data['url'], data['season']))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/nba/spread-backtest', methods=['GET'])
def nba_spread_backtest():
    try:
        #data = request.get_json()
        teams = ["DEN", "HOU", "CHI", "IND", "BOS", "LAC", "POR", "CLE", "ATL", "DAL", "NY", "SAC", "MIL", "WAS", "LAL", "TOR", "OKC", "PHO", "NO", "CHA", "MIN", "BK", "MEM", "GS", "PHI", "ORL", "SA", "MIA", "UTA", "DET"]
        #teams = ["DET"]
        season = '2022-23'
        all_teams_results = []
        
        for team in teams:
            results = {}
            results['team'] = team
            #results['original'] = nbaBacktests.spreadLongRedRunBacktest(team, season)
            sequence = progressive_betting(nbaBacktests.spreadLongRedRunBacktest(team, season))
            results['profit'] = sum(1 for char in sequence if char['outcome'] == 'green')
            results['sequence'] = str([item["outcome"][0] for item in sequence])
            all_teams_results.append(results)

        return all_teams_results
    except Exception as e:
        return jsonify({'error': str(e)})

def progressive_betting(sequence):
    """
    Implements a progressive betting strategy on a sequence of boolean results (True/False).

    Args:
        sequence: A list of booleans representing whether a team beat the spread (True) or not (False).

    Returns:
        A list of dictionaries, where each dictionary represents a betting action
        and its outcome (green/red).
    """

    results = []
    current_streak = 0
    current_streak_value = sequence[0]['beatspread']
    in_sequence = False
    sequence_type = None
    losses_in_sequence = 0
    level = 0
    looking_for_opposite = False

    for match in sequence:
        result = match['beatspread']
        if not in_sequence:  # Not currently in a betting sequence
            # Check for a streak of 5
            if result == current_streak_value:
                current_streak += 1
            else:
                current_streak = 1
                current_streak_value = result

            if current_streak >= 8:
                logging.info(match['date'])
                in_sequence = True
                sequence_type = not result  # Bet on the opposite of the streak
                logging.info(f"Starting progressive sequence, looking for {sequence_type}")
                losses_in_sequence = 0
                level = 1
                looking_for_opposite = False  # Reset at sequence start
                current_streak = 0
                continue

        if in_sequence:  # Currently in a betting sequence
            bet_type = sequence_type  # Store the bet type
            outcome = "green" if result == sequence_type else "red"
            results.append({"bet_type": bet_type, "outcome": outcome})
            logging.info(match['date'])
            logging.info(f"Betting on {bet_type}, Outcome: {outcome}")

            if result == sequence_type:  # Win!
                logging.info("Won!")
                in_sequence = False  # End the sequence
                losses_in_sequence = 0
                level = 0
                looking_for_opposite = False  # Reset at sequence end
            else:  # Loss
                logging.info("Lost!")
                losses_in_sequence += 1
                level += 1

                # if losses_in_sequence >= 3 and level >= 4 and not looking_for_opposite:
                #   looking_for_opposite = True
                #   sequence_type = not sequence_type
                #   logging.info(f"Changing target to {sequence_type} after 3 losses in a row")
                #   bet_type = sequence_type
                #   outcome = "green" if result == sequence_type else "red"
                #   #results[-1] = {"bet_type": bet_type, "outcome": outcome}
                #   #logging.info(f"Betting on {bet_type}, Outcome: {outcome}")

                # elif looking_for_opposite:
                #   bet_type = sequence_type
                #   outcome = "green" if result == sequence_type else "red"
                #   results[-1] = {"bet_type": bet_type, "outcome": outcome}
                #   logging.info(f"Betting on {bet_type}, Outcome: {outcome}")

    return results


@app.route('/telegram', methods=['POST'])
def telegram_scrap_data():
    try:
        return telegramScraps.fetch()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/btts-one-half/generate-csv', methods=['POST'])
def generate_csv_btts():
    try:
        #data = request.get_json()
        return jsonify(bttsOneHalf.generateFileForNextMatchesEbookStrategy())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/goals-fest/matches-by-teams', methods=['GET'])
def gf_get_matches_by_teams():
    try:
        data = request.get_json()
        return goalsFest.compile_matches_by_team(data['previousSeason'], data['season'])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/goals-fest/all-matches-by-team', methods=['GET'])
def gf_get_all_matches_by_team():
    try:
        data = request.get_json()
        return goalsFest.getAllMatchesByTeam(data['season'], data['team'])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/corner-strats-candidates', methods=['GET'])
def get_corner_strats_candidates():
    try:
        return jsonify(experiments.scrappCornerAdAStatsBulk())
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/over25-candidates-betexplorer', methods=['GET'])
def get_over25_betExplorer():
    try:
        return jsonify(experiments.getMatchStatsFromBetExplorer(request.data))
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/over25-leaguestats-betexplorer', methods=['GET'])
def get_leaguestats_betExplorer():
    try:
        return jsonify(experiments.getLeagueOverStatsFromBetExplorer(request.data))
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/lategoals', methods=['GET'])
def get_lateGoals_ada():
    try:
        return jsonify(seleniumScrapping.getLateGoalsMatchesCandidatesFromAdA())
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/transcript', methods=['GET'])
def get_youtube_transcription():
    try:
        return test.transcript_youtube_video()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/h2h-data', methods=['GET'])
def get_distinct_competitions():
    try:
        return test.process_h2h_data()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/fix-h2h-data', methods=['POST'])
def update_with_real_h2h_data():
    try:
        return test.update_with_real_h2h_data()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/sofascore', methods=['POST'])
def test_sofa_score():
    try:
        return ss.testSofaScore()
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/sample', methods=['POST'])
def sample():
    conmsList = []

    for obj in request.get_json():
        conmsList.append(str(obj['conm']))

    list_to_search = ['Momentum Metropolitan Holdings',
                      'Absa Group',
                      'Old Mutual',
                      'Standard Bank Group',
                      'Sanlam',
                      'Firstrand',
                      'MTN',
                      'Sasol',
                      'Vingroup',
                      'Joint Stock Commercial Bank for Foreign Trade of Vietnam',
                      'Vietin Bank',
                      'Commercial Bank For Investment & Development Of Vietnam',
                      'Mercantil Servicios',
                      'Zoetis',
                      'Zimmer Biomet Holdings',
                      'Zebra Technologies',
                      'Yum! Brands',
                      'Xylem',
                      'Xerox',
                      'Xilinx',
                      'Xcel Energy',
                      'XPO Logistics',
                      'Wynn Resorts',
                      'World Fuel Services',
                      'Wintrust Financial',
                      'Williams',
                      'Whirlpool',
                      'Weyerhaeuser Company',
                      'Westlake Chemical',
                      'Western Union',
                      'Western Digital',
                      'Western Alliance Bancorp.',
                      'Welltower',
                      'Wells Fargo',
                      'Waters',
                      'Waste Management',
                      'Walmart',
                      'Westinghouse Air Brake Technologies',
                      'WEC Energy']

    similarties = []
    for s in list_to_search:
        logging.info(s)
        logging.info(difflib.get_close_matches(s.split(' ')[0].upper(), conmsList, 1, cutoff=.6))
        logging.info('\n')

    return similarties


if __name__ == '__main__':
    logging.info("scrapper service is running...")
    #test.replace_month_in_csv()
    app.run(host="0.0.0.0", port=8000, debug=True)
