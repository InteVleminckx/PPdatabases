import datetime
import json

from flask import request, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os
from user_data_acces import *

"""
Deze python file bevat alle functionaliteit die nodig is voor het behandelen van events/berekingen voor
de datasets page
"""


def handelRequests(app, session, request, taskQueue, type_list):
    # Remove and select dataset form
    if request.method == 'GET':

        rqst = request.args.get('datasetSelection')
        dlte = request.args.get('delete_btn')

        # Delete hier de dataset
        if dlte is not None:
            #removeDataset(session, rqst)
            taskQueue.enqueue(removeDataset, session['username'], rqst, job_timeout=600)

        # vernander alle waarder en grafiek op de pagina
        else:
            # return getDatasetInformation(user_data_access, dataset_id)
            pass

    # Add dataset form
    elif request.method == 'POST':
        #taskQueue.enqueue(addDatasetHere, app, session)
        addDatasetHere(app, session, taskQueue, type_list)
    else:
        pass


def addDatasetHere(app, session, tq, type_list):
    if session['username'] == 'admin':  # checken of de user de admin is
        dataset_id = importDataset(tq)
        importArticles(app, dataset_id, tq, type_list)
        importCustomers(app, dataset_id, tq, type_list)
        importPurchases(app, dataset_id, tq)
        tq.enqueue(createDatasetIdIndex)
    else:
        flash("You need admin privileges to upload a dataset", category='error')


def removeDataset(user, dataset_id):
    if user == 'admin':  # checken of de user de admin is
        cursor = dbconnect.get_cursor()
        cursor.execute('DELETE FROM Dataset WHERE dataset_id = %s', (str(dataset_id)))
        dbconnect.commit()
    else:
        flash("You need admin privileges to delete a dataset", category='error')


def getDatasetInformation(dataset_id):
    cursor = dbconnect.get_cursor()
    numberOfUser = getNumberOfUsers(cursor, dataset_id)
    numberOfArticles = getNumberOfArticles(cursor, dataset_id)
    numberOfInteractions = getNumberOfInteractions(cursor, dataset_id)
    numbers = list()

    numbers.append({'users': numberOfUser, 'articles': numberOfArticles, 'interactions': numberOfInteractions, 'distributions': getPriceDistribution(cursor, dataset_id),
                    'activeUsers': getActiveUsers(cursor, dataset_id)})
    dictNumbers = json.dumps(numbers)
    return dictNumbers

def importDataset(tq):
    datasetname = request.form['ds_name']
    datasetId = int(getMaxDatasetID()) + 1
    #addDataset(datasetId, datasetname)
    tq.enqueue(addDataset, datasetId, datasetname)
    return datasetId


def getCSVHeader(app, csv_filename):
    df = request.files[csv_filename]
    uploaded_file = secure_filename(df.filename)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    df.save(filename)
    header = pd.read_csv(filename, header=0, nrows=0).columns.tolist()
    # header_dict = {'header_attr': header}
    return header

def importArticles(app, dataset_id, tq, type_list): #\

    af = request.files['articles_file']
    uploaded_file = secure_filename(af.filename)
    af_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    af.save(af_filename)
    # Add articles to database
    #addArticles(data_articles, dataset_id)
    tq.enqueue(addArticles, af_filename, dataset_id, type_list, job_timeout=1200)


def importCustomers(app, dataset_id, tq, type_list):
    cf = request.files['customers_file']
    uploaded_file = secure_filename(cf.filename)
    cf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    cf.save(cf_filename)
    # Add customers to database
    #addCustomers(data_customers, columns_customers, dataset_id)
    tq.enqueue(addCustomers, cf_filename, dataset_id, type_list, job_timeout=1200)


def importPurchases(app, dataset_id, tq):
    pf = request.files['purchases_file']
    uploaded_file = secure_filename(pf.filename)
    pf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    pf.save(pf_filename)
    # Add purchases to database
    #addPurchases(data_purchases, dataset_id)
    tq.enqueue(addPurchases, pf_filename, dataset_id, job_timeout=3600)


def getCSVHeader(app, csv_filename):
    df = request.files[csv_filename]
    uploaded_file = secure_filename(df.filename)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    df.save(filename)
    header = pd.read_csv(filename, header=0, nrows=0).columns.tolist()
    return header


def getNumberOfUsers(cursor, dataset_id):

    cursor.execute('SELECT attribute FROM customer where dataset_id = %s limit 1', str(dataset_id))
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

    cursor.execute('SELECT attribute FROM Articles WHERE dataset_id = %s LIMIT 1', (str(dataset_id)))
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
    cursor.execute('SELECT count(*) FROM Interaction WHERE dataset_id = %s;', (str(dataset_id)))
    row = cursor.fetchone()
    if not row:
        return 0
    return row[0]

def getActiveUsers(cursor, dataset_id):
    cursor.execute('SELECT count(DISTINCT customer_id), t_dat FROM interaction WHERE dataset_id = %s GROUP BY t_dat;', (str(dataset_id)))
    rows = cursor.fetchall()
    users = list()
    curMonth = ""
    prevMonth = ""
    curCount = 0
    for row in rows:
        date = str(row[1])[0:7]
        if curMonth == "":
            curMonth = date

        if curMonth == date:
            curCount += int(row[0])
            prevMonth = curMonth

        elif curMonth != date:
            users.append({"date": prevMonth, "count": curCount})
            curMonth = date
            curCount = 0

    return users

def getPriceDistribution(cursor, dataset_id):

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




    # return list()
    # cursor.execute('SELECT min(price) as min, max(price) as max, (max(price) - min(price))/10 as interval FROM Interaction WHERE dataset_id = %s', (str(dataset_id)))
    # row = cursor.fetchone()
    #
    # if not row:
    #     return None
    #
    # min, max, interval = row
    #
    # distributions = list()
    #
    # for i in range(1,11):
    #     begin = min + interval*(i-1)
    #     end = min + interval*i
    #     if i == 1:
    #         cursor.execute('SELECT count(*), (%s,%s) AS range FROM Interaction WHERE price >= %s AND price <= %s', (str(begin),str(end),str(begin),str(end)))
    #     else:
    #         cursor.execute('SELECT count(*), (%s,%s) AS range FROM Interaction WHERE price > %s AND price <= %s', (str(begin),str(end),str(begin),str(end)))
    #
    #     row = cursor.fetchone()
    #     if row:
    #         distributions.append({'range':row[1], 'count':row[0]})
    #
    #
    # return distributions

