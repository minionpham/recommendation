#for find song
import requests
from bs4 import BeautifulSoup
import csv
import re
# URL of the webpage (Spotify Daily charts Viet Nam)
url = "https://kworb.net/spotify/country/vn_daily.html"

# Send a GET request to fetch the HTML content
response = requests.get(url)
response.encoding = 'utf-8'  # Ensure the content is decoded in UTF-8
if response.status_code != 200:
    print(f"Failed to retrieve page. Status code: {response.status_code}")
    exit()

html_content = response.text

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table containing the data
table = soup.find('table')
if not table:
    print("Table not found on the page. Please check the page structure.")
    exit()

# Initialize a list to store data
data = []

# Initialize a counter for numerical order
num_order = 1

# Iterate through each row in the table (skipping the header row)
for row in table.find_all('tr')[1:]:  # Skip header row
    # Extract columns (name, days, T10, Pk, (x?), PkStreams, Total)
    columns = row.find_all('td')

    if len(columns) >= 7:
        try:
            # Extract name and artist from the third column (columns[2])
            name_artist = columns[2].text.strip()

            # Check if there is a ' - ' separating artist and track
            if " - " not in name_artist:
                print(f"Skipping row due to missing ' - ': {name_artist}")
                continue

            # Using regex to clean up possible extra spaces around the separator and split
            match = re.match(r"(.+) - (.+)", name_artist)
            if match:
                artist, name = match.groups()
                artist, name = artist.strip(), name.strip()

                # Extract track URL (validating presence of <a> tags)
                link_tags = columns[2].find_all('a')
                if len(link_tags) < 2:
                    print(f"Skipping row due to missing track URL: {row}")
                    continue

                track_url = link_tags[1]['href']
                track_id = track_url.split('/')[-1].split('.')[0]  # Extract ID

                # Append data as a tuple including numerical order
                data.append((num_order, name, artist, track_id))

                # Increment numerical order
                num_order += 1
            else:
                print(f"Skipping row due to unexpected format: {name_artist}")

        except IndexError as e:
            print(f"IndexError: {e} - Skipping row: {row}")

        except Exception as e:
            print(f"Error: {e} - Skipping row: {row}")

# Specify the CSV file path
csv_file = 'spotify_data_vn_daily_chart.csv'

# Write data to CSV file
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Order', 'Name', 'Artist', 'ID'])  # Write header
    writer.writerows(data)

print(f"CSV file '{csv_file}' with ordered data has been created successfully.")

#for server
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

# Fetch only the first 100 songs
df_songs_top_100 = df_songs.head(100)  # This gets the first 50 rows of the DataFrame

@app.route('/api/songs', methods=['GET'])
def get_songs():
    # Fetch only the first 5=100 songs from the DataFrame
    songs_list = df_songs_top_100[['Order', 'Name', 'Artist', 'ID']].to_dict(orient='records')
    return jsonify(songs_list)

if __name__ == '__main__':
    port = 5000  # Default port 
    print(f"Server is running on http://127.0.0.1:{port}")
    app.run(debug=True, port=port)