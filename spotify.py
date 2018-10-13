import requests, base64, json
import csv
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn import preprocessing
from collections import defaultdict
import pdb

url = 'https://api.spotify.com/v1/audio-features/'
token = 'BQBv6f56TsE9UXs-mk9pKtmcXl-x-_h18yA-FEmJq0QSMF4stId-JiWblkO9Uywz7EBLTTaKft31_4pAAYjGuGAtdvqjAwOt-3Zy7XvRSpU1lefNJUsXskY6wtDzaDFGiKSD5FFzOMnpftr6gikzrk4k2z4vmyHYVg7SLtzC-gHo3qeqz6tJW9In3Hyu43wWtlQbrQcsvb9SV2MQhiPDbV7NTnrkKWlycAqXu3rzxebhddgHJTQucSyji536EqoB8G-ROKHLJMhBfw'
jontoken = 'BQCxiNxCN9CKlcldm1RAnn0clJvMDx-SjRWL8VCjFyN3yNnChedyp7oDn7Qpgowg_gN1j6vitVW5A7Eou0-zkeltqXnhFnuqPJZLjdMQdY0sqgwo4RExm1gzR1hhi3lh9UJYbvmthGVHEYreCHyIoukpbc78Eoyhky4Lr0eIudxUnIFjYxfO7ETmo7FU__kyzO-Iig_rhVDrrURixm42CuiCEmN491mDyKY4ZkbFnyPkWvqw4cRb-RdmHmh_e955V_yDyGiYIQCSKw'

headers = { 'Authorization': 'Bearer ' + token }

songIds = set()
idtoname = {}
idtoartists = {}

# for playlistId in playlistIds:
res = requests.get(url='https://api.spotify.com/v1/me/tracks', headers=headers)
while res.status_code == 200:
    for track in res.json()['items']:
        print( track['track']['name'] )
        songIds.add(track['track']['id'])
        idtoname[track['track']['id']] = track['track']['name']
        idtoartists[track['track']['id']] = track['track']['artists'][0]['name']
    nexturl = res.json().get('next', '')
    if nexturl == None:
        break
    res = requests.get(url=nexturl, headers=headers)


songs = []
for id in songIds:
    res = requests.get(url+id, headers=headers)
    if res.status_code == 200:
        res = res.json()
        res['name'] = idtoname[id]
        print( idtoname[id] )
        res['artist'] = idtoartists[id]
        songs.append(res)

with open('names.csv', 'w') as csvfile:
    fieldnames = songs[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for song in songs:
        try:
            writer.writerow(song)
        except:
            print(song['name'])


df = pd.read_csv("names.csv")
filtered_cols = ['duration_ms', 'time_signature', 'key', 'liveness']
print(df.columns)
print(df.shape)
for column in df:
    # print(df[column].dtype)
    # print(type(df[column].dtype))
    if df[column].dtype == np.object:
        filtered_cols.append(column)
df_filtered = df.drop(columns=filtered_cols)
x = df_filtered.values #returns a numpy array
x_scaled = preprocessing.scale(x)
# num1 = []
# num2 = []
# for column in x.T:
#     num1.append(np.mean(column))
# for column in x_scaled.T:
#     num2.append(np.mean(column))
# for i in range(len(num1)):
#     print(num1[i])
#     print(num2[i])
# >>> X_scaled
# array([[ 0.  ..., -1.22...,  1.33...],
#        [ 1.22...,  0.  ..., -0.26...],
#        [-1.22...,  1.22..., -1.06...]])
# min_max_scaler = preprocessing.MinMaxScaler()
# x_scaled = min_max_scaler.fit_transform(x)
df_filtered = pd.DataFrame(x_scaled)
cluster_indices = KMeans(n_clusters=15,n_init=500,init='random').fit_predict(df_filtered.values)
d = defaultdict(list)
for i,elem in enumerate(cluster_indices):
    d[elem].append((df.at[i, 'name'], df.at[i, 'artist']))
for key in d:
    for elem in d[key]:
        print(elem[:50])
    print("************")
    print("***********")
