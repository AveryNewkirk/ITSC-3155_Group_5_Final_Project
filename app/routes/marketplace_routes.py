from flask import Blueprint, render_template, request,session,redirect,jsonify,url_for,abort
from sqlalchemy import desc,func,exists
import pickle
from ..models.pipeline import *
from ..utils import upload_file


marketplace = Blueprint('marketplace', __name__,template_folder='templates',static_folder='static')


batch_limit = 9 #a multiple of 3 per batch is ideal since the community page will generate 3x3 grids at a time
page_num = 1 #start at one for the page number then increment on each request
total_limit = 36

#generate posts from database is kind of janky but works well enough
def generate_data():
    global page_num
    ## offset to increment the query for the posts is a bit unstable
    offset = (page_num - 1) * batch_limit
    page_num += 1    
    marketplace_data = session.get('marketplace_data')
    
    #check for problematic comunity data
    if marketplace_data is None:
        print('problematic')
        return
    
    ##Query to get just the post content, date, and photo_url
    temp = (db.session.query(
        Listing.title,
        Listing.listing_id,
        Listing.description,
        Listing.price,
        Photo.photo_url
    )
    .join(Album, Listing.album_id == Album.album_id)
    .join(Photo, Album.album_id == Photo.album_id)
    .order_by(desc(Listing.listing_id))
    .offset(offset).limit(batch_limit)
    .all()
    )
    
    #cast to tuples to avoid JSON errors 
    processed_temp = ([tuple(row) for row in temp if not(row is None)])


    #add the batch of posts to the total amount of posts the user has generated
    marketplace_data.extend((processed_temp))

    #test byte length if too many end up in the cookie data everything gets deleted
    byte_length = len(pickle.dumps(marketplace_data))
    print(byte_length)

    #IMPORTANT update the session data
    session['marketplace_data'] = sorted(list(set(marketplace_data)), reverse=True)

    #return the batch when ONLY when below the limit
    return processed_temp

    
@marketplace.route('/marketplace') 
def marketplace_page():

    username = session.get('username')
    marketplace_data = session.get('marketplace_data')

        
    #handles if the user has clicked off the page and decided to return before the limit has been reached
    if username in session.values() and len(marketplace_data) < total_limit:
        generate_data()
        return render_template('marketplace.html', marketplace_data = marketplace_data)
    
    #if the user returns to the page just serve them back the posts that they generated
    elif username in session.values() and len(marketplace_data) >= total_limit:
        
        full_set = list(set(marketplace_data))
        return  render_template('marketplace.html', marketplace_data=full_set)
    else:
        #if not in a session, kick them out
        return redirect('/')


#get generated data and append to the end of the webpage if the post is older
@marketplace.route('/get_data')
def more_posts():

    username = session.get('username')
    marketplace_data = session.get('marketplace_data')

    if username not in session.values():
        return redirect('/')
    
    #if the user hit the post limit then yell at the javascript on the page 
    if len(marketplace_data) >= total_limit:
        print("stop")
        return 'STOP'
    else:
        temp = generate_data()
        return  jsonify({'html': render_template('listings_batch.html', temp=temp)})
    

#Get a single instance of a community post
#TODO add design elements
@marketplace.route('/listing/<int:listing_id>',methods=['POST','GET'])
def listing_(listing_id):


    username = session.get('username')
    curr_user = Users.get_by_username(username)
    post = Listing.get_by_id(listing_id=listing_id)

    #kick the user out if they are not in the session
    if not (username or user) or username not in session.values():
        return redirect('/')
    
    #check if the current user is the owner of the post
    owner_flag = True if post.get_owner_id() == curr_user.get_id() else False
    curr_username = curr_user.get_username()
    


    #query to get post content, album, and photo url
    post_content = (db.session.query(
        Listing.title,
        Listing.album_id,
        Listing.description,
        Listing.price,
        Photo.photo_url
    )
    .join(Album, Listing.album_id == Album.album_id)
    .join(Photo, Album.album_id == Photo.album_id)
    .filter(Listing.listing_id == listing_id)
    .first()
    )


    #query to get comments using likes as a junction table
    comments = (
    db.session.query(
        ListingComment.comment_content,
        ListingComment.user_id
    )
    .outerjoin(listing_likes, ListingComment.listing_id == listing_likes.c.listing_id)
    .filter(ListingComment.listing_id == listing_id)
    .group_by(ListingComment.comment_id)
    .all()
    )
        

    #check and see if the current user has liked the post
    user = Users.get_by_username(username)
    like_check = db.session.query(exists().where(
                        listing_likes.c.user_id == user.get_id(),
                        listing_likes.c.listing_id == listing_id
    )).scalar()
    
    
    like_count = get_total_likes_for_listing(listing_id)

    #swap user_id with the username
    comments = [(x,Users.get_username_by_id(int(y))) for x,y in comments]

    #debug return in case of error
    if post_content is None:
        return f"<h1>{post_content} and {listing_id}</h1>"
    
    #send all of the data to the html page
    return render_template('marketplace_singleton.html',
                           listing_id = listing_id,
                           post_content = post_content.title,
                           price = post_content.price,
                           desc = post_content.description,
                           album_id = post_content.album_id,
                           photo_url = post_content.photo_url,
                           comments = comments,
                           likes = like_count,
                           owner = owner_flag,
                           curr_username = curr_username,
                           liked = like_check)




#helps user like and unlike post
@marketplace.route('/marketplace_like', methods = ['POST'])
def marketplace_like():

    username = session.get('username')

    
    post_id = request.form.get("listing_id")
    username = session.get('username')
    user = Users.get_by_username(username=username)
    
    #check if like exists
    like_check = db.session.query(exists().where(
                        listing_likes.c.user_id == user.get_id(),
                        listing_likes.c.listing_id == post_id
    )).scalar()
     

    if like_check:
        #this generates a sql script that will be run by the database
        delete_instance = listing_likes.delete().where(
                listing_likes.c.user_id == user.get_id(),
                listing_likes.c.listing_id == post_id
             )
        
        #execute and commit then refresh the page
        db.session.execute(delete_instance)
        db.session.commit()

        return redirect(url_for('marketplace.listing_',listing_id=post_id ,_method='POST'))
        
    else:
        like_instance = listing_likes.insert().values(
            user_id = user.get_id(),
            listing_id=post_id
        )
        
        db.session.execute(like_instance)
        db.session.commit()
        
        return redirect(url_for('marketplace.listing_',listing_id=post_id ,_method='POST'))



#helps user comment on a post
@marketplace.route('/marketplace_comment', methods = ['POST','GET'])
def marketplace_comment():

    comment = request.form.get('comment')
    username = request.form.get('curr_username')
    listing_id = request.form.get('listing_id')

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
        comment = ListingComment(user_id = user.get_id(),listing_id = listing_id, comment_content=comment)

        db.session.add(comment)
        db.session.commit()
        
        #refresh the page with new information
        return redirect(url_for('marketplace.listing_',listing_id=listing_id ,_method='POST'))
    



@marketplace.route('/new_listing', methods = ['POST'])
def new_post():

    return render_template('sell.html')


#helps user delete their post as long as they are the owner
@marketplace.route('/delete_post/<int:listing_id>',methods=['GET','POST'])
def delete_post(listing_id):
    
    #Search for the post data in the db
    post_content = (db.session.query(
        Listing.post_content,
        Listing.listing_id,
        Listing.description,
        Photo.photo_url
    )
    .join(Album, Listing.album_id == Album.album_id)
    .join(Photo, Album.album_id == Photo.album_id)
    .filter(Listing.listing_id == listing_id)
    .first()
    )
    


    listing = Listing.get_by_id(listing_id=listing_id)
        
    marketplace_data = session.get('marketplace_data')
    
    marketplace_data.remove(post_content)

    #update the list of community posts generated
    session['marketplace_data'] = list(set(marketplace_data))

    db.session.delete(listing)
    db.session.commit()
    return redirect('/marketplace')

