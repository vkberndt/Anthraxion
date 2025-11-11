import os
import json
import base64

# Use environment variables for all secrets.
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID", "0"))
STAFF_ROLE_ID = int(os.environ.get("STAFF_ROLE_ID", "0"))

GSHEET_NAME = os.environ.get("GSHEET_NAME")           # "ANTHRAX - Infractions"
GSHEET_TAB = os.environ.get("GSHEET_TAB")             # "Anthraxions"

# Credentials strategy A: direct JSON text in GOOGLE_CREDENTIALS_JSON
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")

# Credentials strategy B: base64-encoded JSON in GOOGLE_CREDENTIALS_B64
GOOGLE_CREDENTIALS_B64 = os.environ.get("GOOGLE_CREDENTIALS_B64")

def load_google_credentials_dict():
    # I prefer to support both strategies so deployment has options.
    if GOOGLE_CREDENTIALS_JSON:
        return json.loads(GOOGLE_CREDENTIALS_JSON)
    if GOOGLE_CREDENTIALS_B64:
        decoded = base64.b64decode(GOOGLE_CREDENTIALS_B64)
        return json.loads(decoded)
    raise RuntimeError("Google credentials not provided. Set GOOGLE_CREDENTIALS_JSON or GOOGLE_CREDENTIALS_B64.")