CREATE TABLE IF NOT EXISTS CHANNEL(
    _id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS VIDEO(
    _id VARCHAR PRIMARY KEY,
    channel_id VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description VARCHAR,
    video_url VARCHAR NOT NULL,
    thumbnail_url VARCHAR NOT NULL,
    published_at TIMESTAMP NOT NULL,
    vector VARCHAR NOT NULL,
    FOREIGN KEY (channel_id) REFERENCES CHANNEL(_id)
);