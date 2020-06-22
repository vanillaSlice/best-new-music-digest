#!/usr/bin/env python3

"""
Run the application.
"""

import logging

from best_new_music_digest import app

if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        logging.error(e)
