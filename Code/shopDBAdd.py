#!/usr/bin/env python

import os
import cgi
import cgitb
import re
from urllib import parse
import pymysql as mydb
import unicodedata

cgitb.enable()

print('Content-Type: text/html')

host   = 'localhost';
DBname  = 'group1';
DBuser  = 'group1';
DBpswd  = 'group1';

product  = ''

elements = cgi.FieldStorage()

first_name  = elements.getvalue('first_name')  or ""
last_name   = elements.getvalue('last_name')   or ""
addr    = elements.getvalue('addr')    or ""
product     = elements.getvalue('product')     or ""
payment = elements.getvalue('payment') or ""

name_error = ""
addr_error = ""
prod_error = ""
paym_error   = ""
msg = ""

cookies = {}

#==========================================================================
# get_cookies(): retrieve all cookies
#                return a cookies dictionary

def get_cookies():
    cookies = {}

    cookiesStr = os.environ.get('HTTP_COOKIE')
    if not cookiesStr: return cookies

    cookiesArray = cookiesStr.split('; ')
    for cookie in cookiesArray:
        (name, value) = cookie.split('=',1)
        value_decoded = parse.unquote(value)
        cookies[name] = value_decoded

    return cookies

#=============================================================================
# del_cookie(): delete a cookie

def del_cookie(name):
    print(F"Set-Cookie: {name}=xyz; max-age=-999")          #delete a cookie

#=============================================================================
# Validate all required input fields

def validate():
    global name_error,addr_error,prod_error,paym_error,msg

    if (not first_name or not last_name):
        msg        = 'error'
        name_error = '*'
    if (not addr):
        msg        = 'error'
        addr_error = '*'
    if (not product):
        msg        = 'error'
        prod_error = '*'

    if (not payment):
        msg      = 'error'
        paym_error = '*'

    if (msg == 'error'):
        msg  = 'Please enter required field(s) above!'

#==============================================================================
# Display the HTML page
# repopulate the screen with previous entry data
# if there are errors, highlight those with an error message

def display():

    creditcard_checked = 'CHECKED' if (payment == 'creditcard')     else ''
    paypal_checked   =   'CHECKED' if (payment == 'paypal')         else ''
    venmo_checked =      'CHECKED' if (payment == 'venmo')          else ''

    opus_checked =      'CHECKED' if 'Opus_one'                         in product else ''
    scarecrow_checked = 'CHECKED' if 'Scarecrow_cabernet_sauvignon'     in product else ''
    dominus_checked =   'CHECKED' if 'Dominus_estate_christian_moueix'  in product else ''


    first_name = cookies.get('first_name')

    print(F"""
        <html>
        <head>
        <style>
            a {{text-decoration:none; color:brown}}
        </style>
        </head>
        <body bgcolor=lightyellow>
        <h1><center>NAPA WINE</center></h1>

        <h2>Please confirm your order below</h2>
        <form method=POST action={__file__} >
        <fieldset style='width:570px;border-color:red'>
        <legend>Enter Your Information Below</legend>
        <table>
        <tr>
        <td><b>First Name <font color=red> {name_error} </font>
        <td><input type=text name=firstname value='{first_name}'>
            <b>  Last Name </b>
            <input type=text name=lastname value='&nbsp; {last_name}'>
        <tr>
        <td><b>Address <font color=red> {addr_error} </font>
        <td><textarea name=address rows=4 cols=47>{addr}</textarea>
        <tr>
        <td><b>Select Wine Product <font color=red> {prod_error} </font>
        <td>
        <input type='checkbox' name='product' value='Opus_one'                          {opus_checked} />        Opus One
        <input type='checkbox' name='product' value='Scarecrow_cabernet_sauvignon'      {scarecrow_checked} />   Scarecrow Cabernet Sauvignon
        <input type='checkbox' name='product' value='Dominus_estate_christian_moueix'   {dominus_checked} />     Dominus Estate Christian Moueix
        <tr>
        <td><b>Choose Credit Card <font color=red> {paym_error} </font>
        <td>
        <input type=radio name=payment value='creditcard'        {creditcard_checked} /> Credit Card
        <input type=radio name=payment value='paypal' {paypal_checked}   /> Paypal
        <input type=radio name=payment value='venmo'        {venmo_checked} /> Venmo
        <tr>
        <td width=150>
        <input type=submit value='   Place Order   '>
        <td><input type=reset value=Cancel>
        </table>
        </fieldset>
        <br><font color=red> {msg} &nbsp;  </font>
        <br/>
        </form>
        <hr/>
        <center>
        <base href=/~zl2736/group/ >
        <a href=shopCart.py>   shop         </a> |
                               checkout          |
        <a href=shop.py?out=y> logout       </a>
        </center>
       </body>
       </html>
       """)

def write_data():
    global product, msg

    first_name2 = re.sub("[;<>\/'&]","",first_name)
    last_name2  = re.sub("[;<>\/'&]","",last_name)
    addr2   = re.sub("[;<>\/'&]","",addr)

    if type(product) is list:
        product  = ','.join(product)

    try:
        conn = mydb.connect(host=host,user=DBuser,password=DBpswd,database=DBname)

        insert = F"""INSERT INTO cust_order
                     VALUES(0,'{first_name2}','{last_name2}','{addr2}',
                            '{product}','{payment}',{cookies['cust_id']}) """

        cursor = conn.cursor()
        cursor.execute(insert);
        conn.commit()

    except mydb.Error as e:
        (errorNum, errorMsg) = e.args
        msg = 'Database Error - ' + str(errorNum) + errorMsg
        return

    cursor.close()
    conn.close()

    msg = 'Your Order processed successfully';

#=============================================================================
# Delete data from the database

def delete_data():
    global product, msg

    try:
        conn = mydb.connect(host=host,user=DBuser,password=DBpswd,database=DBname)

        delete = F"""DELETE FROM cart
                   WHERE cart_id = {cookies['cart']}"""

        cursor = conn.cursor()
        cursor.execute(delete);
        conn.commit()

    except mydb.Error as e:
        (errorNum, errorMsg) = e.args
        msg = 'Database Error - ' + str(errorNum) + errorMsg
        return

    cursor.close()
    conn.close()

    msg = 'Order processed successfully';

    product  = ''

    del_cookie('cart')
    del_cookie('product')

#=============================================================================
# main
#=============================================================================
cookies = get_cookies()

if not cookies.get('cust_id'):
    print("Location: shop.py \n")
    exit()

if not elements:
    first_name = cookies.get('first_name')   or ''
    last_name  = cookies.get('last_name')   or ''
    addr   = cookies.get('addr')    or ''
    product    = cookies.get('product')  or ''


if elements:
    validate()
    if not msg:
        write_data();
        delete_data();

print('\n')
display()
