#!/usr/bin/env bash

cat ../events.ndjson | SCARF_AUTH_TOKEN=$SCARF_AUTH_TOKEN SCARF_NAME=$SCARF_NAME python3 import.py
