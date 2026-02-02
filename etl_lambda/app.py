import json
import os
import time
import random
import urllib.request
import boto3
from datetime import datetime
from urllib.error import HTTPError, URLError

s3 = boto3.client("s3")

# ===============================
# CONFIG (ENV VARS)
# ===============================
RAWG_API_URL = os.environ.get("RAWG_API_URL", "https://api.rawg.io/api/games")
RAWG_API_KEYS = os.environ.get("RAWG_API_KEYS", "").split(",")

BUCKET_NAME = os.environ.get("BUCKET_NAME", "rawg-data-bucket")
SLEEP_BETWEEN_CALLS = float(os.environ.get("SLEEP_BETWEEN_CALLS", "0.2"))


# ===============================
# HELPERS
# ===============================
def get_api_key():
    if not RAWG_API_KEYS or RAWG_API_KEYS == [""]:
        raise RuntimeError("RAWG_API_KEYS not configured")
    return random.choice(RAWG_API_KEYS)


def fetch_games(page: int, page_size: int = 40):
    api_key = get_api_key()
    url = f"{RAWG_API_URL}?key={api_key}&page={page}&page_size={page_size}"

    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def fetch_game_detail(game_id: int):
    api_key = get_api_key()
    url = f"{RAWG_API_URL}/{game_id}?key={api_key}"

    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def save_to_s3(bucket: str, key: str, payload: dict):
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload).encode("utf-8"),
        ContentType="application/json"
    )


# ===============================
# LAMBDA HANDLER
# ===============================
def lambda_handler(event, context):
    page = int(event.get("page", 1))
    page_size = int(event.get("page_size", 40))

    print(f"Fetching RAWG games: page={page}")

    data = fetch_games(page, page_size)
    games = data.get("results", [])

    if not games:
        print("No games found.")
        return {"status": "empty"}

    for g in games:
        game_id = g.get("id")
        if not game_id:
            continue

        try:
            detail = fetch_game_detail(game_id)

            s3_key = (
                f"rawg/games/"
                f"{game_id}_"
                f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
            )

            save_to_s3(BUCKET_NAME, s3_key, detail)

            print(f"Saved game {game_id} to s3://{BUCKET_NAME}/{s3_key}")

            time.sleep(SLEEP_BETWEEN_CALLS)

        except (HTTPError, URLError) as e:
            print(f"Error fetching game {game_id}: {e}")

    return {
        "status": "ok",
        "games_processed": len(games),
        "page": page
    }

