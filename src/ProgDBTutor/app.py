# TUTORIAL Len Feremans, Sandy Moens and Joey De Pauw
# see tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
from flask import Flask, request, session, jsonify, flash, redirect, url_for
from flask.templating import render_template
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import config_data
from db_connection import DBConnection
from user_data_acces import DataScientist, UserDataAcces
from user_data_acces import UserDataAcces

from werkzeug.security import generate_password_hash, check_password_hash

import pandas as pd
import csv

import os

engine = create_engine('postgresql://app@localhost:5432/db_recommended4you')
db = scoped_session(sessionmaker(bind=engine))

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
    l = session.get('loggedin', False)
    if l:
        return render_template('home.html', app_data=app_data, isLoggedin=session['loggedin'])
    else:
        return render_template('home.html', app_data=app_data)

@app.route("/contact")
# @login_required
def contact():
    return render_template('contact.html', app_data=app_data)

@app.route("/services", methods=['GET', 'POST'])
# @login_required
def services():
    if 'loggedin' in session:
        if request.method == 'POST':
            dataset = request.form.get('datasetSelection')
            print(dataset)
            algo = request.form.get('algoSelection')
            print(algo)
            start = request.form.get('startingpoint')
            print(start)
            end = request.form.get('endpoint')
            print(end)
            stepsize = request.form.get('stepsize')
            print(stepsize)
            topk = request.form.get('topk')
            print(topk)
            if algo == "popularity":
                pass
            elif algo == "recency":
                pass
            elif algo == "itemknn":
                pass
        # add algorithm to database
        return render_template('services.html', app_data=app_data)
    return redirect(url_for('login'))


@app.route("/datasets", methods=['GET', 'POST'])
# @login_required
def datasets():
    if request.method == 'POST':
        if session['username'] == 'admin': # checken of de user de admin is
            a_f = request.files['articles_file']
            p_f = request.files['purchases_file']
            c_f = request.files['customers_file']

            # data = []
            # with open(a_f, 'rb') as file:
            #     csvfile = csv.reader(file)
            #     for row in csvfile:
            #         data.append(row)
            # print(data)

            # df = pd.read_csv(request.files.get('file'))

            """
            cursor = user_data_access.dbconnect.get_cursor()
            df = pd.read_csv('/home/app/PPDB-Template-App/CSVFiles/articles.csv')
            amountRows = len(df.index)
            amountColumns = len(df.columns)
            dataset_id = 0

            for row in range(amountRows):
                for column in range(amountColumns):
                    print(df.iloc[row, column])
                    cursor.execute('INSERT INTO Dataset(dataset_id, item_id, attribute, value) VALUES(%d, %d, %s, %s)',
                                   (int(dataset_id), int(df.iloc[row, 0]), str(df.iloc[0, column]),
                                    str(df.iloc[row, column])))
            """
        else:
            flash("You need admin privileges to upload a dataset", category='error')
    return render_template('datasets.html', app_data=app_data)

# @app.route("/datasetupload")

@app.route("/visualizations")
# @login_required
def visualizations():
    return render_template('visualizations.html', app_data=app_data)

#----------------- User_DB -----------------#
@app.route("/login", methods=['GET'])
def login():

    # user_objects = user_data_access.get_users()
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
        session['loggedin'] = True
        session['username'] = user_username
        return redirect(url_for('main'))

    return render_template('login.html', app_data=app_data)

@app.route("/login", methods=['POST'])
def login_user():
    user_username = request.form.get('username')
    user_password = request.form.get('password')

    # user = DataScientist.query.filter_by(username=user_username).first

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
            session['loggedin'] = True
            session['username'] = user
            return redirect(url_for('main'))
        else:
            flash('Incorrect password, try again.', category='error')
    else:
        flash('Username does not exist.', category='error')

    return render_template('login.html', app_data=app_data)

@app.route("/logout", methods=['GET', 'POST'])
# @login_required
def logout():
    # logout_user()
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login_user'))

# RUN DEV SERVER
if __name__ == "__main__":
    app.run(HOST, debug=True)
