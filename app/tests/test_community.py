import random
import string

def test_route(client):

    #create a user and log them in to get a session going
    dummy_username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    dummy_email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    dummy_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    client.post("/create", data = {'username': dummy_username, 'email': dummy_email, 'password': dummy_password})

    response = client.get('/community')
    
    assert response.data is not None
    assert b"<h2>Community</h2>" in response.data
    