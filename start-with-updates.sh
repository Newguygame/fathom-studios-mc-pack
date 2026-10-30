#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 pi-update-server-mods.py
exec bash ./run.sh nogui
