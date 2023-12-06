create database ThriftMe;
-- Store User information
-- Most important table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    profile_picture BYTEA,
    public_access BOOLEAN NOT NULL
);

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

-- Sample Queries Feel free to add more "dummy" data to test more queries
-- Insert dummy data for three users
INSERT INTO users (username, password, email, profile_picture, public_access)
VALUES
    ('real_person', 'password1', 'user1@example.com', E'\\x89504e470d0a1a0a', true), -- Hexadecimal representation of a profile picture
    ('real_shopper', 'password2', 'user2@example.com', E'\\x89504e470d0a1a0a', true),
    ('real_person_community', 'password3', 'user3@example.com', E'\\x89504e470d0a1a0a', true);

select * from users;

INSERT INTO albums (user_id, album_name)
VALUES (1, 'Averys Post Album');


select * from albums;

INSERT INTO posts (user_id, post_content, album_id)
VALUES (1, 'This is the first users post!', 1);


select * from posts;

INSERT INTO photos (album_id, photo_data)
VALUES (1, E'\\x89504E470D0A1A0A0000000D49484452');

select * from photos;


INSERT INTO likes (user_id, post_id)
VALUES (2, 1);

-- User 3 likes the first user's post
INSERT INTO likes (user_id, post_id)
VALUES (3, 1);

select * from likes;

INSERT INTO comments (user_id, post_id, comment_content)
VALUES (2, 1, 'Great post!');

INSERT INTO comments (user_id, post_id, comment_content)
VALUES (3, 1, 'Awesome!');


--delete records because i messed up

delete from comments
where comment_id in(
select comment_id
from comments order by
comment_id desc
limit 2
);

--query to get comments from a post
select comment_content from comments
left join posts p on comments.post_id = p.post_id
where p.user_id != comment_id;

-- query to get a generic post with its content
select count(l.user_id), post_content,photo_data from posts
inner join likes l on posts.post_id = l.post_id
inner join photos p on posts.album_id = p.album_id
where posts.user_id = :user_id
group by post_content, photo_data, posts.album_id;

--query to get a single post, a caption, and its photo content
SELECT
    COUNT(l.user_id) AS like_count,
    posts.post_content,
    photo_data
FROM
    posts
INNER JOIN
    likes l ON posts.post_id = l.post_id
INNER JOIN
    photos p ON posts.album_id = p.album_id
WHERE
    posts.user_id = :user_id
GROUP BY
    posts.post_content,
    photo_data,
    posts.album_id;


--Query to get a "Timeline" of posts in chronological order
SELECT
    posts.post_id,
    posts.post_content,
    posts.post_date,
    COUNT(likes.user_id) AS like_count
FROM
    posts
LEFT JOIN
    likes ON posts.post_id = likes.post_id
WHERE
    posts.user_id = :user_id
GROUP BY
    posts.post_id, posts.post_content, posts.post_date
ORDER BY
    posts.post_date DESC;


--get a timeline of posts from
SELECT
    posts.post_id,
    posts.post_content,
    posts.post_date,
    COUNT(likes.user_id) AS like_count
FROM
    posts
JOIN
    followers ON posts.user_id = followers.user_id --get posts from accounts that the user follows
LEFT JOIN
    likes ON posts.post_id = likes.post_id
WHERE
    followers.follower_id = :user_id
GROUP BY
    posts.post_id, posts.post_content, posts.post_date
ORDER BY
    posts.post_date DESC;


-- --test if cascade works -> it works
-- --dangerous query
-- DELETE from users; --delete all users and their associated tables
-- ALTER SEQUENCE users_user_id_seq RESTART WITH 1; -- reset the sequence
--
-- select * from users; -- check if the data is cleared