from flask import Blueprint, render_template, request, redirect, session, url_for
from ..models.pipeline import Users, db, Listing ,Photo,Album
profile = Blueprint('main', __name__)
from ..utils import upload_file

#################
@profile.route('/profile', methods=['POST','GET'])
def render_profile():
    # Return user to signup if the user is not logged in, i.e., username returns None
    username = session.get('username')

    if username is None:
        print("No user is logged in.")
        return render_template('signup.html')
    
    user = Users.get_by_username(username)
    userid=None
    if not isinstance(user,Users):
        return render_template('signup.html')
    
    userid=user.user_id
    listings = Listing.query.filter_by(user_id = userid)

    print(f"User {username} is logged in.")
    return render_template('profile.html', username=username, listings=listings)
    
##################

@profile.route('/edit_profile', methods=['POST','GET'])
def render_profile_settings():
    username = session.get('username')
    return render_template('profile_settings.html', username = username)

##################

@profile.route('/edit_username', methods=['POST','GET'])
def render_edit_profile_user():
    username = session.get('username')
    user = Users.get_by_username(username)

    if request.method == 'POST':
                
        newUsername = request.form.get('newUsername')
        
        if newUsername and user is not None:
            user.username = newUsername
            db.session.commit()
            session['username'] = newUsername
        return redirect('/edit_profile')  

    return render_template('index.html', username=username)  

##################

@profile.route('/edit_profile_pic', methods=['POST', 'GET'])
def render_edit_profile():
    username = session.get('username')
    user = Users.get_by_username(username)
    allowed_extensions = {'jpg', 'jpeg'}

    if request.method == 'POST' and 'image' in request.files:
        new_pfp = request.files['image']
        if '.' in new_pfp.filename and new_pfp.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            # Update the user's profile picture in the database
            photo_url = upload_file(new_pfp)
            full_url = url_for('static', filename = 'user_images/' + photo_url)
            print(full_url)
            user.profile_picture = full_url
            db.session.commit()
            session['profile_picture'] = user.profile_picture
            return render_template('profile_settings.html', username=username)

        else:
            return render_template('profile_settings.html', username=username)

    return render_template('profile_settings.html', username=username)

##################

@profile.route('/logout', methods=['POST','GET'])
def logout():
    session.clear()
    print(session)
    return render_template('index.html')