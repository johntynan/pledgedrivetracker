# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################  

# auth.settings.create_user_groups=False
# auth.settings.login_next=URL(r=request, c='default', f='set_cookies')


def url(f, args=[]): return URL(r=request,f=f,args=args)

error_page=URL(r=request,f='error')

@auth.requires_login()
def check_session_organization():
    if not request.function=='session_organization_id_form' and not session.organization:
        redirect(URL(r=request, f='session_organization_id_form'))

@auth.requires_login()
def check_session_pledgedrive():
    if not request.function=='session_pledgedrive_id_form' and not session.pledgedrive:
        redirect(URL(r=request, f='session_pledgedrive_id_form'))

@auth.requires_login()
def check_session_program():
    if not request.function=='session_program_id_form' and not session.program:
        redirect(URL(r=request, f='session_program_id_form'))

@auth.requires_login()
def check_session_person():
    if not request.function=='session_person_id_form' and not session.person:
        redirect(URL(r=request, f='session_person_id_form'))

@auth.requires_login()
def check_session_challenge():
    if not request.function=='session_challenge_id_form' and not session.challenge:
        redirect(URL(r=request, f='session_challenge_id_form'))

@auth.requires_login()
def check_session_segment():
    if not request.function=='session_segment_id_form' and not session.segment:
        redirect(URL(r=request, f='session_segment_id_form'))

def check_session():
    check_session_organization()
    check_session_pledgedrive()
    # segments are not required for challenges or programs, we'll check for them anyway
    check_session_segment()
    # create check_session classes for programs and challenges when adding a segment
    # check for persons when adding a challenge
                
def error():
    return dict(message='something is wrong')

@auth.requires_login()
def index():
    check_session()
    check_session_program()
    check_session_person()
    check_session_challenge()
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """

    response.flash = T('Welcome to the Pledge Drive Tracker')

    organization = session.organization
    pledgedrive=session.pledgedrive
    program=session.program
    person=session.person
    challenge=session.challenge
    segment=session.segment
 
    return dict(message=T('Pledge Drive Tracker'),organization=organization,pledgedrive=pledgedrive,person=person,challenge=challenge,segment=segment)


@auth.requires_login()
def session_organization_id_form():
    organizations=db(db.organization.created_by==auth.user.id).select(orderby=db.organization.name)    
    ids=[o.id for o in organizations]
    names=[o.name for o in organizations]

    form=SQLFORM.factory(Field('organization_id',requires=IS_IN_SET(ids,names))) 
    
    if form.accepts(request.vars, session):
        session.organization_id = form.vars.organization_id
        organization = db(db.organization.id==session.organization_id).select()
        session.organization = organization
        session.organization_name = organization[0].name
        redirect(URL(r=request, f='index'))

    return dict(form=form,organizations=organizations)

@auth.requires_login()
def session_pledgedrive_id_form():

    pledgedrives=db(db.pledgedrive.organization==session.organization_id).select(orderby=db.pledgedrive.title)    
    ids=[o.id for o in pledgedrives]
    titles=[o.title for o in pledgedrives]

    form=SQLFORM.factory(Field('pledgedrive_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        session.pledgedrive_id = form.vars.pledgedrive_id
        pledgedrive = db(db.pledgedrive.id==session.pledgedrive_id).select()
        session.pledgedrive = pledgedrive
        session.pledgedrive_title = pledgedrive[0].title
        redirect(URL(r=request, f='index'))

    return dict(form=form,pledgedrives=pledgedrives)

@auth.requires_login()
def session_segment_id_form():

    segments=db(db.segment.organization==session.organization_id).select(orderby=db.segment.title)    
    ids=[o.id for o in segments]
    titles=[o.title for o in segments]

    form=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        session.segment_id = form.vars.segment_id
        segment = db(db.segment.id==session.segment_id).select()
        session.segment = segment
        session.segment_name = segment[0].title
        redirect(URL(r=request, f='index'))

    return dict(form=form,segments=segments)

def session_program_id_form():

    programs=db(db.program.organization==session.organization_id).select(orderby=db.program.title)    
    ids=[o.id for o in programs]
    titles=[o.title for o in programs]

    form=SQLFORM.factory(Field('program_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        session.program_id = form.vars.program_id
        program = db(db.program.id==session.program_id).select()
        session.program = program
        session.program_name = program[0].title
        redirect(URL(r=request, f='index'))

    return dict(form=form,programs=programs)

@auth.requires_login()
def session_person_id_form():

    persons=db(db.person.organization==session.organization_id).select(orderby=db.person.name)    
    ids=[o.id for o in persons]
    names=[o.name for o in persons]

    form=SQLFORM.factory(Field('person_id',requires=IS_IN_SET(ids,names))) 
    
    if form.accepts(request.vars, session):
        session.person_id = form.vars.person_id
        person = db(db.person.id==session.person_id).select()
        session.person = person
        session.person_name = person[0].name
        redirect(URL(r=request, f='index'))

    return dict(form=form,persons=persons)

@auth.requires_login()
def session_challenge_id_form():

    challenges=db(db.challenge.pledgedrive==session.pledgedrive_id).select(orderby=db.challenge.title)    
    ids=[o.id for o in challenges]
    titles=[o.title for o in challenges]

    form=SQLFORM.factory(Field('challenge_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        session.challenge_id = form.vars.challenge_id
        challenge = db(db.challenge.id==session.challenge_id).select()
        session.challenge = challenge
        redirect(URL(r=request, f='index'))

    return dict(form=form,challenges=challenges)
    
@auth.requires_login()
def create_organization():
    # check_session()
    form=crud.create(db.organization,next=url('index'))
    return dict(form=form)

@auth.requires_login()
def view_organization():
    check_session()
    organization_id=session.organization_id
    organization=db.organization[organization_id] or redirect(error_page)
    return dict(organization=organization)

@auth.requires_login()
def list_organizations():
    check_session()
    organizations=db(db.organization.created_by==auth.user.id).select(orderby=db.organization.name)
    return dict(organizations=organizations)

@auth.requires_login()
def edit_organization():
    check_session()
    organization_id=session.organization_id
    organization=db.organization[organization_id] or redirect(error_page)
    form=crud.update(db.organization,organization,next=url('index'))
    return dict(form=form)

@auth.requires_login()
def create_person():
    check_session_organization()
    organization_id=session.organization_id
    organization=db.organization[organization_id] or redirect(error_page)
    # form=crud.create(db.person,next=url('list_persons_by_organization',organization_id))
    form=crud.create(db.person,next=url('index'))
    return dict(form=form,organization=organization)

@auth.requires_login()
def view_person():
    check_session()
    person_id=request.args(0)
    person=db.person[person_id] or redirect(error_page)
    return dict(person=person)

@auth.requires_login()
def list_persons():
    check_session()
    persons=db(db.person.organization==session.organization_id).select(orderby=db.person.name)
    return dict(persons=persons)

@auth.requires_login()
def edit_person():
    check_session()
    person_id=request.args(0)
    person=db.person[person_id] or redirect(error_page)
    # form=crud.update(db.person,person,next=url('view_person',person_id))
    form=crud.update(db.person,person,next=url('index'))
    return dict(form=form)

@auth.requires_login()    
def list_persons_by_organization():
    check_session()
    organization_id=session.organization_id
    organization=db.organization[organization_id] or redirect(error_page)
    persons=db(db.person.organization==organization.id).select(orderby=db.person.name)
    return dict(organization=organization, persons=persons)

@auth.requires_login()
def create_program():
    check_session_organization()
    organization_id=session.organization_id
    organization=db.organization[organization_id] or redirect(error_page)
    form=crud.create(db.program,next=url('index'))
    return dict(form=form,organization=organization)

@auth.requires_login()
def view_program():
    check_session()
    program_id=request.args(0)
    program=db.program[program_id] or redirect(error_page)
    return dict(program=program)

@auth.requires_login()
def list_programs():
    check_session()
    programs=db(db.program.organization==session.organization_id).select(orderby=db.program.title)
    return dict(programs=programs)

@auth.requires_login()
def edit_program():
    check_session()
    program_id=request.args(0)
    program=db.program[program_id] or redirect(error_page)
    # form=crud.update(db.program,program,next=url('view_program',program_id))
    form=crud.update(db.program,program,next=url('index'))
    return dict(form=form)

@auth.requires_login()
def list_programs_by_organization():
    check_session()
    organization_id=session.organization_id
    organization=db.organization[organization_id] or redirect(error_page)
    programs=db(db.program.organization==organization.id).select(orderby=db.program.title)
    return dict(organization=organization, programs=programs)

@auth.requires_login()
def create_pledgedrive():
    check_session_organization()
    # form=crud.create(db.pledgedrive,next=url('list_pledgedrives'))
    form=crud.create(db.pledgedrive,next=url('index'))
    return dict(form=form)

@auth.requires_login()
def view_pledgedrive():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    return dict(pledgedrive=pledgedrive)

@auth.requires_login()
def list_pledgedrives():
    check_session()
    pledgedrives=db(db.pledgedrive.organization==session.organization_id).select(orderby=db.pledgedrive.title)
    return dict(pledgedrives=pledgedrives)

@auth.requires_login()
def edit_pledgedrive():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    form=crud.update(db.pledgedrive,pledgedrive,next=url('view_pledgedrive',pledgedrive_id))
    return dict(form=form)

@auth.requires_login()
def list_pledgedrives_by_organization():
    check_session_organization()
    organization_id=session.organization_id
    organization=db.organization[organization_id] or redirect(error_page)
    pledgedrives=db(db.pledgedrive.organization==organization.id).select(orderby=db.pledgedrive.title)
    # dollar_goal = db.pledgedrive.pledge_goal * db.pledgedrive.projected_average_pledge
    dollar_goal = 'TBD'
    return dict(organization=organization, pledgedrives=pledgedrives, dollar_goal=dollar_goal)

@auth.requires_login()
def create_challenge():
    check_session_organization()
    check_session_pledgedrive()
    check_session_person()
    organization=session.organization_id
    pledgedrive_id=session.pledgedrive_id
    person_id=session.person_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    person=db.person[person_id] or redirect(error_page)
    form=crud.create(db.challenge,next=url('index'))
    """
    form=SQLFORM(db.challenge)
    if FORM.accepts(form,request.vars):
        session.form_vars=form.vars
    """ 
    return dict(form=form,pledgedrive=pledgedrive,organization=organization,person=person)

@auth.requires_login()
def view_challenge():
    challenge_id=session.challenge_id
    challenge=db.challenge[challenge_id] or redirect(error_page)
    return dict(challenge=challenge)

@auth.requires_login()
def list_challenges():
    check_session()
    challenges=db(db.challenge.organization==session.organization_id).select(orderby=db.challenge.title)
    return dict(challenges=challenges)

@auth.requires_login()
def edit_challenge():
    challenge_id=session.challenge_id
    challenge=db.challenge[challenge_id] or redirect(error_page)
    form=crud.update(db.challenge,challenge,next=url('view_challenge',challenge_id))
    return dict(form=form)

@auth.requires_login()
def list_challenges_by_pledgedrive():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    challenges=db(db.challenge.pledgedrive==pledgedrive.id).select(orderby=db.challenge.title)
    return dict(pledgedrive=pledgedrive, challenges=challenges)

@auth.requires_login()
def create_segment():
    check_session_organization()
    check_session_pledgedrive()
    check_session_program()
    check_session_person()
    check_session_challenge()
    
    # form=crud.create(db.segment,next=url('list_segments'))
    form=crud.create(db.segment,next=url('index'))
    return dict(form=form)

@auth.requires_login()
def view_segment():
    check_session()
    segment_id=request.args(0)
    segment=db.segment[segment_id] or redirect(error_page)
    return dict(segment=segment)

@auth.requires_login()
def list_segments():
    segments=db(db.segment.organization==session.organization_id).select(orderby=db.segment.title)
    return dict(segments=segments)

@auth.requires_login()
def list_segments_by_pledgedrive():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    segments=db(db.segments.pledgedrive==pledgedrive.id).select(orderby=db.segments.start_time)
    return dict(pledgedrive=pledgedrive, segments=segments)

@auth.requires_login()
def edit_segment():
    check_session()
    segment_id=request.args(0)
    segment=db.segment[segment_id] or redirect(error_page)
    form=crud.update(db.segment,segment,next=url('view_segment',segment_id))
    return dict(form=form)

@auth.requires_login()
def list_segments_by_pledgedrive():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    segments=db(db.segment.pledgedrive==pledgedrive.id).select(orderby=db.segment.title)
    return dict(pledgedrive=pledgedrive, segments=segments)

@auth.requires_login()
def create_pledge():
    check_session()
    segment_id=session.segment_id
    segment=db.segment[segment_id] or redirect(error_page)
    form=crud.create(db.pledge)
    return dict(form=form,segment=segment)

@auth.requires_login()
def view_pledge():
    check_session()
    pledge_id=request.args(0)
    pledge=db.pledge[pledge_id] or redirect(error_page)
    return dict(pledge=pledge)

@auth.requires_login()
def list_pledges():
    check_session()
    pledges=db(db.pledge.id>0).select(orderby=db.pledge.name)
    return dict(pledges=pledges)

@auth.requires_login()
def list_pledges_by_pledgedrive():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    pledges=db(db.pledge.pledgedrive==pledgedrive.id).select(orderby=db.pledge.id)
    return dict(pledges=pledges)

@auth.requires_login()
def list_pledges_by_segment():
    check_session()
    segment_id=request.args(0)
    pledgedrive=db.pledgedrive[segment_id] or redirect(error_page)
    pledges=db(db.pledge.segment==segment_id).select(orderby=db.pledge.id)
    return dict(pledges=pledges,segment_id=segment_id)
        
@auth.requires_login()
def edit_pledge():
    check_session()
    pledge_id=request.args(0)
    pledge=db.pledge[pledge_id] or redirect(error_page)
    form=crud.update(db.pledge,pledge,next=url('view_pledge',pledge_id))
    return dict(form=form)

@auth.requires_login()
def list_pledges_by_pledgedrive():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    pledges=db(db.pledge.pledgedrive==pledgedrive.id).select(orderby=db.pledge.id)
    return dict(pledgedrive=pledgedrive, pledges=pledges)

def frame_header():
    check_session()
    # organization_id = request.cookies['organization_id'].value if 'organization_id' in request.cookies else 'unknown'
    organization_id = session.organization_id
    organizations=db(db.organization.id==organization_id).select()
    return dict(message=T('Pledge Drive Tracker'),organizations=organizations,organization_id=organization_id)

def frame_wrapper_onair():
    check_session()
    return dict()

def frame_onair():
    check_session()
    return dict()

def frame_wrapper_pledge_entry():
    check_session()
    return dict()

def frame_pledge_entry():
    check_session()
    return dict()

def report_mini_segment_goal():
    check_session()
    return dict()

def report_mini_segment_challenge():
    check_session()
    return dict()

def report_mini_segment_select():
    check_session()
    return dict()

def report_mini_segment_overview():
    check_session()
    return dict()

def report_mini_pledgedrive_goal():
    check_session()
    return dict()
    
@auth.requires_login()
def mini_create_pledge():
    check_session()
    segment_id=session.segment_id
    segment=db.segment[segment_id] or redirect(error_page)
    form=crud.create(db.pledge)
    return dict(form=form,segment=segment)

@service.json
def mini_pledgedrive_goal():
    check_session()
    return dict()

@service.json
def mini_pledgedrive_totals():
    check_session()

    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db(db.pledgedrive.id==pledgedrive_id).select()
    
    pledgedrive_total_pledges = len(db(db.pledge.pledgedrive==pledgedrive_id).select())

    pledge_amounts_for_pledgdrive = db(db.pledge.pledgedrive==pledgedrive_id).select(db.pledge.amount.sum())

    pledgedrive_total_dollars=pledge_amounts_for_pledgdrive[0]._extra[db.pledge.amount.sum()]
        
    return dict(pledgedrive_total_pledges=pledgedrive_total_pledges,pledgedrive_total_dollars=pledgedrive_total_dollars)

    # content = DIV('<h1>Drive Totals</h1>' + '<p><strong>Total Pledges</strong>: <strong>'+ str(pledgedrive_total_pledges) + '</strong>',  _id='content')
    # return dict(content=content)

    
@service.json
def mini_segment_goal():
    check_session()

    segment_id=session.segment_id
    segment=db(db.segment.id==segment_id).select()
    
    segment_total_pledges = len(db(db.pledge.segment==segment_id).select())

    pledge_amounts_for_segment = db(db.pledge.segment==segment_id).select(db.pledge.amount.sum())

    segment_total_dollars=pledge_amounts_for_segment[0]._extra[db.pledge.amount.sum()]
    
    if segment[0].goal_type == 'Pledge':
    
        goal = 'Pledge Goal:' + str(segment[0].goal)
        progress = segment[0].goal - segment_total_pledges 
    else:
        goal = 'Dollar Goal:'+  str(segment[0].goal)
        progress = segment[0].goal - segment_total_dollars 

    return dict(segment_total_pledges=segment_total_pledges,segment_total_dollars=segment_total_dollars,goal=goal,progress=progress)    

@service.json
def mini_segment_totals():
    check_session()

    segment_id=session.segment_id
    segment=db(db.segment.id==segment_id).select()
    
    segment_total_pledges = len(db(db.pledge.segment==segment_id).select())

    pledge_amounts_for_segment = db(db.pledge.segment==segment_id).select(db.pledge.amount.sum())

    segment_total_dollars=pledge_amounts_for_segment[0]._extra[db.pledge.amount.sum()]
        
    return dict(segment_total_pledges=segment_total_pledges,segment_total_dollars=segment_total_dollars)    
    
@service.json
def mini_segment_challenge():
    check_session()

    segment_id=session.segment_id
    segment=db(db.segment.id==segment_id).select()
    challenge_id = segment[0].challenge
    
    segment_challenge = db(db.challenge.id==challenge_id).select()

    return dict(challenge_id=challenge_id,segment_challenge=segment_challenge)

@service.json
@service.jsonrpc
@service.xml
@service.xmlrpc
@service.run
def service_pledgedrive_pledges(pledgedrive_id):
    pledgedrive_id=pledgedrive_id
    # pledgedrive_id=session.pledgedrive_id
    # pledgedrive_id=request.vars.pledgedrive_id

    # pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select()
    pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select().as_list()

    return dict(pledgedrive_pledges=pledgedrive_pledges)
    
def create_message():
    form = crud.create(db.message)
    return dict(form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
