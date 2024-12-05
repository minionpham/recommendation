#for find song
import requests
from bs4 import BeautifulSoup
import re

# URL of the webpage (Spotify Daily charts Viet Nam)
url = "https://kworb.net/spotify/country/vn_daily.html"

response = requests.get(url)
response.encoding = 'utf-8'  # Ensure the content is decoded in UTF-8
if response.status_code != 200:
    print(f"Failed to retrieve page. Status code: {response.status_code}")
    exit()

html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table containing the data
table = soup.find('table')
if not table:
    print("Table not found on the page. Please check the page structure.")
    exit()

data = []  # List to store extracted song data
num_order = 1  # Counter for song order

# Iterate through each row in the table (skipping the header row)
for row in table.find_all('tr')[1:]:
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

# For server
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Define the route to get the song data
@app.route('/api/songs', methods=['GET'])
def get_songs():
    # Return only the first 100 songs
    songs_list = data[:100]  # Top 100 songs
    formatted_songs = [{'Order': song[0], 'Name': song[1], 'Artist': song[2], 'ID': song[3]} for song in songs_list]
    return jsonify(formatted_songs)

if __name__ == '__main__':
    port = 5000
    print(f"Server is running on http://127.0.0.1:{port}")
    app.run(debug=True, port=port)
