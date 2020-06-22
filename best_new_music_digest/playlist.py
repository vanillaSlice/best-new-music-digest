"""
Playlist helpers.
"""

from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from best_new_music_digest import settings


def create_playlists(digest):
    """
    Creates a Spotify playlist.
    """

    should_create = settings.CREATE_SPOTIFY_PLAYLISTS and any(d["items"] for d in digest)

    if not should_create:
        return None, None

    auth_manager = SpotifyOAuth(scope="playlist-modify-private",
                                client_id=settings.SPOTIFY_CLIENT_ID,
                                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                                username=settings.SPOTIFY_USERNAME,
                                redirect_uri="http://localhost:8888/callback")
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    user_id = spotify.me()["id"]

    album_track_ids = []
    track_ids = []

    for digest_item in digest:
        if digest_item["type"] == "albums":
            album_track_ids.extend(__get_album_track_ids(digest_item, spotify))
        elif digest_item["type"] == "tracks":
            track_ids.extend(__get_track_ids(digest_item, spotify))

    albums_playlist_url = __add_tracks_to_playlist(album_track_ids, spotify, user_id, "albums")
    tracks_playlist_url = __add_tracks_to_playlist(track_ids, spotify, user_id, "tracks")

    return albums_playlist_url, tracks_playlist_url


def __get_album_track_ids(digest_item, spotify):
    album_track_ids = []

    for item in digest_item["items"]:
        artist = item["artist"]
        title = item["title"]

        album_result = spotify.search(q=f"artist:{artist} album:{title}", type="album", limit=1)

        album_items = album_result["albums"]["items"]

        if not album_items:
            continue

        album_id = album_items[0]["id"]

        tracks_result = spotify.album_tracks(album_id)

        for track in tracks_result["items"]:
            album_track_ids.append(track["id"])

    return album_track_ids


def __get_track_ids(digest_item, spotify):
    track_ids = []

    for item in digest_item["items"]:
        artist = item["artist"]
        title = item["title"].split(" ft. ")[0]

        tracks_result = spotify.search(q=f"artist:{artist} track:{title}", type="track", limit=1)

        tracks_items = tracks_result["tracks"]["items"]

        if not tracks_items:
            continue

        track_ids.append(tracks_items[0]["id"])

    return track_ids


def __add_tracks_to_playlist(track_ids, spotify, user_id, playlist_type):
    if not track_ids:
        return None

    date = datetime.utcnow().strftime("%d/%m/%Y")
    playlist_name = f"Best New Music Digest ({playlist_type.capitalize()}) - {date}"
    playlist_response = spotify.user_playlist_create(user_id, playlist_name, public=False)
    playlist_id = playlist_response["id"]
    playlist_url = playlist_response["external_urls"]["spotify"]

    deduplicate_track_ids = []
    for track in track_ids:
        if track not in deduplicate_track_ids:
            deduplicate_track_ids.append(track)

    chunked_track_ids = []
    for i in range(0, len(deduplicate_track_ids), 100):
        chunked_track_ids.append(deduplicate_track_ids[i:i + 100])

    for track_ids_chunk in chunked_track_ids:
        spotify.user_playlist_add_tracks(user_id, playlist_id, track_ids_chunk)

    return playlist_url
