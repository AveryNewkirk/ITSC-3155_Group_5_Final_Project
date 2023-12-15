from flask import Blueprint, render_template, request, redirect, url_for,abort,session
from ..database import bcrypt
from ..models.pipeline import *

login = Blueprint('login', __name__)

@login.route('/login')
def display():
    return render_template('login.html')


@login.route('/auth', methods= ['POST', 'GET'])
def authUser():
    email = request.form.get('email')
    password = request.form.get('password')

    if (not email and not password) or (email=='' and password ==''):
        abort(404)
    
    user = Users.query.filter_by(email=email).first()

    if not user:
        return redirect('/')
    
    if bcrypt.check_password_hash(user.password, password):
        session['username'] = user.username
        print(user.username)
        session['community_data'] = []
        session['marketplace_data'] = [] 
        session['profile_picture'] = user.profile_picture

        return redirect(url_for('user.user_singleton', username=user.username))
    
    return f"<h1>FAILED<h1>"
    
    #if the user.email == user.password
        # redirect to the profile page of said user
    #else
        # throw an error and ask the user to retry




@login.route('/logout')
def logout():
    session.clear()
    return redirect('/')