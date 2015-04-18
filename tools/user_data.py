from tools.login import change_col_db

__author__ = 'Shade390'


def change_user_info(username, form):
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
        change_col_db(username, "age", age, g.db)
    if date:
        print('change date: ' + date)
        change_col_db(username, "date", date, g.db)
    if relationship:
        print('change relationship: ' + relationship)
        change_col_db(username, "relationship", relationship, g.db)
    if occupation:
        print('change occupation: ' + occupation)
        change_col_db(username, "occupation", occupation, g.db)
    if education:
        print('change education: ' + education)
        change_col_db(username, "education", education, g.db)
    if desc:
        print('change desc: ' + desc)
        change_col_db(username, "desc", desc, g.db)
    if home:
        print('change home: ' + home)
        change_col_db(username, "home", home, g.db)
    if phone:
        print('change phone: ' + phone)
        change_col_db(username, "phone", phone, g.db)
