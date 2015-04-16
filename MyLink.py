from datetime import timedelta
import sqlite3
import os

from flask import Flask
from flask import g, render_template, request, session, send_from_directory

from tools.login import login_post, register_user
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


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_user', methods=['POST'])
def register_u():
    name = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    return register_user(name,password1, password2)


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
