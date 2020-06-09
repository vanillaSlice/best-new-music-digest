# pylint: disable=bare-except

"""
Dad jokes.
"""

import requests


def get_dad_joke():
    """
    Returns a dad joke.
    """

    try:
        return requests.get("https://icanhazdadjoke.com/",
                            headers={"Accept": "application/json"}).json()["joke"]
    except:
        return "It would seem that I've run out of dad jokes. I hope you're happy now 😞."
