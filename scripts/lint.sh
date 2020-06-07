#!/usr/bin/env bash

set -e

cd $(dirname $0)/..

pylint best_new_music_digest/ tests/
