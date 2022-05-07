import json

from flask import request, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os

"""
Deze python file bevat alle functionaliteit die nodig is voor het behandelen van events/berekingen voor
de datasets page
"""


def handelRequests(app, user_data_access, session, request):
    # Remove en select dataset form
    if request.method == 'GET':

        rqst = request.args.get('datasetSelection')
        dlte = request.args.get('delete_btn')

        # Delete hier de dataset
        if dlte is not None:
            removeDataset(user_data_access, session)

        # vernander alle waarder en grafiek op de pagina
        else:
            # return getDatasetInformation(user_data_access, dataset_id)
            pass

    # Add dataset form
    elif request.method == 'POST':
        addDataset(app, user_data_access, session)

    else:
        pass


def addDataset(app, user_data_access, session):
    if session['username'] == 'admin':  # checken of de user de admin is
        dataset_id = importDataset(user_data_access)
        importArticles(app, user_data_access, dataset_id)
        importCustomers(app, user_data_access, dataset_id)
        importPurchases(app, user_data_access, dataset_id)
    else:
        flash("You need admin privileges to upload a dataset", category='error')


def removeDataset(user_data_access, session):
    if session['username'] == 'admin':  # checken of de user de admin is
        pass
    else:
        flash("You need admin privileges to delete a dataset", category='error')


def getDatasetInformation(user_data_access, dataset_id):
    cursor = user_data_access.dbconnect.get_cursor()
    numberOfUser = getNumberOfUsers(cursor, dataset_id)
    numberOfArticles = getNumberOfArticles(cursor, dataset_id)
    numberOfInteractions = getNumberOfInteractions(cursor, dataset_id)
    numbers = list()
    numbers.append({'users': numberOfUser, 'articles': numberOfArticles, 'interactions': numberOfInteractions})

    dictNumbers = json.dumps(numbers)
    return dictNumbers

def importDataset(user_data_access):
    datasetname = request.form['ds_name']
    datasetId = int(user_data_access.getMaxDatasetID()) + 1
    user_data_access.addDataset(datasetId, datasetname)
    return datasetId


def importArticles(app, user_data_access, dataset_id):
    af = request.files['articles_file']
    uploaded_file = secure_filename(af.filename)
    af_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    af.save(af_filename)
    data_articles = pd.read_csv(af_filename)
    # Add articles to database
    user_data_access.addArticles(data_articles, dataset_id)


def importCustomers(app, user_data_access, dataset_id):
    cf = request.files['customers_file']
    uploaded_file = secure_filename(cf.filename)
    cf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    cf.save(cf_filename)
    data_customers = pd.read_csv(cf_filename)
    columns_customers = list(data_customers.columns.values)
    # Add customers to database
    user_data_access.addCustomers(data_customers, columns_customers, dataset_id)


def importPurchases(app, user_data_access, dataset_id):
    pf = request.files['purchases_file']
    uploaded_file = secure_filename(pf.filename)
    pf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    pf.save(pf_filename)
    data_purchases = pd.read_csv(pf_filename)
    # Add purchases to database
    user_data_access.addPurchases(data_purchases, dataset_id)


def getNumberOfUsers(cursor, dataset_id):
    # We doen dit op deze manier omdat dit sneller is als distinct, want distinct sorteerd eerst heel de tabel
    cursor.execute('CREATE OR REPLACE VIEW customers AS SELECT customer_number FROM Customer WHERE dataset_id = %s GROUP BY customer_number;', (str(dataset_id)))
    cursor.execute('SELECT count(*) FROM customers;')
    row = cursor.fetchone()
    if not row:
        cursor.execute('DROP VIEW customers;')
        return 0
    users = row[0] - 1
    cursor.execute('DROP VIEW customers;')
    return users


def getNumberOfArticles(cursor, dataset_id):
    # We doen dit op deze manier omdat dit sneller is als distinct, want distinct sorteerd eerst heel de tabel
    cursor.execute('CREATE OR REPLACE VIEW articlesC AS SELECT item_number FROM Articles WHERE dataset_id = %s GROUP BY item_number;', (str(dataset_id)))
    cursor.execute('SELECT count(*) FROM articlesC;')
    row = cursor.fetchone()
    if not row:
        cursor.execute('DROP VIEW articlesC;')
        return 0
    articles = row[0]
    cursor.execute('DROP VIEW articlesC;')
    return articles

def getNumberOfInteractions(cursor, dataset_id):
    cursor.execute('SELECT count(*) FROM Interaction WHERE dataset_id = %s;', (str(dataset_id)))
    row = cursor.fetchone()
    if not row:
        return 0
    return row[0]
