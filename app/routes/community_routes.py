from flask import Blueprint, render_template, request,session,redirect,jsonify,url_for,abort
from sqlalchemy import desc,func,exists
import pickle
from ..models.pipeline import *
from ..utils import upload_file


community = Blueprint('community', __name__,template_folder='templates',static_folder='static')


batch_limit = 6 #a multiple of 3 per batch is ideal since the community page will generate 3x3 grids at a time
page_num = 1 #start at one for the page number then increment on each request
total_limit = 36

#generate posts from database is kind of janky but works well enough
def generate_data():
    global page_num
    ## offset to increment the query for the posts is a bit unstable
    offset = (page_num - 1) * batch_limit
    page_num += 1    
    community_data = session.get('community_data')
    
    #check for problematic comunity data
    if community_data is None:
        print('problematic')
        return
    
    ##Query to get just the post content, date, and photo_url
    temp = (db.session.query(
        CommunityPost.post_content,
        CommunityPost.community_post_id,
        Photo.photo_url
    )
    .join(Album, CommunityPost.album_id == Album.album_id)
    .join(Photo, Album.album_id == Photo.album_id)
    .order_by(desc(CommunityPost.community_post_id))
    .offset(offset).limit(batch_limit)
    .all()
    )
    
    #cast to tuples to avoid JSON errors 
    processed_temp = ([tuple(row) for row in temp if not(row is None)])


    #add the batch of posts to the total amount of posts the user has generated
    community_data.extend((processed_temp))

    #test byte length if too many end up in the cookie data everything gets deleted
    byte_length = len(pickle.dumps(community_data))
    print(byte_length)

    #IMPORTANT update the session data
    session['community_data'] = sorted(list(set(community_data)), reverse=True)

    #return the batch when ONLY when below the limit
    return processed_temp

    
@community.route('/community') 
def community_page():

    username = session.get('username')
    community_data = session.get('community_data')

        
    #handles if the user has clicked off the page and decided to return before the limit has been reached
    if username in session.values() and len(community_data) < total_limit:
        generate_data()
        return render_template('community.html', community_data = (community_data))
    
    #if the user returns to the page just serve them back the posts that they generated
    elif username in session.values() and len(community_data) >= total_limit:
        
        full_set = list(set(community_data))
        return  render_template('community.html', community_data=full_set)
    else:
        #if not in a session, kick them out
        return redirect('/')


#get generated data and append to the end of the webpage if the post is older
@community.route('/get_data')
def more_posts():

    username = session.get('username')
    community_data = session.get('community_data')

    if username not in session.values():
        return redirect('/')
    
    #if the user hit the post limit then yell at the javascript on the page 
    if len(community_data) >= total_limit:
        print("stop")
        return 'STOP'
    else:
        temp = sorted(generate_data(), reverse=True)
        return  jsonify ({'html': render_template('community_posts_batch.html', temp=temp)})
    

#Get a single instance of a community post
#TODO add design elements
@community.route('/community_post/<int:community_post_id>',methods=['POST','GET'])
def community_post_(community_post_id):


    username = session.get('username')
    curr_user = Users.get_by_username(username)
    post = CommunityPost.get_by_id(community_post_id=community_post_id)

    ##owner
    owner_username =Users.get_username_by_id( post.get_owner_id())

    #kick the user out if they are not in the session
    if not (username or user) or username not in session.values():
        return redirect('/')
    
    #check if the current user is the owner of the post
    owner_flag = True if post.get_owner_id() == curr_user.get_id() else False
    curr_username = curr_user.get_username()
    


    #query to get post content, album, and photo url
    post_content = (db.session.query(
        CommunityPost.post_content,
        CommunityPost.album_id,
        Photo.photo_url
    )
    .join(Album, CommunityPost.album_id == Album.album_id)
    .join(Photo, Album.album_id == Photo.album_id)
    .filter(CommunityPost.community_post_id == community_post_id)
    .first()
    )


    #query to get comments using likes as a junction table
    comments = (
    db.session.query(
        CommunityPostComment.comment_content,
        CommunityPostComment.user_id
    )
    .outerjoin(community_post_likes, CommunityPostComment.community_post_id == community_post_likes.c.community_post_id)
    .filter(CommunityPostComment.community_post_id == community_post_id)
    .group_by(CommunityPostComment.comment_id)
    .all()
    )
        

    #check and see if the current user has liked the post
    user = Users.get_by_username(username)
    like_check = db.session.query(exists().where(
                        community_post_likes.c.user_id == user.get_id(),
                        community_post_likes.c.community_post_id == community_post_id
    )).scalar()
    
    
    like_count = get_total_likes_for_community_post(community_post_id)

    #swap user_id with the username
    comments = [(x,Users.get_username_by_id(int(y))) for x,y in comments]

    #debug return in case of error
    if post_content is None:
        return f"<h1>{post_content} and {community_post_id}</h1>"
    
    #send all of the data to the html page
    return render_template('community_singleton.html',
                           community_post_id = community_post_id,
                           post_content = post_content.post_content,
                           album_id = post_content.album_id,
                           photo_url = post_content.photo_url,
                           comments = comments,
                           likes = like_count,
                           owner = owner_flag,
                           curr_username = curr_username,
                           liked = like_check,
                           owner_username = owner_username)




#helps user like and unlike post
@community.route('/community_like', methods = ['POST'])
def community_like():

    username = session.get('username')

    
    post_id = request.form.get("community_post_id")
    username = session.get('username')
    user = Users.get_by_username(username=username)
    
    #check if like exists
    like_check = db.session.query(exists().where(
                        community_post_likes.c.user_id == user.get_id(),
                        community_post_likes.c.community_post_id == post_id
    )).scalar()
     

    if like_check:
        #this generates a sql script that will be run by the database
        delete_instance = community_post_likes.delete().where(
                community_post_likes.c.user_id == user.get_id(),
                community_post_likes.c.community_post_id == post_id
             )
        
        #execute and commit then refresh the page
        db.session.execute(delete_instance)
        db.session.commit()

        return redirect(url_for('community.community_post_',community_post_id=post_id ,_method='POST'))
        
    else:
        like_instance = community_post_likes.insert().values(
            user_id = user.get_id(),
            community_post_id=post_id
        )
        
        db.session.execute(like_instance)
        db.session.commit()
        
        return redirect(url_for('community.community_post_',community_post_id=post_id ,_method='POST'))



#helps user comment on a post
@community.route('/community_comment', methods = ['POST','GET'])
def community_comment():

    comment = request.form.get('comment')
    username = request.form.get('curr_username')
    community_post_id = request.form.get('community_post_id')

    #check for None type anything
    if (username not in session.values()) or ((username or comment) is None ):
        return abort(405)
    
    #forbid empty strings in comments
    elif comment == '':
        return abort(405)
    
    else:

        #get the instance of user currently in the session
        user = Users.get_by_username(session.get('username'))
        #create new comment object
        comment = CommunityPostComment(user_id = user.get_id(),community_post_id = community_post_id, comment_content=comment)

        db.session.add(comment)
        db.session.commit()
        
        #refresh the page with new information
        return redirect(url_for('community.community_post_',community_post_id=community_post_id ,_method='POST'))
    



@community.route('/new_community_post', methods = ['POST'])
def new_post():

    return render_template('new_community_post.html')
    


@community.route('/create_post',methods=['POST'])
def create_post():

    username = session.get('username')
    

    if username not in session.values() or username is None:
        abort(405)

    user = Users.get_by_username(username)
    caption = request.form.get('post-title')
    photo_stream = request.files.getlist('upload-pictures')

    album = Album(user.get_id(),f"{username}'s album")
    db.session.add(album)
    db.session.commit()
    album_id = album.album_id

    community_post = CommunityPost(user_id = user.get_id(),album_id=album_id,post_content=caption)
    db.session.add(community_post)
    db.session.commit()

    for photo in photo_stream:
        if photo and photo.filename:
            photo_url = upload_file(photo)
            if photo_url:
                picture = Photo(album_id=album_id,photo_url=url_for('static',filename = f"user_images/{photo_url}"))
                db.session.add(picture)
                db.session.commit()

    #debug statment to check if data is being added            
    try:
        pass
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.session.rollback()

    #add the new post to the users session 
    data = session.get('community_data')

    data.extend([(community_post.post_content, community_post.community_post_id, picture.photo_url)])
    session['community_data'] = sorted(data,reverse=True)

    return redirect(url_for('community.community_post_', community_post_id=community_post.get_id()))



#helps user delete their post as long as they are the owner
@community.route('/delete_post/<int:community_post_id>',methods=['GET','POST'])
def delete_post(community_post_id):
    
    #Search for the post data in the db
    post_content = (db.session.query(
        CommunityPost.post_content,
        CommunityPost.community_post_id,
        Photo.photo_url
    )
    .join(Album, CommunityPost.album_id == Album.album_id)
    .join(Photo, Album.album_id == Photo.album_id)
    .filter(CommunityPost.community_post_id == community_post_id)
    .first()
    )
    


    community_post = CommunityPost.get_by_id(community_post_id=community_post_id)
        
    community_data = session.get('community_data')
    
    community_data.remove(post_content)

    #update the list of community posts generated
    session['community_data'] = list(set(community_data))

    db.session.delete(community_post)
    db.session.commit()
    return redirect('/community')

