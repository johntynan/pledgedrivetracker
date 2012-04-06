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

import time, datetime

def url(f, args=[]): return URL(r=request,f=f,args=args)

error_page=URL(r=request,f='error')

@auth.requires_login()
def check_session_organization():
    """    
    Makes sure an organization for the current user is selected
    Checks for any organizations created by the current user; if none, redirect to create organization form.
    Checks for valid organization in session, else prompts to reselect
    >>> organizations=db(db.organization.created_by=="1").select().as_list()
    >>> organizations
    [{'phone': '480-834-5627', 'address': '2323 W. 14th Street Tempe, AZ 85281', 'id': 1, 'name': 'KUNC', 'url': 'http://kunc.org', 'created_on': '2010-01-24 23:28:15', 'created_by': '1', 'phone_long_distance': '1-800-888-8888'}]
    """
    organizations = db(db.organization.created_by==auth.user.id).select().as_list()
    valid = False
    if len(organizations) < 1:
        redirect(URL(r=request, f='create_organization'))
    elif (not request.function=='session_organization_id_form' and not session.organization):
        redirect(URL(r=request, f='session_organization_id_form'))
    elif not request.function=='session_organization_id_form':
        for rec in organizations:
            if rec['id'] == session.organization_id:
                valid = True
        if not valid:
            redirect(URL(r=request, f='session_organization_id_form'))

@auth.requires_login()
def check_session_pledgedrive():
    """
    Makes sure a pledgedrive for the current user is selected
    Checks for any pledgedrive created by the current user; if none, redirect to create organization form.
    Checks for valid organization in session, else prompts to reselect
    """
    #function assumes that the session.organization_id item is valid for the user
    #run after check_session_organization in sequence.
    pledgedrives=db(db.pledgedrive.organization==session.organization_id).select().as_list()
    valid = False
    if len(pledgedrives) < 1:
        redirect(URL(r=request, f='create_pledgedrive'))
    elif not request.function=='session_pledgedrive_id_form' and not session.pledgedrive:
        redirect(URL(r=request, f='session_pledgedrive_id_form'))
    elif not request.function=='session_pledgedrive_id_form':
        for rec in pledgedrives:
            if rec['id'] == session.pledgedrive_id:
                valid = True
        if not valid:
            redirect(URL(r=request, f='session_pledgedrive_id_form'))

@auth.requires_login()
def check_session_segment():
    """
    Makes sure a segment for the current user is selected
    """
    #function assumes that the session.pledgedrive_id item is valid for the user/organization
    #run after check_session_pledgedrive in sequence.
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select().as_list()
    valid = False
    if len(segments) < 1:
        redirect(URL(r=request, f='create_segment'))
    elif not request.function=='session_segment_id_form' and not session.segment:
        redirect(URL(r=request, f='session_segment_id_form'))
    elif not request.function=='session_segment_id_form':
        for rec in segments:
            if rec['id'] == session.segment_id:
                valid = True
        if not valid:
            redirect(URL(r=request, f='session_segment_id_form'))
            
@auth.requires_login()
def check_session():
    """
    Sets an order for checking that certain defaults for the program are set and stored in the session
    """
    check_session_organization()
    check_session_pledgedrive()
    check_session_segment()

@auth.requires_login()
def check_program():
    """
    Makes sure a program for the current user is selected
    """
    programs=db(db.program.organization==session.organization_id).select().as_list()
    if len(programs) < 1:
        redirect(URL(r=request, f='create_program'))

@auth.requires_login()
def check_challenge():
    """
    Makes sure a challenge for the current user is selected
    """
    challenges=db(db.challenge.pledgedrive==session.pledgedrive_id).select().as_list()
    if len(challenges) < 1:
        redirect(URL(r=request, f='create_challenge'))

@auth.requires_login()
def check_person():
    """
    Makes sure a person for the current user is selected
    """
    persons=db(db.person.organization==session.organization_id).select().as_list()
    if len(persons) < 1:
        redirect(URL(r=request, f='create_person'))

def error():
    """
    Display error message.
    """
    return dict(message='something is wrong')

def get_valid_id(item_id, table):
    """
    Makes sure a record belongs to the organization before it is selected
    """
    try:
        onerec = db(table.id == item_id).select()[0]
        if onerec['organization']==session.organization_id:
            return item_id
        else:
            redirect(error_page)
    except:
            redirect(error_page)

@auth.requires_login()
def index():
    """
    Loads the initial page for the app.  Sets the defaults.
    """
    check_session()

    organization = session.organization
    pledgedrive=session.pledgedrive
    program=session.program
    person=session.person
    challenge=session.challenge
    segment=session.segment

    return dict(pledgedrive=pledgedrive,person=person,challenge=challenge,segment=segment)


@auth.requires_login()
def session_organization_id_form():
    """
    Prompts the user to select an organization or create a new one.
    """
    organizations=db(db.organization.created_by==auth.user.id).select(orderby=db.organization.name)    
    ids=[o.id for o in organizations]
    names=[o.name for o in organizations]

    form=SQLFORM.factory(Field('organization_id',requires=IS_IN_SET(ids,names))) 
    
    if form.accepts(request.vars, session):
        organization_id = form.vars.organization_id
        organization = db(db.organization.id==organization_id).select()
        session.organization = organization.as_list()[0]
        session.organization_id = organization.as_list()[0]['id']
        redirect(URL(r=request, f='index'))

    response.flash = T('Add or select an organization to make it the current working organization.')
    return dict(form=form,organizations=organizations)

@auth.requires_login()
def session_pledgedrive_id_form():
    """
    Prompts the user to select an pledgedrive or create a new one.
    """
    pledgedrives=db(db.pledgedrive.organization==session.organization_id).select(orderby=db.pledgedrive.title)
    ids=[o.id for o in pledgedrives]
    titles=[o.title for o in pledgedrives]

    form=SQLFORM.factory(Field('pledgedrive_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        pledgedrive_id = form.vars.pledgedrive_id
        pledgedrive = db(db.pledgedrive.id==pledgedrive_id).select()
        session.pledgedrive = pledgedrive.as_list()[0]
        session.pledgedrive_id = pledgedrive.as_list()[0]['id']
        redirect(URL(r=request, f='index'))

    return dict(form=form,pledgedrives=pledgedrives)

@auth.requires_login()
def session_segment_id_form():
    """
    Prompts the user to select a segment or create a new one.
    """
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    titles=[o.title for o in segments]

    form=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        segment_id = form.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']
        redirect(URL(r=request, f='index'))

    return dict(form=form,segments=segments)

def session_program_id_form():
    """
    Prompts the user to select a program or create a new one.
    """
    programs=db(db.program.organization==session.organization_id).select(orderby=db.program.title)    
    ids=[o.id for o in programs]
    titles=[o.title for o in programs]

    form=SQLFORM.factory(Field('program_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        program_id = form.vars.program_id
        program = db(db.program.id==program_id).select()
        session.program = program.as_list()[0]
        session.program_id = program.as_list()[0]['id']
        redirect(URL(r=request, f='index'))

    return dict(form=form,programs=programs)

@auth.requires_login()
def session_person_id_form():
    """
    Prompts the user to select a person or create a new one.
    """
    persons=db(db.person.organization==session.organization_id).select(orderby=db.person.name)    
    ids=[o.id for o in persons]
    names=[o.name for o in persons]

    form=SQLFORM.factory(Field('person_id',requires=IS_IN_SET(ids,names))) 
    
    if form.accepts(request.vars, session):
        person_id = form.vars.person_id
        person = db(db.person.id==person_id).select()
        session.person = person.as_list()[0]
        session.person_id = person.as_list()[0]['id']
        redirect(URL(r=request, f='index'))

    return dict(form=form,persons=persons)

@auth.requires_login()
def session_challenge_id_form():
    """
    Prompts the user to select a challenge or create a new one.
    """
    challenges=db(db.challenge.pledgedrive==session.pledgedrive_id).select(orderby=db.challenge.title)    
    ids=[o.id for o in challenges]
    titles=[o.title for o in challenges]

    form=SQLFORM.factory(Field('challenge_id',requires=IS_IN_SET(ids,titles))) 
    
    if form.accepts(request.vars, session):
        challenge_id = form.vars.challenge_id
        challenge = db(db.challenge.id==challenge_id).select()
        session.challenge = challenge.as_list()[0]
        session.challenge_id = challenge.as_list()[0]['id']
        redirect(URL(r=request, f='index'))

    return dict(form=form,challenges=challenges)
    
#TODO: Don't think this method is needed anymore....
@auth.requires_login()
def create_organization():
    """
    Form to create a new organizations.
    """

    form = SQLFORM(db.organization)

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        organization_id = dict(form.vars)['id']
        organization = db(db.organization.id==organization_id).select()

        session.organization = organization.as_list()[0]
        session.organization_id = organization.as_list()[0]['id']

        redirect(URL(r=request, f='index'))

    elif form.errors: response.flash='form errors'
    return dict(form=form)

#TODO: Don't think this method is needed anymore....
@auth.requires_login()
def view_organization():
    """
    Display details about an organization
    """

    check_session()
    organization_id=request.args(0)#only without call to get_valid_id(request.args(0),db.table), since validated below 
    # organization_id=session.organization['id']
    organizations=db(db.organization.created_by==auth.user.id).select(orderby=db.organization.name)
    organization=db.organization[organization_id] or redirect(error_page)
    if organization in organizations:
        return dict(organization=organization)
    else:
        redirect(error_page)
        
@auth.requires_login()
def list_organizations():
    """
    List organizations created by the current user.
    """
    check_session()
    new_item = False
    if request.args(0):
        try:
            record = db((db.organization.id == request.args(0)) & (db.organization.created_by == auth.user.id)).select()[0]
        except:
            redirect(URL('default', 'list_organizations'))
        form = SQLFORM(db.organization, record, deletable=True)
    else:
        form  = SQLFORM(db.organization)
        new_item = True
    if form.process().accepted:
        response.flash = 'Organization Updated'
    elif form.errors:
        response.flash = 'There were errors in the form.  Please check your work and try again.'
    organizations=db(db.organization.created_by==auth.user.id).select(orderby=db.organization.name)
    return dict(organizations=organizations, form = form, new_item = new_item)

#TODO: Don't think this method is needed anymore....
@auth.requires_login()
def edit_organization():
    """
    Docstring here.
    """
    check_session()
    organization_id=session.organization['id']
    organization=db.organization[organization_id] or redirect(error_page)
    form=crud.update(db.organization,organization,next=url('list_organizations'),deletable=False)
    return dict(form=form)

@auth.requires_login()
def create_person():
    """
    Docstring here.
    """
    check_session_organization()
    organization_id=session.organization['id']
    organization=db.organization[organization_id] or redirect(error_page)
    form=crud.create(db.person,next=url('create_challenge'))
    return dict(form=form,organization=organization)

@auth.requires_login()
def view_person():
    """
    Docstring here.
    """
    check_session()
    person_id=get_valid_id(request.args(0),db.person)
    person=db.person[person_id] or redirect(error_page)
    return dict(person=person)

@auth.requires_login()
def list_persons():
    """
    Docstring here.
    """
    check_session()
    persons=db(db.person.organization==session.organization['id']).select(orderby=db.person.name)
    return dict(persons=persons)

@auth.requires_login()
def edit_person():
    """
    Docstring here.
    """
    check_session()
    person_id=get_valid_id(request.args(0),db.person)
    person=db.person[person_id] or redirect(error_page)
    form=crud.update(db.person,person,next=url('list_persons_by_organization'))
    return dict(form=form)

@auth.requires_login()    
def list_persons_by_organization():
    """
    Docstring here.
    """
    check_session()
    organization_id=session.organization['id']
    organization=db.organization[organization_id] or redirect(error_page)
    persons=db(db.person.organization==organization.id).select(orderby=db.person.name)
    return dict(organization=organization, persons=persons)

@auth.requires_login()
def create_program():
    """
    Docstring here.
    """
    check_session_organization()
    organization_id=session.organization['id']
    organization=db.organization[organization_id] or redirect(error_page)
    # rather than show the programs already in the database for this organization, how can we check to see that the program title entered is unique 
    # (not to the db) but to this particular organization?
    programs=db(db.program.organization==organization_id).select().as_list()

    form=crud.create(db.program,next=url('create_segment'))
    return dict(form=form,organization=organization,programs=programs)

@auth.requires_login()
def create_program_import():
    """
    Docstring here.
    """
#    form = FORM(str(T('or import from csv file'))+" ",INPUT(_type='file',_name='csvfile'),INPUT(_type='submit',_value='import'))
    form = FORM(str(T('List of Programs'))+" ", INPUT(_type='text',_name='progs',requires=IS_LENGTH(100000)),INPUT(_type='submit',_value='import'))
    if form.accepts(request.vars, session):
        if request.vars.progs != None:
            try:
                prog_list=[]
    #           db.program.import_from_csv_file(request.vars.csvfile.file)
                for l in str(request.vars.progs).splitlines():
                    for p in l.split(','):
                        db.program.insert(title=p)
                response.flash = T('data uploaded')
            except:
                response.flash = T('unable to parse comma separated list')
    return dict(form=form)

@auth.requires_login()
def view_program():
    """
    Docstring here.
    """
    check_session()
    program_id=get_valid_id(request.args(0),db.program)
    program=db.program[program_id] or redirect(error_page)
    return dict(program=program)

@auth.requires_login()
def list_programs():
    """
    Docstring here.
    """
    check_session()
    programs=db(db.program.organization==session.organization['id']).select(orderby=db.program.title)
    return dict(programs=programs)

@auth.requires_login()
def edit_program():
    """
    Docstring here.
    """
    check_session()
    program_id=get_valid_id(request.args(0),db.program)
    program=db.program[program_id] or redirect(error_page)
    form=crud.update(db.program,program,next=url('list_programs_by_organization'))
    return dict(form=form)

@auth.requires_login()
def list_programs_by_organization():
    """
    Docstring here.
    """
    check_session()
    organization_id=session.organization['id']
    organization=db.organization[organization_id] or redirect(error_page)
    programs=db(db.program.organization==organization.id).select(orderby=db.program.title)
    return dict(organization=organization, programs=programs)

@auth.requires_login()
def create_pledgedrive():
    """
    Docstring here.
    """
    check_session_organization()

    form = SQLFORM(db.pledgedrive)

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        pledgedrive_id = dict(form.vars)['id']
        pledgedrive = db(db.pledgedrive.id==pledgedrive_id).select()
        session.pledgedrive = pledgedrive.as_list()[0]
        session.pledgedrive_id = pledgedrive.as_list()[0]['id']

        redirect(URL(r=request, f='index'))

    elif form.errors: response.flash='form errors'
    return dict(form=form)

@auth.requires_login()
def view_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=get_valid_id(request.args(0),db.pledgedrive)
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    dollar_goal = pledgedrive.pledge_goal * pledgedrive.projected_average_pledge
    return dict(pledgedrive=pledgedrive,dollar_goal=dollar_goal)

@auth.requires_login()
def list_pledgedrives():
    """
    Docstring here.
    """
    pledgedrives=db(db.pledgedrive.organization==session.organization['id']).select(orderby=db.pledgedrive.title)
    return dict(pledgedrives=pledgedrives)

@auth.requires_login()
def edit_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    form=crud.update(db.pledgedrive,pledgedrive,next=url('list_pledgedrives_by_organization'),deletable=False)
    return dict(form=form)

@auth.requires_login()
def list_pledgedrives_by_organization():
    """
    Docstring here.
    """
    check_session_organization()
    organization_id=session.organization['id']
    organization=db.organization[organization_id] or redirect(error_page)
    pledgedrives=db(db.pledgedrive.organization==organization_id).select(orderby=db.pledgedrive.title)
    dollar_goal = pledgedrives[0].pledge_goal * pledgedrives[0].projected_average_pledge
    return dict(organization=organization, pledgedrives=pledgedrives, dollar_goal=dollar_goal)

@auth.requires_login()
def create_challenge():
    """
    Docstring here.
    """
    check_session_organization()
    check_session_pledgedrive()
    check_person()

    organization=session.organization['id']
    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)

    form = SQLFORM(db.challenge)

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        challenge_id = dict(form.vars)['id']
        challenge = db(db.challenge.id==challenge_id).select()
        session.challenge = challenge.as_list()[0]
        session.challenge_id = challenge.as_list()[0]['id']

        redirect(URL(r=request, f='index'))

    return dict(form=form,pledgedrive=pledgedrive,organization=organization)

@auth.requires_login()
def view_challenge():
    """
    Docstring here.
    """
    challenge_id=get_valid_id(request.args(0),db.challenge)
    challenge=db.challenge[challenge_id] or redirect(error_page)
    return dict(challenge=challenge)

@auth.requires_login()
def list_challenges():
    """
    Docstring here.
    """
    check_session()
    challenges=db(db.challenge.organization==session.organization['id']).select(orderby=db.challenge.title)
    return dict(challenges=challenges)

@auth.requires_login()
def edit_challenge():
    """
    Docstring here.
    """
    challenge_id=get_valid_id(request.args(0),db.challenge)
    challenge=db.challenge[challenge_id] or redirect(error_page)
    form=crud.update(db.challenge,challenge,next=url('list_challenges_by_pledgedrive'))
    return dict(form=form)

@auth.requires_login()
def list_challenges_by_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    challenges=db(db.challenge.pledgedrive==pledgedrive.id).select(orderby=db.challenge.title)
    return dict(pledgedrive=pledgedrive, challenges=challenges)

@auth.requires_login()
def create_segment():
    """
    Docstring here.
    """
    check_session_organization()
    check_session_pledgedrive()
    check_program()

    form = SQLFORM(db.segment)

    if form.accepts(request.vars, session): 
        response.flash='record inserted'

        segment_id = dict(form.vars)['id']
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']

        redirect(URL(r=request, f='index'))

    elif form.errors: response.flash='form errors'

    return dict(form=form)

@auth.requires_login()
def view_segment():
    """
    Docstring here.
    """
    check_session()
    segment_id=get_valid_id(request.args(0),db.segment)
    segment=db.segment[segment_id] or redirect(error_page)
    return dict(segment=segment)

@auth.requires_login()
def list_segments():
    """
    Docstring here.
    """
    segments=db(db.segment.organization==session.organization['id']).select(orderby=db.segment.start_time)
    return dict(segments=segments)

@auth.requires_login()
def list_segments_by_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    segments=db(db.segment.pledgedrive==pledgedrive.id).select(orderby=db.segment.start_time)
    return dict(pledgedrive=pledgedrive, segments=segments)

@auth.requires_login()
def edit_segment():
    """
    Docstring here.
    """
    check_session()
    segment_id=get_valid_id(request.args(0),db.segment)
    segment=db.segment[segment_id] or redirect(error_page)
    form=crud.update(db.segment,segment,next=url('list_segments_by_pledgedrive'))
    return dict(form=form)

@auth.requires_login()
def create_pledge():
    """
    Docstring here.
    """
    check_session()
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)

    form = SQLFORM(db.pledge,next=url('index'))

    if form.accepts(request.vars, session): 
        response.flash='record inserted'
        session.pledge=dict(form.vars)
        redirect(URL(r=request, f='index'))
    elif form.errors: response.flash='form errors'

    return dict(form=form,segment=segment)

@auth.requires_login()
def view_pledge():
    """
    Docstring here.
    """
    check_session()
    pledge_id=get_valid_id(request.args(0),db.pledge)
    pledge=db.pledge[pledge_id] or redirect(error_page)
    return dict(pledge=pledge)

@auth.requires_login()
def list_pledges():
    """
    Docstring here.
    """
    check_session()
    pledges=db(db.pledge.id>0).select(orderby=db.pledge.name)
    return dict(pledges=pledges)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def list_pledges_by_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=get_valid_id(request.args(0),db.pledgedrive)
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    pledges=db(db.pledge.pledgedrive==pledgedrive.id).select(orderby=db.pledge.id)
    return dict(pledges=pledges)

# @cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def list_pledges_by_segment():
    """
    Docstring here.
    """
    check_session()
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    pledges=db(db.pledge.segment==segment_id).select()
    return dict(pledges=pledges,segment_id=segment_id)
    # return response(dict(pledges=pledges,segment_id=segment_id))

@auth.requires_login()
def delete_pledges_by_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    pledges = db.pledge.pledgedrive==pledgedrive.id

    db(pledges).delete()
    response.flash='Deleted'
    return dict()

@auth.requires_login()
def delete_pledges_by_segment():
    """
    Docstring here.
    """
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    pledges=db.pledge.segment==segment_id

    db(pledges).delete()
    response.flash='Deleted'
    return dict()
        
@auth.requires_login()
def edit_pledge():
    """
    Docstring here.
    """
    check_session()
    pledge_id=get_valid_id(request.args(0),db.pledge)
    pledge=db.pledge[pledge_id] or redirect(URL('default', 'all_pledges'))
    form=crud.update(db.pledge,pledge,next=url('list_pledges_by_segment'))
    return dict(form=form)

def all_pledges():
    '''
    NOTES:Returns a list of all pledges for a particular segment.  You can then edit a pledge from there.
    TODO: No view implemented
    '''
    all_segments = db(db.segment.id > 0).select(orderby=db.segment.start_time)
    segment_pledges = db(db.pledge.segment == (request.args(0) or session.segment_id)).select()
    print all_segments
    print segment_pledges
    return dict(segments = all_segments, pledges = segment_pledges)


@auth.requires_login()
def list_pledges_by_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    pledges=db(db.pledge.pledgedrive==pledgedrive.id).select()
    return dict(pledgedrive=pledgedrive, pledges=pledges)

def pledge_entry():
    """
    This page takes the various views required by the person entering 
    pledges and refreshes that data accordingly.
    """
    response.title="Pleage Entry Page"
    #Check if everything is setup for the pladge (This could be a decorator)
    check_session()
    
    #Load the organization id
    organization_id = session.organization['id']
    
    #Load all the organization data.
    organizations=db(db.organization.id==organization_id).select()
    
    #The form for letting the producer post a message.
    form_producer_message = SQLFORM(db.post)
    if form_producer_message.accepts(request.vars, session): 
        response.flash="Message Posted"
    elif form_producer_message.errors: response.flash='Message had errors... did not post...'
    
    #Get all the producers Posts
    producer_messages=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)
    
    #The totals for the pledge drive...
    pledgedrive_id=session.pledgedrive_id
    try:
        pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select()
        pledgedrive_total_pledges = len(pledgedrive_pledges)

        all_pledges = pledgedrive_pledges.as_list()

        pledgedrive_total_dollars = 0
        
        for o in all_pledges:
            pledgedrive_total_dollars = pledgedrive_total_dollars + o['amount']

        pledgedrive_average_pledge = pledgedrive_total_dollars / pledgedrive_total_pledges
    except:
        pledgedrive_total_pledges = 0
        pledgedrive_total_dollars = 0
        pledgedrive_average_pledge = 0
    drive_totals = {"pledges":pledgedrive_total_pledges, "dollars": pledgedrive_total_dollars, "average":pledgedrive_average_pledge}
    
    #Segment Goals and totals
    segment_id=session.segment['id']
    segment=db(db.segment.id==segment_id).select()
    segment_pledges = db(db.pledge.segment==segment_id).select()
    segment_total_pledges = len(segment_pledges)
    try:
        all_pledges_for_segment = segment_pledges.as_list()
        segment_total_dollars = 0

        for o in all_pledges_for_segment:
            segment_total_dollars = segment_total_dollars + o['amount']

        segment_average_pledge = segment_total_dollars / segment_total_pledges

    except:
        segment_total_pledges = 0
        segment_total_dollars = 0
        segment_average_pledge = 0

    if segment[0].goal_type == 'Pledge':
        goal = 'Pledge Goal:' + str(segment[0].goal)
        progress = segment[0].goal - segment_total_pledges 
    else:
        goal = 'Dollar Goal:'+  str(segment[0].goal)
        progress = segment[0].goal - segment_total_dollars
    segment_goals = {"pledges":segment_total_pledges,"dollors":segment_total_dollars, "average":segment_average_pledge}
    
    #Get the thank you list...
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    pledges=db(db.pledge.segment==segment_id).select(orderby=~db.pledge.created_on)
    
    #Pledge Form
    form_pledge=SQLFORM(db.pledge)
    if form_pledge.accepts(request.vars, session):
        flash_amount = form_pledge.vars.amount
        flash_name = form_pledge.vars.name
        response.flash='New Pledge Created:' + flash_amount + ' : ' + flash_name
    elif form_pledge.errors:
        response.flash='There were errors in entering a pledge'
    
    form_segment = SQLFORM(db.segment)

    #All Segments
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)
    
    #The current Segment
    segment = db(db.segment['id']).select()
    return dict(organizations=organizations,
                organization_id=organization_id,
                form_producer_message = form_producer_message,
                drive_totals = drive_totals,
                segment_goals = segment_goals,
                producer_messages=producer_messages,
                thank_yous = pledges,
                form_segment = form_segment,
                segments = segments,
                segment = segment,
                form_pledge = form_pledge)

def frame_header():
    """
    Docstring here.
    """
    check_session()
    organization_id = session.organization['id']
    organizations=db(db.organization.id==organization_id).select()
    return dict(message=T('Pledge Drive Tracker'),organizations=organizations,organization_id=organization_id)

def frame_header_onair():
    """
    Docstring here.
    """
    return frame_header()
    
def  frame_header_pledge_entry():
    """
    Docstring here.
    """
    return frame_header()


def frame_wrapper_onair():
    """
    Docstring here.
    """
    check_session()
    return dict()

def frame_onair():
    """
    Docstring here.
    """
    check_session()
    return dict()

def frame_wrapper_pledge_entry():
    """
    Docstring here.
    """
    check_session()
    return dict()

def frame_pledge_entry():
    """
    Docstring here.
    """
    check_session()
    return dict()

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def report_pledge_level():
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    segs = db(db.segment.pledgedrive == pledgedrive_id).select()
    segs = segs.sort(lambda row:row.start_time)
    seg_dicts = []
    total_pledges = 0
    buckets = [500,200,100,36,35,0]
    bucket_counter = [0,0,0,0,0,0]
    for s in segs:
	pledge_list = db(db.pledge.segment == s.id).select().as_list()
    	segment_total_pledges = len(pledge_list)
	total_pledges = total_pledges + segment_total_pledges
	seg_bucket_counter = [0,0,0,0,0,0]
    	for i in pledge_list:
		j = 0
		while i['amount']<buckets[j]:
			j = j+1
		seg_bucket_counter[j] = seg_bucket_counter[j] + 1
		bucket_counter[j] = bucket_counter[j] + 1
	d = dict(title=s.title, total_pledges=segment_total_pledges, bucket_counter=seg_bucket_counter, dt=s.start_time)
	seg_dicts.append(d)
    return dict(seg_dicts=seg_dicts,total_pledges=total_pledges,buckets=buckets,bucket_counter=bucket_counter)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def report_day_total_summary():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    dt_str = request.vars.date or str(datetime.date.today())
    dt_lst = dt_str.split('-')
    date = datetime.date(int(dt_lst[0]),int(dt_lst[1]),int(dt_lst[2]))
    form = SQLFORM.factory(\
                    Field('date','date',default=date),_action=URL(r=request))
    form.accepts(request.vars,session)
    if not form.errors:
        dt_str = request.vars.date or str(datetime.date.today())
        dt_lst = dt_str.split('-')
        date = datetime.date(int(dt_lst[0]),int(dt_lst[1]),int(dt_lst[2]))
    else:
        redirect(error_page)
        return
    #dt_str = str(datetime.date.today())
    #dt_lst = dt_str.split('-')
    #date = datetime.date(int(dt_lst[0]),int(dt_lst[1]),int(dt_lst[2]))
    segs = db(db.segment.pledgedrive == pledgedrive_id).select().find(lambda row:(row.start_time.year==int(dt_lst[0]) and row.start_time.month==int(dt_lst[1]) and row.start_time.day==int(dt_lst[2])))
#    segs = segs.find(lambda row:row.start_time.month==dt_lst[1])
#    segs = segs.find(lambda row:row.start_time.day==dt_lst[2])
    segs = segs.sort(lambda row:row.start_time)
    seg_dicts = []
    total_dollars = 0
    total_pledges = 0
    for s in segs:
        pledge_list = db(db.pledge.segment == s.id).select().as_list()
        segment_total_pledges = len(pledge_list)
        total_pledges = total_pledges + segment_total_pledges
        segment_total_dollars = 0
        for i in pledge_list:
            segment_total_dollars = segment_total_dollars + i['amount']
        total_dollars = total_dollars + segment_total_dollars
        d = dict(start_time = s.start_time, end_time=s.end_time,goal=s.goal, goal_type=s.goal_type, title=s.title, total_pledges=segment_total_pledges, total_dollars = segment_total_dollars)
        seg_dicts.append(d)
    # return dict(form=form,seg_dicts=seg_dicts,total_dollars=total_dollars,total_pledges=total_pledges)
    return response.render(dict(form=form,seg_dicts=seg_dicts,total_dollars=total_dollars,total_pledges=total_pledges))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def report_single_segment():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive_id
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    request.vars.segment = request.vars.segment or session.segment_id
    form = SQLFORM.factory(\
        Field('segment',default=request.vars.segment, requires=IS_IN_DB(db(db.segment.pledgedrive==pledgedrive_id),'segment.id','%(title)s'),unique=True),\
                    _action=URL(r=request))
    form.accepts(request.vars,session)
    if not form.errors:
        segment_id=request.vars.segment
    else:
        segment_id=session.segment_id
    segment = db.segment[segment_id] or redirect(error_page)
    program = db.program[segment.program]
    pledge_list = db(db.pledge.segment == segment_id).select().as_list()
    segment_total_pledges = len(pledge_list)
    segment_total_dollars = 0
    for i in pledge_list:
        segment_total_dollars = segment_total_dollars + i['amount']
    # return dict(segment=segment,pledge_list=pledge_list,segment_total_pledges=segment_total_pledges,segment_total_dollars=segment_total_dollars,program_title=program.title,form=form)
    return response.render(dict(segment=segment,pledge_list=pledge_list,segment_total_pledges=segment_total_pledges,segment_total_dollars=segment_total_dollars,program_title=program.title,form=form))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def report_segments_by_pledgedrive():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db.pledgedrive[pledgedrive_id] or redirect(error_page)
    segments=db(db.segment.pledgedrive==pledgedrive.id).select(orderby=db.segment.start_time)

    segment_dates = []
    segment_titles = []
    segment_goal_types = []
    segment_goals = []
    pledge_totals = []
    dollar_totals = []
    compiled_data = []

    for o in segments:
        segment_dates.append(o.start_time.strftime("%m/%d : %I:%M %p"))
        segment_titles.append(o.title)
        segment_goal_types.append(o.goal_type)
        segment_goals.append(o.goal)
        pledge_totals.append(len(db(db.pledge.segment==o.id).select()))

        segment_pledges=db(db.pledge.segment==o.id).select().as_list()

        segment_total_dollars = 0

        for i in segment_pledges:
            segment_total_dollars = segment_total_dollars + i['amount']

        dollar_totals.append(segment_total_dollars)

    compiled_list = [segment_dates,segment_titles,segment_goal_types,segment_goals,pledge_totals,dollar_totals]
    converted_list=[]

    x = len(segment_dates)

    while x:
        x = x-1
        new_row = [compiled_list[0][x],compiled_list[1][x],compiled_list[2][x],compiled_list[3][x],compiled_list[4][x],compiled_list[5][x]]
        converted_list.append(new_row)

    # return dict(pledgedrive=pledgedrive,segments=segments,compiled_list=compiled_list,converted_list=converted_list)
    return response.render(dict(pledgedrive=pledgedrive,segments=segments,compiled_list=compiled_list,converted_list=converted_list))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def report_pledgedrive_totals():
    """
    Docstring here.
    """
    check_session()

    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db(db.pledgedrive.id==pledgedrive_id).select()
    
    pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select()

    pledgedrive_total_pledges = len(pledgedrive_pledges)

    all_pledges = pledgedrive_pledges.as_list()

    pledgedrive_total_dollars = 0
    
    for o in all_pledges:

        pledgedrive_total_dollars = pledgedrive_total_dollars + o['amount']

    return dict(pledgedrive_total_pledges=pledgedrive_total_pledges,pledgedrive_total_dollars=pledgedrive_total_dollars)


@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def report_pledgedrive_totals_detailed():
    """
    Docstring here.
    """
    check_session()

    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db(db.pledgedrive.id==pledgedrive_id).select()
    
    pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select()

    pledgedrive_total_pledges = len(pledgedrive_pledges)

    all_pledges = pledgedrive_pledges.as_list()
    pledgedrive_total_dollars = 0
    
    for o in all_pledges:
        pledgedrive_total_dollars = pledgedrive_total_dollars + o['amount']

    pledge_goal = pledgedrive[0].pledge_goal

    projected_average_pledge = pledgedrive[0].projected_average_pledge

    dollar_goal = pledgedrive[0].pledge_goal * pledgedrive[0].projected_average_pledge

    dollars_remaining = dollar_goal - pledgedrive_total_dollars

    pledges_remaining = pledge_goal - pledgedrive_total_pledges

    '''
    pledgedrive_start_time=session.pledgedrive['start_time']
    pledgedrive_end_time=session.pledgedrive['end_time']
    time_difference = pledgedrive_end_time - pledgedrive_start_time
    '''

    return dict(pledgedrive_total_pledges=pledgedrive_total_pledges,pledgedrive_total_dollars=pledgedrive_total_dollars,dollar_goal=dollar_goal,pledge_goal=pledge_goal,projected_average_pledge=projected_average_pledge,dollars_remaining=dollars_remaining,pledges_remaining=pledges_remaining)


def report_mini_segment_goal():
    """
    Docstring here.
    """
    check_session()
    return dict()

def report_mini_segment_challenge():
    """
    Docstring here.
    """
    check_session()
    return dict()

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def report_mini_segment_select():
    """
    Docstring here.
    """
    check_session()

    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    labels=[(str(o.start_time.strftime("%m/%d : %I:%M %p")) + ' - ' + o.title) for o in segments]

    form=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,labels))) 
    
    if form.accepts(request.vars, session):
        segment_id = form.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']
        redirect(URL(r=request, f='report_mini_segment_select'))

    return dict(form=form,segments=segments)


def report_mini_segment_overview():
    """
    Docstring here.
    """
    check_session()
    return dict()

def report_mini_pledgedrive_goal():
    """
    Docstring here.
    """
    check_session()
    return dict()
    
@auth.requires_login()
def mini_create_pledge():
    """
    Docstring here.
    """
    check_session()

    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    labels=[(str(o.start_time.strftime("%m/%d : %I:%M %p")) + ' - ' + o.title) for o in segments]
    session.segments = segments.as_list()

    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    # form=crud.create()

    form=SQLFORM(db.pledge) 
    if form.accepts(request.vars, session):
        flash_amount = form.vars.amount
        flash_name = form.vars.name
        response.flash='pledge inserted:' + flash_amount + ' : ' + flash_name
    elif form.errors:
        response.flash='there are errors'


    form2=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,labels))) 
    
    if form2.accepts(request.vars, session):
        segment_id = form2.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']
        redirect(URL(r=request, f='mini_create_pledge'))

    return dict(form=form,form2=form2,segment=segment,segments=segments)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_pledgedrive_goal():
    """
    Docstring here.
    """
    check_session()
    return dict()

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_pledgedrive_totals():
    """
    Docstring here.
    """
    check_session()
    pledgedrive_id=session.pledgedrive_id
    
    try:
        pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select()
        pledgedrive_total_pledges = len(pledgedrive_pledges)

        all_pledges = pledgedrive_pledges.as_list()

        pledgedrive_total_dollars = 0
        
        for o in all_pledges:
            pledgedrive_total_dollars = pledgedrive_total_dollars + o['amount']

        pledgedrive_average_pledge = pledgedrive_total_dollars / pledgedrive_total_pledges
    except:
        pledgedrive_total_pledges = 0
        pledgedrive_total_dollars = 0
        pledgedrive_average_pledge = 0

    return dict(pledgedrive_total_pledges=pledgedrive_total_pledges,pledgedrive_total_dollars=pledgedrive_total_dollars,pledgedrive_average_pledge=pledgedrive_average_pledge)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_pledgedrive_totals_no_reload():
    """
    Docstring here.
    """
    check_session()

    pledgedrive_id=session.pledgedrive_id
    
    try:
        pledges = db(db.pledge.pledgedrive==pledgedrive_id).select()
        pledgedrive_total_pledges = len(pledges)
        all_pledges = pledges.as_list()
        pledgedrive_total_dollars = 0
        for o in all_pledges:
            pledgedrive_total_dollars = pledgedrive_total_dollars + o['amount']

        pledgedrive_average_pledge = pledgedrive_total_dollars / pledgedrive_total_pledges
    except:
        pledgedrive_total_pledges = 0
        pledgedrive_total_dollars = 0
        pledgedrive_average_pledge = 0

    return dict(pledgedrive_total_pledges=pledgedrive_total_pledges,pledgedrive_total_dollars=pledgedrive_total_dollars,pledgedrive_average_pledge=pledgedrive_average_pledge)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@service.xml
def report_progress_meter_flash():
    """
    Docstring here.
    """
    check_session()

    response.headers['Content-Type']='text/xml'

    pledgedrive_id=session.pledgedrive['id']
    pledgedrive=db(db.pledgedrive.id==pledgedrive_id).select()
    
    pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select()

    pledgedrive_total_pledges = len(pledgedrive_pledges)

    all_pledges = pledgedrive_pledges.as_list()
    pledgedrive_total_dollars = 0
    
    for o in all_pledges:
        pledgedrive_total_dollars = pledgedrive_total_dollars + o['amount']

    pledge_goal = pledgedrive[0].pledge_goal

    projected_average_pledge = pledgedrive[0].projected_average_pledge

    dollar_goal = pledgedrive[0].pledge_goal * pledgedrive[0].projected_average_pledge

    dollars_remaining = dollar_goal - pledgedrive_total_dollars

    pledges_remaining = pledge_goal - pledgedrive_total_pledges

    if dollar_goal >= 10 and dollar_goal < 100:
        factor_text = 'tens'
        factor_value = 10
    if dollar_goal >= 100 and dollar_goal < 1000:
        factor_text = 'hundreds'
        factor_value = 100
    elif dollar_goal >= 1000 and dollar_goal < 1000000:
        factor_text = 'thousands'
        factor_value = 1000
    elif dollar_goal >= 1000000:
        factor_text = 'millions'
        factor_value = 1000000

    dollar_goal_adjusted = dollar_goal / factor_value


    return dict(pledgedrive_total_dollars=pledgedrive_total_dollars,dollar_goal_adjusted=dollar_goal_adjusted,factor_text=factor_text)
    
@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_segment_goal():
    """
    Docstring here.
    """
    check_session()
    segment_id=session.segment['id']
    segment=db(db.segment.id==segment_id).select()
    
    segment_pledges = db(db.pledge.segment==segment_id).select()
    segment_total_pledges = len(segment_pledges)

    all_pledges_for_segment = segment_pledges.as_list()
    segment_total_dollars = 0

    for o in all_pledges_for_segment:
        segment_total_dollars = segment_total_dollars + o['amount']

    if segment[0].goal_type == 'Pledge':
    
        goal = 'Pledge Goal:' + str(segment[0].goal)
        progress = segment[0].goal - segment_total_pledges 
    else:
        goal = 'Dollar Goal:'+  str(segment[0].goal)
        progress = segment[0].goal - segment_total_dollars 

    return dict(segment_total_pledges=segment_total_pledges,segment_total_dollars=segment_total_dollars,goal=goal,progress=progress)    


@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_segment_goal_and_totals():
    """
    Docstring here.
    """
    check_session()

    segment_id=session.segment['id']
    segment=db(db.segment.id==segment_id).select()
    segment_pledges = db(db.pledge.segment==segment_id).select()
    segment_total_pledges = len(segment_pledges)

    try:
        all_pledges_for_segment = segment_pledges.as_list()
        segment_total_dollars = 0

        for o in all_pledges_for_segment:
            segment_total_dollars = segment_total_dollars + o['amount']

        segment_average_pledge = segment_total_dollars / segment_total_pledges

    except:
        segment_total_pledges = 0
        segment_total_dollars = 0
        segment_average_pledge = 0

    if segment[0].goal_type == 'Pledge':
        goal = 'Pledge Goal:' + str(segment[0].goal)
        progress = segment[0].goal - segment_total_pledges 
    else:
        goal = 'Dollar Goal:'+  str(segment[0].goal)
        progress = segment[0].goal - segment_total_dollars

    return dict(segment_total_pledges=segment_total_pledges,segment_total_dollars=segment_total_dollars,goal=goal,progress=progress,segment_average_pledge=segment_average_pledge)    

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_segment_totals():
    """
    Docstring here.
    """
    check_session()

    segment_id=session.segment['id']
    segment=db(db.segment.id==segment_id).select()
    segment_pledges = db(db.pledge.segment==segment_id).select()
    segment_total_pledges = len(segment_pledges)

    try:
        all_pledges_for_segment = segment_pledges.as_list()
        segment_total_dollars = 0
        
        for o in all_pledges_for_segment:
            segment_total_dollars = segment_total_dollars + o['amount']

        segment_average_pledge = segment_total_dollars / segment_total_pledges

    except:
        segment_total_pledges = 0
        segment_total_dollars = 0
        segment_average_pledge = 0
        
    return dict(segment_total_pledges=segment_total_pledges,segment_total_dollars=segment_total_dollars,segment_average_pledge=segment_average_pledge)    
    
@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_segment_challenge():
    """
    Docstring here.
    """
    check_session()
    segment_id=session.segment_id
    challenge_desc = db(db.challenge.segment == segment_id).select().as_list()
    return dict(segment_challenges=challenge_desc, seg_talkingpoints=db.segment[segment_id].talkingpoints)

@auth.requires_login()
def mini_segment_select():
    """
    Docstring here.
    """
    check_session()

    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    labels=[(str(o.start_time.strftime("%m/%d : %I:%M %p")) + ' - ' + o.title) for o in segments]

    form=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,labels))) 
    
    if form.accepts(request.vars, session):
        segment_id = form.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']
        redirect(URL(r=request, f='mini_segment_navigation'))

    return dict(form=form,segments=segments)


@auth.requires_login()
def mini_segment_select_pledge():
    """
    Docstring here.
    """
    check_session()

    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    labels=[(str(o.start_time.strftime("%m/%d : %I:%M %p")) + ' - ' + o.title) for o in segments]

    form=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,labels))) 
    
    if form.accepts(request.vars, session):
        segment_id = form.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']
        redirect(URL(r=request, f='mini_create_pledge'))

    return dict(form=form,segments=segments)

@auth.requires_login()
def mini_segment_navigation():
    """
    Docstring here.
    """
    check_session()

    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    labels=[(str(o.start_time.strftime("%m/%d : %I:%M %p")) + ' - ' + o.title) for o in segments]
    session.segments = segments.as_list()

    form=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,labels))) 
    
    if form.accepts(request.vars, session):
        segment_id = form.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']
        redirect(URL(r=request, f='mini_segment_navigation'))

    return dict(form=form,segments=segments)

def mini_segment_navigation_previous():
    """
    Docstring here.
    """
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    tests = [o.id for o in segments]
    counter = 0
    for i in tests:
        if i == session.segment_id:
            previous_test = int(tests[counter-1])
            segment = db(db.segment.id==previous_test).select()
            session.segment = segment.as_list()[0]
            session.segment_id = segment.as_list()[0]['id']
            break
        counter = counter + 1

    redirect(URL(r=request, f='mini_segment_navigation'))
    
    return dict()

def mini_segment_navigation_next():
    """
    Docstring here.
    """
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    tests = [o.id for o in segments]
    counter = 0
    for i in tests:
        if i == session.segment_id:
            next_test = int(tests[counter+1])
            segment = db(db.segment.id==next_test).select()
            session.segment = segment.as_list()[0]
            session.segment_id = segment.as_list()[0]['id']
            break
        counter = counter + 1

    redirect(URL(r=request, f='mini_segment_navigation'))
    
    return dict()

def mini_segment_navigation_previous_pledge():
    """
    Docstring here.
    """
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    tests = [o.id for o in segments]
    counter = 0
    for i in tests:
        if i == session.segment_id:
            previous_test = int(tests[counter-1])
            segment = db(db.segment.id==previous_test).select()
            session.segment = segment.as_list()[0]
            session.segment_id = segment.as_list()[0]['id']
            break
        counter = counter + 1

    redirect(URL(r=request, f='mini_create_pledge'))
    
    return dict()

def mini_segment_navigation_next_pledge():
    """
    Docstring here.
    """
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    tests = [o.id for o in segments]
    counter = 0
    for i in tests:
        if i == session.segment_id:
            next_test = int(tests[counter+1])
            segment = db(db.segment.id==next_test).select()
            session.segment = segment.as_list()[0]
            session.segment_id = segment.as_list()[0]['id']
            break
        counter = counter + 1

    redirect(URL(r=request, f='mini_create_pledge'))
    
    return dict()


@auth.requires_login()
def post_add():
    """
    Docstring here.
    """
    form = SQLFORM(db.post)

    if form.accepts(request.vars, session): 
        session.flash='post updated'
        redirect(URL(r=request, f='post_list'))
    elif form.errors: response.flash='form errors'

    return dict(form=form)

@auth.requires_login()
def post_edit():
    """
    Docstring here.
    """
    post_id=get_valid_id(request.args(0),db.post)
    post=db.post[post_id] or redirect(error_page)
    form = SQLFORM(db.post,post,deletable=True)

    if form.accepts(request.vars, session): 
        session.flash='record deleted'
        redirect(URL(r=request, f='post_list'))
    elif form.errors: response.flash='form errors'

    return dict(form=form)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def post_list():
    """
    Docstring here.
    """
    posts=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)
    # return dict(posts=posts)
    return response.render(dict(posts=posts))

@auth.requires_login()
def delete_posts_by_organization():
    """
    Docstring here.
    """
    check_session()
    organization_id=session.organization['id']
    posts=db.post.organization==organization_id

    db(posts).delete()

    redirect(URL(r=request, f='post_list'))
    response.flash='Producer Messages Deleted'

    return dict(posts=posts)


@auth.requires_login()
def mini_post_add():
    """
    Docstring here.
    """
    form = SQLFORM(db.post)

    if form.accepts(request.vars, session): 
        response.flash='post updated'
    elif form.errors: response.flash='form errors'
    
    return dict(form=form)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def mini_post_list():
    """
    Docstring here.
    """
    posts=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)
    # return dict(posts=posts)
    return response.render(dict(posts=posts))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_pledge_names():
    """
    Docstring here.
    """
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    pledges=db(db.pledge.segment==segment_id).select(orderby=~db.pledge.created_on)
    # return dict(pledges=pledges,segment_id=segment_id)
    return response.render(dict(pledges=pledges,segment_id=segment_id))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_pledge_names_no_reload():
    """
    Docstring here.
    """
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    pledges=db(db.pledge.segment==segment_id).select(orderby=~db.pledge.created_on)
    # return dict(pledges=pledges,segment_id=segment_id)
    return response.render(dict(pledges=pledges,segment_id=segment_id))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def mini_pledge_names_nav():
    """
    Docstring here.
    """
    check_session()
    return dict()

@auth.requires_login()
def quick_setup_segment():
    """
    Docstring here.
    """
    check_session()

    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)

    units=[1,2,3,4,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]    
    ids=[o for o in units]
    labels=[o for o in units]

    form=SQLFORM.factory(Field('units',requires=IS_IN_SET(ids,labels)))

    if form.accepts(request.vars, session):
        units = form.vars.units
        organization_id=session.organization['id']
        pledgedrive_id=session.pledgedrive['id']
        segment_id=session.segment['id']
        segment_start_time=session.segment['start_time']
        segment_end_time=session.segment['end_time']
        time_format = "%Y-%m-%d %H:%M:%S"
        segment_start_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(segment_start_time, time_format)))
        segment_end_time = datetime.datetime.fromtimestamp(time.mktime(time.strptime(segment_end_time, time_format)))

        units = int(units)
        a = 1

        description=session.segment['description']
        goal=session.segment['goal']
        goal_type=session.segment['goal_type']
        program=session.segment['program']

        while a <= units:

            segment_id += 1
            # print segment_id

            title='Auto Segment: ' + str(a)

            time_difference = segment_end_time - segment_start_time
            segment_end_time = segment_end_time + time_difference
            segment_start_time = segment_start_time + time_difference
            # print segment_start_time
            # print time_difference
            # print segment_end_time

            db.segment.insert(title=title,description=description,goal=goal,goal_type=goal_type,program=program,start_time=segment_start_time,end_time=segment_end_time)

            # print a
            a += 1
            
        response.flash='records inserted'
        redirect(URL(r=request, f='quick_setup_segment'))

    elif form.errors: response.flash='check for errors'

    return dict(form=form, segments=segments)

@auth.requires_login()
def quick_setup_pledgedrive():
    """
    Make a copy of the original_pledgedrive and all the original_segments associated with that drive.
    Change the start_time and end_time for each new segment to correspond with the date(s) the user has supplied in the form.
    Make a copy of all the original_challenges then create new challenges, make sure to associate each challenge with its corresponding newly created segment.
    """
    check_session()

    form=SQLFORM(db.pledgedrive)

    # this will be useful at various points within this function
    time_format = "%Y-%m-%d %H:%M:%S"

    # make a copy of the original_pledgedrive and all the original_segments associated with that drive
    # make two lists of the unique original_segment_dates
    original_pledgedrive=session.pledgedrive
    original_segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)
    original_segment_dates = []
    original_segment_dates_labels = []

    # make a lists of the original_challenges, and a list of orignal_challenge_ids
    original_challenges=db(db.challenge.pledgedrive==session.pledgedrive_id).select(orderby=db.challenge.segment)

    new_challenge_ids = []

    # create a list of new challenges
    new_challenges = []

    for s in original_segments:
        x = str(s.start_time.year) + '-' + str(s.start_time.month) + '-' + str(s.start_time.day) + ' 00:00:00'
        x = datetime.datetime.strptime(x,time_format)
        if x not in original_segment_dates:
            original_segment_dates.append(x)

    counter = 0
    # make two lists of the unique original_segment_dates, one as datetime type, the other as a string
    # add form fields for these dates to the form for creating a new pledgedrive
    for s in original_segment_dates:
        s = s.strftime("%A, %B %d %Y")
        original_segment_dates_labels.append(s)
        fieldname = 'new_segment_date_' + str(counter)
        fieldname = TR(LABEL(s),INPUT(_name=fieldname, _class='date', _id=counter, value=time.strftime("%Y-%m-%d"), _type='text'))
        form[0].insert(-1,fieldname)
        counter = counter + 1

    form.vars.title = 'New: ' + original_pledgedrive['title']
    form.vars.start_time = time.strftime(time_format)
    form.vars.end_time = time.strftime(time_format)
    form.vars.description = original_pledgedrive['description']
    form.vars.pledge_goal = original_pledgedrive['pledge_goal']
    form.vars.projected_average_pledge = original_pledgedrive['projected_average_pledge']

    if form.accepts(request.vars, session): 
        # create a new pledgedrive based on the values the user has added to the form
        response.flash='record inserted'

        # set the new pledgedrive as a variable for use here
        # set the new pledgedrive as a session variable
        # make the new pledgedrive the "currently selected pledgedrive"
        pledgedrive_id = dict(form.vars)['id']
        pledgedrive = db(db.pledgedrive.id==pledgedrive_id).select()
        session.pledgedrive = pledgedrive.as_list()[0]
        session.pledgedrive_id = pledgedrive.as_list()[0]['id']

        organization_id=session.organization['id']
        pledgedrive_id=session.pledgedrive['id']

        # create a list of new segments
        new_segments = []

        for a in original_segments:
            title = str(a.title)
            description = str(a.description)
            talkingpoints = str(a.talkingpoints)
            goal = str(a.goal)
            goal_type = str(a.goal_type)
            program = str(a.program)
            start_time = a.start_time
            end_time = a.end_time
            original_segment_id = a.id

            # change the start_time and end_time for each new segment to correspond with the date(s) the user has supplied in the form
            counter = 0
            for x in original_segment_dates:
                # check to see if the original_segment currently being tested (a) contains the same Year, Month and Day 
                # (but not minutes, seconds or miliseconds) as a date in the list of original_segment_dates (x)
                # then, replace this date with the corresponding (new_date) value that the user has supplied in the form

                # does a == x?  If so:
                if int(str(a.start_time.year) + str(a.start_time.month) + str(a.start_time.day)) == int(str(x.year) + str(x.month) + str(x.day)):
                    # get the name(s) of the form fields where the user has entered in a new date                    
                    segment_date_name = 'new_segment_date_' + str(counter)

                    # create a string (new_date) with the date information from the form
                    # then add some dummy time information
                    new_date = dict(form.vars)[segment_date_name] + ' 00:00:00'
                    # convert the new_date into a datetime object
                    new_date = datetime.datetime.strptime(new_date,time_format)

                    # replace the Year, Month and Day with the corresponding new_date provided in the form (temp variable z)
                    z = str(new_date.year) + '-' + str(new_date.month) + '-' + str(new_date.day) + ' ' + str(a.start_time.hour) + ':' + str(a.start_time.minute) + ':' + str(a.start_time.second)
                    start_time = datetime.datetime.strptime(z,time_format)

                    end_time = str(new_date.year) + '-' + str(new_date.month) + '-' + str(new_date.day) + ' ' + str(a.end_time.hour) + ':' + str(a.end_time.minute) + ':' + str(a.end_time.second)

                    end_time = datetime.datetime.strptime(end_time,time_format)

                else:
                    counter = counter + 1

            d = dict(title=title,description=description,talkingpoints=talkingpoints,goal=goal,goal_type=goal_type,program=program,start_time=start_time,end_time=end_time)

            # add the newly created segment to the list of new_segments
            new_segments.append(d)

            # add the newly created segment to the database, gets the id as a variable
            new_segment_id=db.segment.insert(title=title,description=description,talkingpoints=talkingpoints,goal=goal,goal_type=goal_type,program=program,pledgedrive=pledgedrive_id,start_time=start_time,end_time=end_time)

            for y in original_challenges:
                # associate the new challenge with the newly created pledgedrive
                y.pledgedrive = pledgedrive_id

                # test to see if the segment id of the current challenge being iterated contains the original_segment_id
                if y.segment == original_segment_id:
                    # test to see if a challenge for this segment has not already been added to new_challenge_ids
                    if y.segment not in new_challenge_ids:
                        y.segment = new_segment_id
                        new_challenge_ids.append(new_segment_id)
                        new_challenges.append(y)

                        # add the newly created challenge to the database
                        db.challenge.insert(title=y.title,person=y.person,pledgedrive=y.pledgedrive,segment=y.segment,amount=y.amount,description=y.description,type=y.type,condition=y.condition,state=y.state,organization=y.organization)


        # set the first segment and segment_id as session variables
        segment_id = db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)[0].id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']


        # the redirect will prevent response.flash from displaying the message, use session.flash instead
        session.flash='Pledgedrive successfully copied'

        # all done. back to the index page
        redirect(URL(r=request, f='index'))

    elif form.errors: response.flash='form errors'

    # send these variables to the quick_setup_pledgedrive page, build the form.
    return dict(form=form,original_segment_dates_labels=original_segment_dates_labels,original_segments=original_segments)


@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@service.xml
@service.xmlrpc
@service.run
def service_pledgedrive_pledges(pledgedrive_id):
    pledgedrive_id=pledgedrive_id
    pledgedrive_pledges = db(db.pledge.pledgedrive==pledgedrive_id).select().as_list()[0]

    return dict(pledgedrive_pledges=pledgedrive_pledges)

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
