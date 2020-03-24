import requests, base64, json
import csv
from requests.auth import HTTPBasicAuth
import auth

url = 'https://api.spotify.com/v1/audio-features/'
token = auth.get_access_token()
headers = { 'Authorization': 'Bearer ' + token }

song_ids = set()
id_to_name = {}
id_to_artist = {}

# for playlistId in playlistIds:
res = requests.get(url='https://api.spotify.com/v1/me/tracks', headers=headers)
while res.status_code == 200:
    for track in res.json()['items']:
        print( track['track']['name'] )
        song_ids.add(track['track']['id'])
        id_to_name[track['track']['id']] = track['track']['name']
        id_to_artist[track['track']['id']] = track['track']['artists'][0]['name']
    nexturl = res.json().get('next', '')
    if nexturl == None:
        break
    res = requests.get(url=nexturl, headers=headers)


songs = []
for id in song_ids:
    res = requests.get(url+id, headers=headers)
    if res.status_code == 200:
        res = res.json()
        res['name'] = id_to_name[id]
        print( id_to_name[id] )
        res['artist'] = id_to_artist[id]
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
