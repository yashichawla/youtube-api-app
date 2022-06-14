import os
import pytz
import json
import datetime
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()
IST = pytz.timezone("Asia/Kolkata")


class VideoDatabase:
    def __init__(self):
        """
        Initialize the database connection and create the tables if they do not exist
        """
        DATABASE_URL = os.environ.get("DATABASE_URL")
        self.base = declarative_base()
        self.engine = create_engine(DATABASE_URL)
        self.metadata = MetaData()

        # obtain database connection
        while True:
            try:
                self.connection = self.engine.connect()
                self.Session = sessionmaker(bind=self.engine)
                self.session = self.Session()
                self.connection.execute("SELECT 1")
                logging.debug(f"Database connection established: {self}")
            except Exception as e:
                logging.error(f"Exception while connecting to database: {e}")
                continue
            else:
                break

        # setup tables
        self.setup_tables()
        self.table_page_size = 10

        # obtain table objects
        self.video_table = Table(
            "video", self.metadata, autoload=True, autoload_with=self.engine
        )

        self.channel_table = Table(
            "channel", self.metadata, autoload=True, autoload_with=self.engine
        )

    def setup_tables(self):
        """
        Create the tables if they do not exist
        """
        with open("app/conf/setup_db.sql") as f:
            # obtain each table creation query and execute it
            queries = f.read().strip().split("\n\n")
            for query in queries:
                try:
                    self.connection.execute(query)
                except Exception as e:
                    logging.error(f"Exception while executing query: {query}: {e}")

    def check_video_id_in_db(self, _id):
        """
        Check if the video with the given id exists in the database
        """
        query = self.video_table.select().where(self.video_table.c._id == _id)
        result = self.connection.execute(query)
        return result.rowcount > 0

    def check_channel_id_in_db(self, _id):
        """
        Check if the channel with the given id exists in the database
        """
        query = self.channel_table.select().where(self.channel_table.c._id == _id)
        result = self.connection.execute(query)
        return result.rowcount > 0

    def add_video(
        self,
        _id,
        channel_id,
        title,
        description,
        video_url,
        thumbnail_url,
        published_at,
        vector,
    ):
        """
        Add a video to the database
        """

        # check video id in database
        if self.check_video_id_in_db(_id):
            logging.error(f"Video with id {_id} already exists")
            return

        # insert video
        query = self.video_table.insert().values(
            _id=_id,
            channel_id=channel_id,
            title=title,
            description=description,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            published_at=published_at,
            vector=vector,
        )
        try:
            self.connection.execute(query)
        except Exception as e:
            logging.error(f"Exception while executing query: {query}: {e}")

    def add_channel(self, _id, title):
        """
        Add a channel to the database
        """

        # check channel id in database
        if self.check_channel_id_in_db(_id):
            logging.error(f"Channel with id {_id} already exists")
            return

        # insert channel
        query = self.channel_table.insert().values(_id=_id, title=title)
        try:
            self.connection.execute(query)
        except Exception as e:
            logging.error(f"Exception while executing query: {query}: {e}")

    def get_paginated_video_results(self, offset, limit):
        """
        Get paginated results of videos
        offset - starting index of the results
        limit - number of results to return
        """
        query = (
            self.video_table.select()
            .order_by(self.video_table.c.published_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = self.connection.execute(query)
        data = list()
        for row in result:
            item = {
                "_id": row._id,
                "channel_id": row.channel_id,
                "title": row.title,
                "description": row.description,
                "video_url": row.video_url,
                "thumbnail_url": row.thumbnail_url,
                "published_at": datetime.datetime.strftime(
                    row.published_at, "%Y-%m-%dT%H:%M:%SZ"
                ),
            }
            data.append(item)
        return data

    def get_video_vectors(self):
        """
        Return the vectors of all the videos in the database
        """
        query = self.video_table.select()
        result = self.connection.execute(query)
        data = list()
        for row in result:
            item = {"_id": row._id, "vector": json.loads(row.vector)}
            data.append(item)
        return data

    def get_video_details_by_id(self, _id):
        """
        Return the details of the video with the given id
        """
        query = self.video_table.select().where(self.video_table.c._id == _id)
        result = self.connection.execute(query)
        for row in result:
            item = {
                "_id": row._id,
                "channel_id": row.channel_id,
                "title": row.title,
                "description": row.description,
                "video_url": row.video_url,
                "thumbnail_url": row.thumbnail_url,
                "published_at": datetime.datetime.strftime(
                    row.published_at, "%Y-%m-%dT%H:%M:%SZ"
                ),
            }
        return item
