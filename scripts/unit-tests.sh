#!/usr/bin/env bash

set -e

cd $(dirname $0)/..

pytest tests/ --cov=best_new_music_digest --cov-report=term-missing --cov-fail-under=100
