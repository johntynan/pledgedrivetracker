# coding: utf8

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

# response.title = request.application
# response.title = T('Pledge Drive Tracker')
response.title = T('Pledge Drive Tracker Demo')
response.subtitle = T('Making Public Broadcasting Fund Drives More Efficient')
response.author = 'John Tynan'

# subscription app help file:
helphome = "http://pledgedrivetracker.appspot.com/pledgedrives/static/documentation/_build/html/"
# demo app help file:
# helphome = "http://pledgedrivetrackerdemo.appspot.com/pledgedrives/static/documentation/_build/html/"
helpdefault = "index.html"
urls = {"frame_header_onair":"on_air_screen.html","frame_header_pledge_entry":"pledge_entry.html","create_program":"setup.html#program-s"}


##########################################
## this is the authentication menu
## remove if not necessary
##########################################

if 'auth' in globals():
    # comment out for the following block of code if you are using the subscription app

    if not auth.is_logged_in():
       response.menu_auth = [
           [T('Login'), False, auth.settings.login_url,
            [
                   [T('Register'), False,
                    URL(request.application,'default','user/register')],
                   [T('Lost Password'), False,
                    URL(request.application,'default','user/retrieve_password')]]
            ],
           ]
    else:

    # comment out the following line if you are using the demo app
    # if auth.is_logged_in():
       response.menu_auth = [
            ['User: '+auth.user.first_name,False,None,
             [
                    [T('Logout'), False, 
                     URL(request.application,'default','user/logout')],
                    [T('Edit Profile'), False, 
                     URL(request.application,'default','user/profile')],
                    [T('Change Password'), False,
                     URL(request.application,'default','user/change_password')]]
             ],
            ]

##########################################
## this is the main application menu
## add/remove items as required
##########################################
response.helpurl = helphome + helpdefault
if urls.has_key(str(request.function)):
    response.helpurl = helphome + urls[str(request.function)] 

response.menu = [
    [T('Index'), False, 
     URL(request.application,'default','index'), []],
    ]


##########################################
## this is here to provide shortcuts
## during development. remove in production 
##########################################
'''
response.menu_edit=[
  [T('Edit'), False, URL('admin', 'default', 'design/%s' % request.application),
   [
            [T('Controller'), False, 
             URL('admin', 'default', 'edit/%s/controllers/default.py' \
                     % request.application)],
            [T('View'), False, 
             URL('admin', 'default', 'edit/%s/views/%s' \
                     % (request.application,response.view))],
            [T('Layout'), False, 
             URL('admin', 'default', 'edit/%s/views/layout.html' \
                     % request.application)],
            [T('Stylesheet'), False, 
             URL('admin', 'default', 'edit/%s/static/base.css' \
                     % request.application)],
            [T('DB Model'), False, 
             URL('admin', 'default', 'edit/%s/models/db.py' \
                     % request.application)],
            [T('Menu Model'), False, 
             URL('admin', 'default', 'edit/%s/models/menu.py' \
                     % request.application)],
            [T('Database'), False, 
             URL(request.application, 'appadmin', 'index')],
            ]
   ],
  ]
'''
