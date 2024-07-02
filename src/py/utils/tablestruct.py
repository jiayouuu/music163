comments_sql = """
CREATE TABLE IF NOT EXISTS `{name}` (
    comment_id varchar(30) PRIMARY KEY,
    comment_content VARCHAR(255),
    comment_time INT,
    user_id varchar(30),
    location VARCHAR(20),
    platform VARCHAR(20),
    nickname VARCHAR(30),
    birthday INT,
    gender ENUM('female','male'),
    city_code INT,
    keyword VARCHAR(255),
    emotion FLOAT
);
"""
songs_sql = """
CREATE TABLE IF NOT EXISTS `{name}` (
    song_id varchar(30) PRIMARY KEY,
    song_name VARCHAR(255),
    update_time INT DEFAULT 0,
    is_completed TINYINT(1) DEFAULT 1,
    comment_hour_minute TEXT,
    location TEXT,
    platform varchar(255),
    generation varchar(255),
    gender varchar(255),
    keywords MEDIUMTEXT,
    emotion TEXT   
);
"""