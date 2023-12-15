create database ThriftMe;
-- Store User information
-- Most important table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    profile_picture TEXT,
    public_access BOOLEAN NOT NULL
);

alter table Users alter column profile_picture type text
-- RUN THIS TO CHANGE TABLE ON LOCAL

--Stores photos for posts
--allows different types of posts to have more than 1 photo
CREATE TABLE albums (
    album_id SERIAL PRIMARY KEY,
    user_id INT,
    album_name VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);



-- Table to store photos
--Albums will rely on this table
-- Run the following commands to fix your local DB:
-- ALTER TABLE photos DROP COLUMN photo_data DROP COLUMN photo_mimetype;
-- ALTER TABLE photos ADD COLUMN photo_url TEXT;
CREATE TABLE photos (
    photo_id SERIAL PRIMARY KEY,
    album_id INT,
    photo_url TEXT,
    FOREIGN KEY (album_id) REFERENCES albums(album_id) ON DELETE CASCADE
);

-- Posts Created by users and holds text
--References album
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    user_id INT,
    post_content TEXT,
    album_id INT,
    post_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES albums(album_id) ON DELETE SET NULL
);

-- Holds an album of photos for listings
-- Store albums for posts and price information
CREATE TABLE listings (
    listing_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    album_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES albums(album_id) ON DELETE SET NULL
);

--forgot to add photos to listings lol PLEASE RUN THIS
ALTER TABLE listings
ADD COLUMN album_id INT,
ADD FOREIGN KEY (album_id) REFERENCES albums(album_id) ON DELETE SET NULL;


-- Represents community posts that can reference albums and a reference to listings if needed
CREATE TABLE community_posts (
    community_post_id SERIAL PRIMARY KEY,
    user_id INT,
    post_content TEXT,
    album_id INT,
    listing_id INT,
    post_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES albums(album_id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id) ON DELETE CASCADE
);

-- Relationship between users and followers
CREATE TABLE followers (
    user_id INT, 
    follower_id INT,
    PRIMARY KEY (user_id, follower_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE
);


-- Different likes tables across posts for easier queries

-- Relationship between users and posts
CREATE TABLE likes (
    user_id INT,
    post_id INT,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

-- Relationship between users and community posts allowing users to like community posts
CREATE TABLE community_post_likes (
    user_id INT,
    community_post_id INT,
    PRIMARY KEY (user_id, community_post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (community_post_id) REFERENCES community_posts(community_post_id) ON DELETE CASCADE
);

-- Likes between users and listings
CREATE TABLE listing_likes (
    user_id INT,
    listing_id INT,
    PRIMARY KEY (user_id, listing_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id) ON DELETE CASCADE
);



---Separate comments tables for easier queries
-- Comments on posts
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    user_id INT,
    post_id INT,
    comment_content TEXT,
    comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE
);

-- Comments on community posts
CREATE TABLE community_post_comments (
    comment_id SERIAL PRIMARY KEY,
    user_id INT,
    community_post_id INT,
    comment_content TEXT,
    comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (community_post_id) REFERENCES community_posts(community_post_id) ON DELETE CASCADE
);

-- Comments on listings
CREATE TABLE listing_comments (
    comment_id SERIAL PRIMARY KEY,
    user_id INT,
    listing_id INT,
    comment_content TEXT,
    comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id) ON DELETE CASCADE
);

INSERT INTO users (username, password, email, profile_picture, public_access)
VALUES
    ('real_person', 'password1', 'user1@example.com', E'\\x89504e470d0a1a0a', true), -- Hexadecimal representation of a profile picture
    ('real_shopper', 'password2', 'user2@example.com', E'\\x89504e470d0a1a0a', true),
    ('real_person_community', 'password3', 'user3@example.com', E'\\x89504e470d0a1a0a', true);
