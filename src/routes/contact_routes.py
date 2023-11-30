from flask import Blueprint, render_template, request, redirect, url_for

contact = Blueprint('contact', __name__)

@contact.route('/contact')
def contact_page():
    return render_template('contact.html')