#!/usr/bin/python3
import os
import cgi                            #cgi 
import cgitb                          #cgi with traceback error handling
from urllib import parse              #for url encoding
import pymysql as mydb                #Mysql 3x database driver
             
cgitb.enable()

print("Content-Type: text/html")     #required http response header (w/ no extra line)

elements = cgi.FieldStorage()         #obtain the input from screen

msg     = "" 
cust_id = ""
save    = ""
fname   = ""
lname   = ""
addr    = ""

#=============================================================================
# Validate all required input fields
#=============================================================================
def validate_form():
    global msg

    if (not user or not pswd) :                         #if nothing is entered on screen
        msg  = 'Please enter user id and password!'     
        return

#=============================================================================
# Read pswd from the database
# validates to make sure user exists, and pswd is validate for user
#=============================================================================
def read_pswd():
    global cust_id, fname, lname, addr, msg   
 
    sql = F""" SELECT cust_id, password, first_name, last_name,address
               FROM customer 
               WHERE lower(user) = '{user}' """         #not case sensitive
    try:
        conn = mydb.connect(host='localhost',user='team1',password='team1',database='team1')
 
        cursor = conn.cursor()                          #create a cursor
        cursor.execute(sql);                            #execute the sql

    except mydb.Error as e:
        errorNum = e.args[0]
        errorMsg = e.args[1]
        error = 'Database Error - ' + str(errorNum) + errorMsg
        return      
       
    results = cursor.fetchall()                     #get all the rows (should only be 1 row)
    if (not results):
        msg = F"User {user} does not exist.  Please register first"
        return        

    row     = results[0]                            #take first row
    cust_id = row[0]                                #first column
    DBpswd  = row[1]
    fname   = row[2]
    lname   = row[3]
    addr    = row[4]
    if (pswd != DBpswd):                            #if pswd entered != database pswd
        msg = F"Password is invalid for {user}"
                            
    cursor.close()                                  #close the cursor/buffer
    conn.close()                                    #close the connection

#==============================================================================
# Display the HTML page  
# if there are errors, display message
#==============================================================================
def display():

    checked='checked' if save else ''               #if save user flag is on -> checked
    print(F"""
        <html>
        <head>
        <title>Nile.com</title>
        <style>
            a {{text-decoration:none; color:brown}}
        </style>
        </head>

        <body bgcolor=lightyellow>
        <h1 align=center>Shop.Com</H1>

        <form method=GET action={__file__}>
        <fieldset style='width:350;border-color:red'>
        <legend align='left'>Sign In</legend>
        <table>
        <tr><td>Enter your user id       <td><input type=text     name=user value='{user}' >
        <tr><td>Enter your password      <td><input type=password name=pswd value='{pswd}' >
        <tr><td align=right>Save user id <td><input type=checkbox name=save value='y' {checked} >
        <tr><td><td><input type=submit value='         Sign In       '> 
        </table>
        </fieldset>
        <br>
        <fieldset style='width:350;border-color:red'>
        <legend align='center'>Register</legend>
        &nbsp;<input type=button value='Register  ' onClick="location.href='shopProf.py'">
        If first time user, please register
        <br><br>
        </fieldset>
        </form>
        <div style='color:red;'> {msg} &nbsp; </div>
        <hr/>
        <center>
        <base href=/~zl2736/formdata/ >
                               login         |
        <a href=shopProf.py>   register </a> |
        <a href=shopCart.py>    shop    </a>    
        </center>
        </body>
        </html>
    """)

#==========================================================================
# get_cookies(): retrieve all cookies
#                return a cookies dictionary
#==========================================================================
def get_cookies():
    cookies = {}                                            #create a cookie dictionary

    cookiesStr = os.environ.get('HTTP_COOKIE')              #obtain the HTTP cookies
    if not cookiesStr: return cookies                       #if no cookies, return 

    cookiesArray = cookiesStr.split('; ')                   #split on ;
    for cookie in cookiesArray:                             #loop thru all cookies
        (name, value) = cookie.split('=',1)                 #split on first =
        value_decoded = parse.unquote(value)                #decode the value (if encoded)
        cookies[name] = value_decoded                       #cookie value (encoded)

    return cookies

#=============================================================================
# Save the cookies
#=============================================================================
def save_cookies():
    user2  = parse.quote(user)                              #url encode the cookies
    fname2 = parse.quote(fname)                         
    lname2 = parse.quote(lname)
    addr2  = parse.quote(addr)

    print(F"Set-Cookie: cust_id={cust_id}")                 #create temporary cookies
    print(F"Set-Cookie: fname ={fname2}")                 
    print(F"Set-Cookie: lname = {lname2}")              
    print(F"Set-Cookie: addr = ={addr2}")       
    if save:
        print(F"Set-Cookie: user={user2}; max-age=604800")  #save cookie for 1 week                              
    if not save:
        print(F"Set-Cookie: user=xyz; max-age=-999")        #delete the cookie                               
#=============================================================================
# logout and delete the temporary cookie
#=============================================================================
def delete_cookies():
    print("Set-Cookie: cust_id=xyz; max-age=-999")      #delete cookies
    print("Set-Cookie: fname=xyz;   max-age=-999")    
    print("Set-Cookie: lname=xyz;   max-age=-999")    
    print("Set-Cookie: addr=xyz;    max-age=-999")    
    if not save:
        print(F"Set-Cookie: user=xyz; max-age=-999")                                

#=============================================================================
# main
#=============================================================================
user   = elements.getvalue('user') or ""        #text field             
pswd   = elements.getvalue('pswd') or ""        #pswd field 
save   = elements.getvalue('save') or ""        #save field 
logout = elements.getvalue('out')  or ""        #logout requested?

cookies = get_cookies()                         #get the cookies
if not user:                                    #if user is not entered
    user = cookies.get('user') or ''            #check to see if user cookie exist
    if user:                                    #if exists
        save ='y'                               #turn the save flag on

if not logout:                                          #if not logging out
    if elements:                                       #if data entered in screen
        validate_form()
        if not msg:                                     #if no errors
            read_pswd()
        if not msg:
            save_cookies()  
            print('location: shopCart.py \n')
            exit()         
    msg = 'Please enter login info, or register' 
    print('\n')                                         #end of headers
    display()                                           #display the page

if logout:                                              #if logging out
    delete_cookies()                                    #delete cookies
    msg = 'You have logged out successfully'
    print('\n')                                         #end of headers
    display()                                           #display the page
 