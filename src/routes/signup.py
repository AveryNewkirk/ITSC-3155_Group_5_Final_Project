
from flask import Blueprint, abort, render_template, request, redirect, session
from ..database import db,bcrypt
from app.models.pipeline import Users
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

    user = Users.get_by_username(username) # get instance of user based on username


    """
    Im just putting this here to check, a logged in user 
    with a session should not be able to access the sign in page.
    """
    sesh_usr  = session.get('username') 

    if user is not None or sesh_usr is not None: # if the user exists redirect them to the login page
        return redirect('/login')

    if not username or not password or not email:
        abort(400)

    hashed_password = bcrypt.generate_password_hash(password,12)
    new_user = Users(username,email,hashed_password)

    ##adding user session upon creation of a new user
    session['username'] = username
    db.session.add(new_user)
    db.session.commit()
    print(f"\n{username}\n{email}\n{hashed_password}\n")
    return redirect('/')
