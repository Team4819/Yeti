#!/bin/bash

set -e
cd `dirname $0`

PYTHONPATH=.. python3 -m coverage run --source yeti -m pytest $@
python -m coverage report -m
