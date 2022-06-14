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

config.fileConfig("app/conf/logging.conf")

parser = argparse.ArgumentParser("YouTube API Video Fetcher")
parser.add_argument("--query", type=str, help="Search query", required=True)
parser.add_argument(
    "--time-interval-minutes",
    help="Time interval in minutes",
    default=10,
)
parser.add_argument("--max-results", help="Max results", default=25)
parser.add_argument("--debug", action="store_true", help="Debug mode")
parser.add_argument("--host", help="Host", default="0.0.0.0")
parser.add_argument("--port", help="Port", default=5000)
args = parser.parse_args()

load_dotenv()
app = Flask(__name__)
IST = pytz.timezone("Asia/Kolkata")


def parse_arguments():
    """
    Parse arguments from the command line
    """
    global args

    # assign host to default if no value or null string is passed
    args.host = (
        "0.0.0.0"
        if (args.host is not None and isinstance(args.host, str) and not args.host)
        else args.host
    )

    # assign query to default if no value or null string is passed
    args.query = (
        "fampay"
        if (args.query is not None and isinstance(args.query, str) and not args.query)
        else args.query
    )

    # assign port to default if no value or null string is passed
    try:
        if args.port is not None and isinstance(args.port, str) and not args.port:
            args.port = 5000
        else:
            args.port = int(args.port)
    except ValueError:
        args.port = 5000

    # assign time interval to default if no value or null string is passed
    try:
        if (
            args.time_interval_minutes is not None
            and isinstance(args.time_interval_minutes, str)
            and not args.time_interval_minutes
        ):
            args.time_interval_minutes = 10
        else:
            args.time_interval_minutes = int(args.time_interval_minutes)
    except ValueError:
        args.time_interval_minutes = 10

    # assign max results to default if no value or null string is passed
    try:
        if (
            args.max_results is not None
            and isinstance(args.max_results, str)
            and not args.max_results
        ):
            args.max_results = 25
        else:
            args.max_results = int(args.max_results)
    except ValueError:
        args.max_results = 25


@app.route("/")
def index():
    """
    Default home page
    """
    return "Hello, World!"


@app.route("/fetch")
def fetch():
    """
    Fetch results from database for a given page
    """
    page_id = request.args.get("page_id", 0)
    try:
        # check if page_id is an integer
        page_id = int(page_id)
    except ValueError:
        logging.error(f"Invalid page id received: {page_id}")
        return jsonify({"error": "Invalid page id received"}), 400

    logging.info(f"Fetching page {page_id}")

    # obtain the current page and the next page and return
    results = api.db.get_paginated_video_results(
        page_id * api.db.table_page_size, api.db.table_page_size
    )
    next_results = api.db.get_paginated_video_results(
        (page_id + 1) * api.db.table_page_size, api.db.table_page_size
    )

    results = {
        "page_id": page_id,
        "next_page_id": page_id + 1 if next_results else None,
        "items": results,
    }
    return jsonify(results), 200


@app.route("/search")
def search():
    """
    Search for videos in the database relevant to a search query
    """
    title_query = request.args.get("title", "")
    description_query = request.args.get("description", "")

    # check if either title or description is set
    if not title_query and not description_query:
        logging.error("Title and description query both empty")
        return jsonify({"error": "Title and description query both empty"}), 400

    logging.info(
        f"Searching for videos with title: {title_query} and description: {description_query}"
    )
    query = f"{title_query} {description_query}".strip()

    # find most similar results and return
    results = search_model.get_similar_videos(query)
    results = {
        "items": results,
    }
    return jsonify(results), 200


if __name__ == "__main__":
    """
    Entry point of the application
    """
    parse_arguments()
    logging.debug(args)
    logging.info(f"Starting YouTube API Video Fetcher")
    logging.info(
        f"Retrieving new videos for '{args.query}' every {args.time_interval_minutes} minutes"
    )

    # initialize the database, search model and API
    db = VideoDatabase()
    search_model = SearchModel(db)
    api = YouTubeAPI(
        args.query, args.time_interval_minutes, db, search_model, args.max_results
    )

    # initialize the scheduler and start the job
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        api.fetch_latest_videos, "interval", minutes=args.time_interval_minutes
    )
    scheduler.start()

    # run the application
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)
