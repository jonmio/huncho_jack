import requests, base64, json
import csv
from requests.auth import HTTPBasicAuth


url = 'https://api.spotify.com/v1/audio-features/'
token = 'BQBYmDLNnT2SsfwOnQjfqw7mipww1JaJVe9P-SacTX571U3Yl93ssFPbtxcayXHM5PQNRe2oEGdhfbvGE-9YCcOL9T1l7zEhRCVkbKREJlV9oFLTzLlQffxePijtNjmaXEG7OpNZVS-NUqNA5Im-CSepokK7e8yViozOZ6hajVKOq_2_FpwKskEZ4sem8S9J6LzvdY00NqHzCf2G3ZUQ-svh_xvv6psOFxo_8zOFWSIBMD95L_QteQ1F3MJs3RYpYACNLakRTMUwmw'#
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

with open('songs_in_spotify_library.csv', 'w') as csvfile:
    fieldnames = songs[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for song in songs:
        try:
            writer.writerow(song)
        except:
            print(song['name'])
