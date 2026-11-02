#!/usr/bin/env bash
# Fetch current weather from Open-Meteo (no API key)
set -euo pipefail
LAT="${1:-40.71}"
LON="${2:--74.01}"
LABEL="${3:-}"
URL="https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
if ! command -v curl >/dev/null; then
  echo "curl required" >&2
  exit 1
fi
json=$(curl -fsS "$URL")
if command -v python3 >/dev/null; then
  python3 - "$json" "$LAT" "$LON" "$LABEL" <<'PY'
import json, sys
data = json.loads(sys.argv[1])
lat, lon, label = sys.argv[2], sys.argv[3], sys.argv[4]
c = data["current"]
CODES = {0:"clear",1:"mainly clear",2:"partly cloudy",3:"overcast",45:"fog",61:"rain",71:"snow",95:"thunder"}
place = label or f"{lat},{lon}"
print(f"Weather @ {place}")
print(f"  temp: {c['temperature_2m']}°C")
print(f"  humidity: {c['relative_humidity_2m']}%")
print(f"  wind: {c['wind_speed_10m']} km/h")
print(f"  conditions: {CODES.get(c['weather_code'], 'code '+str(c['weather_code']))}")
PY
else
  echo "$json"
fi
