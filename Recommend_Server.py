import os
import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# URL of the Spotify Daily Charts (Vietnam)
url = "https://kworb.net/spotify/country/vn_daily.html"

# Scrape data from the webpage
response = requests.get(url)
response.encoding = 'utf-8'  # Ensure correct decoding
if response.status_code != 200:
    print(f"Failed to retrieve page. Status code: {response.status_code}")
    data = []
else:
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract table data
    table = soup.find('table')
    data = []  # To store song data
    if table:
        num_order = 1
        for row in table.find_all('tr')[1:]:  # Skip header row
            columns = row.find_all('td')
            if len(columns) >= 7:
                try:
                    name_artist = columns[2].text.strip()
                    if " - " not in name_artist:
                        continue

                    match = re.match(r"(.+) - (.+)", name_artist)
                    if match:
                        artist, name = match.groups()
                        artist, name = artist.strip(), name.strip()

                        link_tags = columns[2].find_all('a')
                        if len(link_tags) < 2:
                            continue
                        track_url = link_tags[1]['href']
                        track_id = track_url.split('/')[-1].split('.')[0]  # Extract track ID

                        data.append((num_order, name, artist, track_id))
                        num_order += 1
                except Exception as e:
                    print(f"Error: {e} - Skipping row.")

# Define Flask route for API
@app.route('/api/songs', methods=['GET'])
def get_songs():
    # Return only the first 100 songs
    songs_list = data[:100]
    formatted_songs = [{'Order': song[0], 'Name': song[1], 'Artist': song[2], 'ID': song[3]} for song in songs_list]
    return jsonify(formatted_songs)

# Entry point for Gunicorn
if __name__ == '__main__':
    # Render dynamically sets the port; default to 5000 for local testing
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'

    # Provide log information based on the environment
    render_url = os.getenv('RENDER_EXTERNAL_HOSTNAME')  # Render provides this environment variable
    if render_url:
        print(f"Server is running on: https://{render_url}/api/songs")
    else:
        print(f"Server is running on: http://127.0.0.1:{port}/api/songs")
    
    app.run(host=host, port=port)
