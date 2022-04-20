# TUTORIAL Len Feremans, Sandy Moens and Joey De Pauw
# see tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
from flask import Flask, request, session, jsonify, flash, redirect, url_for
from flask.templating import render_template
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import config_data
from db_connection import DBConnection
from user_data_acces import DataScientist, UserDataAcces

from werkzeug.security import generate_password_hash, check_password_hash

# engine = create_engine('postgresql://max@localhost:5432/postgres')
# db = scoped_session(sessionmaker(bind=engine))

# INITIALIZE SINGLETON SERVICES
app = Flask('Tutorial ')
app.secret_key = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'
app_data = dict()
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
user_data_access = UserDataAcces(connection)

# login_manager = LoginManager()
# login_manager.login_view = 'app.login_user'
# login_manager.init_app(app)
#
# @login_manager.user_loader
# def load_user(username):
#
#     cursor = user_data_access.dbconnect.get_cursor()
#     cursor.execute("SELECT username FROM datascientist WHERE username = %s", (username,))
#
#     return cursor

DEBUG = False
HOST = "127.0.0.1" if DEBUG else "0.0.0.0"

#----------------- VIEW -----------------#
@app.route("/")
@app.route("/home")
def main():
    # print('hallo1')
    # l = db.execute('SELECT * FROM datascientist').fetchall()
    # for i in l:
    #     print(i.username)
    # print('hallo2')
    return render_template('home.html', app_data=app_data)

@app.route("/contact")
@login_required
def contact():
    return render_template('contact.html', app_data=app_data)

@app.route("/services")
@login_required
def services():
    return render_template('services.html', app_data=app_data)

@app.route("/datasets")
@login_required
def datasets():
    return render_template('datasets.html', app_data=app_data)

@app.route("/visualizations")
@login_required
def visualizations():
    return render_template('visualizations.html', app_data=app_data)

#----------------- User_DB -----------------#
@app.route("/login", methods=['GET'])
def login():

    user_objects = user_data_access.get_users()
    return render_template('login.html', app_data=app_data)


@app.route("/login/<string:email>", methods=['GET'])
def get_user(username):
    user_object = user_data_access.get_user(username)

    return jsonify([user_object.to_dct()])


@app.route("/register", methods=['POST'])
def add_user():
    user_firstname = request.form.get('firstname')
    user_lastname = request.form.get('lastname')
    user_username = request.form.get('username')
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    cursor = user_data_access.dbconnect.get_cursor()
    cursor.execute("SELECT username FROM datascientist WHERE username = %s", (user_username,))
    row = cursor.fetchone()
    # user = DataScientist.query.filter_by(username=user_username).first

    # some basic checks (if they trigger, they 'flash' a message on the page (see the login.html doc))
    if row is not None: # check to see if user with the email already exists in the database
        flash('This username already exists.', category='error')
    else:
        user_obj = DataScientist(firstname=user_firstname, lastname=user_lastname, username=user_username, email=user_email, password=generate_password_hash(user_password, method='sha256'))
        print('Adding {}'.format(user_obj.to_dct()))
        user_obj = user_data_access.add_user(user_obj)
        # login_user(user_obj, remember=True)
        flash('Account succesfully registered!', category='success')

        return redirect(url_for('main'))

    return render_template('login.html', app_data=app_data)

@app.route("/login", methods=['POST'])
def login_user():
    user_username = request.form.get('username')
    user_password = request.form.get('password')

    # user = DataScientist.query.filter_by(email=user_email).first

    cursor = user_data_access.dbconnect.get_cursor()
    cursor.execute("SELECT username FROM datascientist WHERE username = %s", (user_username,))
    row = cursor.fetchone()
    if row is not None: # als de username is gevonden
        user = row[0]
        cursor1 = user_data_access.dbconnect.get_cursor()
        cursor1.execute("SELECT password FROM authentication WHERE username = %s", (user_username,))
        if check_password_hash(cursor1.fetchone()[0], user_password):
            flash('Logged in successfully!', category='success')
            # login_user(user, remember=True)
            return redirect(url_for('main'))
        else:
            flash('Incorrect password, try again.', category='error')
    else:
        print(cursor.fetchone())
        print(cursor.fetchall())
        flash('Username does not exist.', category='error')

    return render_template('login.html', app_data=app_data)

# @app.route("/logout", methods=['POST'])
# @login_required
# def logout_user():
#     logout_user()
#     return redirect(url_for('login_user'))

# RUN DEV SERVER
if __name__ == "__main__":
    app.run(HOST, debug=True)
