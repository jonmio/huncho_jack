import requests
import json
import spotify_secrets

refresh_token = spotify_secrets.secrets['refresh_token']
client_id = spotify_secrets.secrets['client_id']
client_secret = spotify_secrets.secrets['client_secret']

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    req_body = {}
    req_body['grant_type'] = 'refresh_token'
    req_body['refresh_token'] = refresh_token
    req_body['client_id'] = client_id
    req_body['client_secret'] = client_secret
    res = requests.post(url, data=req_body)
    if res.status_code != 200 and res.status_code != 201:
        raise Exception("Failed to get access token.")
    return json.loads(res.text)['access_token']
