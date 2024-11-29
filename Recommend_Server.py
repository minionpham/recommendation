from flask import Flask, jsonify, request
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup Spotify API
cid = "4353ed52ef66416193e5490b48292603"
secret = "53b482e23bc34c2bb26d9df40b759734"
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load song data from CSV (make sure this path is correct)
df_songs = pd.read_csv('spotify_data_vn_daily_chart.csv')

# Fetch only the first 50 songs
df_songs_top_50 = df_songs.head(50)  # This gets the first 50 rows of the DataFrame

@app.route('/api/songs', methods=['GET'])
def get_songs():
    # Fetch only the first 50 songs from the DataFrame
    songs_list = df_songs_top_50[['Order', 'Name', 'Artist', 'ID']].to_dict(orient='records')
    return jsonify(songs_list)

if __name__ == '__main__':
    app.run(debug=True)
