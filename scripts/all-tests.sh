#!/usr/bin/env bash

set -e

cd $(dirname $0)

./lint.sh
./unit-tests.sh
