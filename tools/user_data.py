from tools.login import change_col_db
from flask import Flask, render_template, session, g, current_app as app, url_for

__author__ = 'Shade390'


def change_user_info(username, form, db):

    age = form['age']
    date = form['date']
    relationship = form['relationship']
    occupation = form['occupation']
    education = form['education']
    desc = form['desc']
    home = form['home']
    phone = form['phone']

    if age:
        print('change age: ' + age)
        change_col_db(username, "age", age, db)
    if date:
        print('change date: ' + date)
        change_col_db(username, "date", date, db)
    if relationship:
        print('change relationship: ' + relationship)
        change_col_db(username, "relationship", relationship, db)
    if occupation:
        print('change occupation: ' + occupation)
        change_col_db(username, "occupation", occupation, db)
    if education:
        print('change education: ' + education)
        change_col_db(username, "education", education, db)
    if desc:
        print('change desc: ' + desc)
        change_col_db(username, "desc", desc, db)
    if home:
        print('change home: ' + home)
        change_col_db(username, "home", home, db)
    if phone:
        print('change phone: ' + phone)
        change_col_db(username, "phone", phone, db)


def friends_data(username, db):
    friends     = ''
    requested   = ''
    requests    = ''
    
    return render_template('friends_page.html', friends=friends, requests=requests, requested=requested)