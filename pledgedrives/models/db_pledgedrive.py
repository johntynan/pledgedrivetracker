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
GOAL_TYPES = ('Matching','Pledge')
CHALLENGE_TYPES = ('Matching','Pledge')
CHALLENGE_CONDITIONS = ('Refundable','Non-refundable')
CHALLENGE_STATES = ('Pending','Achieved','Missed','Recycled')


db.define_table('organization',
    Field('name'),
    Field('url'),
    Field('address'),
    Field('phone'),
    Field('phone_long_distance'),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
# db.organization.name.requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,'organization.name')]
db.organization.name.requires=[IS_NOT_EMPTY()]
db.organization.url.requires=IS_URL()
db.organization.phone.requires=is_phone

db.define_table('person',
    Field('name'),
    # for some reason, organization['id'] does not work here.  Have to save the organization_id in the session as a separate variable.
    # Field('organization',db.organization,default=session.organization['id'],readable=False,writable=False),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('role')
    )
# it may be possible to have a single donor contribute to multiple organizations.  Removing IS_NOT_IN_DB until this is ironed out.
# db.person.name.requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,'person.name')]
db.person.name.requires=[IS_NOT_EMPTY()]
db.person.role.requires=IS_IN_SET(ROLE_TYPES)
db.person.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')

db.define_table('program',
    Field('title'),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
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
db.pledgedrive.title.requires=IS_NOT_EMPTY()
db.pledgedrive.start_time.default=request.now
db.pledgedrive.end_time.default=request.now
db.pledgedrive.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')

db.define_table('challenge',
    Field('title'),
    # Field('person',db.person,default=session.person_id,readable=False,writable=False),
    Field('person',db.person,'%(name)s'),
    Field('pledgedrive',db.pledgedrive,default=session.pledgedrive_id,readable=False,writable=False),
    Field('amount','integer'),
    Field('description','text'),
    Field('talkingpoints','text'),
    # Field('type'),
    Field('condition'),
    Field('state'),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)    
)
db.challenge.person.requires=IS_IN_DB(db,'person.id','%(name)s')
db.challenge.pledgedrive.requires=IS_IN_DB(db,'pledgedrive.id','%(title)s')
db.challenge.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
# db.challenge.type.requires=IS_IN_SET(CHALLENGE_TYPES)
db.challenge.condition.requires=IS_IN_SET(CHALLENGE_CONDITIONS)
db.challenge.state.requires=IS_IN_SET(CHALLENGE_STATES)

db.define_table('segment',
    Field('title'),
    Field('start_time','datetime'),
    Field('end_time','datetime'),
    Field('description','text'),
    Field('goal','integer'),
    Field('goal_type'),
    Field('program',db.program,'%(title)s'),
    # Field('program',db.program,default=session.program_id,readable=False,writable=False),
    Field('challenge',db.challenge,'%(title)s'),
    # Field('challenge',db.challenge,default=session.challenge_id,readable=False,writable=False),
    Field('pledgedrive',db.pledgedrive,default=session.pledgedrive_id,readable=False,writable=False),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
db.segment.title.requires=IS_NOT_EMPTY()
db.segment.goal.requires=IS_NOT_EMPTY()
db.segment.start_time.default=request.now
db.segment.end_time.default=request.now
db.segment.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
db.segment.program.requires=IS_IN_DB(db,'program.id','%(title)s')
db.segment.pledgedrive.requires=IS_IN_DB(db,'pledgedrive.id','%(title)s')
db.segment.challenge.requires=IS_IN_DB(db,'challenge.id','%(title)s')
db.segment.goal_type.requires=IS_IN_SET(GOAL_TYPES)


db.define_table('pledge',
    Field('amount','integer'),
    Field('name'),
    Field('segment',db.segment,default=session.segment_id,readable=False,writable=False), 
    Field('pledgedrive',db.pledgedrive,default=session.pledgedrive_id,readable=False,writable=False),
    Field('organization',db.organization,default=session.organization_id,readable=False,writable=False),
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
)
# db.pledge.person.requires=IS_IN_DB(db,'person.id','%(name)s')
# db.pledge.program.requires=IS_IN_DB(db,'program.id','%(title)s')
db.pledge.segment.requires=IS_IN_DB(db,'segment.id','%(title)s')
db.pledge.pledgedrive.requires=IS_IN_DB(db,'pledgedrive.id','%(title)s')
db.pledge.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
db.pledge.name.requires=IS_ALPHANUMERIC()

db.define_table('message',
    Field('person',db.person),
    Field('body','text'),
    Field('organization',db.organization), # default=request.args(0),readable=False,writable=False 
    Field('created_by',default=me,writable=False,readable=False),
    Field('created_on','datetime',default=request.now,writable=False,readable=False)
    )
db.message.organization.requires=IS_IN_DB(db,'organization.id','%(name)s')
db.message.person.requires=IS_IN_DB(db,'person.id','%(name)s')
db.message.body.requires=IS_NOT_EMPTY()
