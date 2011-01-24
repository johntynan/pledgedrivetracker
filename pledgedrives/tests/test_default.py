#!/usr/bin/python 
import sys 
import unittest

from gluon.globals import Request  # So we can reset the request for each test 

sys.arvg = sys.argv[5:]  # web2py.py passes the whole command line to this script.

# db = DAL('sqlite://testing.sqlite')
# db = DAL('sqlite:memory') 

db = test_db  # Rename the test database so that functions will use it instead of the real database.  See the end of db_pledgedrive.py

# print db

execfile("applications/pledgedrives/controllers/default.py", globals())  # Brings the controller's functions into this script's scope 

session.organization == 1
# organization = session.organization

# print organization

# check_person()

def test_create_user():
    """
    Add a new user to the test app.
    """

    print 'hello world'

def test_create_organization():
    """
    Add a new organization to the test app.
    """
    organization_id = 1

    organization = db(db.organization.id==organization_id).select()

    session.organization = organization.as_list()[0]
    session.organization_id = organization.as_list()[0]['id']

    print session.organization

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
