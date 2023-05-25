#!/bin/sh

export MID_BOTKEY="$1"
export MID_CHANNEL="$2"
export MID_URL="$3"
export MID_ID="$4"
export MID_CODE="$5"

. ./venv/bin/activate
python bot.py
