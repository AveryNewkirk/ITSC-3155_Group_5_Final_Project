from ast import alias
import mimetypes
from turtle import back
from typing import Optional
from ..database import db
import random, binascii, os
#TODO make classes for the other tables



##User session object used to store variables related to the users privlages and behavior
class UserSession():
    def __init__(self, username):
        self.username = username
        community_request_limit = 20
        #can add other limits and behaviors if needed


"""
User class that makes people able to login to the app
Also serves as a central hub to all other tables
This establishes user activities such as liking posts, commenting ect.
[user] -> [every other table]
"""
class Users(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.LargeBinary)
    public_access = db.Column(db.Boolean, nullable=False)

    

    #Constructor that creates dummy user 
    # def __init__(self,email: str, password: str) -> None:
    #     self.email = email
    #     self.password = password
    #     self.public_access = True
    #     #can omit later since there is no logic to create a username or uplad profile picture right now
    #     self.username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(5,20)))
    #     self.profile_picture = binascii.b2a_base64(os.urandom(17))
    
    
    def __init__(self,username,email,pw_hash):
        self.username = username
        self.email = email 
        self.password = pw_hash
        self.public_access = True
    
    def get_username(self):
        return self.username
    
    def get_id(self):
        return self.user_id
    
    #simple lookup using query id, returns none if not in db
    def get_by_username(self, username):
        
        usr_instance = Users.query.filter_by(username=username).first()
        return usr_instance 

    
    
    ##test code to see if user is created
    def __str__(self) -> str:
        return (f"user_id: {self.user_id}\n"
                f"username: {self.username}\n"
                f"email: {self.email}\n"
                f"public access: {self.public_access}\n"
                f"profile picture: {self.profile_picture}")

class Listing(db.Model):
    __tablename__ = 'listings'
    
    # Fields
    listing_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description =  db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    user = db.relationship('Users', backref='listings')
    album = db.relationship('Album', backref='listing', uselist=False)
    
    # Constructor
    def __init__(self, title: str, description: str, price: float, user_id: int, album_id: Optional[int] = None):
        self.title = title
        self.description = description
        self.price = price 
        self.user_id = user_id
        self.album_id = album_id

    # Object as string
    def __str__(self) -> str:
        return(
            f"title: {self.title}\n"
            f"description: {self.description}\n"
            f"price: {self.price}\n"
            f"user_id: {self.user_id}\n"
            f"album_id: {self.album_id}\n"
        )


"""
Album stores refrences to photos 
[One User] -> [Many albums(posts)]
[One album] -> [Many photos]
"""
    
class Album(db.Model):
    __tablename__ = 'albums'

    # Fields
    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    album_name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    photos = db.relationship('Photo', backref='album', lazy=True)
    
    def __init__(self, user_id: int, album_name: Optional[str] = None):
        self.user_id = user_id
        self.album_name = album_name




"""
Table to store many photos 
[album] -> [photo(s)]
"""
class Photo(db.Model):
    __tablename__ = 'photos'

    # Fields
    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id', ondelete='CASCADE'), nullable=False)
    photo_url = db.Column(db.Text)
    
    def __init__(self, album_id: int, photo_url: str):
        self.album_id = album_id
        self.photo_url = photo_url



"""
each post is assocated with one user and one album
the album stores the photo(s) in the post

[user] -> [post(s)] -> [album] -> [photo(s)]

"""
class Post(db.Model):
    __tablename__ = 'posts'

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    post_content = db.Column(db.Text)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id', ondelete='SET NULL'))


"""
model to define comments 
one post can have many comments 

[post] -> [comment(s)]
"""

class Comment(db.Model):
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'))
    comment_content = db.Column(db.Text)
    comment_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())


"""
Likes is a junction table that represents the relatinship between 
users and posts. This allows users to like multiple posts. 
[user(s)] <-> [like] <-> [post(s)]
"""
likes = db.Table(
    'likes', 
    db.Column('user_id',db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    db.Column('post_id',db.Integer, db.ForeignKey('posts.post_id', ondelete='CASCADE'), primary_key=True)
)


"""
Followers is a junction table that represents the relationship between 
users and followers.
[users(s)] <-> [follower(s)]
"""

followers = db.Table(
    'followers',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    db.Column('follower_id', db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
)






"""
TODO Implement the listing and community models and tables
"""



