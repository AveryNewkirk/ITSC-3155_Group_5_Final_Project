from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_bcrypt import Bcrypt
from app.models.pipeline import Users
login = Blueprint('login', __name__)

@login.route('/login')
def display():
    return render_template('login.html')

@login.route('/home')
def home():
    return render_template('profile.html')


@login.post('/auth')
def authUser():
    email = request.form.get('email')
    password = request.form.get('password')
    if not password or not email:
        abort(400)
    temp = Users.query.filter_by(email = email).first_or_404()
    if temp.password == password:
        return render_template('/home')
    else:
        abort(401)
    #if the user.email == user.password
        # redirect to the profile page of said user
    #else
        # throw an error and ask the user to retry



