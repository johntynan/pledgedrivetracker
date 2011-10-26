# coding: utf8

# is_phone=IS_MATCH('(\d{2}\-)?[\d\-]+(\#\d+)?')
# * allows for empty phone number?
is_phone=IS_MATCH('(\d{2}\-)?[\d\-]*(\#\d+)?$')

if auth.is_logged_in():
    me=auth.user.id
else:
    me=None

"""
auth=Auth(globals(),db)

auth.settings.table_user = db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length=128,default=''),
    Field('last_name', length=128,default=''),
    Field('password', 'password', readable=False,label='Password', requires=CRYPT()),
    Field('registration_key', length=128,writable=False, readable=False,default=''),
    # Field('organization',db.organization,requires=IS_IN_DB(db,'organization.id','%(name)s')),
    Field('email', length=128,default='',requires = [IS_EMAIL(),IS_NOT_IN_DB(db,'%s.email'%self.settings.table_user_name)])

    )
auth.settings.table_user=db.auth_user
auth.define_tables() 
"""

ROLE_TYPES = ('Donor','Listener')
GOAL_TYPES = ('Dollar','Pledge')
CHALLENGE_TYPES = ('Matching','Pledge')
CHALLENGE_CONDITIONS = ('Refundable','Non-refundable')
CHALLENGE_STATES = ('Pending','Achieved','Missed','Recycled')
#CHALLENGE_OPTIONS = ('Never', 'Optional', 'Mandatory')

db.define_table('organization',
    Field('name', unique=True),
    Field('url', unique=True),
    Field('address'),
    Field('phone'),
    Field('phone_long_distance'),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )

db.organization.name.requires=[IS_NOT_EMPTY()]
db.organization.url.requires=IS_URL()
db.organization.phone.requires=is_phone

db.define_table('person',
    Field('name'),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('role'),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
#Validate:
#On Insert: Select person name and if organizations are the same, do not insert; validate that user is in group for organization, else deny.
#On Read: Validate that user is in group for organization, else deny.

db.person.name.requires=[IS_NOT_EMPTY()]
db.person.role.requires=IS_IN_SET(ROLE_TYPES)
db.person.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')

db.define_table('program',
    Field('title'),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
#Validate:
#On Insert: Select program name and if organizations are the same, do not insert; validate that user is in group for organization, else deny.
#On Read: Validate that user is in group for organization, else deny.

db.program.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')

db.define_table('pledgedrive',
    Field('title'),
    Field('start_time','datetime'),
    Field('end_time','datetime'),
    Field('description','text'),
    Field('pledge_goal','integer'),
    Field('projected_average_pledge','double'),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
#Validate:
#On Insert: Select on pledgedrive title and if organizations are the same, do not insert; validate that user is in group for organization, else deny.
#On Read: Validate that user is in group for organization, else deny.
    
db.pledgedrive.title.requires=IS_NOT_EMPTY()
db.pledgedrive.start_time.default=request.now
db.pledgedrive.end_time.default=request.now
db.pledgedrive.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
db.pledgedrive.start_time.requires=IS_DATETIME('%Y-%m-%d %H:%M:%S')
db.pledgedrive.end_time.requires=IS_DATETIME('%Y-%m-%d %H:%M:%S')
db.pledgedrive.pledge_goal.requires=IS_NOT_EMPTY()
db.pledgedrive.projected_average_pledge.requires=IS_NOT_EMPTY()

db.define_table('segment',
    Field('title'),
    Field('start_time','datetime'),
    Field('end_time','datetime'),
    Field('description','text'),
    Field('talkingpoints','text'),
    Field('goal','integer'),
    Field('goal_type'),
    Field('program',db.program,'%(title)s'),
    Field('pledgedrive',db.pledgedrive,default=session.pledgedrive_id,readable=False,writable=False),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
#Validate:
#On Insert: Select on title/program/pledgedrive and if organizations are the same, do not insert; validate program and pledgedrive are connected to org; validate that user is in group for organization, else deny;      
#On Read: Validate that user is in group for organization, else deny.

db.segment.title.requires=IS_NOT_EMPTY()
db.segment.goal.requires=IS_NOT_EMPTY()
db.segment.start_time.default=request.now
db.segment.end_time.default=request.now
db.segment.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
db.segment.program.requires=IS_IN_DB(db(db.program.organization==session.organization_id),db.program.id,'%(title)s')
db.segment.pledgedrive.requires=IS_IN_DB(db,'pledgedrive.id','%(title)s')
db.segment.start_time.requires=IS_DATETIME('%Y-%m-%d %H:%M:%S')
db.segment.end_time.requires=IS_DATETIME('%Y-%m-%d %H:%M:%S')
db.segment.goal.requires=IS_NOT_EMPTY()
db.segment.goal_type.requires=IS_IN_SET(GOAL_TYPES)


db.define_table('challenge',
    Field('title'),
    Field('person',db.person,'%(name)s'),
    Field('pledgedrive',db.pledgedrive,default=session.pledgedrive_id,readable=False,writable=False),
    Field('segment',db.segment,default=session.segment_id),
    Field('amount','integer'),
    Field('description','text'),
    Field('type'),
    Field('condition'),
    Field('state'),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)    
)
#Validate:
#On Insert: Select on title/person/pledgedrive/segment and if organizations are the same, do not insert; validate person and pledgedrive are connected to org; validate that user is in group for organization, else deny;      
#On Read: Validate that user is in group for organization, else deny.

db.challenge.person.requires=IS_IN_DB(db(db.person.organization==session.organization_id),db.person.id,'%(name)s')
db.challenge.pledgedrive.requires=IS_IN_DB(db,'pledgedrive.id','%(title)s')
db.challenge.segment.requires=IS_NULL_OR(IS_IN_DB(db(db.segment.pledgedrive==session.pledgedrive_id),db.segment.id,'%(title)s'))
db.challenge.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
db.challenge.type.requires=IS_IN_SET(CHALLENGE_TYPES)
db.challenge.condition.requires=IS_IN_SET(CHALLENGE_CONDITIONS)
db.challenge.state.requires=IS_IN_SET(CHALLENGE_STATES)
db.challenge.amount.requires=IS_NOT_EMPTY()


db.define_table('pledge',
    Field('amount','integer'),
    Field('name'),#should likely reference the person table...
    Field('comment'),
    Field('segment',db.segment,default=session.segment_id,readable=False,writable=False), 
    Field('pledgedrive',db.pledgedrive,default=session.pledgedrive_id,readable=False,writable=False),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
)
#Validate:
#On Insert: that segment has this pledgedrive; that pledgedrive shares this organization; validate that user is in group for organization, else deny;
#On Read: Validate that user is in group for organization, else deny.

# db.pledge.person.requires=IS_IN_DB(db,'person.id','%(name)s')
# db.pledge.program.requires=IS_IN_DB(db,'program.id','%(title)s')
db.pledge.segment.requires=IS_IN_DB(db,'segment.id','%(title)s')
db.pledge.pledgedrive.requires=IS_IN_DB(db,'pledgedrive.id','%(title)s')
db.pledge.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
# db.pledge.name.requires=IS_ALPHANUMERIC()
db.pledge.amount.requires=IS_NOT_EMPTY()

db.define_table('post',
    Field('body','text'),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    #should this also have an item for pledgedrive?
    )
#Validate:
#On Insert: validate that user is in group for organization, else deny;
#On Read: Validate that user is in group for organization, else deny;

db.post.body.requires=IS_NOT_EMPTY()
db.post.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')


#########################################################################
## for use with the unit tests in the applications/yourapp/tests directory
##
'''
import copy 
test_db = DAL('sqlite://testing.sqlite')  # DB name and location 
for tablename in db.tables:  # Copy tables! 
    table_copy = [copy.copy(f) for f in db[tablename]] 
    test_db.define_table(tablename, *table_copy) 
'''
#########################################################################
