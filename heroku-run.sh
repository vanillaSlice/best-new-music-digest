#!/usr/bin/env bash

echo ${SPOTIFY_CACHE} > .cache-${SPOTIFY_USERNAME}

python run.py