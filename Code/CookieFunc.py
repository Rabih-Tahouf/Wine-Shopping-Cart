#####################################################################################
# Cookie set and get functions
#####################################################################################
import os
from http import cookies
from urllib import parse
#====================================================================================
# setCookie(): Set a cookie
#        args: name, value, expiration days (could be positive or negative)
#====================================================================================
def setCookie(name, value, expire=0):

    c = cookies.SimpleCookie()              #create object to to help create cookies
    name  = parse.quote(name)               #url encode the name
    value = parse.quote(value)
    c['name'] = value                         #create a cookie
    if int(expire) != 0 : 
        maxAge = int(expire) * (24*60*60)   #compute from days to seconds
        c[name]['max-age'] = maxAge         #set for future (or past) date
    c[name]['path'] = '/'                   #make it accessible to a wider path
    print(c)                                #Write the cookie headers

#====================================================================================
# getCookies(): Get all cookies  
#      returns: all cookies as a dictionary
#====================================================================================
def getCookies():

    cookieStr = os.environ.get('HTTP_COOKIE')     #obtain the HTTP cookies
    if cookieStr is None: return

    cookiesDict = {}                              #create a dictionary

    cookiesArray = cookieStr.split('; ')          #split on semi-colon space
    for cookie in cookiesArray:
        (name, value) = cookie.split('=',1)       #split on first =
        value2 = parse.unquote(value)             #cookie value (decoded)
        cookiesDict[name] = value2                #build the cookies dictionary

    return cookiesDict 

#====================================================================================
# getCookie(): Get a single cookie
#        args: cookie name
#     returns: cookie value  
#====================================================================================
def getCookie(name):
    
    allCookies = getCookies()
    try:
        value = allCookies[name]                #get the value of a single cookie
    except:
        value = ""

    return value

#====================================================================================