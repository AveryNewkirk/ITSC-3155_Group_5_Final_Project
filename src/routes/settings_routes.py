from flask import Blueprint, render_template, request, redirect, url_for, session,flash
from ..database import bcrypt
from ..models.pipeline import Users,db
# Create Blueprint
settings = Blueprint('settings', __name__)


#SETTINGS PAGE
@settings.route('/settings')
def render_settings():

    username = session.get('username')
    user = Users.get_by_username(username)

    if user is None:
        return render_template('index.html')

    if username in session.values() and session['username']==username:
        
        email = user.email
        password = mask_first_half(user.password)
        access = 'Public' if user.public_access == True else 'Private'
        username = session.get('username')

        return render_template('settings.html', email=email, access=access,password=password,username=username )
    
    print(f"all conditions failed {session.get('userusername')}")
    return render_template('settings.html')
       
#delete the user account no questions asked

@settings.route('/delete' ,methods =['GET','POST'])
def delete_account():

    username = session.get('username')

    if  username in session.values() and session['username'] == username:
        goner = Users.query.filter_by(username = username).first()
        db.session.delete(goner)
        session.pop('username')
        session.pop('community_data')
        db.session.commit()
        return render_template('index.html')
        
    else:
        return render_template('index.html')


@settings.route('/edit_user/<arg>' ,methods = ['POST','GET'])
def edit_user_info(arg):

    #check if the argumet is valid
    valid_arg = arg in ['email', 'password', 'access']

    username = session.get('username')
    user = Users.query.filter_by(username= username).first()
    email = user.email
    password = mask_first_half(user.password)
    access = 'Public' if user.public_access == True else 'Private'

    #validate if the user and return homepage if anything is wrong
    if user != None and valid_arg and username in session.values() and session['username'] == username:

        return render_template('edit_user.html',arg=arg, email=email,password=password,access=access)
    else:
        return render_template('index.html')

"""
Helps the user alter their account accepst differnt arguments and makes one change at a time based on that argument
"""
@settings.route('/edit', methods = ['POST','GET'])
def change_account_info():

    email = request.form.get('email')
    password = request.form.get('password')

    
    flag = request.form.get('flag')

    username = session.get('username')


    #validate the user and change the information then commit the changes
    if  username in session.values() and session['username'] == username:
        
        user = Users.get_by_username(username)

        if flag == 'change-access':
            user.public_access = not user.public_access

        if flag == 'change-password':
            hashed_password = bcrypt.generate_password_hash(password,12)
            user.password = hashed_password

        if flag == 'change-email':
            user.email = email


        db.session.commit()
        return redirect('/settings')
    else:
        return redirect('/')

#makes half of the password 
def mask_first_half(input_string):
    length = len(input_string)
    altered_length = length // 15

    masked_string = '*' * altered_length
    return masked_string