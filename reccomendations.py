import requests, base64, json
import csv
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np
# from sklearn.cluster import KMeans
from sklearn import preprocessing
import pdb
from sklearn.neighbors import NearestNeighbors
import sys
import auth

MIN_COMMON_SONGS = 1
token = auth.get_access_token()

def build_featurized_df(df):
    filtered_cols = ['duration_ms', 'time_signature', 'key', 'mode']
    for column in df:
        if df[column].dtype == np.object:
            filtered_cols.append(column)
    df_filtered = df.drop(columns=filtered_cols)
    x = df_filtered.values
    x_scaled = preprocessing.scale(x)
    return pd.DataFrame(x_scaled, index = df_filtered.index, columns = df_filtered.columns)

def find_song_index_from_title(song_title, df):
    song_index = -1
    for i, row in df.iterrows():
        if song_title == row['name']:
            return i
    if song_index == -1:
        raise Exception("Could not locate song title.")

def get_reccomendations(song_index, df, KNN_engine, MIN_COMMON_SONGS, token):
    dists, reccomended_ids = neigh.kneighbors([df_filtered.iloc[song_index].tolist()])
    dists = dists[0]
    reccomended_ids = reccomended_ids[0]
    final_reccomend = []


    url = 'https://api.spotify.com/v1/tracks/'
    headers = { 'Authorization': 'Bearer ' + token}

    song1_id = df.at[song_index, 'id']
    res = requests.get(url + song1_id, headers=headers)
    if res.status_code == 200:
        res = res.json()
        artist1_id = map(lambda artist: artist['id'], res['artists'])
    else:
        raise Exception('Request failed')

    artist1_genres = set()

    for artist in artist1_id:
        res = requests.get('https://api.spotify.com/v1/artists/' + artist, headers=headers)
        if res.status_code == 200:
            res = res.json()
            artist1_genres.update(res['genres'])
        else:
            raise Exception('Request failed')

    reccomended_song_ids = [df.at[i, 'id'] for i in reccomended_ids]
    ids = ",".join(reccomended_song_ids)
    res = requests.get("https://api.spotify.com/v1/tracks?ids=" + ids, headers=headers)
    if res.status_code != 200:
        raise Exception('Request failed')
    res = res.json()
    artist_ids = [track['artists'][0]['id'] for track in res['tracks']]

    for i, (dist, id) in enumerate(zip(dists, reccomended_ids)):
        artist2_id = artist_ids[i]
        res = requests.get('https://api.spotify.com/v1/artists/' + artist2_id, headers=headers)
        if res.status_code != 200:
            raise Exception('Request failed')
        res = res.json()
        artist2_genres = set(res['genres'])
        if 'pop' in artist1_genres and 'pop' in artist2_genres:
            artist1_genres.remove('pop')
            artist2_genres.remove('pop')

        if len(artist1_genres.intersection(artist2_genres)) >= MIN_COMMON_SONGS or not artist1_genres or not artist2_genres:
            print("Added : ", df.at[id, 'name'], df.at[id, 'artist'])
            final_reccomend.append(id)
        else:
            print("Skipped : ", df.at[id, 'name'], df.at[id, 'artist'])

    return final_reccomend

def add_reccomendations_to_playlist(song_ids, df, token):
    req_body = {}
    headers = { 'Authorization': 'Bearer ' + token, 'Content-Type': "application/json"}
    url = 'https://api.spotify.com/v1/users/jonmio/playlists/'
    req_body['name'] = "\\Playlist based on " + sys.argv[1]
    req_body['description'] = "Reccomendations from a python script based on " + sys.argv[1]
    req_body['public'] = False
    res = requests.post(url, data=json.dumps(req_body), headers=headers)
    if res.status_code != 200 and res.status_code != 201:
        raise Exception("Failed to create playlist")
    playlist_id = res.json()['id']
    song_uris = ",".join([df.at[id, 'uri'] for id in song_ids])
    url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks?uris=' + song_uris
    requests.post(url, headers=headers)


df = pd.read_csv("./songs_in_spotify_library.csv")
neigh = NearestNeighbors(n_neighbors=50, n_jobs=-1)
df_filtered = build_featurized_df(df)
neigh.fit(df_filtered.values)
song_title = sys.argv[1]
song_index = find_song_index_from_title(song_title, df)
reccomendations = get_reccomendations(song_index, df, neigh, MIN_COMMON_SONGS, token)
add_reccomendations_to_playlist(reccomendations, df, token)
