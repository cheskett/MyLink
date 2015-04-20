from datetime import timedelta
import sqlite3
import os

from flask import Flask, abort, flash
from flask import g, render_template, request, session, send_from_directory, redirect, url_for
from itsdangerous import BadSignature

from tools.user_data import change_user_info, friends_data, unfriend
from tools.friends import request_friend
from tools.login import get_serializer, user_exists, set_user_active
from tools.login import login_post, register_user, check_password, change_password_db
from tools import mysession


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'picture_share.db')
IMAGEPATH = 'images/'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/images'
app.config['ALLOWED_EXTENSIONS'] = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def app_login():
    return render_template('login.html')


@app.route('/Log_Out')
def logout():
    if mysession.check_session() == 'passed':
        username = session['username']
        mysession.logout(username);
        return render_template('login.html')
    else:
        return render_template('login.html', bad_session=True)


@app.route('/return')
def app_return():
    if mysession.check_session() == 'passed':
        username = session['username']
        return render_template("picture_options.html", user=username)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_user', methods=['POST'])
def register_u():
    name = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    return register_user(name, password1, password2)


@app.route('/trylogin', methods=['POST'])
def try_login():
    name = request.form['username']
    password = request.form['password']
    return login_post(name, password, g.db)


@app.route('/newalbum')
def new_album():
    return


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if mysession.check_session() == 'passed':
        if request.method == "GET":
            print('IN UPLOAD: ' + session['username'])
            return render_template("upload.html")
        else:
            file = request.files['file']
            # Get user
            user = session['username']

            # Check if the file was uploaded
            if file and allowed_file(file.filename):
                # Make the filename safe, remove unsupported chars
                filename = file.filename.replace(" ", "_")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template("upload_success.html",
                                       filename=filename)

            else:
                return 'No file was uploaded'
    else:
        return render_template('login.html',
                               bad_session=True)


@app.route('/users/activate/<payload>')
def activate_user(payload):
    s = get_serializer()
    try:
        user_id = s.loads(payload)
    except BadSignature:
        abort(404)

    if user_exists(user_id) is True:
        set_user_active(user_id)
        flash("User activated successfully")
        return redirect(url_for('app_login'))
    else:
        flash("User activation failed")
        return redirect(url_for('app_login'))


@app.route('/Change_Password_Page', methods=['POST', 'GET'])
def change_password_page():
    if mysession.check_session() == 'passed':
        return render_template('change_password_page.html');
    else:
        return render_template('login.html', bad_session=False)


@app.route('/change_password', methods=['POST'])
def change_password():
    oldPass = request.form['oldPassword']
    newPass1 = request.form['newPassword1']
    newPass2 = request.form['newPassword2']
    username = session['username']
    if mysession.check_session() == 'passed':
        if check_password(username, oldPass, g.db) == "passed":
            if newPass1 == newPass2:
                change_password_db(username, newPass1, g.db)
                return render_template('change_password_success.html')
            else:
                return render_template('change_password_page.html', bad_match=True)
        else:
            return render_template('change_password_page.html', bad_password=True)
    else:
        return render_template('login.html', bad_session=False)


@app.route('/Change_User_Info_Page', methods=['POST', 'GET'])
def change_info_page():
    if mysession.check_session() == 'passed':
        return render_template('change_user_info_page.html');
    else:
        return render_template('login.html', bad_session=False)


@app.route('/Change_User_Info', methods=['POST'])
def change_info_event():
    if mysession.check_session() == 'passed':
        username = session['username']
        form = request.form
        change_user_info(username,form, g.db)
        return render_template('change_user_success.html')
    else:
        return render_template('login.html', bad_session=False)

@app.route('/Friend_Request_Page')
def friend_request_page():
    if mysession.check_session() == 'passed':
        return render_template("friend_request_page.html")
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Friend_Request_Sent', methods=['POST'])
def friend_request_sent():
    if mysession.check_session() == 'passed':
        requested = request.form["request"]
        if user_exists(requested):
            if request_friend(requested):
                return render_template('friend_request_sent.html', now_friend=True)
            else:
                return render_template('friend_request_sent.html', now_friend=False)
        else:
            return render_template('friend_request_page.html', bad_user=True)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Friends_Page')
def friends_page():
    if mysession.check_session() == 'passed':
        username = session['username']
        return friends_data(username, g.db, False)
    else:
        return render_template('login.html', bad_session=True)

@app.route('/Unfriend', methods=['POST'])
def unfriend_event():
    if mysession.check_session() == 'passed':
        username = session['username']
        other = request.form["other"]
        return unfriend(username,other, g.db)
    else:
        return render_template('login.html', bad_session=True)

@app.route('/Circles_Page', methods=['GET'])
def circles_page():
    if mysession.check_session() == 'passed':
        username = session['username']
        return circles_page_db(username,g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


if __name__ == '__main__':
    app.debug = "True"
    app.run()
