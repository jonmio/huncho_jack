import requests, base64, json
import csv
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np
# from sklearn.cluster import KMeans
from sklearn import preprocessing
import pdb
from sklearn.neighbors import NearestNeighbors

def traverse(song_index, visited, df, df_filtered, curr):
    if len(curr) == 20:
        return
    if song_index not in visited:
        visited.add(song_index)
        curr.append(song_index)

        dists, reccomended_ids = neigh.kneighbors([df_filtered.iloc[song_index].tolist()])
        dists = dists[0]
        reccomended_ids = reccomended_ids[0]
        for dist, id in zip(dists, reccomended_ids):
            song1_qualities = df_filtered.iloc[song_index]
            song2_qualities = df_filtered.iloc[id]
            diff = [abs(q1 - q2) <= 1.5 for (q1,q2) in zip(song1_qualities, song2_qualities)]
            # if False in diff:
            #     continue
            traverse(id, visited, df, df_filtered, curr)

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
        if song_title in row['name']:
            return i
    if song_index == -1:
        raise Exception("Could not locate song title.")

def get_reccomendations(song_index, df, KNN_engine, degree_of_similarity):
    dists, reccomended_ids = neigh.kneighbors([df_filtered.iloc[song_index].tolist()])
    dists = dists[0]
    reccomended_ids = reccomended_ids[0]
    final_reccomend = []


    url = 'https://api.spotify.com/v1/tracks/'
    token = 'BQDRBsigDvWzbetW3F7KABfWq_xaBfL1Q1OHpbozS0_B56MIZvNbV7dtDgV53JWQQ1g0sejawku2tY_dofYdFu84_Jagk2YMkIVvK_aXJiyDHlD5qLMu7PwBljc_GNh02-FKLKA1_BudSB7kEsRsawXwj6eHwbVJ3DSBX7a17yQYzuiSsth67qI7yc0GSOKWD0gEQeWGjrqzYKTN_TnonPxTlR0vltqOnGc1sJbKhdlSrlzRCkhuQ7xdk-YjLffxVZPCnTUk_xmHIA'#
    headers = { 'Authorization': 'Bearer ' + token}

    song1_id = df.at[song_index, 'id']
    res = requests.get(url + song1_id, headers=headers)
    if res.status_code == 200:
        res = res.json()
        artist1_id = res['artists'][0]['id']
    else:
        raise Exception('Request failed')
    res = requests.get('https://api.spotify.com/v1/artists/' + artist1_id, headers=headers)
    if res.status_code == 200:
        res = res.json()
        artist1_genres = res['genres']
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
        artist2_genres = res['genres']
        if 'pop' in artist1_genres and 'pop' in artist2_genres:
            artist1_genres.remove('pop')
            artist2_genres.remove('pop')

        if len(artist1_genres) + len(artist2_genres) - len(set(artist1_genres + artist2_genres)) >= degree_of_similarity :
            print("Added : ", df.at[id, 'name'], df.at[id, 'artist'])
            final_reccomend.append(id)
        else:
            print("Skipped : ", df.at[id, 'name'], df.at[id, 'artist'])

    return final_reccomend

def add_reccomendations_to_playlist(song_ids):
    for id in song_ids:
        pass

df = pd.read_csv("./songs_in_spotify_library.csv")

neigh = NearestNeighbors(n_neighbors=50)
df_filtered = build_featurized_df(df)
neigh.fit(df_filtered.values)

song_title = "Stairway"
song_index = find_song_index_from_title(song_title, df)

# genres = [
#     set(["rock", "alternative", "grunge", "metal", "classic rock"]),
#     set(["house", "bass house", "edm", "dubstep", "electronic"]),
#     set(["rap", "hip hop", "hip-hop"])
# ]

degree_of_similarity = 2

reccomendations = get_reccomendations(song_index, df, neigh, degree_of_similarity)
add_reccomendations_to_playlist(reccomendations)

# # for _ in range(10):
# visited = set()
# curr = []
# traverse(song_index, visited, df, df_filtered, curr)
# print("Playlist:")
# for id in curr:
#     print(df.at[id, 'name'], df.at[id, 'artist'], id)
# print("\n")
# print("\n")
    #
    # # print(df.at[song_index, 'name'], df.at[song_index, 'artist'])
    #
    #
    # dists, reccomended_ids = neigh.kneighbors([df_filtered.iloc[song_index].tolist()])
    # dists = dists[0]
    # reccomended_ids = reccomended_ids[0]
    # print("Reccomandations:")
    # for dist, id in zip(dists, reccomended_ids):
    #     song1_qualities = df_filtered.iloc[song_index]
    #     song2_qualities = df_filtered.iloc[id]
    #     diff = [abs(q1 - q2) <= 1.5 for (q1,q2) in zip(song1_qualities, song2_qualities)]
    #     if False in diff:
    #         continue
    #     print(df.at[id, 'name'], df.at[id, 'artist'], id)
    # print("\n")
    # print("\n")

# # d = defaultdict(list)
# # for i,elem in enumerate(cluster_indices):
# #     d[elem].append((df.at[i, 'name'], df.at[i, 'artist']))
# # for key in d:
# #     for elem in d[key]:
# #         print(elem[:50])
# #     print("************")
# #     print("***********")
#
#
# print(neigh.kneighbors([[1., 1., 1.]]))
# (array([[0.5]]), array([[2]]))
#
# distorsions = []
# for k in nge(3, 1000, 20):
#     kmeans = KMeans(n_clusters=k)
#     kmeans.fit(X)
#     distorsions.append(kmeans.inertia_)
#
# fig = plt.figure(figsize=(15, 5))
# plt.plot(range(3, 1000,20), distorsions)
# plt.grid(True)
# plt.title('Elbow curve')
# plt.show()

# cluster_indices = KMeans(n_clusters=100,n_init=1000,init='random').fit_predict(df_filtered.values)
# d = defaultdict(list)
# for i,elem in enumerate(cluster_indices):
#     d[elem].append((df.at[i, 'name'], df.at[i, 'artist']))
# for key in d:
#     for elem in d[key]:
#         print(elem[:50])
#     print("************")
#     print("***********")