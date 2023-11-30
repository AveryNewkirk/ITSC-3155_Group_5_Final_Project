from flask import Blueprint, render_template, request, redirect, url_for,jsonify
import random

community = Blueprint('community', __name__)

limit = float('inf')
user = []


#just to test infinite scrolling
def generate_dummy_data():

    payload = [''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(10,20))) for i in range(9)]

    user.extend(payload) #append to the end of the user list if you want to limit the amount of posts a user can generate
                         #somewhat problematic as if the user hits the post limit and clicks off the page no posts will show up

    return payload

    

@community.route('/community')
def community_page():

    """
    TODO
    fix the amount of post that can be requested form each user and keep that template handy
    """

    fake_data = generate_dummy_data() 

    return render_template('community.html', fake_data=fake_data)


#Send data to the webpage
@community.route('/get_data')
def more_posts():
    if len(user) > limit:
        print("post limit exceeded")
        return ""

    data = generate_dummy_data()

    return jsonify ({'html': render_template('community_posts_batch.html', data=data)})
