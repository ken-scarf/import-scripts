#!/usr/bin/env bash

cat ./events.ndjson.gz | SCARF_AUTH_TOKEN=<token> python3 import.py
