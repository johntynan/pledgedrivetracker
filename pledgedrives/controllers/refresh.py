# coding: utf8
from gluon.tools import prettydate

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def index():
    """
    Builds a special view based on parameters
    """
    response.title="Pick a view..."
    if not len(request.args):
        redirect(URL('refresh', "possible_views"))
    views = request.args
    #views = ["create_producer_message", 'segments', 'create_pledge', 'thank_yous', 'totals']
    overlays = ["create_producer_message","previous_segment", "next_segment", "select_different_segment"]
    return dict(views=views, overlays = overlays)

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def possible_views():
    #A list of commonly used portal views
    return dict()

def create_producer_message():
    #The form for letting the producer post a message.
    form_producer_message = SQLFORM(db.post)
    if form_producer_message.accepts(request.vars, session): 
        response.flash="Message Posted"
    elif form_producer_message.errors: response.flash='Message had errors... did not post...'
    return dict(form_producer_message = form_producer_message)

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
@auth.requires_login()
def segments():
    #All Segments
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)
    return dict(segments=segments)

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def current_segment():
    return dict()

@auth.requires_login()
def create_segment():
    """
    Docstring here.
    """
    form = SQLFORM(db.segment)

    if form.accepts(request.vars, session): 
        response.flash='Segment Created'

        segment_id = dict(form.vars)['id']
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']

        redirect(URL(r=request, f='index'))

    elif form.errors: response.flash='There seems to have been an error.'

    return dict(form=form)

def create_pledge():
    #Pledge Form
    form_pledge=SQLFORM(db.pledge)
    if form_pledge.accepts(request.vars, session):
        flash_amount = form_pledge.vars.amount
        flash_name = form_pledge.vars.name
        response.flash='New Pledge Created:' + flash_amount + ' : ' + flash_name
    elif form_pledge.errors:
        response.flash='There were errors in entering a pledge'
    return dict(form_pledge = form_pledge)

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def thank_yous():
    #Get the thank you list...
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    # pledges=db(db.pledge.segment==segment_id).select(orderby=~db.pledge.created_on)
    pledges=db((db.pledge.segment==segment_id) & (db.pledge.read == False)).select(orderby=~db.pledge.created_on)
    return dict(pledges = pledges)
    # return response.render(pledges)

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def totals():
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
    segment_totals = {"pledges":segment_total_pledges,"dollors":segment_total_dollars, "average":segment_average_pledge}
    return dict(drive_totals = drive_totals, segment_totals = segment_totals)

def producers_posts():
    #Get all the producers Posts
    # producer_messages=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)

    messages=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)
    return dict(messages = messages, prettydate = prettydate)

def read_message():
    if not request.args(0):
        return None
    db(db.pledge.id == request.args(0)).update(read=True)
    return None

def header():
    # display organization information
    organization_id=session.organization['id']
    organization=db.organization[organization_id] or redirect(error_page)

    return dict(organization=organization)


@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def segment_goal():
    """
    Docstring here.
    """
    # check_session()
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


@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def segment_totals():
    """
    Docstring here.
    """
    # check_session()

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

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def segment_goal_and_totals():
    """
    Docstring here.
    """
    # check_session()

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


@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def pledgedrive_totals():
    """
    Docstring here.
    """
    # check_session()
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

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def segment_challenge():
    """
    Docstring here.
    """
    # check_session()
    segment_id=session.segment_id
    challenge_desc = db(db.challenge.segment == segment_id).select().as_list()
    return dict(segment_challenges=challenge_desc, seg_talkingpoints=db.segment[segment_id].talkingpoints)

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def producer_messages():
    """
    Docstring here.
    """
    posts=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)
    return dict(posts=posts)

@cache(request.env.path_info, time_expire=5, cache_model=cache.ram)
def producers_posts():
    messages=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)
    return dict(messages = messages, prettydate = prettydate)

def read_message():
    if not request.args(0):
        return None
    db(db.pledge.id == request.args(0)).update(read=True)
    return None
