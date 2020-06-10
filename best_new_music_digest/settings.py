"""
Loads application settings.
"""

import os

import dotenv

dotenv.load_dotenv()

def __check_properties_present(properties):
    missing_properties = []

    for prop in properties:
        if prop not in os.environ:
            missing_properties.append(prop)

    if missing_properties:
        raise Exception(f"Missing mandatory properties: {missing_properties}.")

def __get_env_var(prop, default=None):
    return os.environ.get(prop, str(default))

def __get_env_var_bool(prop, default=True):
    return __get_env_var(prop, default).lower() == "true"

def __get_env_var_choice(prop, choices, default):
    choice = __get_env_var(prop, default).lower()
    if choice not in choices:
        raise Exception(f"'{prop}' should be one of: {choices}.")
    return choice

__check_properties_present([
    "MONGODB_URI",
    "RECIPIENT_EMAIL",
    "SENDER_EMAIL",
    "SENDGRID_API_KEY",
    "SENDGRID_TEMPLATE_ID",
])

ALWAYS_EMAIL = __get_env_var_bool("ALWAYS_EMAIL", False)
DAD_JOKE = __get_env_var_bool("DAD_JOKE")
DAY_OF_WEEK_TO_RUN = __get_env_var_choice(
    "DAY_OF_WEEK_TO_RUN",
    choices=[
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    ],
    default="monday").lower()
MONGODB_URI = __get_env_var("MONGODB_URI")
PITCHFORK_ALBUMS = __get_env_var_bool("PITCHFORK_ALBUMS")
PITCHFORK_TRACKS = __get_env_var_bool("PITCHFORK_TRACKS")
RECIPIENT_EMAIL = __get_env_var("RECIPIENT_EMAIL")
SENDER_EMAIL = __get_env_var("SENDER_EMAIL")
SENDER_NAME = __get_env_var("SENDER_NAME", "Best New Music Digest")
SENDGRID_API_KEY = __get_env_var("SENDGRID_API_KEY")
SENDGRID_TEMPLATE_ID = __get_env_var("SENDGRID_TEMPLATE_ID")
SPUTNIKMUSIC_ALBUMS = __get_env_var_bool("SPUTNIKMUSIC_ALBUMS")
THE_NEEDLE_DROP_ALBUMS = __get_env_var_bool("THE_NEEDLE_DROP_ALBUMS")
THE_NEEDLE_DROP_TRACKS = __get_env_var_bool("THE_NEEDLE_DROP_TRACKS")

if THE_NEEDLE_DROP_ALBUMS or THE_NEEDLE_DROP_TRACKS:
    __check_properties_present(["YOUTUBE_API_KEY"])

YOUTUBE_API_KEY = __get_env_var("YOUTUBE_API_KEY")
