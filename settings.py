import os

import dotenv

dotenv.load_dotenv()

def __check_properties_present(properties):
    missing_properties = []

    for property in properties:
        if property not in os.environ:
            missing_properties.append(property)

    if missing_properties:
        raise Exception("missing mandatory properties: {}".format(missing_properties))

def __get_env_var(property, default=None):
    return os.environ.get(property, str(default))

def __get_env_var_bool(property, default=True):
    return __get_env_var(property, default).lower() == "true"

__check_properties_present([
    "MONGODB_URI",
    "RECIPIENT_EMAIL",
    "SENDER_EMAIL",
    "SENDER_PASSWORD",
])

MONGODB_URI = __get_env_var("MONGODB_URI")
PITCHFORK_ALBUMS = __get_env_var_bool("PITCHFORK_ALBUMS")
PITCHFORK_TRACKS = __get_env_var_bool("PITCHFORK_TRACKS")
RECIPIENT_EMAIL = __get_env_var("RECIPIENT_EMAIL")
SENDER_EMAIL = __get_env_var("SENDER_EMAIL")
SENDER_NAME = __get_env_var("SENDER_NAME", "Best New Music Digest")
SENDER_PASSWORD = __get_env_var("SENDER_PASSWORD")
SPUTNIKMUSIC_ALBUMS = __get_env_var_bool("SPUTNIKMUSIC_ALBUMS")
THE_NEEDLE_DROP_ALBUMS = __get_env_var_bool("THE_NEEDLE_DROP_ALBUMS")
THE_NEEDLE_DROP_TRACKS = __get_env_var_bool("THE_NEEDLE_DROP_TRACKS")

if THE_NEEDLE_DROP_ALBUMS or THE_NEEDLE_DROP_TRACKS:
   __check_properties_present(["YOUTUBE_API_KEY"])

YOUTUBE_API_KEY = __get_env_var("YOUTUBE_API_KEY")
