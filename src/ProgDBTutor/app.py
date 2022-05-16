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
import redis
from rq import Queue

# from config import config_data
# from db_connection import DBConnection
from user_data_acces import * # , UserDataAcces
# from user_data_acces import UserDataAcces

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import pandas as pd
import csv
import os
import a_b_tests as abtest
from datetime import datetime, timedelta

from config import config_data
from db_connection import DBConnection
# from user_data_acces import UserDataAcces

"""
Imports voor pages
"""
from datasets import *
from userpagina import *


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'.csv'}


app = Flask('Tutorial')
app.secret_key = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'
app_data = dict()
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

algo_list = list()
algo_dict = dict()

engine = create_engine('postgresql://app@localhost:5432/db_recommended4you')
db = scoped_session(sessionmaker(bind=engine))

#For threading
rds = redis.Redis()
datasetQueue = Queue('queue1', connection=rds)  #queue for dataset processes
abTestQueue = Queue('queue2', connection=rds)   #queue for abTest processes

# INITIALIZE SINGLETON SERVICES


algo_id = 1
abtest_id = getMaxABTestID()+1

file_attr_types = ["string", "float", "int", "image_url"]
# attributes = dict({'articles': list(), 'customers': list()})
# article_attr = ["aa", "ab", "ac", "ad", "ae", "af", "ag0bvb", "ah"]
# customer_attr = ["ca", "cb", "cc", "cd"]
# attributes['articles'] = article_attr
# attributes['customers'] = customer_attr

jsonData = dict() # dictionary om de general parameters voor de ab-test pagina op te slaan


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

DEBUG = True
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
    #


    if l:
        return render_template('home.html', app_data=app_data, isLoggedin=session['loggedin'])
    else:
        return render_template('home.html', app_data=app_data)

@app.route("/contact")
# @login_required
def contact():
    return render_template('contact.html', app_data=app_data)

#----------------- A/B-test page -----------------#

@app.route("/services/addalgorithm", methods=['GET', 'POST'])
def addalgorithm():
    if request.method == 'POST':
        global jsonData
        jsonData = request.get_json()
        # print(jsonData)
        return jsonData

@app.route("/services", methods=['GET', 'POST'])
# @login_required
def services():
    global algo_id
    global algo_list
    global algo_dict
    global abtest_id
    global algo_dict
    if 'loggedin' in session:
        if request.method == 'POST':

            s = request.form.get('submit_button')
            if s == 'algoSubmit':

                algo = request.form.get('algoSelection')

                if algo == "popularity":
                    windowsize = request.form.get('windowsize', None)
                    retraininterval = request.form.get('retraininterval1', None)
                    if windowsize == "" or retraininterval == "":
                        flash('Algorithm parameters not fully filled in.', category='error')
                    else:
                        algo_list.append((algo_id, "popularity", "windowsize", windowsize))
                        algo_list.append((algo_id, "popularity", "retraininterval", retraininterval))
                        algo_dict[algo_id] = "popularity"
                        algo_id += 1
                elif algo == "recency":
                    retraininterval = request.form.get('retraininterval2', None)
                    if retraininterval == "":
                        flash('Algorithm parameters not fully filled in.', category='error')
                    else:
                        algo_list.append((algo_id, "recency", "retraininterval", retraininterval))
                        algo_dict[algo_id] = "recency"
                        algo_id += 1
                elif algo == "itemknn":
                    k = request.form.get('k')
                    window = request.form.get('window')
                    normalize = request.form.get('normalize')
                    retraininterval = request.form.get('retraininterval3')
                    if k == None or window == "" or normalize == "" or retraininterval == "":
                        flash('Algorithm parameters not fully filled in.', category='error')
                    else:
                        algo_list.append((algo_id, "itemknn", "k", k))
                        algo_list.append((algo_id, "itemknn", "window", window))
                        algo_list.append((algo_id, "itemknn", "normalize", normalize))
                        algo_list.append((algo_id, "itemknn", "retraininterval", retraininterval))
                        algo_dict[algo_id] = "itemknn"
                        algo_id += 1

            elif s == 'abtestSubmit':
                cursor = connection.get_cursor()

                # Params for foreign keys
                creator = session['username']

                # General parameters for ABtest
                start = request.form.get('startingpoint')
                end = request.form.get('endpoint')
                stepsize = request.form.get('stepsize')
                topk = request.form.get('topk')
                dataset = request.form.get('datasetSelection')
                if not dataset:
                    return redirect(url_for('visualizations'))
                dataset_id = ""
                for char in dataset:
                    if char.isdigit():
                        dataset_id += char

                i = 1
                while i < algo_id:
                    # Add entry for ABtest table
                    addAB_Test(abtest_id, i, start, end, stepsize, topk)
                    # abTestQueue.enqueue(addAB_Test, abtest_id, i, start, end, stepsize, topk)

                    # Add entries for Algorithm table
                    for j in range(len(algo_list)):
                        if algo_list[j][0] == i:
                            algorithm_param = algo_list[j][2]
                            addAlgorithm(abtest_id, i, algo_list[j][1], algo_list[j][2],
                            algo_list[j][3])
                            abTestQueue.enqueue(addAlgorithm, abtest_id, i, algo_list[j][1], algo_list[j][2],
                                        algo_list[j][3])

                    # Add entry for result table
                    #addResult(abtest_id, i, dataset_id, algorithm_param, creator)
                    abTestQueue.enqueue(addResult, abtest_id, i, dataset_id, algorithm_param, creator)

                    i += 1

                # Remove algorithms from list and dicts
                algo_list = []
                algo_dict = {}
                connection.commit()

                # Call function to start a/b tests
                maxABtestID = getMaxABTestID()
                #abtest.startAB(maxABtestID, dataset_id)
                #abtest.getABtestResults(maxABtestID, dataset_id)
                #abtest.getAB_Pop_Active(maxABtestID, dataset_id)

                abTestQueue.enqueue(abtest.startAB, maxABtestID,dataset_id)
                abTestQueue.enqueue(abtest.getABtestResults, maxABtestID, dataset_id)
                abTestQueue.enqueue(abtest.getAB_Pop_Active, maxABtestID, dataset_id)

                abtest_id += 1
                algo_id = 1
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

        dataset_names = getDatasets()
        return render_template('services.html', app_data=app_data, algo_dict=algo_dict, genParDict=jsonData, names=dataset_names)

    return redirect(url_for('login_user'))

#----------------- Dataset page -----------------#

@app.route("/datasets/<ds_id>", methods=['GET', 'POST'])
def getData(ds_id):
    if request.method == 'GET':
        return getDatasetInformation(ds_id)
    else:
        pass


@app.route("/datasets", methods=['GET', 'POST'])
# @login_required
def datasets():
    handelRequests(app, session, request, datasetQueue)
    dataset_names = getDatasets()

    return render_template('datasets.html', app_data=app_data, names=dataset_names, attr_types=json.dumps(file_attr_types))

@app.route("/fileupload", methods=['GET', 'POST'])
def fileupload():
    if request.method == 'POST':
        headerDict = {}
        if request.files.get('articles_file').filename != '':
            headerList = getCSVHeader(app, 'articles_file')
            headerDict['articles_attr'] = headerList
            headerDict['changed'] = 'articles_attr'
        if request.files.get('customers_file').filename != '':
            headerList = getCSVHeader(app, 'customers_file')
            headerDict['customers_attr'] = headerList
            headerDict['changed'] = 'customers_attr'
        # print(headerDict)
        return headerDict

@app.route("/datasetupload")
def datasetupload(rowData):
    cursor = connection.get_cursor()
    # remove dataset(s) with id=rowData
    try:
        cursor.execute("DELETE FROM Dataset WHERE dataset_id = %s", (rowData))
        connection.commit()
    except:
        connection.rollback()

    return redirect(url_for('datasets'))

#----------------- A/B-test Visualization page -----------------#

@app.route("/visualizations")
# @login_required
def visualizations():
    return render_template('visualizations.html', app_data=app_data)

#----------------- A/B-test list -----------------#

@app.route("/testlist")
def testlist():
    cursor = connection.get_cursor()
    cursor.execute("SELECT DISTINCT(abtest_id) FROM ABTest")

    testList = list()
    for row in cursor:
        testList.append(row[0])

    return render_template('testlist.html', app_data=app_data, testList = testList)


#----------------- User section page -----------------#
@app.route("/usersection")
def usersection():
    dataset_id = request.args.get("dataset_id")
    customer_id = request.args.get("customer_id")
    abtest_id = request.args.get("abtest_id")
    value = 0
    recommendations, history, interval, graph = getUserInformation(abtest_id, dataset_id, customer_id)
    datasetname = getDatasetname(dataset_id)

    return render_template('user.html', username=customer_id, datasetname=datasetname, history=history, url="", recommendations=recommendations, graphdata=graph, abtestInterval=interval)

#----------------- User_Login -----------------#

@app.route("/register", methods=['GET', 'POST'])
def add_user():
    user_firstname = request.form.get('firstname')
    user_lastname = request.form.get('lastname')
    user_username = request.form.get('username')
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    cursor = connection.get_cursor()
    cursor.execute("SELECT username FROM datascientist WHERE username = %s", (user_username,))
    row = cursor.fetchone()
    # user = DataScientist.query.filter_by(username=user_username).first

    # some basic checks (if they trigger, they 'flash' a message on the page (see the login.html doc))
    if row is not None: # check to see if user with the email already exists in the database
        flash('This username already exists.', category='error')
    else:
        user_obj = DataScientist(firstname=user_firstname, lastname=user_lastname, username=user_username, email=user_email, password=generate_password_hash(user_password, method='sha256'))
        print('Adding {}'.format(user_obj.to_dct()))
        user_obj = add_user(user_obj)
        # login_user(user_obj, remember=True)

        flash('Account succesfully registered!', category='success')
        session['loggedin'] = True
        session['username'] = user_username
        return redirect(url_for('services'))

    return render_template('login.html', app_data=app_data)

@app.route("/login", methods=['GET', 'POST'])
def login_user():

    if request.method == 'POST':

        user_username = request.form.get('username')
        user_password = request.form.get('password')

        # user = DataScientist.query.filter_by(username=user_username).first
        cursor = connection.get_cursor()
        cursor.execute("SELECT username FROM datascientist WHERE username = %s", (user_username,))
        row = cursor.fetchone()
        if row is not None: # als de username is gevonden
            user = row[0]
            cursor1 = connection.get_cursor()
            cursor1.execute("SELECT password FROM authentication WHERE username = %s", (user_username,))
            password = cursor1.fetchone()[0]
            if check_password_hash(password, user_password) or (user_username == 'admin' and password == user_password):
                flash('Logged in successfully!', category='success')
                # login_user(user, remember=True)
                session['loggedin'] = True
                session['username'] = user
                return redirect(url_for('services'))
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
    # session.pop('_flashes', None)
    return redirect(url_for('login_user'))

# RUN DEV SERVER
if __name__ == "__main__":
    #os.system("kill `ps -A | grep rq | grep -v grep | awk '{ print $1 }'`")
    app.run(HOST, debug=True)
