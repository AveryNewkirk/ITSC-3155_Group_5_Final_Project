from flask import Blueprint, render_template, request, redirect, url_for

marketplace = Blueprint('marketplace', __name__)

@marketplace.route('/marketplace')
def marketplace_page():
    return render_template('marketplace.html')