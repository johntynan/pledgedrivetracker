# coding: utf8

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

def error():
    """
    Display error message.
    """
    return dict(message='something is wrong')

def report_segment_goal():
    """
    Docstring here.
    """
    check_session()
    return dict()

def report_segment_challenge():
    """
    Docstring here.
    """
    check_session()
    return dict()

@auth.requires_login()
def report_segment_select():
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
        redirect(URL(r=request, f='report_segment_select'))

    return dict(form=form,segments=segments)

def report_segment_overview():
    """
    Docstring here.
    """
    check_session()
    return dict()

def report_pledgedrive_goal():
    """
    Docstring here.
    """
    check_session()
    return dict()
    
@auth.requires_login()
def create_pledge():
    """
    Docstring here.
    """
    check_session()
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)

    form=SQLFORM(db.pledge) 
    if form.accepts(request.vars, session):
        flash_amount = form.vars.amount
        flash_name = form.vars.name
        response.flash='pledge inserted:' + flash_amount + ' : ' + flash_name
    elif form.errors:
        response.flash='there are errors'

    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    labels=[(str(o.start_time.strftime("%m/%d : %I:%M %p")) + ' - ' + o.title) for o in segments]

    form2=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,labels))) 
    
    if form2.accepts(request.vars, session):
        segment_id = form2.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']
        redirect(URL(r=request, f='create_pledge'))

    return dict(form=form,form2=form2,segment=segment,segments=segments)

@service.json
def pledgedrive_goal():
    """
    Docstring here.
    """
    check_session()
    return dict()

@service.json
def pledgedrive_totals():
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

@service.json
def pledgedrive_totals_no_reload():
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

@service.json
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
    
@service.json
def segment_goal():
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


@service.json
def segment_goal_and_totals():
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

@service.json
def segment_totals():
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
    
@service.json
def segment_challenge():
    """
    Docstring here.
    """
    check_session()
    segment_id=session.segment_id
    challenge_desc = db(db.challenge.segment == segment_id).select().as_list()
    return dict(segment_challenges=challenge_desc, seg_talkingpoints=db.segment[segment_id].talkingpoints)

@auth.requires_login()
def segment_select():
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
        redirect(URL(r=request, f='segment_navigation'))

    return dict(form=form,segments=segments)


@auth.requires_login()
def segment_select_pledge():
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
        redirect(URL(r=request, f='create_pledge'))

    return dict(form=form,segments=segments)

@auth.requires_login()
def segment_navigation():
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
        redirect(URL(r=request, f='segment_navigation'))

    return dict(form=form,segments=segments)

def segment_navigation_previous():
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

    redirect(URL(r=request, f='segment_navigation'))
    
    return dict()

def segment_navigation_next():
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

    redirect(URL(r=request, f='segment_navigation'))
    
    return dict()

def segment_navigation_previous_pledge():
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

    redirect(URL(r=request, f='create_pledge'))
    
    return dict()

def segment_navigation_next_pledge():
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

    redirect(URL(r=request, f='create_pledge'))
    
    return dict()

@service.json
def pledge_names_no_reload():
    """
    Docstring here.
    """
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    pledges=db(db.pledge.segment==segment_id).select(orderby=~db.pledge.created_on)
    return dict(pledges=pledges,segment_id=segment_id)

@service.json
def pledge_names_nav():
    """
    Docstring here.
    """
    check_session()
    return dict()
