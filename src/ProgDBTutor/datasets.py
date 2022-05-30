# import datetime
import json

from flask import request, flash
from werkzeug.utils import secure_filename
# import pandas as pd
import os
from user_data_acces import *

"""
Deze python file bevat alle functionaliteit die nodig is voor het behandelen van events/berekingen voor
de datasets page
"""
def handelRequests(app, session, request, taskQueue, type_list):
    """
    handle the possible requests for the datasets
    """
    # Remove and select dataset form
    if request.method == 'GET':

        rqst = request.args.get('datasetSelection')
        dlte = request.args.get('delete_btn')

        # Delete the dataset here
        if dlte is not None:
            taskQueue.enqueue(removeDataset, session['username'], int(rqst), job_timeout=600)

    # Add dataset form
    elif request.method == 'POST':
        return addDatasetHere(app, session, taskQueue, type_list)
    else:
        pass


def addDatasetHere(app, session, tq, type_list):
    """
    Function to add a dataset to the database, this will call the appropriate import functions
    """
    if session['username'] == 'admin':  # checken of de user de admin is
        dataset_id = importDataset(tq)
        importArticles(app, dataset_id, tq, type_list)
        importCustomers(app, dataset_id, tq, type_list)
        id3 = importPurchases(app, dataset_id, tq)
        tq.enqueue(createDatasetIdIndex, job_timeout=600)
        return {'id': dataset_id, id3: False}
    else:
        flash("You need admin privileges to upload a dataset", category='error')


def removeDataset(user, dataset_id):
    """
    remove the dataset from the database
    """
    if user == 'admin':  # checken of de user de admin is
        cursor = dbconnect.get_cursor()
        cursor.execute('DELETE FROM Dataset WHERE dataset_id = %s', (str(dataset_id)))
        dbconnect.commit()
    else:
        flash("You need admin privileges to delete a dataset", category='error')


def getDatasetInformation(dataset_id):
    """
    return all information of a dataset with a certain id
    """
    cursor = dbconnect.get_cursor()
    numberOfUser = getNumberOfUsers(cursor, dataset_id)
    numberOfArticles = getNumberOfArticles(cursor, dataset_id)
    numberOfInteractions = getNumberOfInteractions(cursor, dataset_id)
    numbers = list()

    activeUsers, interactionsPermonth = getActiveUsers(cursor, dataset_id)

    numbers.append({'users': numberOfUser, 'articles': numberOfArticles, 'interactions': numberOfInteractions, 'distributions': getPriceDistribution(cursor, dataset_id),
                    'activeUsers': activeUsers, 'interactionPerMonth' : interactionsPermonth})
    dictNumbers = json.dumps(numbers)
    return dictNumbers

def importDataset(tq):
    """
    import a dataset by generating a new ID
    """
    datasetname = request.form['dataset_name']
    datasetId = int(getMaxDatasetID()) + 1
    tq.enqueue(addDataset, datasetId, datasetname)
    return datasetId

def importArticles(app, dataset_id, tq, type_list, session):
    """
    import the articles from the csv file into the database
    """
    af_filename = ""
    try:
        af_filename = session['articlesFile']
    except:
        af = request.files['articles_file']
        uploaded_file = secure_filename(af.filename)
        af_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
        af.save(af_filename)
    # Add articles to database
    tq.enqueue(addArticles, af_filename, dataset_id, type_list, job_timeout=1200)


def importCustomers(app, dataset_id, tq, type_list, session):
    """
    import the curtomers from the csv file into the database
    """

    cf_filename = ""
    try:
        cf_filename = session['customersFile']
    except:
        cf = request.files['customers_file']
        uploaded_file = secure_filename(cf.filename)
        cf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
        cf.save(cf_filename)
    # Add customers to database
    tq.enqueue(addCustomers, cf_filename, dataset_id, type_list, job_timeout=1200)


def importPurchases(app, dataset_id, tq):
    """
    import the purchases from the csv file into the database
    """
    pf = request.files['purchases_file']
    uploaded_file = secure_filename(pf.filename)
    pf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    pf.save(pf_filename)
    # Add purchases to database
    job = tq.enqueue(addPurchases, pf_filename, dataset_id, job_timeout=3600)
    return job.id

def getCSVHeader(app, csv_filename, session):
    """
    Get the header for a certain csv file
    """
    df = request.files[csv_filename]
    uploaded_file = secure_filename(df.filename)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    df.save(filename)
    if csv_filename == "articles_file":
        session['articlesFile'] = filename
    elif csv_filename == "customers_file":
        session['customersFile'] = filename
    header = pd.read_csv(filename, header=0, nrows=0).columns.tolist()
    return header


def getNumberOfUsers(cursor, dataset_id):
    """
    Get the number of all users from the dataset
    """

    cursor.execute('SELECT attribute FROM customer where dataset_id = %s limit 1', str(dataset_id), )
    attr = cursor.fetchone()
    if not attr:
        return 0
    else:
        attr = attr[0]

    cursor.execute('SELECT count(*) FROM customer WHERE dataset_id = %s AND attribute = %s',
                   (str(dataset_id), str(attr)))
    row = cursor.fetchone()
    if not row:
        return 0
    return row[0] - 1

def getNumberOfArticles(cursor, dataset_id):
    """
    get all Items that the store has to offer
    """

    cursor.execute('SELECT attribute FROM Articles WHERE dataset_id = %s LIMIT 1', (str(dataset_id), ))
    attribute = cursor.fetchone()
    if not attribute:
        return 0
    else:
        attribute = attribute[0]

    cursor.execute('SELECT count(*) FROM Articles WHERE dataset_id = %s AND attribute = %s', (str(dataset_id), str(attribute)))
    row = cursor.fetchone()
    if not row:
        return 0
    articles = row[0]
    return articles


def getNumberOfInteractions(cursor, dataset_id):
    """
    Get number of interactions for the entire dataset
    """
    cursor.execute('SELECT count(*) FROM Interaction WHERE dataset_id = %s;', (str(dataset_id)))
    row = cursor.fetchone()
    if not row:
        return 0
    return row[0]

def getActiveUsers(cursor, dataset_id):
    """
    Get all active users for the entire dataset
    """
    cursor.execute('SELECT count(DISTINCT customer_id), t_dat, count(*) FROM interaction WHERE dataset_id = %s GROUP BY t_dat;', (str(dataset_id)))
    rows = cursor.fetchall()
    users = list()
    purchases = list()
    curMonth = ""
    prevMonth = ""
    curCount = 0
    curPurch = 0

    for row in rows:
        date = str(row[1])[0:10]
        curCount = int(row[0])
        curPurch = int(row[2])

        users.append({"date": date, "count": curCount})
        purchases.append({"date": date, "count": curPurch})


    return users, purchases

def getPriceDistribution(cursor, dataset_id):
    """
    Get the price distribution for the entire dataset
    """

    cursor.execute('SELECT min(price) as min, max(price) as max, (max(price) - min(price))/20 as interval FROM Interaction WHERE dataset_id = %s', (str(dataset_id)))
    row = cursor.fetchone()
    min, max, interval = row
    if not min and not max and not interval:
        return list()
    cursor.execute('SELECT count(*), price FROM Interaction WHERE dataset_id = %s GROUP BY price', (str(dataset_id)))
    rows = cursor.fetchall()
    distr = list()
    for i in range(1, 21):
        begin = min + interval * (i - 1)
        end = min + interval * i
        distr.append({"begin": begin, "end": end , "count":0})

    for row in rows:
        for i in range(1, 21):
            begin = min + interval * (i - 1)
            end = min + interval * i
            if begin <= row[1] and row[1] <= end:
                distr[i-1]["count"] += int(row[0])
                break

    return distr






