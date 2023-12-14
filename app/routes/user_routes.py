from flask import Blueprint, render_template, session,redirect
from ..models.pipeline import Users
user = Blueprint('user', __name__)

@user.route('/user')
def user_page():
    return render_template('user.html')

#endpoint for singe usser page, redirects to profile if they are in the session.
@user.route('/user/<string:username>' , methods = ['POST','GET'])
def user_singleton(username):
    
    if username in session.values() and session['username'] == username:
        return redirect('/profile')
    
    usr = Users.get_by_username(username=username)

    if usr.get_access() == False:
        return redirect('/')
    
    return render_template('user.html',username=username)

@user.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_singleton_id(user_id):
    user = Users.query.get(user_id)
    username = None
    if isinstance(user, Users):
        username = user.username
    else:
        return redirect('/')
    if username in session.values() and session['username'] == username:
        return redirect('/profile')
    return render_template('user.html', username=username)
    