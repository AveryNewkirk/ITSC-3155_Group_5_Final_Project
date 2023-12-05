import mimetypes
from flask import Blueprint, render_template, request, redirect, url_for, session
from ..models.pipeline import db, Users, Listing, Album, Photo

sell = Blueprint('sell', __name__)

@sell.route('/sell', methods=["GET", "POST"])
def create_listing():
    
    # Verify user is logged in and, if so, get user object
    # if 'userd_id' not in session:
    #     return(redirect(url_for('login_routes.login')))
    
    # Create user for testing purposes
    user = Users('testuser', 'testemail', 'testpass')
    db.session.add(user)
    db.session.commit()
    
    if request.method == 'POST':
        # Get field from dummy user
        user_id = user.user_id
        
        # Extract form fields
        title = request.form['listing-title']
        description = request.form['item-description']
        price = float(request.form['price'])
        listing_photos = request.files.getlist('upload-pictures')
        
        # Create Album object for images
        listing_album = Album(user_id)
        db.session.add(listing_album)
        db.session.commit()
        
        # Get album_id
        album_id = listing_album.album_id
        
        # Create new listing
        new_listing = Listing(title=title, description=description, price=price, user_id=user_id, album_id=album_id)
        db.session.add(new_listing)
        db.session.commit()
        
        # Create Photo objects and add to db
        for file in listing_photos:
            if file and file.filename:
                file_data = file.read()
                photo_mimetype = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
                
                photo = Photo(album_id=album_id, photo_data=file_data, photo_mimetype=photo_mimetype)
                db.session.add(photo)
        db.session.commit()
        
        return redirect(url_for('sell.sell_success', listing_id=new_listing.listing_id))
        
    # Default to showing empty Sell page
    return render_template('sell.html')

@sell.route('/sell_success/<int:listing_id>')
def sell_success(listing_id):
    listing = Listing.query.get(listing_id)
    return render_template('sell_success.html', listing=listing)