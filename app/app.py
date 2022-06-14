import pytz
import logging
import argparse
from api import YouTubeAPI
from db import VideoDatabase
from search import SearchModel
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler

from logging import config
config.fileConfig('app/conf/logging.conf')

parser = argparse.ArgumentParser("YouTube API Video Fetcher")
parser.add_argument("-q", "--query", type=str, help="Search query", required=True)
parser.add_argument("-t", "--time-interval-minutes", type=int, help="Time interval in minutes", default=10)
parser.add_argument("-m", "--max-results", type=int, help="Max results", default=25)
parser.add_argument("--debug", action="store_true", help="Debug mode")
parser.add_argument("--host", type=str, help="Host", default="0.0.0.0")
parser.add_argument("--port", type=int, help="Port", default=5000)
args = parser.parse_args()

load_dotenv()
app = Flask(__name__)
IST = pytz.timezone("Asia/Kolkata")

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/fetch")
def fetch():
    page_id = request.args.get("page_id", 0)
    try:
        page_id = int(page_id)
    except ValueError:
        logging.error(f"Invalid page id received: {page_id}")
        return jsonify({"error": "Invalid page id received"}), 400

    logging.info(f"Fetching page {page_id}")
    results = api.db.get_paginated_video_results(page_id * api.db.table_page_size, api.db.table_page_size)
    results = {
        "page_id": page_id,
        "next_page_id": page_id + 1,
        "items": results,
    }
    return jsonify(results), 200

@app.route("/search")
def search():
    title_query = request.args.get("title", "")
    description_query = request.args.get("description", "")
    if not title_query and not description_query:
        logging.error("Title and description query both empty")
        return jsonify({"error": "Title and description query both empty"}), 400

    logging.info(f"Searching for videos with title: {title_query} and description: {description_query}")
    query = f"{title_query} {description_query}".strip()
    results = search_model.get_similar_videos(query)
    results = {
        "items": results,
    }
    return jsonify(results), 200

if __name__ == "__main__":
    db = VideoDatabase()
    search_model = SearchModel(db)
    api = YouTubeAPI(args.query, args.time_interval_minutes, db, search_model, args.max_results)
    scheduler = BackgroundScheduler()
    scheduler.add_job(api.fetch_latest_videos, "interval", minutes=args.time_interval_minutes)
    scheduler.start()
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)