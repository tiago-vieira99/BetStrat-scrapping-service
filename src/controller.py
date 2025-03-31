from flask import Flask, jsonify, request
import scrapping
import seleniumScrapping
import experiments
import goalsFest
import bttsOneHalf
import footystats
import aDaScrappings
import difflib
import json
import test
import time
from collections import OrderedDict

app = Flask(__name__)


@app.route('/last-matches/<int:n>', methods=['POST'])
def get_last_n_matches(n):
    try:
        allLeagues = False
        if request.args.get("allleagues") == 'true':
            allLeagues = True

        if "worldfootball" in request.data.decode("utf-8"):
            return jsonify(scrapping.getLastNMatchesFromWF(request.data, n, request.args.get("team"), allLeagues, request.args.get("season")))
        elif "zerozero" in request.data.decode("utf-8"):
            return jsonify(scrapping.getLastNMatchesFromZZ(request.data, n, request.args.get("team")))
        else:
            return jsonify(scrapping.getLastNMatchesFromAdA(request.data, n))
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/next-match', methods=['POST'])
def get_next_match():
    try:
        allLeagues = False
        if request.args.get("allleagues") == 'true':
            allLeagues = True

        if "worldfootball" in request.data.decode("utf-8"):
            return jsonify(scrapping.getNextMatchFromWF(request.data, request.args.get("team"), request.args.get("season"), allLeagues))
        elif "zerozero" in request.data.decode("utf-8"):
            return jsonify(scrapping.getNextMatchFromZZ(request.data, request.args.get("team")))
        else:
            return jsonify(scrapping.getNextMatchFromAdA(request.data))
    except Exception as e:
        return jsonify({'error': str(e)})


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

        if "worldfootball" in request.data.decode("utf-8"):
            return jsonify(scrapping.getLeagueTeamsFromWF(request.data))
        else:
            return 'url not supported'
    except Exception as e:
        return jsonify({'error': str(e)})


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
            #print(element['3. match'])
            element['4. ft_result'] = test.get_goals_mins(element)
            #break
            # time.sleep(2)
            # #print(str(len(mins))+ " !! " + str(int(element['total goals'][0])))
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
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({'error': str(e)})

@app.route('/btts-one-half/matches-between-teams', methods=['GET'])
def btts_get_matches_between_teams():
    try:
        data = request.get_json()
        return bttsOneHalf.getMatchesBetweenFilteredTeams(data['previousSeason'], data['season'])
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return jsonify({'error': str(e)})

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
        return aDaScrappings.scrappAdAStatsBulk('1')
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
        print(s)
        print(difflib.get_close_matches(s.split(' ')[0].upper(), conmsList, 1, cutoff=.6))
        print('\n')

    return similarties


if __name__ == '__main__':
    print("scrapper service is running...")
    #test.replace_month_in_csv()
    app.run(host="0.0.0.0", port=8000, debug=True)
