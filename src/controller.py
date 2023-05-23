from flask import Flask, jsonify, request
import scrapping

app = Flask(__name__)

@app.route('/last-matches/<int:n>', methods=['GET'])
def get_last_n_matches(n):
    try:
        # matches = scraping.getLastNMatches(n)
        # return jsonify(matches)
        print(n)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/next-match/<string:team>', methods=['GET'])
def get_next_match(team):
    try:
        print(request.data)
        return jsonify(scrapping.scrapeDataFromPage())        
        # match = scraping.getNextMatch()
        # if match:
        #     return jsonify(match)
        # else:
        #     return jsonify({'message': 'No upcoming match found.'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)