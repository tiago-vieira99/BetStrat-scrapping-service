from flask import Flask, jsonify, request
import scrapping
import seleniumScrapping

app = Flask(__name__)

@app.route('/last-matches/<int:n>', methods=['POST'])
def get_last_n_matches(n):
    try:
        return jsonify(scrapping.getLastNMatchesFromAdA(request.data, n))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/next-match', methods=['POST'])
def get_next_match():
    try:
        return jsonify(scrapping.getNextMatchFromAdA(request.data))
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/live-matches', methods=['GET'])
def get_live_matches():
    try:
        return jsonify(seleniumScrapping.getLiveResultsFromAdA())
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)