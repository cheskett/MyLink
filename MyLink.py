from datetime import timedelta
import sqlite3
import os

from flask import Flask, abort, flash
from flask import g, render_template, request, session, send_from_directory, redirect, url_for
from itsdangerous import BadSignature
from tools.home import home_page
from tools.needed import e_post_images, a_post_images, r_post_images, get_data, user_image_page_select, \
    user_image_page_get

from tools.user_data import change_user_info, friends_data, unfriend, circles_page_db, circle_create, circle_edit, \
    circle_remove, circle_add_f, circle_remove_f, friends_posts_home, your_posts_home, create_post_db, \
    create_post_page_db, edit_post_circles_db, remove_post_db, r_post_circles_db, a_post_circles_db, \
    change_info_get
from tools.friends import request_friend
from tools.login import get_serializer, user_exists, set_user_active
from tools.login import login_post, register_user, check_password, change_password_db
from tools import mysession, pictures


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
        mysession.logout(username)
        session.clear()
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
        albums = pictures.get_albums()
        cur_album = None
        selected = request.args.get('selected')
        if selected is not None:
            cur_album = selected
        elif albums:
            cur_album = albums[0]['name']
        images = pictures.get_pictures(session['username'], cur_album)
        if request.method == "GET":
            return render_template("upload.html", albums=albums, images=images)
        else:
            if 'privacy' in request.form:
                pictures.create_album(request.form)
                return redirect(url_for('upload'))
                # return render_template("upload.html", albums=albums, images=images)
            else:
                file = request.files['file']
                album = request.form['album']
                return pictures.upload_image(file, album)
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
        username = session['username']
        return change_info_get(username, g.db)
    else:
        return render_template('login.html', bad_session=False)


@app.route('/Change_User_Info', methods=['POST'])
def change_info_event():
    if mysession.check_session() == 'passed':
        username = session['username']
        form = request.form
        change_user_info(username, form, g.db)
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
        return unfriend(username, other, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Circles_Page', methods=['GET'])
def circles_page():
    if mysession.check_session() == 'passed':
        username = session['username']
        return circles_page_db(username, g.db, False, False)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Create_Circle', methods=['POST'])
def create_c():
    if mysession.check_session() == 'passed':
        name = request.form["name"]
        username = session['username']
        return circle_create(username, name, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Edit_Circle', methods=['POST'])
def edit_c():
    if mysession.check_session() == 'passed':
        username = session['username']
        name = request.form["circle"]
        return circle_edit(username, name, g.db, False, False, False)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Remove_Circle', methods=['POST'])
def remove_c():
    if mysession.check_session() == 'passed':
        username = session['username']
        name = request.form["circle"]
        return circle_remove(username, name, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Add_Friend', methods=['POST'])
def add_f():
    if mysession.check_session() == 'passed':
        username = session['username']
        name = request.form["name"]
        circle = request.form["circle"]
        # print("user:"+username+" name:"+name+" circle: "+ circle)
        return circle_add_f(username, name, circle, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Remove_Friend', methods=['POST'])
def remove_f():
    if mysession.check_session() == 'passed':
        username = session['username']
        name = request.form["name"]
        circle = request.form["circle"]
        return circle_remove_f(username, name, circle, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Friend_Posts', methods=['GET'])
def friend_posts():
    if mysession.check_session() == 'passed':
        username = session['username']
        return friends_posts_home(username, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Your_Posts', methods=['GET'])
def your_posts():
    if mysession.check_session() == 'passed':
        username = session['username']
        return your_posts_home(username, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Create_Post_Page', methods=['GET'])
def create_post_page():
    if mysession.check_session() == 'passed':
        username = session['username']
        if not request.args.get("album"):
            return create_post_page_db(username, g.db)
        else:
            album = request.args.get("album")
            return create_post_page_db(username, g.db, album)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Create_Post', methods=['POST'])
def create_post():
    if mysession.check_session() == 'passed':
        username = session['username']
        postTitle = request.form["postTitle"]
        postText = request.form["postText"]
        print(postText)
        picture_list = request.form.getlist("pictures")
        if picture_list:
            return create_post_db(username, postTitle, postText, g.db, picture_list)
        else:
            return create_post_db(username, postTitle, postText, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Remove_Post', methods=['POST'])
def remove_post():
    if mysession.check_session() == 'passed':
        username = session['username']
        postid = request.form["postid"]
        return remove_post_db(username, postid, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Edit_Post_Circles', methods=['POST'])
def edit_post_circles():
    if mysession.check_session() == 'passed':
        username = session['username']
        postid = request.form["postid"]
        return edit_post_circles_db(username, postid, g.db, False, False)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Remove_Circle_Post', methods=['POST'])
def remove_post_circles():
    if mysession.check_session() == 'passed':
        username = session['username']
        cid = request.form["circle"]
        postid = request.form["postid"]
        return r_post_circles_db(username, cid, postid, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Add_Circle_Post', methods=['POST'])
def add_post_circles():
    if mysession.check_session() == 'passed':
        username = session['username']
        cid = request.form["circle"]
        postid = request.form["postid"]
        return a_post_circles_db(username, cid, postid, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Edit_Post_Images', methods=['GET'])
def edit_post_images():
    if mysession.check_session() == 'passed':
        username = session['username']
        postid = request.form["postid"]
        return e_post_images(username, postid, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Add_Post_Images', methods=['GET'])
def add_post_images():
    if mysession.check_session() == 'passed':
        username = session['username']
        postid = request.form["postid"]
        picid = request.form["picid"]
        return a_post_images(username, postid, picid, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Remove_Post_Images', methods=['GET'])
def remove_post_images():
    if mysession.check_session() == 'passed':
        username = session['username']
        postid = request.form["postid"]
        picid = request.form["picid"]
        return r_post_images(username, postid, picid, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/Home_Page', methods=['GET'])
def new_home_page():
    if mysession.check_session() == 'passed':
        username = session['username']
        return home_page(username, g.db)
    else:
        return render_template('login.html', bad_session=True)


@app.route('/User_Image_Page', methods=['GET'])
def user_image_page():
    if mysession.check_session() == 'passed':
        username = session['username']
        return user_image_page_get(username, g.db, success=0)
    else:
        return render_template('login.html', bad_session=True)

@app.route('/Change_User_Image', methods=['POST'])
def change_user_image():
    if mysession.check_session() == 'passed':
        username = session['username']
        picid = request.form["picid"]
        return user_image_page_select(username,picid, g.db)
    else:
        return render_template('login.html', bad_session=True)



@app.route('/user/<user>')
def user_data_get(user):
    if mysession.check_session() == 'passed':
        username = session['username']
        return get_data(username, user, g.db)
    else:
        return render_template('login.html', bad_session=True)


# @app.route('/images/<filename>')
# def uploaded_file(filename):
# return send_from_directory(app.config['UPLOAD_FOLDER'],
# filename)


@app.route('/images/<user>/<filename>')
def uploaded_file(user, filename):
    if mysession.check_session() == 'passed':
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], user),
                                   filename)
    else:
        flash("You must login to access images")
        return redirect(url_for('logout'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


if __name__ == '__main__':
    app.debug = "True"
    app.run()
