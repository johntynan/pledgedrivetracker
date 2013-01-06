# coding: utf8
from gluon.tools import prettydate

@auth.requires_login()
@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def index():
    """
    Builds a special view based on parameters
    """
    # response.title="Pick a view..."
    """
    if not len(request.args):
        redirect(URL('refresh', "possible_views"))
    elif request.args(0) in response.page_templates:
        views = response.page_templates[request.args(0)]
    else:
        views = request.args
    """

    segement_goal_url = 'segment_goal/' + str(session.segment_id)
    segment_totals_url = 'segment_totals/' + str(session.segment_id)
    segment_challenge_url = 'segment_challenge/' + str(session.segment_id)
    pledge_list_url = 'pledge_list/' + str(session.segment_id)

    if not len(request.args):
        redirect(URL('default', "index"))
    elif request.args(0) == 'pledge_entry':
        session.refreshed = 1
        views = [segement_goal_url, segment_totals_url, "pledgedrive_totals", "post_list", "create_pledge", pledge_list_url]
        response.title="Pledge Entry"
    elif request.args(0) == 'on_air':
        session.refreshed = 1
        views = [segement_goal_url, segment_totals_url, "pledgedrive_totals", pledge_list_url, segment_challenge_url, "post_list"]
        response.title="Producer Screen"
    elif request.args(0) == 'pitch':
        session.refreshed = 1
        views = [pledge_list_url, segement_goal_url]
        response.title="Pitch Screen"
    else:
        redirect(URL('default', "index"))

    overlays = ["create_producer_message"]

    return dict(views=views, overlays = overlays)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def possible_views():
    #A list of commonly used portal views
    return dict()

def create_producer_message():
    #make a part of feilds in the database not readable here...
    db.post.read.readable=False
    db.post.read.writable=False
    #The form for letting the producer post a message.
    form_producer_message = SQLFORM(db.post)
    if form_producer_message.accepts(request.vars, session): 
        response.flash="Message Posted"
    elif form_producer_message.errors: response.flash='Message had errors... did not post...'
    return dict(form_producer_message = form_producer_message)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
@auth.requires_login()
def segments():
    #All Segments
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)
    return dict(segments=segments)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
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
    #make certain feilds in the pledge unreadable and unwritable as 
    #they are not needed here.
    db.pledge.read.readable=False
    db.pledge.read.writable=False
    #Pledge Form
    form_pledge=SQLFORM(db.pledge)
    if form_pledge.accepts(request.vars, session):
        flash_amount = form_pledge.vars.amount
        flash_name = form_pledge.vars.name
        response.flash='New Pledge Created:' + flash_amount + ' : ' + flash_name
    elif form_pledge.errors:
        response.flash='There were errors in entering a pledge'
    return dict(form_pledge = form_pledge)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def pledge_list():
    #Get the thank you list...
    sorted_pledges = []
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    # pledges=db((db.pledge.segment==segment_id) & (db.pledge.read != True)).select(orderby=~db.pledge.created_on)
    # orderby=~db.pledge.created_on seems to cause an error in GAE when cache is turned on:
    pledges=db((db.pledge.segment==segment_id) & (db.pledge.read != True)).select()
    # return dict(pledges = pledges)
    # This seems to resolve the error with GAE:
    for row in pledges.sort(lambda row: row.created_on,reverse=True):
        sorted_pledges.append(row)
    return response.render(dict(pledges=sorted_pledges))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def pledge_list_all():
    #Get the thank you list...
    sorted_pledges = []
    segment_id=session.segment['id']
    segment=db.segment[segment_id] or redirect(error_page)
    pledges=db(db.pledge.segment==segment_id).select()
    for row in pledges.sort(lambda row: row.created_on,reverse=True):
        sorted_pledges.append(row)
    return response.render(dict(pledges=sorted_pledges))

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
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
    #We also need to check if this item is part of this segment... don't want people to rendomly delete posts do we?
    if not request.args(0):
        return None
    db(db.post.id == request.args(0)).update(read=True)
    return "Processing..."

def read_pledge():
    #We also need to check if this item is part of this segment... don't want people to rendomly delete posts do we?
    if not request.args(0):
        return None
    db(db.pledge.id == request.args(0)).update(read=True)
    return "Processing..."

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def segment_goal():
    """
    Docstring here.
    """
    segment_id=session.segment['id']
    # segment_id = request.args[0]
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
def segment_totals():
    """
    Docstring here.
    """
    segment_id=session.segment['id']
    # segment_id = request.args[0]
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
def segment_goal_and_totals():
    """
    Docstring here.
    """
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
def pledgedrive_totals():
    """
    Docstring here.
    """
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
def segment_challenge():
    """
    Docstring here.
    """
    segment_id=session.segment_id
    # segment_id = request.args[0]
    challenge_desc = db(db.challenge.segment == segment_id).select().as_list()
    return dict(segment_challenges=challenge_desc, seg_talkingpoints=db.segment[segment_id].talkingpoints)

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def post_list():
    """
    Docstring here.
    """
    sorted_posts=[]
    # posts=db((db.post.organization==session.organization['id']) & (db.post.read != True)).select(orderby=~db.post.created_on)
    # orderby=~db.post.created_on seems to cause an error in GAE when cache is turned on:
    posts=db((db.post.organization==session.organization['id']) & (db.post.read != True)).select()
    # This seems to resolve the error with GAE:
    for row in posts.sort(lambda row: row.created_on,reverse=True):
        sorted_posts.append(row)
    # return dict(posts=posts)
    return response.render(dict(posts=sorted_posts))

def post_mark_as_read():
    """
    if not request.args(0):
        print 'nuthin'
        return None
    """
    row = db(db.post.id == request.args(0)).update(read=True)
    # print request.args(0)
    # print request
    row.update(read=True)
    row.update_record()
    # print row
    return None

@cache(request.env.path_info, time_expire=3, cache_model=cache.ram)
def edit_producer_messages():
    """
    Docstring here.
    """
    sorted_posts = []

    posts=db(db.post.organization==session.organization['id']).select()

    for row in posts.sort(lambda row: row.created_on,reverse=True):
        sorted_posts.append(row)

    return response.render(dict(posts=sorted_posts))
    # return response.render(dict(posts=posts))
    # return dict(posts=posts)

def delete_producer_messages():
    """
    Docstring here.
    """
    # redirect(URL(r=request,c='default',f='delete_posts_by_organization',args=session.organization['id']))
    return dict()

def producers_posts():
    messages=db(db.post.organization==session.organization['id']).select(orderby=~db.post.created_on)
    return dict(messages = messages, prettydate = prettydate)

def pledge_mark_as_read():
    if not request.args(0):
        return None
    db(db.pledge.id == request.args(0)).update(read=True)
    return None

def edit_pledges():
    """
    Docstring here.
    """
    sorted_pledges = []

    pledges=db(db.pledge.segment==session.segment['id']).select()

    for row in pledges.sort(lambda row: row.created_on,reverse=True):
        sorted_pledges.append(row)

    return response.render(dict(pledges=sorted_pledges))

def segment_navigation():
    """
    Docstring here.
    """
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

    session.refreshed = 0
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

    session.refreshed = 0
    redirect(URL(r=request, f='segment_navigation'))
    
    return dict()

def segment_select():
    """
    Docstring here.
    """
    segments=db(db.segment.pledgedrive==session.pledgedrive_id).select(orderby=db.segment.start_time)    
    ids=[o.id for o in segments]
    labels=[(str(o.start_time.strftime("%m/%d : %I:%M %p")) + ' - ' + o.title) for o in segments]

    form=SQLFORM.factory(Field('segment_id',requires=IS_IN_SET(ids,labels))) 

    if form.accepts(request.vars, session):
        segment_id = form.vars.segment_id
        segment = db(db.segment.id==segment_id).select()
        session.segment = segment.as_list()[0]
        session.segment_id = segment.as_list()[0]['id']

        session.refreshed = 0
    
        redirect(URL(r=request, f='segment_navigation'))

    return dict(form=form,segments=segments)

