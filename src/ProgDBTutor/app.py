# TUTORIAL Len Feremans, Sandy Moens and Joey De Pauw
# see tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
import time

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
from werkzeug.utils import secure_filename

import pandas as pd
import csv
import os
import a_b_tests as abtest


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'.csv'}

algo_list = list()
algo_dict = dict()

engine = create_engine('postgresql://app@localhost:5432/db_recommended4you')
db = scoped_session(sessionmaker(bind=engine))

# INITIALIZE SINGLETON SERVICES
app = Flask('Tutorial ')
app.secret_key = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'
app_data = dict()
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
user_data_access = UserDataAcces(connection)

algo_id = 1
abtest_id = user_data_access.getMaxABTestID()+1

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route("/services/start", methods=['GET', 'POST'])
def start():
    pass

@app.route("/services", methods=['GET', 'POST'])
# @login_required
def services():
    global algo_id
    global algo_list
    global abtest_id
    if 'loggedin' in session:
        if request.method == 'POST':
            s = request.form.get('submit_button')
            if s == 'algoSubmit':

                algo = request.form.get('algoSelection')

                if algo == "popularity":
                    windowsize = request.form.get('windowsize')
                    retraininterval = request.form.get('retraininterval1')

                    algo_list.append((algo_id, "popularity", "windowsize", windowsize))
                    algo_list.append((algo_id, "popularity", "retraininterval", retraininterval))
                    algo_dict[algo_id] = "popularity"
                    algo_id += 1
                elif algo == "recency":
                    retraininterval = request.form.get('retraininterval2')
                    algo_list.append((algo_id, "recency", "retraininterval", retraininterval))
                    algo_dict[algo_id] = "recency"
                    algo_id += 1
                elif algo == "itemknn":
                    k = request.form.get('k')
                    window = request.form.get('window')
                    normalize = request.form.get('normalize')
                    retraininterval = request.form.get('retraininterval3')
                    algo_list.append((algo_id, "itemknn", "k", k))
                    algo_list.append((algo_id, "itemknn", "window", window))
                    algo_list.append((algo_id, "itemknn", "normalize", normalize))
                    algo_list.append((algo_id, "itemknn", "retraininterval", retraininterval))
                    algo_dict[algo_id] = "itemknn"
                    algo_id += 1

            elif s == 'abtestSubmit':
                cursor = user_data_access.dbconnect.get_cursor()

                # Params for foreign keys
                creator = session['username']
                cursor.execute('SELECT item_id, attribute FROM Dataset LIMIT 1')
                item = cursor.fetchone()
                algorithm_param = ""
                item_id = item[0]
                attribute_dataset = item[1]

                # General parameters for ABtest
                start = request.form.get('startingpoint')
                end = request.form.get('endpoint')
                stepsize = request.form.get('stepsize')
                topk = request.form.get('topk')
                dataset = request.form.get('datasetSelection')
                dataset_id = ""
                for char in dataset:
                    if char.isdigit():
                        dataset_id += char

                i = 1
                while i < algo_id:
                    # Add entry for ABtest table
                    user_data_access.addAB_Test(abtest_id, i, start, end, stepsize, topk)

                    # Add entries for Algorithm table
                    for j in range(len(algo_list)):
                        if algo_list[j][0] == i:
                            algorithm_param = algo_list[j][2]
                            user_data_access.addAlgorithm(abtest_id, i, algo_list[j][1], algo_list[j][2], algo_list[j][3])

                    # Add entry for result table
                    user_data_access.addResult(abtest_id, i, dataset_id, item_id, attribute_dataset, algorithm_param, creator)

                    i += 1

                # Remove algorithms from list and dicts
                algo_list = []
                algo_dict = {}
                user_data_access.datasetId += 1
                user_data_access.dbconnect.commit()

                # Call function to start a/b tests
                abtest.startAB(abtest_id, user_data_access.datasetId-1)

                abtest_id += 1

                return redirect(url_for('visualizations'))

            # Remove the last add algorithm
            elif s == "remove":
                algo_id -= 1
                if algo_id == 0:
                    algo_id = 1
                else:
                    if algo_dict[algo_id] == 'popularity':
                        algo_list = algo_list[:-2]
                    elif algo_dict[algo_id] == 'recency':
                        algo_list = algo_list[:-1]
                    elif algo_dict[algo_id] == 'itemknn':
                        algo_list = algo_list[:-4]
                    del algo_dict[algo_id]

        return render_template('services.html', app_data=app_data, algo_dict=algo_dict)
    return redirect(url_for('login'))


@app.route("/datasets", methods=['GET', 'POST'])
# @login_required
def datasets():
    if request.method == 'POST':
        if session['username'] == 'admin': # checken of de user de admin is
            # Filepath to articles file
            af = request.files['articles_file']
            uploaded_file = secure_filename(af.filename)
            af_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
            af.save(af_filename)
            data_articles = pd.read_csv(af_filename)
            columns_articles = list(data_articles.columns.values)
            #Add articles to database
            user_data_access.addArticles(data_articles, columns_articles)

            # Filepath to customers file
            cf = request.files['customers_file']
            uploaded_file = secure_filename(cf.filename)
            cf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
            cf.save(cf_filename)
            data_customers = pd.read_csv(cf_filename)
            columns_customers = list(data_customers.columns.values)
            #Add customers to database
            user_data_access.addCustomers(data_customers, columns_customers)

            # Filepath to purchase file
            pf = request.files['purchases_file']
            uploaded_file = secure_filename(pf.filename)
            pf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
            pf.save(pf_filename)
            data_purchases = pd.read_csv(pf_filename)
            #Add purchases to database
            user_data_access.addPurchases(data_purchases)

        else:
            flash("You need admin privileges to upload a dataset", category='error')
    return render_template('datasets.html', app_data=app_data)

# @app.route("/datasetupload")

@app.route("/visualizations")
# @login_required
def visualizations():
    return render_template('visualizations.html', app_data=app_data)

#----------------- User_DB -----------------#
# @app.route("/login", methods=['GET'])
# def login():
#
#     # user_objects = user_data_access.get_users()
#     return render_template('login.html', app_data=app_data)
#
#
# @app.route("/login/<string:email>", methods=['GET'])
# def get_user(username):
#     user_object = user_data_access.get_user(username)
#
#     return jsonify([user_object.to_dct()])


@app.route("/register", methods=['POST'])
def add_user():
    user_firstname = request.form.get('firstname')
    user_lastname = request.form.get('lastname')
    user_username = request.form.get('username')
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    cursor = user_data_access.dbconnect.get_cursor()
    cursor.execute("SELECT username FROM datascientist WHERE username = %s", (user_username))
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

@app.route("/login", methods=['GET', 'POST'])
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
        password = cursor1.fetchone()[0]
        if check_password_hash(password, user_password) or (user_username == 'admin' and password == user_password):
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
