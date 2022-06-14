import os
import json
import requests
import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

class YouTubeAPI:
    def __init__(self, search_query, time_interval_minutes, db, search_model, max_results=25):
        self.search_query = search_query
        self.time_interval_minutes = time_interval_minutes
        self.max_results = max_results
        self.db = db
        self.search_model = search_model
        self.API_KEY = os.environ.get("YOUTUBE_API_KEY")
        self.YOUTUBE_ENDPOINT = "https://youtube.googleapis.com/youtube/v3/search"

    def get_videos_from_query(self, query, published_after):
        if not isinstance(published_after, str):
            published_after = published_after.strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "part": "snippet",
            "q": query,
            "key": self.API_KEY,
            "maxResults": self.max_results,
            "order": "date",
            "type": "video",
            "publishedAfter": published_after
        }
        response = requests.get(self.YOUTUBE_ENDPOINT, params=params)
        return response.json()

    def fetch_latest_videos(self, query=None):
        query = query if query is not None else self.search_query
        current_time = datetime.datetime.utcnow()
        last_interval_time = current_time - datetime.timedelta(minutes=self.time_interval_minutes)
        last_interval_time_string = last_interval_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        logging.info(f"Fetching videos for {query} from {last_interval_time_string} to {current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        try:
            results = self.get_videos_from_query(query, last_interval_time_string)
            logging.debug(results)
            for video_result in results["items"]:
                try:
                    _id = video_result["id"]["videoId"]
                    publish_time = video_result["snippet"]["publishedAt"]
                    channel_id = video_result["snippet"]["channelId"]
                    title = video_result["snippet"]["title"]
                    description = video_result["snippet"]["description"]
                    video_url = f"https://www.youtube.com/watch?v={_id}"
                    thumbnail_url = video_result["snippet"]["thumbnails"]["high"]["url"]
                    channel_title = video_result["snippet"]["channelTitle"]
                    vector = self.search_model.vectorize_text(f"{title} {description}")
                    vector_text = json.dumps(vector.tolist())

                    publish_time_datetime = datetime.datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%SZ")
                    if publish_time_datetime >= last_interval_time:
                        self.db.add_channel(channel_id, channel_title)
                        self.db.add_video(_id, channel_id, title, description, video_url, thumbnail_url, publish_time, vector_text)

                except Exception as e:
                    logging.error(f"Exception while parsing video result: {e}")
        except Exception as e:
            logging.error(f"Exception while fetching videos: {e}")