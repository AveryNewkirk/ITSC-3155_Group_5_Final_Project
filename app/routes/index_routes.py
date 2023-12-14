from flask import Blueprint, render_template, request, redirect, url_for

# Create Blueprint
index = Blueprint('index', __name__)

# Define main index route
@index.route('/')
def home():
    return render_template('index.html')
