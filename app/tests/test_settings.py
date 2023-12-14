
import random
import string
from app.models.pipeline import Users
from app.database import bcrypt


#Test creating a user account then deleting that account
def test_adding_and_deleting_user(client):
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))


    client.post("/create", data = {'username': username, 'email': email, 'password': password})
    response = client.get('/settings')

    assert Users.query.count() == 1
    assert Users.query.first().username == username
    assert response.status_code == 200
   
    response = client.get('/delete')


    assert Users.query.count() == 0
    assert Users.query.first() == None
   
#Test the ability to read the users account info. 
def test_read_user_data(client):
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))


    client.post("/create", data = {'username': username, 'email': email, 'password': password})
    response = client.get('/settings')

    assert b'*' and email.encode() and (b'Public' or b'Private') in response.data
    


#Test updating the users data from what it was when the account was created.
def test_update_user_data(client):
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

    new_email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(25)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(25))
    new_password= ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(19))

    client.post("/create", data = {'username': username, 'email': email, 'password': password})

    user = Users.get_by_username(username)
    curr_access = user.get_access()

    client.post('/edit' , data ={'flag' : 'change-access'})
    client.post('/edit', data = {'flag': 'change-email', 'email' : new_email})
    client.post('/edit', data= {'flag' : 'change-password', 'password' : new_password})

    assert curr_access != user.get_access()
    assert new_email == user.email
    assert bcrypt.check_password_hash(user.password, new_password)



