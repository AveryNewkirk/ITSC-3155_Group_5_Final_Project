from flask import Blueprint, render_template, request, redirect, url_for, session,flash

from ..models.pipeline import Users,db
# Create Blueprint
settings = Blueprint('settings', __name__)


#SETTINGS PAGE
@settings.route('/settings')
def render_settings():

    username = session.get('username')
    user = Users.get_by_username(username)

    if user is None:
        return render_template('settings.html')

    if username in session.values() and session['username']==username:
        
        email = user.email
        password = mask_first_half(user.password)
        access = 'Public' if user.public_access == True else 'Private'
        username = session.get('username')

        return render_template('settings.html', email=email, access=access,password=password,username=username )
    
    print(f"all conditions failed {session.get('userusername')}")
    return render_template('settings.html')
       


@settings.route('/delete' ,methods =['GET','POST'])
def delete_account():

    username = session.get('username')
    if  username in session.values() and session['username'] == username:
        goner = Users.query.filter_by(username = username).first()
        print(f"\nto be deleted:")
        print(f"\n\n{goner}\n\n")
        db.session.delete(goner)
        session.pop('username')
        db.session.commit()
        return render_template('index.html')
        
    else:
        print(f"\n\n{username} and {session.values()} currently in the session\n\n")
        return render_template('index.html')


@settings.route('/edit_user/<arg>' ,methods = ['POST','GET'])
def edit_user_info(arg):

    #arg = request.form.get('arg')
    print(f"\n\n{arg}\n\n")
    #check if the argument is valid (shortens the if statment)
    valid_arg = arg in ['email', 'password', 'access']

    username = session.get('username')
    user = Users.query.filter_by(username= username).first()
    email = user.email
    password = mask_first_half(user.password)
    access = 'Public' if user.public_access == True else 'Private'
    if user != None and valid_arg and username in session.values() and session['username'] == username:

        return render_template('edit_user.html',arg=arg, email=email,password=password,access=access)
    else:
        return render_template('index.html')

#makes half of the password 
def mask_first_half(input_string):
    length = len(input_string)
    half_length = length // 2

    masked_string = '*' * half_length + input_string[half_length:]
    return masked_string