import os 
import pytest

from app import create_app


@pytest.fixture()
def app(): 
    
    #flag for testing
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli.runner()