
import os
from app.database import db,bcrypt
from sqlalchemy import inspect,text
import random
import string 
from app.models.pipeline import Users

#Test if the database uri matches the one meant for testing
def test_connection(client):

    inspector = inspect(db.engine)
    all_tables = inspector.get_table_names()
    
    assert db.engine.url.render_as_string(hide_password=False) == f'postgresql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("TEST_DB_NAME")}'
    for table_name in all_tables:
        res = db.session.execute(text(f" select count(*) from {table_name};"))
        count = res.scalar()
        assert count == 0
    
#testing adding a user to the database and seeing if it makes it to the ORM
def test_adding_user(client):
    username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    email = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)) + '@' +''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))


    response = client.post("/create", data = {'username': username, 'email': email, 'password': password})

    assert Users.query.count() == 1
    assert Users.query.first().username == username
    assert Users.query.first().email == email
    assert bcrypt.check_password_hash(Users.query.first().password, password)
    assert response.status_code == 302
