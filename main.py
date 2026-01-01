from dotenv import load_dotenv
import os
import base64
from requests import post, get
from flask import Flask, request, jsonify, render_template

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes),"utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = result.json()["artists"]["items"]
    if len(json_result) == 0:
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=IN"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()["tracks"]
    songs = []
    for track in json_result:
        songs.append(track["name"])
    return songs

def get_artist_by_song(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={song_name}&type=track&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = result.json()["tracks"]["items"]
    if len(json_result) == 0:
        return None
    r = json_result[0]["artists"]

    if len(r) == 0:
        return None
    elif len(r) > 1:
        return [artist["name"] for artist in r]
    elif len(r) == 1:
        return f"Artist: {r[0]['name']}"

    return None

def get_track_id_by_song(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={song_name}&type=track&limit=1"

    result = get(url + query, headers=headers)
    items = result.json()["tracks"]["items"]

    if not items:
        return None

    return f"https://open.spotify.com/embed/track/{items[0]['id']}"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    songs = []
    artists = []
    artist_name = ""
    song_name = ""
    preview_url = None  

    if request.method == "POST":
        action = request.form.get("action")
        token = get_token()


        if action == "artist":
            artist_name = request.form.get("artist_name")
            artist = search_for_artist(token, artist_name)

            if artist:
                songs = get_songs_by_artist(token, artist["id"])


        elif action == "song":
            song_name = request.form.get("song_name")
            artists = get_artist_by_song(token, song_name)

        elif action == "play":
            song_name = request.form.get("song_name_")
            preview_url = get_track_id_by_song(token, song_name)


    return render_template(
        "index.html",
        songs=songs,
        artist=artist_name,
        artists=artists,
        song=song_name,
        preview_url=preview_url
    )

if __name__ == "__main__":
    app.run(port=9748)



