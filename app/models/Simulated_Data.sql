
--test if cascade works -> it works
--dangerous query
DELETE from users; --delete all users and their associated tables
ALTER SEQUENCE users_user_id_seq RESTART WITH 1; -- reset the sequence
ALTER SEQUENCE photos_photo_id_seq RESTART WITH 1;
ALTER SEQUENCE albums_album_id_seq RESTART WITH 1;
ALTER SEQUENCE community_posts_community_post_id_seq RESTART WITH 1;


--Dummy users for test data
INSERT INTO users (username, password, email, profile_picture, public_access)
VALUES
    ('real_person', 'password1', 'user1@example.com', E'\\x89504e470d0a1a0a', true), -- Hexadecimal representation of a profile picture
    ('real_shopper', 'password2', 'user2@example.com', E'\\x89504e470d0a1a0a', true),
    ('real_person_community', 'password3', 'user3@example.com', E'\\x89504e470d0a1a0a', true);

select * from users; -- check if the data is cleared
select * from community_posts;
select * from photos;
select * from albums;


-- Verify the inserted community posts
SELECT * FROM community_posts;


delete from community_posts;
select * from photos;
select * from albums;


--translate this to SQLAlchemy later > done

SELECT
    cp.post_content,
    cp.post_date,
    p.photo_url
FROM
    community_posts cp
JOIN
    albums a ON cp.album_id = a.album_id
LEFT JOIN
    photos p ON a.album_id = p.album_id;


-- TEST SCRIPT generate 50 user post with all dummy users interacting with them
-- Basically a giant do-while loop
-- Insert 50 community posts owned by 'real_person_community'
DO $$
DECLARE
    userId INT;
    communityPostId INT;
    albumId INT;
    photoId INT;
    counter INT;
BEGIN
    -- Get the user_id for 'real_person_community'
    SELECT user_id INTO userId FROM users WHERE username = 'real_person_community';

    -- Loop to create 50 community posts
    counter := 1;

    WHILE counter <= 10
    LOOP
        -- Insert community post
        INSERT INTO community_posts (user_id, post_content, post_date)
        VALUES (userId, 'Community Post Content ' || counter, CURRENT_TIMESTAMP)
        RETURNING community_post_id INTO communityPostId;

        -- Insert an album for the community post
        INSERT INTO albums (user_id, album_name)
        VALUES (userId, 'Community Post Album ' || counter)
        RETURNING album_id INTO albumId;

        -- Insert a photo for the album
        INSERT INTO photos (album_id, photo_url)
        VALUES (albumId, CASE WHEN counter % 3 = 1 THEN '/static/images/ThriftMe_logo.png'  -- ThriftMe_logo.png
                             WHEN counter % 3 = 2 THEN '/static/images/profileTemp.png'  -- callus.png
                             ELSE '/static/images/callus.png' END)
        RETURNING photo_id INTO photoId;

        -- Update the album_id for the community post
        UPDATE community_posts SET album_id = albumId WHERE community_post_id = communityPostId;

        -- Update the listing_id for the community post
        UPDATE community_posts SET listing_id = NULL WHERE community_post_id = communityPostId;

        -- Insert likes and comments for 'real_person' and 'real_shopper'
        INSERT INTO community_post_likes (user_id, community_post_id) VALUES
            ((SELECT user_id FROM users WHERE username = 'real_person'), communityPostId),
            ((SELECT user_id FROM users WHERE username = 'real_shopper'), communityPostId);

        INSERT INTO community_post_comments (user_id, community_post_id, comment_content, comment_date) VALUES
            ((SELECT user_id FROM users WHERE username = 'real_person'), communityPostId, 'Nice post!', CURRENT_TIMESTAMP),
            ((SELECT user_id FROM users WHERE username = 'real_shopper'), communityPostId, 'Great content!', CURRENT_TIMESTAMP);

        counter := counter + 1;
    END LOOP;
END $$;

SELECT
    cp.community_post_id,
    cp.post_content,
    cp.post_date,
    cpc.comment_content,
    COUNT(cpl.user_id) AS like_count,
    ph.photo_url
FROM
    community_posts cp
JOIN
    community_post_comments cpc ON cp.community_post_id = cpc.community_post_id
LEFT JOIN
    community_post_likes cpl ON cp.community_post_id = cpl.community_post_id
LEFT JOIN
    albums alb ON cp.album_id = alb.album_id
LEFT JOIN
    photos ph ON alb.album_id = ph.album_id
WHERE
    cp.community_post_id = :community_post_id -- Replace with the desired community_post_id
GROUP BY
    cp.community_post_id, cp.post_content, cp.post_date, cpc.comment_content, ph.photo_url;


select * from community_posts;
select * from albums;
select * from photos;