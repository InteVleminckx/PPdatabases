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
            # getDatasetInformation(user_data_access, dataset_id)
            pass

    # Add dataset form
    elif request.method == 'POST':
        addDataset(app, user_data_access, session)

    else:
        pass


def addDataset(app, user_data_access, session):
    if session['username'] == 'admin':  # checken of de user de admin is
        importArticles(app, user_data_access)
        importCustomers(app, user_data_access)
        importPurchases(app, user_data_access)
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


def importArticles(app, user_data_access):
    af = request.files['articles_file']
    uploaded_file = secure_filename(af.filename)
    af_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    af.save(af_filename)
    data_articles = pd.read_csv(af_filename)
    columns_articles = list(data_articles.columns.values)
    # Add articles to database
    user_data_access.addArticles(data_articles, columns_articles)


def importCustomers(app, user_data_access):
    cf = request.files['customers_file']
    uploaded_file = secure_filename(cf.filename)
    cf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    cf.save(cf_filename)
    data_customers = pd.read_csv(cf_filename)
    columns_customers = list(data_customers.columns.values)
    # Add customers to database
    user_data_access.addCustomers(data_customers, columns_customers)


def importPurchases(app, user_data_access):
    pf = request.files['purchases_file']
    uploaded_file = secure_filename(pf.filename)
    pf_filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
    pf.save(pf_filename)
    data_purchases = pd.read_csv(pf_filename)
    # Add purchases to database
    user_data_access.addPurchases(data_purchases)


def getNumberOfUsers(cursor, dataset_id):
    #We doen dit op deze manier omdat dit sneller is als distinct, want distinct sorteerd eerst heel de tabel
    query = 'CREATE OR REPLACE VIEW customers AS SELECT customer_id FROM Customer WHERE dataset_id = %s GROUP BY' \
            'customer_id; SELECT count(*) FROM customers; DROP VIEW customers;', (str(dataset_id),)

    cursor.execute(query)
    # we doen min 1 omdat we een extra user hebben toegevoegd voor de a/b tests dat eigenlijk een algemene user is voor
    # alles
    return cursor.fetchone()[0] - 1


def getNumberOfArticles(cursor, dataset_id):
    #We doen dit op deze manier omdat dit sneller is als distinct, want distinct sorteerd eerst heel de tabel
    query = 'CREATE OR REPLACE VIEW articlesC AS SELECT item_id FROM Dataset WHERE dataset_id = %s GROUP BY' \
            'item_id; SELECT count(*) FROM articlesC; DROP VIEW articlesC;', (str(dataset_id),)

    cursor.execute(query)
    return cursor.fetchone()[0]


def getNumberOfInteractions(cursor, dataset_id):
    query = 'SELECT count(*) FROM Interaction WHERE dataset_id = %s;', (str(dataset_id),)

    cursor.execute(query)
    return cursor.fetchone()[0]