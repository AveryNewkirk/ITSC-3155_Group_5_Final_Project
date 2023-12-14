from flask import Blueprint, render_template
from ..models.pipeline import Listing, Album, Photo

cards = Blueprint('cards', __name__)

@cards.route('/cards', methods=['GET', 'POST'])
def load_cards():
    listings = [
        Listing.query.get(32),
        Listing.query.get(33),
        Listing.query.get(34)
    ]
    
    return render_template('listing_card_test.html', listings=listings)