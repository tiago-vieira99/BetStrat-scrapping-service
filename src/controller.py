from flask import Flask, jsonify, request
import scrapping
import seleniumScrapping
import experiments

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
        return jsonify(experiments.scrappAdAStatsBulk())
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/over25-candidates', methods=['GET'])
def get_over25_candidates():
    try:
        return jsonify(experiments.scrappAdAStatsBulk())
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

if __name__ == '__main__':
    print("scrapper service is running...")
    app.run(host="0.0.0.0", port=8000, debug=True)