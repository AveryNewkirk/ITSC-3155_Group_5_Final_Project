from flask import Blueprint, render_template, request, redirect, url_for, abort, session


from src.models.pipeline import Users
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
    if temp.password == password: # type: ignore
        session['user'] = {
            'email' : temp.email,
            'username' : temp.username,
            'picture' : temp.profile_picture
        }
        return redirect('/secret')
    else:
        abort(401)

@login.route('/secret')
def get_user_page():
    if 'user' not in session:
        abort(401)
    return render_template('profile.html')


@login.post('/logout')
def signout():
    del session['user']
    return redirect('/')


