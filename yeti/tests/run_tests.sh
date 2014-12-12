#!/bin/bash

set -e

PYTHONPATH=yeti python3 -m pytest --cov yeti
python -m coverage report -m
