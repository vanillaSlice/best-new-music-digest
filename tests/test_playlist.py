# pylint: disable=import-outside-toplevel, invalid-name, missing-class-docstring, missing-function-docstring, missing-module-docstring, redefined-builtin

from unittest.mock import patch

from freezegun import freeze_time

from tests import helpers


@freeze_time("2020-01-01")
class TestPlaylist(helpers.TestBase):

    def setUp(self):
        super().setUp()

        from best_new_music_digest import playlist
        self.__playlist = playlist

        self.__user_id = "some-user-id"
        self.__playlist_id = "some-playlist_id"

    @patch("best_new_music_digest.playlist.SpotifyOAuth")
    @patch("best_new_music_digest.playlist.spotipy.Spotify")
    def test_create_playlist_disabled(self, spotify, _):
        spotify = spotify()

        self._settings.CREATE_SPOTIFY_PLAYLISTS = False

        self.__playlist.create_playlist([
            self._load_json_test_data("the_needle_drop_albums_output_with_checkpoint.json"),
        ])

        spotify.user_playlist_create.assert_not_called()

    @patch("best_new_music_digest.playlist.SpotifyOAuth")
    @patch("best_new_music_digest.playlist.spotipy.Spotify")
    def test_create_playlist_no_digest_items(self, spotify, _):
        spotify = spotify()

        self.__playlist.create_playlist([])

        spotify.user_playlist_create.assert_not_called()

    @patch("best_new_music_digest.playlist.SpotifyOAuth")
    @patch("best_new_music_digest.playlist.spotipy.Spotify")
    def test_create_playlist_with_albums(self, spotify, _):
        spotify = spotify()

        self.__with_spotify_responses(spotify)

        self.__playlist.create_playlist([
            self._load_json_test_data("pitchfork_albums_output_without_checkpoint.json"),
            self._load_json_test_data("sputnikmusic_albums_output_without_checkpoint.json"),
            self._load_json_test_data("the_needle_drop_albums_output_without_checkpoint.json"),
        ])

        spotify.user_playlist_create.assert_called_with(
            self.__user_id,
            "Best New Music Digest (Albums) - 01/01/2020",
            public=False,
        )

        track_ids = [
            "1EjzcBTVLV7ATtdsQwyV31",
            "5taqLrLouA4vCjM7ZQpEtW",
            "2uxudaBcJamtfgvUjSDdkZ",
            "6tfrMstZ8tw7nZJ6HP0PyW",
            "3tDIjnh6wdwMWDHRHF97XC",
            "2pVvB487ZwqdzTxEvEEors",
            "10vS4ZLi4XWlIsNXSQXgqh",
            "3vrOmd6lTTKXGjaYeq8kni",
            "30gsURaHDTPnDJDINiTCsK",
            "1uE4PBDSPZ0cT4do1bmT7A",
            "1hxVQkhDJN2UnkgeqX68D3",
            "73SBAGI4fPFm4VkB3NjXq8",
            "2pDKE8Q40TDGPl1O11DKKn",
            "4SdubskbLiOkpsIjRVVsya",
            "12WhIX6MvI93bS3wPSStSY",
            "5hnOzmFuGltDDAm008jFDh",
            "17QLp5uadHptxnmq9clK8U",
            "1YsWyCYqpA8uZaR9SfYAnY",
            "0jH0IsCBGackT3RmHBbSUI",
            "2OQpQTRogZ1AhnUHJiT9Nb",
            "7eGoc6UmwiRAVnilTZajNC",
            "5BBWr1LUsCH1tECJLAUGnP",
            "4baGw8dAfqNl7RrmlMtzb5",
            "6VU4Ys4rbbbwJ84g1ZuYA5",
        ]

        spotify.user_playlist_add_tracks.assert_called_with(
            self.__user_id,
            self.__playlist_id,
            track_ids,
        )

    @patch("best_new_music_digest.playlist.SpotifyOAuth")
    @patch("best_new_music_digest.playlist.spotipy.Spotify")
    def test_create_playlist_with_tracks(self, spotify, _):
        spotify = spotify()

        self.__with_spotify_responses(spotify)

        self.__playlist.create_playlist([
            self._load_json_test_data("pitchfork_tracks_output_without_checkpoint.json"),
            self._load_json_test_data("the_needle_drop_tracks_output_without_checkpoint.json"),
        ])

        spotify.user_playlist_create.assert_called_with(
            self.__user_id,
            "Best New Music Digest (Tracks) - 01/01/2020",
            public=False,
        )

        track_ids = [
            "7loXmEHvxWvdvwKzLFAMmc",
            "7vxuYx5faAjfHqAEq2xZGs",
        ]

        spotify.user_playlist_add_tracks.assert_called_with(
            self.__user_id,
            self.__playlist_id,
            track_ids,
        )

    def __with_spotify_responses(self, spotify):
        def get_me_response():
            return {"id": self.__user_id}

        def get_user_playlist_create_response(*_, **_kwargs):
            return {"id": self.__playlist_id}

        def get_search_response(q, type, **_):
            if type == "album":
                if q in ("artist:Run the Jewels album:RTJ4",
                         "artist:Run the Jewels album:Run the Jewels 4"):
                    return self._load_json_test_data("spotify_albums_rtj_response.json")

                if q == "artist:Fiona Apple album:Fetch The Bolt Cutters":
                    return self._load_json_test_data("spotify_albums_fiona_apple_response.json")

                return self._load_json_test_data("spotify_albums_empty_response.json")

            if q == "artist:Blake Mills track:Vanishing Twin":
                return self._load_json_test_data("spotify_track_blake_mills_response.json")

            if q == "artist:slowthai track:Magic":
                return self._load_json_test_data("spotify_track_slowthai_response.json")

            return self._load_json_test_data("spotify_track_empty_response.json")

        def get_album_tracks_response(album_id):
            if album_id == "6cx4GVNs03Pu4ZczRnWiLd":
                return self._load_json_test_data("spotify_tracks_rtj_response.json")

            if album_id == "0fO1KemWL2uCCQmM22iKlj":
                return self._load_json_test_data("spotify_tracks_fiona_apple_response.json")

            return self._load_json_test_data("spotify_track_empty_response.json")

        spotify.me.side_effect = get_me_response
        spotify.user_playlist_create.side_effect = get_user_playlist_create_response
        spotify.search.side_effect = get_search_response
        spotify.album_tracks.side_effect = get_album_tracks_response
