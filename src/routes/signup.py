
from flask import Blueprint, abort, render_template, request, redirect, session
from ..database import db,bcrypt
from src.models.pipeline import Users
signup = Blueprint('signup', __name__)
# bcrypt = Bcrypt(signup)
# signup.secret_key = os.getenv()


@signup.route('/signup')
def display():
    return render_template('signup.html')


@signup.route('/home')
def home():
    return render_template('profile.html')

@signup.post('/create')
def create():
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')
    #user = Users.get_by_username(username) # get instance of user based on username
    
    

    """
    Im just putting this here to check, a logged in user 
    with a session should not be able to access the sign in page.
    """
    sesh_usr  = session.get('username') 
    user = Users.get_by_username(session['username'])
    if user is not None or sesh_usr is not None: # if the user exists redirect them to the login page
        return redirect('/login')

    if not username or not password or not email:
        abort(400)

    hashed_password = bcrypt.generate_password_hash(password,12).decode('utf-8')
    print(hashed_password)
    new_user = Users(username,email,hashed_password)

    ##adding user session upon creation of a new user
    # community_data = []
    # session['username'] = username
    # session['community_data'] = community_data
    # db.session.add(new_user)
    # db.session.commit()
    community_data = []
    session['username'] = username
    session['community_data'] = community_data
    db.session.add(new_user)
    db.session.commit()
    print(f"\n{username}\n{email}\n\n")
    return redirect('/')
