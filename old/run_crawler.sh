#!/bin/bash

# Activate virtual environment and run crawler
cd "$(dirname "$0")"
source venv/bin/activate
python yellowpages_full_crawler.py