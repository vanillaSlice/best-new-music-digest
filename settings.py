import os

import dotenv

dotenv.load_dotenv()

__MANDATORY_PROPERTIES = [
    "MONGODB_URI",
    "RECIPIENT_EMAIL",
    "SENDER_EMAIL",
    "SENDER_PASSWORD",
    "YOUTUBE_API_KEY",
]

__missing_properties = []

for property in __MANDATORY_PROPERTIES:
    if property not in os.environ:
        __missing_properties.append(property)

if __missing_properties:
    raise Exception("missing mandatory properties: {}".format(__missing_properties))

MONGODB_URI = os.environ["MONGODB_URI"]
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]
SENDER_NAME = os.environ.get("SENDER_NAME", "Best New Music Digest")
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]
YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
