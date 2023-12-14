import random
import string

from app.models.pipeline import Users,CommunityPost,Photo
from io import BytesIO
from flask import url_for


#Test if the community route works properly
def test_route(client):

    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    client.post("/create", data = {'username': username, 'email': email, 'password': password})

    response = client.get('/community')
    
    assert response.data is not None
    assert b"<h2>Community</h2>" in response.data



    """
    The tests below simulates file uploads using the create post endpoint. 
    Be careful running these over and over as they will fill app/static/user_images with a bunch 
    of copies of the same picture since there is no code that deletes pictures from the filesystem.
    """

#Test if a user can create a post and then view said post in isolation
def test_create_and_read_post(client,app):
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    client.post("/create", data = {'username': username, 'email': email, 'password': password})


    with open('app/tests/file_test/Y2KBaggyJean.png', 'rb') as file:  
        
        client.post('/create_post', data = {'post-title' : 'test_post', 
                                                       'upload-pictures' :(BytesIO(file.read()),'Y2KBaggyJean.png')})
    

    post = CommunityPost.query.first()
    photo = Photo.query.first()
    with app.test_request_context():
        response = client.post(url_for('community.community_post_', community_post_id = post.get_id()))


    assert post.post_content.encode() in response.data
    assert photo.photo_url.encode() in response.data
    

#Test to create and delete posts from user
def test_create_and_delete_post(client,app):
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    client.post("/create", data = {'username': username, 'email': email, 'password': password})


    with open('app/tests/file_test/Y2KBaggyJean.png', 'rb') as file:  
        
        client.post('/create_post', data = {'post-title' : 'test_post', 
                                                       'upload-pictures' :(BytesIO(file.read()),'Y2KBaggyJean.png')})
    

    post = CommunityPost.query.first()
    post_id = post.get_id()
    with app.test_request_context():
        client.post(url_for('community.delete_post', community_post_id = post_id))
    
    assert CommunityPost.query.first() == None



#Test creates 2 users and one likes the others post and both comment on the post
def test_liking_and_commenting_on_other_user_post(client,client_2, app):
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    client.post("/create", data = {'username': username, 'email': email, 'password': password})

    other_username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    other_email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    other_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    client_2.post("/create", data = {'username': other_username, 'email': other_email, 'password': other_password})

    comment_data = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(19))
    other_comment_data = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(21))


    other_user = Users.get_by_username(other_username)
    with open('app/tests/file_test/Y2KBaggyJean.png', 'rb') as file:  
        
        client_2.post('/create_post', data = {'post-title' : 'test_post', 
                                                       'upload-pictures' :(BytesIO(file.read()),'Y2KBaggyJean.png')})
    

    post = CommunityPost.query.filter_by(user_id = other_user.user_id).first()

    
    client.post('/community_like', data= {'community_post_id' : int(post.get_id())})
    client.post('/community_comment', data = {'comment' : comment_data, 'curr_username' : username, 'community_post_id' : int(post.get_id())})
    client_2.post('/community_comment', data = {'comment' : other_comment_data, 'curr_username' : other_username, 'community_post_id' : int(post.get_id())})

    with app.test_request_context():
        response = client.get(url_for('community.community_post_', community_post_id = post.get_id()))

        assert b'<span id = "like-count">1</span>' in response.data
        assert comment_data.encode() in response.data
        assert other_comment_data.encode() in response.data