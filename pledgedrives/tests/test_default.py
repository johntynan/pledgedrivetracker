#!/usr/bin/python 
import sys 
import unittest

from gluon.globals import Request  # So we can reset the request for each test 
from gluon.globals import Session, Storage, Response

sys.arvg = sys.argv[5:]  # web2py.py passes the whole command line to this script.

# db = DAL('sqlite://testing.sqlite')
# db = DAL('sqlite:memory') 

db = test_db  # Rename the test database so that functions will use it instead of the real database.  See the end of db_pledgedrive.py

# print db

execfile("applications/pledgedrives/controllers/default.py", globals())  # Brings the controller's functions into this script's scope 

request = Request()  # Use a clean request
session = Session()  # Use a clean session

# def user():
#     return dict(form = auth())


def test_create_user():
    """
    Add a new user to the test app.
    """
    db.auth_user.insert(first_name='fff', last_name='lll', email='whatever@localhost', password='mmm', registration_key="")
    user = db(db.auth_user.id=='1').select()
    auth.environment.session.auth = Storage(user=user, last_visit=request.now, expiration=auth.settings.expiration)
    # session.auth.user = Storage(user=user, last_visit=request.now, expiration=auth.settings.expiration)

    print user

    auth.login_bare('whatever@localhost', 'mmm')

    print auth.is_logged_in()

    # auth = auth.environment.session.auth

    # auth.user.id = '1'

    # session.auth.user.id = '1'

    # print auth.user.id

    # print auth.user

    # print session.auth.user

    # auth.impersonate(user_id='1')

    # print auth.retrieve_username()

    # check_session()

    # print db

    # print session

@auth.requires_login()
def test_create_organization():
    """
    Form to create a new organizations.
    """


test_create_user()

# test_create_organization()

# test_create_pledgedrive
# test_create_program
# test_create_segment
# test_create_person
# test_create_challenge
# test_create_pledge
# test_create_post

# index()
