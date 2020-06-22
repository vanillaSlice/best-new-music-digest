#!/usr/bin/env bash

echo ${SPOTIFY_CACHE} > .cache-${SPOTIFY_USERNAME}

cat .cache-${SPOTIFY_USERNAME}

python run.py
