from flask import Blueprint, render_template, request, request, redirect, url_for, session
from app.models.pipeline import db, Listing
from flask import abort

# Create Blueprint
index = Blueprint('index', __name__)

# Define main index route
@index.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    return render_template('index.html')

@index.post('/logout')
def logout():
    del session['username']
    return redirect('/')

@index.route('/delete_listing/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.user.username != session['username']:
        abort(401)
    db.session.delete(listing)
    db.session.commit()
    return redirect('/')

@index.route('/edit_listing/<int:listing_id>', methods=['GET','POST'])
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.user.username != session['username']:
        abort(401)
    if request.method == 'POST':
        listing.title = request.form['edit-title'] if request.form['edit-title'] != '' else listing.title
        listing.description = request.form['edit-description'] if request.form['edit-description'] != '' else listing.description
        listing.price = request.form['edit-price'] if request.form['edit-price'] != '' else listing.price
        
        db.session.commit()
        
        return render_template('sell_success.html', listing=listing, listing_id=listing_id)
    return render_template('edit_listing.html', listing_id=listing_id, listing=listing)
  
    return redirect('/')
