from flask import Blueprint, render_template, request, redirect, url_for


login = Blueprint('login', __name__)

@login.route('/login')
def display():
    return render_template('login.html')


@login.route('/auth')
def authUser():
    email = request.form.get('email')
    password = request.form.get('password')
    
    #if the user.email == user.password
        # redirect to the profile page of said user
    #else
        # throw an error and ask the user to retry



