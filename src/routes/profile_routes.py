from flask import Blueprint, render_template, request, redirect, url_for

profile = Blueprint('main', __name__)



@profile.route('/profile', methods=['POST','GET'])
def render_profile():
    return render_template('profile.html')