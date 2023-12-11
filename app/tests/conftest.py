import os 
import pytest


from app import create_app
from ..database import db
from sqlalchemy import text


@pytest.fixture()
def app(): 
    
    #flag for testing
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    clear_db()
    yield app
    clear_db()
   


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli.runner()


#clear database function

def clear_db():
   
    delete_command = """
            select tablename from pg_tables where schemaname = 'test_thriftme';

            DO $$
            DECLARE
                table_name text;
            BEGIN
                FOR table_name IN (SELECT tablename FROM pg_catalog.pg_tables where schemaname= 'public')
                LOOP
                    EXECUTE 'DELETE FROM ' || quote_ident(table_name) || ' CASCADE';
                END LOOP;
            END $$;
                    """
    db.session.execute(text(delete_command))
    db.session.commit()
