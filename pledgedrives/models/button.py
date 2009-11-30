def button(text,action,args=[]):
    return TAG.button(text,_onclick="document.location='%s'" % URL(r=request,f=action,args=args))
