from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.pipeline import db, Users, Listing, Album, Photo
from openai import OpenAI
from ..utils import upload_file

sell = Blueprint('sell', __name__)

@sell.route('/sell', methods=["GET", "POST"])
def create_listing():
    
    # TODO
    # Verify user is logged in and, if so, get user object
    # if 'userd_id' not in session:
    #     return(redirect(url_for('login_routes.login')))
    
    # Create user for testing purposes

    
    if request.method == 'POST':
        #-------------------------------------------------------------------------------------
        username = session.get('username')
        

        if username not in session.values() or username is None:
            return(render_template("index.html"))

        user = Users.get_by_username(username)
        title = request.form['listing-title']
        description = request.form['item-description']
        price = float(request.form['price'])
        photo_stream = request.files.getlist('upload-pictures')

        album = Album(user.get_id(),f"{username}'s album")
        db.session.add(album)
        db.session.commit()
        album_id = album.album_id

        new_listing = Listing(title=title, description=description, price=price, user_id = user.get_id(), album_id=album_id)
        db.session.add(new_listing)
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
        data = session.get('marketplace_data')

        data.extend([(new_listing.title, new_listing.listing_id, picture.photo_url, new_listing.description, new_listing.price)])
        session['marketplace_data'] = sorted(data,reverse=True)

        return redirect(url_for('sell.sell_success', listing_id=new_listing.listing_id))
        #-------------------------------------------------------------------------------------
        
    # Default to showing empty Sell page
    return render_template('sell.html')

@sell.route('/sell_success/<int:listing_id>')
def sell_success(listing_id):
    listing = Listing.query.get(listing_id)
    return render_template('sell_success.html', listing=listing)