from dotenv import load_dotenv
import os
import base64
from requests import post, get
from flask import Flask, request, jsonify, render_template
from urllib.parse import quote

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
    
def get_song_url(song_name):
    nbase_url = "https://dlkitgo-o3njscwgh-aadisankar1s-projects.vercel.app/spotify/search?q=" + quote(song_name)
    base_url = "https://dlkitgo.vercel.app/spotify/search?q=" + quote(song_name)
    try:
        response = get(base_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        if response.status_code == 200: 
            return results[0].get('url', 'URL not found')
    except Exception as e:
        print(f"Error fetching song URL: {e}")

def get_download_link(song_name):
    url = get_song_url(song_name)
    if url == 'URL not found':
        return None
    try:
        base_download_link = "https://dlkitgo.vercel.app/spotify/stream?url=" + url
        data = get(base_download_link).json()
        source = data.get('source', [])
        if not source:
            return None
    except Exception as e:
        print(f"Error fetching download link: {e}")
        return None
    download_link = source[0].get('url', None)
    return download_link

    return f"https://open.spotify.com/embed/track/{items[0]['id']}"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    songs = []
    artists = []
    artist_name = ""
    song_name = ""
    preview_url = None
    download_link = None

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

        elif action == "download":
            song_name = request.form.get("song_name_dl")
            download_link = get_download_link(song_name)

    return render_template(
        "index.html",
        songs=songs,
        artist=artist_name,
        artists=artists,
        song=song_name,
        preview_url=preview_url,
        download_link=download_link
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
