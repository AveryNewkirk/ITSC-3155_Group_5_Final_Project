
from flask import Blueprint, abort, render_template, request, redirect, url_for
from ..database import db
from app.models.pipeline import Users
#from __init__ import bcrypt
from flask_bcrypt import Bcrypt
import bcrypt
signup = Blueprint('signup', __name__)

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
    if not password or not email:
        abort(400)
    #hashed_password = Bcrypt.generate_password_hash(password,12).decode() # type: ignore
    new_user = Users(email,password)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/home')