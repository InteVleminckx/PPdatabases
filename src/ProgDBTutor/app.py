# TUTORIAL Len Feremans, Sandy Moens and Joey De Pauw
# see tutor https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
#import json
#import time

from flask import Flask, request, session, jsonify, flash, redirect, url_for
from flask.templating import render_template
#from flask_login import login_user, login_required, logout_user, current_user, UserMixin
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import scoped_session, sessionmaker
import redis
from rq import Queue

#from user_data_acces import *  # , UserDataAcces

from werkzeug.security import generate_password_hash, check_password_hash
#from werkzeug.utils import secure_filename

#import pandas as pd
#import csv
#import os
import a_b_tests as abtest
#from datetime import datetime, timedelta

#from config import config_data
#from db_connection import DBConnection


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

# For threading
rds = redis.Redis()
datasetQueue = Queue('queue1', connection=rds)  # queue for dataset processes
abTestQueue = Queue('queue2', connection=rds)  # queue for abTest processes

# INITIALIZE SINGLETON SERVICES

file_attr_types = ["string", "float", "int", "image_url"]

DEBUG = True
HOST = "127.0.0.1" if DEBUG else "0.0.0.0"


# ----------------- VIEW -----------------#
@app.route("/")
@app.route("/home")
def main():
    """
    Main function for home page.
    :return:
    """

    l = session.get('loggedin', False)

    if l:
        return render_template('home.html', app_data=app_data, isLoggedin=session['loggedin'])
    else:
        return render_template('home.html', app_data=app_data)

# ----------------- A/B-test page -----------------#

@app.route("/services/addalgorithm", methods=['GET', 'POST'])
def addalgorithm():

    """
    Adds an algorithm to the list of algorithms (for the A/B-test page).
    :return: (dict)
    """
    if request.method == 'POST':

        dataDict = request.get_json()
        form_data = dataDict['form_data']
        algo_id = dataDict['algo_id']
        algo_list = dataDict['algo_list']
        algo_dict = dataDict['algo_dict']

        algo = form_data['algoSelection']
        changed = True # False when algorithm should not be added.
        if algo == "popularity":
            windowsize = form_data['input_windowsize_p']
            retraininterval = form_data['input_retraininterval_p']
            if windowsize == "" or retraininterval == "":
                flash('Algorithm parameters not fully filled in.', category='error')
                changed = False
            elif int(windowsize) <= 0 or int(retraininterval) <= 0:
                flash('Bad algorithm parameter(s). Make sure they are positive integers.', category='error')
                changed = False
            else:
                algo_list.append([algo_id, "popularity", "windowsize", windowsize])
                algo_list.append([algo_id, "popularity", "retraininterval", retraininterval])
                algo_dict[str(algo_id)] = "popularity"
                algo_id += 1
        elif algo == "recency":
            retraininterval = form_data['input_retraininterval_r']
            if retraininterval == "":
                flash('Algorithm parameters not fully filled in.', category='error')
                changed = False
            elif int(retraininterval) <= 0:
                flash('Bad algorithm parameter(s). Make sure they are positive integers.', category='error')
                changed = False
            else:
                algo_list.append([algo_id, "recency", "retraininterval", retraininterval])
                algo_dict[str(algo_id)] = "recency"
                algo_id += 1
        elif algo == "itemknn":
            k = form_data['input_k']
            window = form_data['input_windowsize_i']
            normalize = form_data['input_normalize']
            retraininterval = form_data['input_retraininterval_i']
            if k == "" or window == "" or normalize == "" or retraininterval == "":
                flash('Algorithm parameters not fully filled in.', category='error')
                changed = False
            elif int(k) <= 0 or int(window) <= 0 or int(retraininterval) <= 0 or int(normalize) < 0:
                flash('Bad algorithm parameter(s). Make sure they are positive integers (the normalize parameter is allowed to be 0).', category='error')
                changed = False
            else:
                algo_list.append([algo_id, "itemknn", "k", k])
                algo_list.append([algo_id, "itemknn", "window", window])
                algo_list.append([algo_id, "itemknn", "normalize", normalize])
                algo_list.append([algo_id, "itemknn", "retraininterval", retraininterval])
                algo_dict[str(algo_id)] = "itemknn"
                algo_id += 1

        data_dict = {'algo_id': algo_id, 'algo_list': algo_list, 'algo_dict': algo_dict, 'changed': changed}
        return data_dict

@app.route("/get_flashes", methods=['GET', 'POST'])
def get_flashes():
    """
    Returns the template that contains html code for the flash messages.
    :return:
    """

    return render_template('_flashes.html')

@app.route("/services", methods=['GET', 'POST'])
def services():

    """
    Main function that renders the A/B-test page. Submitted A/B-tests are handled here too.
    :return:
    """

    if 'loggedin' in session:

        if request.method == 'POST':

            dataDict = request.get_json()

            form_data = dataDict['form_data']
            algo_id = dataDict['algo_id']
            algo_list = dataDict['algo_list']
            algo_dict = dataDict['algo_dict']

            # Params for foreign keys
            creator = session['username']

            # General parameters for ABtest
            start = form_data['input_startpoint']
            end = form_data['input_endpoint']
            stepsize = form_data['input_stepsize']
            topk = form_data['input_topk']
            dataset = 0
            if 'datasetSelection' in form_data:
                dataset = form_data['datasetSelection']

            ABTestID = getMaxABTestID() + 1

            # Make dictionary to store results from abtest_job
            algo_times = {'abtest_id': ABTestID, 'times': {}}

            dataset_id = ""
            for char in dataset:
                if char.isdigit():
                    dataset_id += char

            current_id = 1
            while len(algo_dict) != 0:
                for i in range(1, algo_id + 1):
                    if str(i) in algo_dict:
                        # Add entry for ABtest table
                        abTestQueue.enqueue(addAB_Test, ABTestID, current_id, start, end, stepsize, topk, creator, dataset_id)

                        # Add entries for Algorithm table
                        for j in range(len(algo_list)):
                            if algo_list[j][0] == i:
                                abTestQueue.enqueue(addAlgorithm, ABTestID, current_id, algo_list[j][1], algo_list[j][2],
                                                    algo_list[j][3])

                        del algo_dict[str(i)]
                        algo_times['times'][current_id] = 0
                        current_id += 1

            # Remove algorithms from list and dicts
            algo_list = []
            algo_dict = {}
            connection.commit()

            # Call function to start a/b tests
            abtest_job = abTestQueue.enqueue(abtest.startAB, args=(ABTestID, dataset_id), job_timeout=3600, meta=algo_times)
            session["algo_times"] = abtest_job.id

            jobABvisualisations = abTestQueue.enqueue(getInfoVisualisationPage, ABTestID, dataset_id, job_timeout=600)

            recos = abTestQueue.enqueue(getTopkMostRecommendItemsPerAlgo, "", "", dataset_id, topk, ABTestID)
            totPurch = abTestQueue.enqueue(getTopkMostPurchasedItems, "", "", dataset_id, topk, ABTestID)
            totRev = abTestQueue.enqueue(getTotaleRevenue, "", "", dataset_id, ABTestID)
            listUsers = abTestQueue.enqueue(getListOfActiveUsers, "", "", dataset_id, ABTestID)

            session["abVisualistation"] = [jobABvisualisations.id, recos.id, totPurch.id, totRev.id, listUsers.id]
            data_dict = {'algo_id': algo_id, 'algo_list': algo_list, 'algo_dict': algo_dict}

            return data_dict

        elif request.method == 'GET':
            pass

        genParDict = {}
        selected_ds_id = request.args.get('selected_ds_id', None)
        if selected_ds_id is not None:
            genParDict['selected_ds_id'] = selected_ds_id

        dataset_names = getDatasets()
        return render_template('services.html', app_data=app_data, genParDict=json.dumps(genParDict), names=dataset_names)

    return redirect(url_for('login_user'))


# ----------------- Dataset page -----------------#

@app.route("/datasets/<ds_id>", methods=['GET', 'POST'])
def getData(ds_id):

    """
    Gets all the information for the dataset with given dataset id.
    :return: (list(dict)) [{'users': numberOfUser, 'articles': numberOfArticles, 'interactions': numberOfInteractions, 'distributions': getPriceDistribution(cursor, dataset_id),
                    'activeUsers': activeUsers, 'interactionPerMonth' : interactionsPermonth}]
    """

    if request.method == 'GET':
        print("/datasets/<ds_id>")
        return getDatasetInformation(ds_id)

@app.route("/datasets", methods=['GET', 'POST'])
def datasets():
    """
    Main function that renders the dataset page. Used to setup the type list for the uploaded files.
    :return:
    """
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

        session['jobsDataset'] = []
        jobs = handelRequests(app, session, request, datasetQueue, type_list)
        if 'jobsDataset' not in session:
            session['jobsDataset'] = []
        if jobs:
            c = session['jobsDataset']
            c.append(jobs)
            session['jobsDataset'] = c

        dataset_names = getDatasets()

        if jobs:
            if jobs['id'] == 'delete':
                deleted_id = jobs['deleted_id']
                for i in range(len(dataset_names)):
                    if dataset_names[i][0] == deleted_id:
                        del dataset_names[i]
                        break

        # Delete hier de dataset
        return render_template('datasets.html', app_data=app_data, names=dataset_names,
                                   attr_types=json.dumps(file_attr_types))

    return redirect(url_for('login_user'))

@app.route("/datasets/update/<ds_id>")
def datasetUpdate(ds_id):
    """
    This function returns done if the dataset with the given id is in the dataset
    :return: string
    """
    if ds_id == "-1":   #if no id is selected
        return 'no refresh'
    if 'jobsDataset' in session:
        finished = True
        dsIdinQueue = False
        if len(session['jobsDataset']) == 0:    # if the queue is empty
            return 'no refresh'
        for i in range(len(session['jobsDataset'])):
            if ds_id == str(session['jobsDataset'][i]['id']):   #If the given id is present between the recent processes
                dsIdinQueue = True
            for key, value in session['jobsDataset'][i].items():    #Loop over the job id's
                if key == 'id' or value == True:
                    continue
                j = datasetQueue.fetch_job(key)
                if j is not None:
                    if str(j.get_status()) == "finished":   #if the job has been finisched
                        l = session['jobsDataset'][i]
                        l[key] = True
                        session['jobsDataset'][i] = l
                else:   #if the job result is not in the queue anymore, its finished
                    l = session['jobsDataset'][i]
                    l[key] = True
                    session['jobsDataset'][i] = l

            for key, value in session['jobsDataset'][i].items():    #checking if reading in a dataset is finished
                if key != 'id' and value == False:
                    finished = False

            #if dataset with given id is completly read in
            if finished and str(session['jobsDataset'][i]['id']) == ds_id:
                l = session['jobsDataset']
                l.remove(session['jobsDataset'][i])
                session['jobsDataset'] = l
                return 'done'
            elif finished:  #if reading in a dataset has finisched but its not selected, delete from list
                l = session['jobsDataset']
                l.remove(session['jobsDataset'][i])
                session['jobsDataset'] = l

        if not dsIdinQueue: #If the dataset with the given id is not in the list, so it already finished
            return 'done'

    return 'notDone'

@app.route("/fileupload", methods=['GET', 'POST'])
def fileupload():
    """
    Returns the headers of each of the uploaded files.
    :return: (dict)
    """

    if request.method == 'POST':
        headerDict = {}
        if request.files.get('articles_file').filename != '':
            headerList = getCSVHeader(app, 'articles_file', session)
            headerDict['articles_attr'] = headerList
            headerDict['changed'] = 'articles_attr'

        if request.files.get('customers_file').filename != '':
            headerList = getCSVHeader(app, 'customers_file', session)
            headerDict['customers_attr'] = headerList
            headerDict['changed'] = 'customers_attr'
        return headerDict


# ----------------- A/B-test Visualization page -----------------#

@app.route("/visualizations")
def visualizations():

    """
    Main function that renders the vizualisations page.
    :return:
    """
    if len(request.args) > 0:
        ABTestID = request.args["abtest_id"]
        dataset_id = request.args["dataset_id"]
        abtest = getAB_Test(ABTestID)
        topk = abtest.topk

        jobABvisualisations = abTestQueue.enqueue(getInfoVisualisationPage, ABTestID, dataset_id, job_timeout=600)

        recos = abTestQueue.enqueue(getTopkMostRecommendItemsPerAlgo, "", "", dataset_id, topk, ABTestID)
        totPurch = abTestQueue.enqueue(getTopkMostPurchasedItems, "", "", dataset_id, topk, ABTestID)
        totRev = abTestQueue.enqueue(getTotaleRevenue, "", "", dataset_id, ABTestID)
        listUsers = abTestQueue.enqueue(getListOfActiveUsers, "", "", dataset_id, ABTestID)

        session["abVisualistation"] = [jobABvisualisations.id, recos.id, totPurch.id, totRev.id, listUsers.id]
    return render_template('visualizations.html', app_data=app_data)

@app.route("/visualizations/request", methods=["GET", "POST"])
def visualizationsRequest():
    if request.method == "POST":
        data = request.get_json()
        dataset_id = data["dataset_id"]
        ABTestID = data["abtest_id"]
        start = data["startdate"]
        end = data["enddate"]
        abtest = getAB_Test(ABTestID)
        topk = abtest.topk

        recos = abTestQueue.enqueue(getTopkMostRecommendItemsPerAlgo, start, end, dataset_id, topk, ABTestID)
        totPurch = abTestQueue.enqueue(getTopkMostPurchasedItems, start, end, dataset_id, topk, ABTestID)
        totRev = abTestQueue.enqueue(getTotaleRevenue, start, end, dataset_id, ABTestID)
        listUsers = abTestQueue.enqueue(getListOfActiveUsers, start, end, dataset_id, ABTestID)

        session["abVisualistationRequest"] = [recos.id, totPurch.id, totRev.id, listUsers.id]

    return {}

@app.route("/visualizations/updateRequest")
def visualizationsUpdateRequest():
    if "abVisualistationRequest" in session:
        job = session["abVisualistationRequest"]
        job_ = abTestQueue.fetch_job(job[-1])
        if job_ is not None:
            if str(job_.get_status()) == "finished":
                topkReco = abTestQueue.fetch_job(job[0]).result
                topkPurchases = abTestQueue.fetch_job(job[1]).result
                totRev = abTestQueue.fetch_job(job[2]).result
                listUsers, listUsersSort, totUsers = abTestQueue.fetch_job(job[3]).result

                return {"topkRecommendations": topkReco, "topkPurchases": topkPurchases,
                        "totaleRevenue": totRev, "totaleUsers": totUsers, "listUsers": listUsers, "sortingOrder": listUsersSort}
    return {}


@app.route("/visualizations/update")
def visualizationsUpdate():
    """
    Route used to update the visualization page
    :return:
    """
    if "abVisualistation" in session:
        job = session["abVisualistation"]
        job_ = abTestQueue.fetch_job(job[-1])
        if job_ is not None:
            if str(job_.get_status()) == "finished":
                visualization = abTestQueue.fetch_job(job[0]).result
                topkReco = abTestQueue.fetch_job(job[1]).result
                topkPurchases = abTestQueue.fetch_job(job[2]).result
                totRev = abTestQueue.fetch_job(job[3]).result
                listUsers, orderedUsers,totUsers = abTestQueue.fetch_job(job[4]).result

                return {"visualization": visualization, "topkRecommendations": topkReco, "topkPurchases": topkPurchases,
                        "totaleRevenue": totRev, "totaleUsers": totUsers, "listUsers": listUsers, "sortingOrder": orderedUsers}

    return {}

@app.route("/visualizations/exextimes")
def visualizationsTimesRequest():

    if "algo_times" in session:
        job = session["algo_times"]
        fetchJob = abTestQueue.fetch_job(job)
        fetchJob.refresh()
        algorithmsTime = {"times": [], "finished": False}
        abtest_id = fetchJob.meta["abtest_id"]
        for key, value in fetchJob.meta["times"].items():
            algoname = getAlgorithm(abtest_id, key)
            algorithmsTime["times"].append([str(algoname.name), str(round(float(value), 6))])

        if str(fetchJob.get_status()) == "finished":
            algorithmsTime["finished"] = True

        return algorithmsTime

    return {}

# ----------------- A/B-test list -----------------#

@app.route("/testlist")
def testlist():

    """
    Main function that renders the testlist page.
    :return:
    """

    creator = session['username']
    testList = []
    cursor = connection.get_cursor()
    cursor.execute("SELECT distinct(a.abtest_id), a.dataset_id, d.dataset_name, a.start_point, a.end_point, "
                   "a.stepsize, a.topk FROM ABTest a, Dataset d WHERE a.creator = %s AND "
                   "a.dataset_id = d.dataset_id", (creator,))
    for row in cursor:
        d = {'abtest_id': row[0], 'dataset_id': row[1], 'dataset_name': row[2], 'startingpoint': str(row[3])[:10],
             'endpoint': str(row[4])[:10], 'stepsize': row[5], 'topk': row[6], 'algorithms': None}
        testList.append(d)
    for i in range(len(testList)):
        algos = {}

        cursor.execute("SELECT distinct(a.param_name), a.algorithm_id, a.name, a.value FROM Algorithm a, ABTest ab WHERE "
                       "a.abtest_id = %s AND a.abtest_id = ab.abtest_id AND ab.creator = %s", (testList[i]['abtest_id'], creator))
        for row in cursor:
            if row[1] in algos.keys():
                algos[row[1]][1][row[0]] = row[3]
            else:
                algos[row[1]] = [row[2], {row[0]: row[3]}]

        testList[i]['algorithms'] = algos

    return render_template('testlist.html', app_data=app_data, testList=testList)


@app.route("/abTestRemove", methods=['GET', 'POST'])
def abTestRemove():

    """
    Removes an A/B-test (from the database).
    :return:
    """

    data = request.get_json()
    abTest_id = data['abtest_id']
    cursor = connection.get_cursor()
    cursor.execute("DELETE FROM ABTest WHERE abtest_id = %s", (str(abTest_id),))
    connection.commit()
    return {}


# ----------------- User section page -----------------#

@app.route("/usersection/update")
def usersectionUpdate():
    """
    Route used to update the contents of the user page
    :return:
    """
    if "userpage" in session:
        userpage = session["userpage"]
        job = abTestQueue.fetch_job(userpage)
        if job is not None:
            if str(job.get_status()) == "finished":
                recommendations, history, interval, graph, topkListprint, dates = job.result
                return {"recommendations": recommendations, "history": history, "interval": interval, "graph": graph,
                        "topkListprint": topkListprint, "dates": dates}
    return {}


@app.route("/usersection")
def usersection():

    """
    Main function that renders the user page.
    :return:
    """

    dataset_id = request.args.get("dataset_id")
    customer_id = request.args.get("customer_id")
    abtest_id = request.args.get("abtest_id")
    information = abTestQueue.enqueue(getUserInformation, abtest_id, dataset_id, customer_id)

    session["userpage"] = information.id
    datasetname = getDatasetname(dataset_id)
    return render_template('user.html', username=customer_id, datasetname=datasetname, abtest_id=abtest_id, dataset_id=dataset_id)


@app.route("/itemsection_graph", methods=['POST', 'GET'])
def itemsection_graph():
    """
    Route that is used to compute all the values needed for the graphs on the item page
    :return:
    """
    if request.method == 'POST':
        dataset_id = request.form.get('dataset_id', None)
        abtest_id = request.form.get("abtest_id", None)
        item_id = request.form.get("item_id", None)

        numbers = []
        maxYValue = 0
        columns = []

        graph_type = request.form.get('graph_select', None)
        begin_date = request.form.get('input_startpoint', None)
        end_date = request.form.get('input_endpoint', None)
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
            algorithm_ids = getAlgorithmIds(abtest_id, dataset_id)
            for algorithm_id in algorithm_ids:
                algorithm = getAlgorithm(abtest_id, algorithm_id)
                if algorithm.name == 'popularity':
                    firstRow.append('Popularity' + str(algorithm_id))
                elif algorithm.name == 'recency':
                    firstRow.append('Recency' + str(algorithm_id))
                elif algorithm.name == 'itemknn':
                    firstRow.append('ItemKNN' + str(algorithm_id))

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
            algorithm_ids = getAlgorithmIds(abtest_id, dataset_id)
            for algorithm_id in algorithm_ids:
                algorithm = getAlgorithm(abtest_id, algorithm_id)
                if algorithm.name == 'popularity':
                    columns.append('Popularity' + str(algorithm_id) + ' recommendations')
                    columns.append('Popularity' + str(algorithm_id) + ' correct recommendations')
                elif algorithm.name == 'recency':
                    columns.append('Recency' + str(algorithm_id) + ' recommendations')
                    columns.append('Recency' + str(algorithm_id) + ' correct recommendations')
                elif algorithm.name == 'itemknn':
                    columns.append('ItemKNN' + str(algorithm_id) + ' recommendations')
                    columns.append('ItemKNN' + str(algorithm_id) + ' correct recommendations')

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
            for i in range(len(algorithm_ids) - 1):
                numbers.append([begin_counter, end_counter])
                begin_counter += 1
                numbers.append([begin_counter, end_counter])
                begin_counter += 1
                end_counter += 1

        d = {'graph_type': graph_type, 'data': data, 'numbers': numbers, 'maxYValue': maxYValue, 'name': 'item_graph',
             'columns': columns}

        return d


# ----------------- Item section page -----------------#
@app.route("/itemsection", methods=['POST', 'GET'])
def itemsection():

    """
    Main function that renders the item page.
    :return:
    """

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

    """
    Registers a user on the website and adds him to the database.
    :return: Redirect to datasets page if successful, stays on login page if unsuccessful.
    """

    user_firstname = request.form.get('firstname')
    user_lastname = request.form.get('lastname')
    user_username = request.form.get('username')
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    cursor = connection.get_cursor()
    cursor.execute("SELECT username FROM datascientist WHERE username = %s", (user_username,))
    row = cursor.fetchone()

    # some basic checks (if they trigger, they 'flash' a message on the page (see the login.html doc))
    if row is not None:  # check to see if user with the email already exists in the database
        flash('This username already exists.', category='error')
    else:
        user_obj = DataScientist(firstname=user_firstname, lastname=user_lastname, username=user_username,
                                 email=user_email, password=generate_password_hash(user_password, method='sha256'))
        print('Adding {}'.format(user_obj.to_dct()))
        addUser(user_obj)

        flash('Account successfully registered!', category='success')
        session['loggedin'] = True
        session['username'] = user_username
        return redirect(url_for('datasets'))

    return render_template('login.html', app_data=app_data)


@app.route("/login", methods=['GET', 'POST'])
def login_user():

    """
    Logs a user in on the website.
    :return: Redirect to datasets page if successful, stays on login page if unsuccessful.
    """

    if request.method == 'POST':

        user_username = request.form.get('username')
        user_password = request.form.get('password')

        cursor = connection.get_cursor()
        cursor.execute("SELECT username FROM datascientist WHERE username = %s", (user_username,))
        row = cursor.fetchone()
        if row is not None:  # als de username is gevonden
            user = row[0]
            cursor1 = connection.get_cursor()
            cursor1.execute("SELECT password FROM authentication WHERE username = %s", (user_username,))
            password = cursor1.fetchone()[0]
            if check_password_hash(password, user_password) or (user_username == 'admin' and password == user_password):
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
def logout():

    """
    Logs the user out on the website.
    :return:
    """
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('abVisualistation', None)
    session.pop('userpage', None)
    return redirect(url_for('login_user'))


# RUN DEV SERVER
if __name__ == "__main__":
    app.run(HOST, debug=False)
