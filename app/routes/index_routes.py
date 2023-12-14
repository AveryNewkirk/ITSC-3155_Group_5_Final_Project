from flask import Blueprint, redirect, render_template, session

# Create Blueprint
index = Blueprint('index', __name__)

# Define main index route
@index.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', username=username)
    return render_template('index.html')

@index.post('/logout')
def logout():
    del session['username']
    return redirect('/')