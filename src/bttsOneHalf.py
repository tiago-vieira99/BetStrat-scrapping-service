import csv
from collections import Counter
from datetime import datetime, timedelta
import requests
import sys, os
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras
import json
import logging
import pika

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# quiet pika logs
logging.getLogger("pika").setLevel(logging.WARNING)

def publish_match(match_data, rabbitQueue):
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbit"))
    channel = connection.channel()

    # Ensure queue exists
    channel.queue_declare(queue=rabbitQueue, durable=True)

    # Publish message
    channel.basic_publish(
        exchange="",
        routing_key=rabbitQueue,
        body=json.dumps(match_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )
    logging.info(f"Published data in queue '{rabbitQueue}': {match_data} ")
    connection.close()

# testing strategy: https://www.financial-spread-betting.com/sports/Goals-betting-system.html#respond
# get matches from database that would be considered for over2.5 strategy
def getOVERMatchesByDateFromDB(date_str):
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


# get matches from database that would be considered for btts_one_half strategy
def getBTTSMatchesByDateFromDB(date_str):
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

                    teams_goals_avg = float((home_total_goals_avg_at_home_pre + away_total_goals_avg_at_away_pre) / 2)

                    #if (btts_streak_length >= 6 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 6 and float(over_streak_value/over_streak_length) >= 0.75) and home_total_goals_avg_at_home_pre >= 2 and away_total_goals_avg_at_away_pre >= 2:
                    ##working: if home_total_goals_avg_at_home_pre >= 3 and away_total_goals_avg_at_away_pre >= 3 and (btts_streak_length >= 5 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 5 and float(over_streak_value/over_streak_length) >= 0.75) and ( (home_btts_streak_length >= 5 and float(home_btts_streak_value/home_btts_streak_length) >= 0.75) and (home_over_streak_length >= 5 and float(home_over_streak_value/home_over_streak_length) >= 0.75) or (away_btts_streak_length >= 5 and float(away_btts_streak_value/away_btts_streak_length) >= 0.75) and (away_over_streak_length >= 5 and float(away_over_streak_value/away_over_streak_length) >= 0.75) ):
                    if teams_goals_avg >= 3.5 and (btts_streak_length >= 5 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 5 and float(over_streak_value/over_streak_length) >= 0.75) and ( (home_btts_streak_length >= 5 and float(home_btts_streak_value/home_btts_streak_length) >= 0.75) and (home_over_streak_length >= 5 and float(home_over_streak_value/home_over_streak_length) >= 0.75) or (away_btts_streak_length >= 5 and float(away_btts_streak_value/away_btts_streak_length) >= 0.75) and (away_over_streak_length >= 5 and float(away_over_streak_value/away_over_streak_length) >= 0.75) ):
                    #if (btts_streak_length >= 5 and float(btts_streak_value/btts_streak_length) >= 0.75) and (over_streak_length >= 5 and float(over_streak_value/over_streak_length) >= 0.75) and ( (home_btts_streak_length >= 5 and float(home_btts_streak_value/home_btts_streak_length) >= 0.75) and (home_over_streak_length >= 5 and float(home_over_streak_value/home_over_streak_length) >= 0.75) or (away_btts_streak_length >= 5 and float(away_btts_streak_value/away_btts_streak_length) >= 0.75) and (away_over_streak_length >= 5 and float(away_over_streak_value/away_over_streak_length) >= 0.75) ):
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