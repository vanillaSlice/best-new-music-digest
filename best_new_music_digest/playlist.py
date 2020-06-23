"""
Playlist helpers.
"""

from datetime import datetime
from difflib import SequenceMatcher

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

        # Try to find album using the artist and album title
        album_id = __get_album_id(
            artist,
            title,
            f"artist:{artist} album:{title}",
            spotify,
            single_match=True,
        )

        # Try to find album using the artist's name under latest releases
        if not album_id:
            album_id = __get_album_id(artist, title, f"artist:{artist} tag:new", spotify)

        # Try to find album using the album title under latest releases
        if not album_id:
            album_id = __get_album_id(artist, title, f"album:{title} tag:new", spotify)

        # Try splitting the artist into multiple artists and searching under latest releases
        if not album_id:
            for artist in artist.split(" & "):
                album_id = __get_album_id(artist, title, f"artist:{artist} tag:new", spotify)
                if album_id:
                    break

        # Give up
        if not album_id:
            continue

        tracks_result = spotify.album_tracks(album_id)

        for track in tracks_result["items"]:
            album_track_ids.append(track["id"])

    return album_track_ids


def __get_album_id(artist, title, query, spotify, single_match=False):
    limit = 1 if single_match else 10
    album_result = spotify.search(q=query, type="album", limit=limit)

    album_items = album_result["albums"]["items"]

    for album_item in album_items:
        if single_match:
            return album_item["id"]

        artist_match = any(__similar_enough(artist, a["name"]) for a in album_item["artists"])
        title_match = __similar_enough(title, album_item["name"])
        if artist_match and title_match:
            return album_item["id"]

    return None


def __similar_enough(str1, str2):
    str1_lower = str1.lower()
    str2_lower = str2.lower()

    return str1_lower in str2_lower or \
           str2_lower in str1_lower or \
           SequenceMatcher(None, str1_lower, str2_lower).ratio() >= 0.75


def __get_track_ids(digest_item, spotify):
    track_ids = []

    for item in digest_item["items"]:
        artist = item["artist"]
        title = item["title"]

        # Try to find track using the artist and track title
        track_id = __get_track_id(
            artist,
            title,
            f"artist:{artist} track:{title}",
            spotify,
            single_match=True,
        )

        # Try to find track using the artist's name under latest releases
        if not track_id:
            track_id = __get_track_id(artist, title, f"artist:{artist} tag:new", spotify)

        # Try to find track using the track title under latest releases
        if not track_id:
            track_id = __get_track_id(artist, title, f"track:{title} tag:new", spotify)

        # Try splitting the artist into multiple artists and searching under latest releases
        if not track_id:
            for artist in artist.split(" & "):
                track_id = __get_track_id(artist, title, f"artist:{artist} tag:new", spotify)
                if track_id:
                    break

        # Give up
        if not track_id:
            continue

        track_ids.append(track_id)

    return track_ids


def __get_track_id(artist, title, query, spotify, single_match=False):
    limit = 1 if single_match else 10
    tracks_result = spotify.search(q=query, type="track", limit=limit)

    tracks_items = tracks_result["tracks"]["items"]

    for track_item in tracks_items:
        if single_match:
            return track_item["id"]

        artist_match = any(__similar_enough(artist, a["name"]) for a in track_item["artists"])
        title_match = __similar_enough(title, track_item["name"])
        if artist_match and title_match:
            return track_item["id"]

    return None


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
