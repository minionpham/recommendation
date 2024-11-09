from flask import Flask, jsonify, request
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from Recommend_method import recommend_songs, recommend_songs_listened
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup Spotify API
cid = "5ce22bf9a89040eb895942284fe06912"
secret = "28251d136c45461e88942dd633250ae4"
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load playlist songs data
df_songs = pd.read_csv('Top_songs_2018-Now.csv')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    song_id = data.get('song_id')
    num_recommendations = data.get('num_recommendations', 5)  # Default to 5 recommendations

    recommended_song_ids = recommend_songs(song_id, sp, df_songs, num_recommendations)
    return jsonify(recommended_song_ids)

@app.route('/api/recommendations_listened', methods=['GET'])
def get_recommendations_listened():
    token = request.headers.get('Authorization').split(' ')[1]  # Extract the token from the Authorization header
    num_recommendations = request.args.get('num_recommendations', 5, type=int)  # Default to 5 recommendations

    recommended_song_ids = recommend_songs_listened(sp, df_songs, token, num_recommendations)
    return jsonify(recommended_song_ids)

if __name__ == '__main__':
    app.run(debug=True)
