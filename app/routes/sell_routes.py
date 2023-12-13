from crypt import methods
from email import message
from fileinput import filename
from typing import Iterable
from exceptiongroup import catch
from flask import Blueprint, current_app, jsonify, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import os
from pydantic import InstanceOf
from sqlalchemy import desc

from ..models.pipeline import db, Users, Listing, Album, Photo
from ..utils import upload_file
from openai import OpenAI
import base64

# Constants and variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
aiClient = OpenAI()

# Create Flask Blueprint
sell = Blueprint('sell', __name__)

@sell.route('/sell', methods=["GET", "POST"])
def create_listing():
    
    # TODO:
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
                photo_url = upload_file(file)
                if photo_url:
                    photo = Photo(album_id=album_id, photo_url=photo_url)
                    db.session.add(photo)
        db.session.commit()
        
        return redirect(url_for('sell.sell_success', listing_id=new_listing.listing_id))
        
    # Default to showing empty Sell page
    return render_template('sell.html')

@sell.route('/upload_images', methods=['POST'])
def upload_images():
    photos = request.files.getlist('upload-pictures')
    
    # Create user for testing purposes
    user = Users('testuser', 'testemail', 'testpass')
    db.session.add(user)
    db.session.commit()
    
    # Create Album object for images
    album = Album(user.user_id)
    db.session.add(album)
    db.session.commit()
    
    # Create Photo objects and add to db
    for file in photos:
        if file and file.filename:
            photo_url = upload_file(file)
            if photo_url:
                photo = Photo(album_id=album.album_id, photo_url=photo_url)
                db.session.add(photo)
    db.session.commit()
    
    # Get album_id
    return {'album_id': album.album_id}

@sell.route('/generate_description', methods=['POST'])
def handle_generate_description():
    print('REACHED: begin handle_generate_description')
    try:
        data = request.get_json()
        album_id = data.get('album_id')
        response = generate_description(album_id)
        description = response.choices[0].message.content if response else ''
        print('REACHED: handle_generate_description return')
        print('DESCRIPTION: ')
        print(description)
        return jsonify(description=description)
    except Exception as e:
        print(e)
        return jsonify(error=str(e)), 500
    
@sell.route('/generate_pictures', methods=['POST'])
def generate_pictures():
    data = request.get_json()
    description = data.get('description')
    print('GENERATE_PICTURES: description: ')
    print(description)
    
    concise_prompt = '''
    You will be provided with the description of a clothing item from an online store. 
    Please abstract out the physical attributes of the clothing item, 
    including type, fit, style, material, color, pattern/design, and detailing. 
    Please return a concise summary of these physical attributes without any additional filler or fluff. \n
    Clothing item description: \n
    '''
    
    if description:
        concise_prompt += description
    else:
        return jsonify({'error': 'Description is missing'}), 400
    
    response_1 = aiClient.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": concise_prompt
        }]
    )
    print('GENERATE_PICTURES: response_1 completed')
    
    concise_description = response_1.choices[0].message.content
    print('GENERATE_PICTURES: concise_description: ')
    print(concise_description)
    
    image_prompt = '''
    You will be provided with a detailed summary of the physical attributes of a clothing item.
    Using these attributes, you will generate a true-to-life photo of an appropriate human model 
    wearing the clothing item while posing against an off-white backdrop. 
    The photo must depict a full view of the entirety of the clothing item. \n
    Clothing item physical attributes summary: \n
    '''
    
    if concise_description:
        image_prompt += concise_description
    else:
        return jsonify({'error': 'Concise description is missing'}), 400
    
    response_2 = aiClient.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1024x1024",
        quality="standard",
        style='vivid',
        n=1
    )
    print('GENERATE_PICTURES: response_2 completed')
    
    # TODO: populate imgs on webpage and add selected options to the db
    
    image_url = response_2.data[0].url
    print('GENERATE_PICTURES: image_url: ')
    print(image_url)
    return jsonify({'image_url': image_url})


# Alternative /generate_pictures route for testing
# @sell.route('/generate_pictures', methods=['POST'])
# def generate_pictures():
#     image_url = 'https://art.pixilart.com/a4d7353d97dd6d4.png'
#     return jsonify({'image_url': image_url})

@sell.route('/sell_success/<int:listing_id>')
def sell_success(listing_id):
    listing = Listing.query.get(listing_id)
    return render_template('sell_success.html', listing=listing)

# UTILITY FUNCTIONS
# Function to encode images in base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
# Function to get mime type
def get_mime_type(file_path):
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'tiff': 'image/tiff',
        'webp': 'image/webp'
    }
    ext = file_path.split('.')[-1].lower()
    return mime_types.get(ext, 'image/jpeg')

# Function to generate AI generated model pictures
def generate_description(album_id):
    # List to hold message content to OpenAI API
    content = []
    # Initial prompt
    content.append({
        "type": "text", 
        "text": '''
        The attached image is a photograph of a single item of clothing. 
        Any additional attached images are additional photographs of the same item of clothing taken from various angles.

        Your task is to please create a highly detailed description of the clothing item shown in the photograph(s). 
        The description should be extremely thorough and include any and all possible information about the clothing item. 
        At the very least, the description should describe each of the following attributes of the clothing item in comprehensive detail:

        List of clothing item attributes:
        1. Type: Defines the category of clothing, such as a shirt, pants, dress, jacket, etc.
        2. Style: The specific design or fashion style, such as casual, formal, vintage, modern, etc.
        3. Color: The primary and secondary colors, including shades and tones.
        4. Material: The material used, like cotton, polyester, silk, leather, etc., including blends.
        5. Texture: The feel of the material, like smooth, rough, ribbed, plush, etc.
        6. Fit: How the clothing fits the body, like loose, slim, tailored, oversized, etc.
        7. Pattern/Design: Any prints or patterns on the fabric, like stripes, floral, polka dots, abstract, etc.
        8. Detailing: Any features like embroidery, lace, buttons, zippers, pockets, ruffles, etc.

        Take a minimal approach to sentence structure and cut out unnecessary words. 
        Avoid simply listing out information and write in full paragraphs instead. 
        As you write, act as though the clothing item is right in front of you and do not acknowledge the existence of the image whatsoever. 
        Finally, write the description in the style of an online seller writing a description for a listing.
        '''
    })
    
    # Adding images to content
    album = Album.get_by_id(album_id)
    if isinstance(album, Album):
        photos = album.photos
        if isinstance(photos, Iterable):
            for photo in photos:
                image_path = os.path.join(current_app.root_path, 'static', 'user_images', photo.photo_url)
                base64_image = encode_image(image_path)
                mime_type = get_mime_type(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                })
                print('PATH: ' + image_path)
    
    # Sending request to OpenAI gpt-4-vision
    response = aiClient.chat.completions.create(
        model = "gpt-4-vision-preview",
        messages = [{
            "role": "user",
            "content": content,
        }],
        max_tokens = 300
    )
    
    print('REACHED: generate_description return')
    return response