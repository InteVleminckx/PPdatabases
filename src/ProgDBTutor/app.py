# TUTORIAL Len Feremans, Sandy Moens and Joey De Pauw
# see tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
import json
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
from user_data_acces import *  # , UserDataAcces
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
from visualisation import *

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'.csv'}

app = Flask('Tutorial')
app.secret_key = '*^*(*&)(*)(*afafafaSDD47j\3yX R~X@H!jmM]Lwf/,?KT'
app_data = dict()
app_data['app_name'] = config_data['app_name']
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# algo_list = list()
algo_dict = dict()

engine = create_engine('postgresql://app@localhost:5432/db_recommended4you')
db = scoped_session(sessionmaker(bind=engine))

# For threading
rds = redis.Redis()
datasetQueue = Queue('queue1', connection=rds)  # queue for dataset processes
abTestQueue = Queue('queue2', connection=rds)  # queue for abTest processes

# INITIALIZE SINGLETON SERVICES


# algo_id = 1
abtest_id = getMaxABTestID() + 1

file_attr_types = ["string", "float", "int", "image_url"]


jsonData = dict()  # dictionary om de general parameters voor de ab-test pagina op te slaan

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


# ----------------- VIEW -----------------#
@app.route("/")
@app.route("/home")
def main():
    l = session.get('loggedin', False)

    if l:
        return render_template('home.html', app_data=app_data, isLoggedin=session['loggedin'])
    else:
        return render_template('home.html', app_data=app_data)


@app.route("/contact")
# @login_required
def contact():
    return render_template('contact.html', app_data=app_data)


# ----------------- A/B-test page -----------------#

@app.route("/services/addalgorithm", methods=['GET', 'POST'])
def addalgorithm():
    if request.method == 'POST':

        dataDict = request.get_json()
        form_data = dataDict['form_data']
        algo_id = dataDict['algo_id']
        algo_list = dataDict['algo_list']
        algo_dict = dataDict['algo_dict']

        algo = form_data['algoSelection']

        if algo == "popularity":
            windowsize = form_data['windowsize']
            retraininterval = form_data['retraininterval1']
            if windowsize == "" or retraininterval == "":
                flash('Algorithm parameters not fully filled in.', category='error')
            else:
                algo_list.append([algo_id, "popularity", "windowsize", windowsize])
                algo_list.append([algo_id, "popularity", "retraininterval", retraininterval])
                algo_dict[str(algo_id)] = "popularity"
                algo_id += 1
        elif algo == "recency":
            retraininterval = form_data['retraininterval2']
            if retraininterval == "":
                flash('Algorithm parameters not fully filled in.', category='error')
            else:
                algo_list.append([algo_id, "recency", "retraininterval", retraininterval])
                algo_dict[str(algo_id)] = "recency"
                algo_id += 1
        elif algo == "itemknn":
            k = form_data['k']
            window = form_data['window']
            normalize = form_data['normalize']
            retraininterval = form_data['retraininterval3']
            if k == "" or window == "" or normalize == "" or retraininterval == "":
                flash('Algorithm parameters not fully filled in.', category='error')
            else:
                algo_list.append([algo_id, "itemknn", "k", k])
                algo_list.append([algo_id, "itemknn", "window", window])
                algo_list.append([algo_id, "itemknn", "normalize", normalize])
                algo_list.append([algo_id, "itemknn", "retraininterval", retraininterval])
                algo_dict[str(algo_id)] = "itemknn"
                algo_id += 1

        data_dict = {'algo_id': algo_id, 'algo_list': algo_list, 'algo_dict': algo_dict}
        # print("success")
        # print(data_dict)
        return data_dict


@app.route("/services", methods=['GET', 'POST'])
# @login_required
def services():
    if 'loggedin' in session:

        if request.method == 'POST':

            dataDict = request.get_json()
            print(dataDict)

            form_data = dataDict['form_data']
            algo_id = dataDict['algo_id']
            algo_list = dataDict['algo_list']
            algo_dict = dataDict['algo_dict']

            cursor = connection.get_cursor()

            # Params for foreign keys
            creator = session['username']

            # General parameters for ABtest
            start = form_data['startingpoint']
            end = form_data['endpoint']
            stepsize = form_data['stepsize']
            topk = form_data['topk']
            dataset = form_data['datasetSelection']
            ABTestID = getMaxABTestID() + 1
            if not dataset:
                return redirect(url_for('visualizations'))
            dataset_id = ""
            for char in dataset:
                if char.isdigit():
                    dataset_id += char

            i = 1
            while i < algo_id:
                # Add entry for ABtest table
                # addAB_Test(abtest_id, i, start, end, stepsize, topk)
                abTestQueue.enqueue(addAB_Test, ABTestID, i, start, end, stepsize, topk)

                # Add entries for Algorithm table
                for j in range(len(algo_list)):
                    if algo_list[j][0] == i:
                        algorithm_param = algo_list[j][2]
                        # addAlgorithm(abtest_id, i, algo_list[j][1], algo_list[j][2],
                        # algo_list[j][3])
                        abTestQueue.enqueue(addAlgorithm, ABTestID, i, algo_list[j][1], algo_list[j][2],
                                            algo_list[j][3])

                # Add entry for result table
                # addResult(abtest_id, i, dataset_id, algorithm_param, creator)
                abTestQueue.enqueue(addResult, ABTestID, i, dataset_id, algorithm_param, creator)

                i += 1

            # Remove algorithms from list and dicts
            algo_list = []
            algo_dict = {}
            connection.commit()

            # Call function to start a/b tests
            # abtest.startAB(maxABtestID, dataset_id)
            # abtest.getABtestResults(maxABtestID, dataset_id)
            # abtest.getAB_Pop_Active(maxABtestID, dataset_id)

            abTestQueue.enqueue(abtest.startAB, ABTestID, dataset_id, job_timeout=3600)
            # jobABRes = abTestQueue.enqueue(abtest.getABtestResults, ABTestID, dataset_id)
            # jobPopAct = abTestQueue.enqueue(abtest.getAB_Pop_Active, ABTestID, dataset_id)
            jobABvisualisations = abTestQueue.enqueue(getInfoVisualisationPage, ABTestID, dataset_id, job_timeout=600)

            recos = abTestQueue.enqueue(getTopkMostRecommendItemsPerAlgo, "", "", dataset_id, 5, ABTestID)
            totPurch = abTestQueue.enqueue(getTopkMostPurchasedItems, "", "", dataset_id, 5, ABTestID)
            totRev = abTestQueue.enqueue(getTotaleRevenue, "", "", dataset_id, ABTestID)
            listUsers = abTestQueue.enqueue(getListOfActiveUsers, "", "", dataset_id, ABTestID)

            session["abVisualistation"] = [jobABvisualisations.id, recos.id, totPurch.id, totRev.id, listUsers.id]

            # return redirect(url_for('visualizations')) #TODO if not work turn on

            data_dict = {'algo_id': algo_id, 'algo_list': algo_list, 'algo_dict': algo_dict}

            return data_dict

        elif request.method == 'GET':
            pass
        dataset_names = getDatasets()
        return render_template('services.html', app_data=app_data, genParDict=jsonData, names=dataset_names)

    return redirect(url_for('login_user'))


# ----------------- Dataset page -----------------#

@app.route("/datasets/<ds_id>", methods=['GET', 'POST'])
def getData(ds_id):
    if request.method == 'GET':
        return getDatasetInformation(ds_id)


@app.route("/datasets", methods=['GET', 'POST'])
# @login_required
def datasets():
    if 'loggedin' in session:

        type_list = {}
        if request.method == 'POST':
            type_list = {'articles_types': [], 'customers_types': [], 'articles_name_column': '',
                         'customers_name_column': ''}
            type_item = 0
            while request.form.get(f"{type_item}"):
                type_list['articles_types'].append(request.form.get(f"{type_item}"))
                type_item += 1
            type_item = -1
            while request.form.get(f"{type_item}"):
                type_list['customers_types'].append(request.form.get(f"{type_item}"))
                type_item -= 1
            art_col_name = request.form.get("articles_name_column")
            if art_col_name:
                type_list['articles_name_column'] = art_col_name
            cust_col_name = request.form.get("customers_name_column")
            if cust_col_name:
                type_list['customers_name_column'] = cust_col_name

        # handelRequests(app, session, request, datasetQueue, type_list)
        jobs = handelRequests(app, session, request, datasetQueue, type_list)
        if 'jobsDataset' not in session:
            session['jobsDataset'] = []
        if jobs:
            session['jobsDataset'] = []
            c = session['jobsDataset']
            c.append(jobs)
            session['jobsDataset'] = c
        dataset_names = getDatasets()

        return render_template('datasets.html', app_data=app_data, names=dataset_names,
                               attr_types=json.dumps(file_attr_types))
    return redirect(url_for('login_user'))


@app.route("/datasets/update")
def datasetUpdate():
    if 'jobsDataset' in session:
        finished = True
        notInQueue = True
        if len(session["jobsDataset"]) == 0:
            return 'done'

        for i in range(len(session["jobsDataset"])):
            for key, value in session["jobsDataset"][i]:
                j = datasetQueue.fetch_job(key)
                if j is not None:
                    notInQueue = False
                    if str(j.get_status()) == "finished":
                        l = session["jobsDataset"][i]
                        l[key] = True
                        session["jobsDataset"] = l
            if notInQueue:
                l = session["jobsDataset"]
                l.pop(i)
                session["jobsDataset"] = l

            for key, value in session["jobsDataset"][i]:
                if not value:
                    finished = False

            if finished:
                return 'done'
    return 'notDone'


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

# ----------------- A/B-test Visualization page -----------------#

@app.route("/visualizations")
# @login_required
def visualizations():
    return render_template('visualizations.html', app_data=app_data)


@app.route("/visualizations/update")
def visualizationsUpdate():
    if "abVisualistation" in session:
        job = session["abVisualistation"]
        job_ = abTestQueue.fetch_job(job[-1])
        if job_ is not None:
            if str(job_.get_status()) == "finished":
                visualization = abTestQueue.fetch_job(job[0]).result
                topkReco = abTestQueue.fetch_job(job[1]).result
                topkPurchases = abTestQueue.fetch_job(job[2]).result
                totRev = abTestQueue.fetch_job(job[3]).result
                listUsers, orderedList, totUsers = abTestQueue.fetch_job(job[4]).result

                return {"visualization": visualization, "topkRecommendations": topkReco, "topkPurchases": topkPurchases,
                        "totaleRevenue": totRev, "totaleUsers": totUsers, "listUsers": listUsers, "sortingOrder": orderedList}
    return {}


# ----------------- A/B-test list -----------------#

@app.route("/testlist")
def testlist():
    creator = session['username']
    testList = []
    cursor = connection.get_cursor()
    cursor.execute("SELECT distinct(a.abtest_id), r.dataset_id, d.dataset_name, a.start_point, a.end_point, "
                   "a.stepsize, "
                   "a.topk FROM ABTest a, Dataset d, Result r WHERE r.creator = %s AND a.abtest_id = r.abtest_id AND "
                   "a.result_id = r.result_id AND r.dataset_id = d.dataset_id", (creator,))
    for row in cursor:
        d = {'abtest_id': row[0], 'dataset_id': row[1], 'dataset_name': row[2], 'startingpoint': str(row[3])[:10],
             'endpoint': str(row[4])[:10], 'stepsize': row[5], 'topk': row[6], 'algorithms': None}
        testList.append(d)
    for i in range(len(testList)):
        algos = {}  # per (key, value), de value bevat op index 0 de naam van de algoritme en alles erna zijn de
        # parameters.
        cursor.execute("SELECT distinct(a.param_name), a.result_id, a.name, a.value FROM Algorithm a,  Result r WHERE "
                       "a.abtest_id = %s "
                       "AND r.creator = %s", (testList[i]['abtest_id'], creator))
        for row in cursor:
            if row[1] in algos.keys():
                algos[row[1]][1][row[0]] = row[3]
            else:
                algos[row[1]] = [row[2], {row[0]: row[3]}]

        testList[i]['algorithms'] = algos

    print(testList)
    return render_template('testlist.html', app_data=app_data, testList=testList)


@app.route("/abTestRemove", methods=['GET', 'POST'])
def abTestRemove():
    data = request.get_json()
    abTest_id = data['abtest_id']

    cursor = connection.get_cursor()
    cursor.execute("DELETE FROM ABTest WHERE abtest_id = %s", (str(abTest_id),))
    return {}


# ----------------- User section page -----------------#

@app.route("/usersection/update")
def usersectionUpdate():
    print("update")
    if "userpage" in session:
        userpage = session["userpage"]
        job = abTestQueue.fetch_job(userpage)
        print(job.get_status())
        if job is not None:
            if str(job.get_status()) == "finished":
                recommendations, history, interval, graph, topkListprint, dates = abTestQueue.fetch_job(userpage[0])
                return {"recommendations": recommendations, "history": history, "interval": interval, "graph": graph,
                        "topkListprint": topkListprint, "dates": dates}
    return {}


@app.route("/usersection")
def usersection():
    dataset_id = request.args.get("dataset_id")
    customer_id = request.args.get("customer_id")
    abtest_id = request.args.get("abtest_id")
    information = abTestQueue.enqueue(getUserInformation, abtest_id, dataset_id, customer_id)

    session["userpage"] = information.id
    datasetname = getDatasetname(dataset_id)
    return render_template('user.html', username=customer_id, datasetname=datasetname)


@app.route("/itemsection_graph", methods=['POST', 'GET'])
def itemsection_graph():
    if request.method == 'POST':
        dataset_id = request.form.get('dataset_id', None)
        abtest_id = request.form.get("abtest_id", None)
        item_id = request.form.get("item_id", None)

        numbers = []
        maxYValue = 0
        columns = []

        graph_type = request.form.get('graph_select', None)
        begin_date = request.form.get('begin_time', None)
        end_date = request.form.get('end_time', None)
        data = []

        # Compute popularity item graph
        if graph_type == 'Popularity item':
            startPoint = datetime.strptime(begin_date, '%Y-%m-%d')
            endPoint = datetime.strptime(end_date, '%Y-%m-%d')
            stepsize = timedelta(days=1)

            # Add first row to data
            data = [['Date', 'Purchases']]

            while startPoint <= endPoint:
                amountCorrectRecommendations = getItemPurchases(dataset_id, item_id, str(startPoint)[0:10])
                data.append([str(startPoint)[0:10], amountCorrectRecommendations])
                startPoint += stepsize

        # Compute recommendation count graph
        elif graph_type == 'Recommendation count':
            startPoint = datetime.strptime(begin_date, '%Y-%m-%d')
            endPoint = datetime.strptime(end_date, '%Y-%m-%d')
            stepsize = timedelta(days=1)

            # Add first row that contains all algorithm names
            firstRow = ['Date']
            resultIDs = getResultIds(abtest_id, dataset_id)
            for result_id in resultIDs:
                algorithm = getAlgorithm(abtest_id, result_id)
                if algorithm.name == 'popularity':
                    firstRow.append('Popularity' + str(result_id))
                elif algorithm.name == 'recency':
                    firstRow.append('Recency' + str(result_id))
                elif algorithm.name == 'itemknn':
                    firstRow.append('ItemKNN' + str(result_id))

            data.append(firstRow)

            while startPoint <= endPoint:
                amountRecommendations = getItemRecommendations(startPoint, item_id, abtest_id, dataset_id)
                subdata = [str(startPoint)[0:10]] + amountRecommendations
                data.append(subdata)
                startPoint += stepsize

        # Compute recommendation correctness graph
        elif graph_type == 'Recommendation correctness':
            startPoint = datetime.strptime(begin_date, '%Y-%m-%d')
            endPoint = datetime.strptime(end_date, '%Y-%m-%d')
            stepsize = timedelta(days=1)

            # Determine the columns that we need to use in the index.html
            resultIDs = getResultIds(abtest_id, dataset_id)
            for result_id in resultIDs:
                algorithm = getAlgorithm(abtest_id, result_id)
                if algorithm.name == 'popularity':
                    columns.append('Popularity' + str(result_id) + ' recommendations')
                    columns.append('Popularity' + str(result_id) + ' correct recommendations')
                elif algorithm.name == 'recency':
                    columns.append('Recency' + str(result_id) + ' recommendations')
                    columns.append('Recency' + str(result_id) + ' correct recommendations')
                elif algorithm.name == 'itemknn':
                    columns.append('ItemKNN' + str(result_id) + ' recommendations')
                    columns.append('ItemKNN' + str(result_id) + ' correct recommendations')

            # Determine the data that we need for the graph
            while startPoint <= endPoint:
                temp_data = [str(startPoint)[0:10]]
                amountRecommendations = getItemRecommendations(startPoint, item_id, abtest_id, dataset_id)
                amountCorrectRecommendations = getRecommendationCorrectness(startPoint, item_id, abtest_id, dataset_id)
                for index in range(len(amountRecommendations)):
                    temp_data.append(amountRecommendations[index])
                    temp_data.append(amountCorrectRecommendations[index])
                    sum = amountRecommendations[index] + amountCorrectRecommendations[index]
                    if sum > maxYValue:
                        maxYValue = sum
                data.append(temp_data)
                startPoint += stepsize

            begin_counter = 2
            end_counter = 1
            for i in range(len(resultIDs) - 1):
                numbers.append([begin_counter, end_counter])
                begin_counter += 1
                numbers.append([begin_counter, end_counter])
                begin_counter += 1
                end_counter += 1

        d = {'graph_type': graph_type, 'data': data, 'numbers': numbers, 'maxYValue': maxYValue, 'name': 'item_graph',
             'columns': columns}

        print(request.form, d)

        return d


# ----------------- Item section page -----------------#
@app.route("/itemsection", methods=['POST', 'GET'])
def itemsection():
    abtest_id = request.args.get("abtest_id")
    dataset_id = request.args.get("dataset_id")
    item_id = request.args.get("item_id")
    attrAndVal = []
    image_url = ""

    # Request all the attributes of this item from the database
    item = getItem(item_id, dataset_id)
    for key in item.attributes:
        attrAndVal.append((key, item.attributes[key]))

    # Request the image_url from the database
    if 'image_url' in item.attributes:
        image_url = item.attributes['image_url']
    else:
        image_url = None

    return render_template('item.html', attr_val=attrAndVal, item_picture=image_url, data1=None,
                           name=None, title=None, abtest_id=abtest_id, dataset_id=dataset_id, item_id=item_id)


# ----------------- User_Login -----------------#

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
    if row is not None:  # check to see if user with the email already exists in the database
        flash('This username already exists.', category='error')
    else:
        user_obj = DataScientist(firstname=user_firstname, lastname=user_lastname, username=user_username,
                                 email=user_email, password=generate_password_hash(user_password, method='sha256'))
        print('Adding {}'.format(user_obj.to_dct()))
        addUser(user_obj)
        # login_user(user_obj, remember=True)

        flash('Account succesfully registered!', category='success')
        session['loggedin'] = True
        session['username'] = user_username
        return redirect(url_for('datasets'))

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
        if row is not None:  # als de username is gevonden
            user = row[0]
            cursor1 = connection.get_cursor()
            cursor1.execute("SELECT password FROM authentication WHERE username = %s", (user_username,))
            password = cursor1.fetchone()[0]
            if check_password_hash(password, user_password) or (user_username == 'admin' and password == user_password):
                flash('Logged in successfully!', category='success')
                # login_user(user, remember=True)
                session['loggedin'] = True
                session['username'] = user
                return redirect(url_for('datasets'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    session['jobsDataset'] = []

    return render_template('login.html', app_data=app_data)


@app.route("/logout", methods=['GET', 'POST'])
# @login_required
def logout():
    # logout_user()
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('abVisualistation', None)
    session.pop('userpage', None)
    # session.pop('_flashes', None)
    return redirect(url_for('login_user'))


# RUN DEV SERVER
if __name__ == "__main__":
    # os.system("kill `ps -A | grep rq | grep -v grep | awk '{ print $1 }'`")
    app.run(HOST, debug=False)
