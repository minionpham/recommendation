import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import spotipy
import requests

def cosine_similarity_vec(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0][0]

def recommend_songs(song_id, sp, df_songs, num_recommendations=5):
    try:
        song_features = sp.audio_features(song_id)[0]
    except Exception as e:
        print(f"Error: Failed to fetch audio features for the input song ID: {e}")
        return []

    song_features_selected = [
        song_features['danceability'], song_features['energy'], song_features['key'], 
        song_features['loudness'], song_features['mode'], song_features['speechiness'], 
        song_features['acousticness'], song_features['instrumentalness'], song_features['liveness'], 
        song_features['valence'], song_features['tempo']
    ]

    similarities = []
    for index, row in df_songs.iterrows():
        if row['id'] == song_id:
            continue

        other_song_features_selected = [
            row['danceability'], row['energy'], row['key'], row['loudness'], 
            row['mode'], row['speechiness'], row['acousticness'], 
            row['instrumentalness'], row['liveness'], row['valence'], row['tempo']
        ]
        similarity = cosine_similarity_vec(song_features_selected, other_song_features_selected)
        similarities.append((index, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    recommended_song_ids = [df_songs.loc[similarity[0], 'id'] for similarity in similarities[:num_recommendations]]

    return recommended_song_ids

def recommend_songs_listened(sp, df_songs, token, num_recommendations=5):
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=20', headers=headers)
        response.raise_for_status()
        results = response.json()
        recently_played = results['items']

        # Collect the feature vectors of recently played songs
        feature_vectors = []
        for item in recently_played:
            song_id = item['track']['id']
            try:
                song_features = sp.audio_features(song_id)[0]
                if not song_features:
                    print(f"Warning: No audio features found for song ID {song_id}")
                    continue
            except Exception as e:
                print(f"Error fetching audio features for song ID {song_id}: {e}")
                continue

            song_features_selected = [
                song_features['danceability'], song_features['energy'], song_features['key'], 
                song_features['loudness'], song_features['mode'], song_features['speechiness'], 
                song_features['acousticness'], song_features['instrumentalness'], song_features['liveness'], 
                song_features['valence'], song_features['tempo']
            ]
            feature_vectors.append(song_features_selected)

        if not feature_vectors:
            print("No valid features found for recently played songs.")
            return []

        # Compute the average feature vector
        avg_feature_vector = np.mean(feature_vectors, axis=0)

        # Calculate cosine similarity with the average feature vector for each song in df_songs
        similarities = []
        for index, row in df_songs.iterrows():
            other_song_features_selected = [
                row['danceability'], row['energy'], row['key'], row['loudness'], 
                row['mode'], row['speechiness'], row['acousticness'], 
                row['instrumentalness'], row['liveness'], row['valence'], row['tempo']
            ]
            similarity = cosine_similarity_vec(avg_feature_vector, other_song_features_selected)
            similarities.append((index, similarity))

        # Sort by similarity and get the top recommendations
        similarities.sort(key=lambda x: x[1], reverse=True)
        recommended_song_ids = [df_songs.loc[similarity[0], 'id'] for similarity in similarities[:num_recommendations]]

        return recommended_song_ids
    except Exception as e:
        print(f"Error in recommend_songs_listened: {e}")
        return []