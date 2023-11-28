from ..database import db
import random,binascii,os
#TODO make classes for the other tables

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

    

    #Constructor that creates the "User"
    def __init__(self,email: str, password: str) -> None:
        self.email = email
        self.password = password
        self.public_access = True
        #can omit later since there is no logic to create a username or uplad profile picture right now
        self.username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(5,20)))
        self.profile_picture = binascii.b2a_base64(os.urandom(17))
        
    
    def get_username(self):
        return self.username
    
    def get_id(self):
        return self.user_id
    
    #simple lookup using query id, returns none if not in db
    def get_by_username(username):
        
        return Users.query.filter_by(username=username).first()

    
    
    ##test code to see if user is created
    def __str__(self) -> str:
        return (f"user_id: {self.user_id}\n"
                f"username: {self.username}\n"
                f"email: {self.email}\n"
                f"public access: {self.public_access}\n"
                f"profile picture: {self.profile_picture}")




"""
Album stores refrences to photos 
[One User] -> [Many albums(posts)]
[One album] -> [Many photos]
"""
    
class Album(db.Model):
    __tablename__ = 'albums'

    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    album_name = db.Column(db.String(100), nullable=False)




"""
Table to store many photos 
[album] -> [photo(s)]
"""
class Photo(db.Model):
    __tablename__ = 'photos'

    photo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id', ondelete='CASCADE'), nullable=False)
    photo_data = db.Column(db.LargeBinary)



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



