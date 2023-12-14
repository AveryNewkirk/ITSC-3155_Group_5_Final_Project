from flask import Blueprint, render_template, request, redirect, url_for, abort, session
from app.database import bcrypt

from app.models.pipeline import Users
login = Blueprint('login', __name__)


@login.route('/')
def home():
    return render_template('/index.html')


@login.route('/login')
def display():
    if 'user' in session:
        return redirect('/secret')
    return render_template('login.html')

@login.post('/auth')
def authUser():
    email = request.form.get('email')
    password = request.form.get('password')

    if not password or not email:
        abort(400)
    temp = Users.query.filter_by(email = email).first_or_404()
    if bcrypt.check_password_hash(password,temp.password):
        session['email'] = temp.email
        session['username'] = temp.username
        return redirect('/secret')
    else:
        abort(401)

@login.route('/secret')
def get_user_page():
    if 'user' not in session:
        abort(401)
    return render_template('profile.html', username = session['user'].get('username'))


@login.post('/logout')
def signout():
    del session['user']
    return redirect('/')


