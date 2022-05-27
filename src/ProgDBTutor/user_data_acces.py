import time

import pandas as pd
import numpy
from psycopg2.extensions import register_adapter, AsIs
import psycopg2.extras
from config import config_data
from db_connection import DBConnection
from datetime import datetime, timedelta

"""
This class is to hold an datascientist out of the database
"""
class DataScientist:
    def __init__(self, firstname, lastname, username, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.email = email
        self.password = password

    def to_dct(self):
        return {'firstname': self.firstname, 'lastname': self.lastname, 'username': self.username,'email': self.email, 'password': self.password}

"""
This class represents an item out of the database
"""
class Item:
    def __init__(self, item_number, atributesAndVals, dataset_id):
        self.item_number = item_number
        self.attributes = atributesAndVals
        self.dataset_id = dataset_id

    def to_dct(self):
        return {'number' : self.item_number, 'attributes' : self.attributes, 'datasetId' : self.dataset_id}

"""
This class represents a customer from the Customer table
"""
class Customer:
    def __init__(self, dataset_id, customer_id, attributes):
        self.dataset_id = dataset_id
        self.customer_id = customer_id
        self.attributes = attributes

    def to_dct(self):
        return {'dataset_id' : self.dataset_id, 'customer_id' : self.customer_id, 'attributes' : self.attributes}

"""
This class represents an interaction in the Interaction table
"""
class Interaction:
    def __init__(self, customer_id, dataset_id, item_number, attribute_customer, time_date, price):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.item_number = item_number
        self.attribute_customer = attribute_customer
        self.time_date = time_date
        self.price = price

    def to_dct(self):
        return {'customer_id' : self.customer_id, 'dataset_id' : self.dataset_id, 'item_number' : self.item_number,
                'attribute_customer' : self.attribute_customer, 'time_date' : self.time_date, 'price' : self.price}

"""
This class represents an entry out of the AB_Test table
"""
class AB_Test:
    def __init__(self, test_id, result_id, start_point, end_point, stepsize, topk):
        self.test_id = test_id
        self.result_id = result_id
        self.start_point =  start_point
        self.end_point = end_point
        self.stepsize = stepsize
        self.topk = topk

    def to_dct(self):
        return {'test_id' : self.test_id, 'result_id' : self.result_id, 'start_point' : self.start_point, 'end_point' : self.end_point,
            'stepsize' : self.stepsize, 'topK' : self.topk}

"""
This class represents an entry out of the Algorithm table in the database.
"""
class Algorithm:
    def __init__(self, abtest_id, result_id, name, params):
        self.abtest_id= abtest_id
        self.result_id = result_id
        self.name = name
        self.params = params

    def to_dct(self):
        return {'abtest_id' : self.abtest_id, 'result_id' : self.result_id, 'name' : self.name, 'parameters' : self.params,}

"""
This table represents an entry out of the Result table in the database.
"""
class Result:
    def __init__(self, abtest_id, result_id, dataset_id, algorithm_param, creator):
        self.abtest_id = abtest_id
        self.result_id = result_id
        self.dataset_id = dataset_id
        self.algorithm_param = algorithm_param
        self.creator = creator

    def to_dct(self):
        return {'abtest_id' : self.abtest_id, 'result_id' : self.result_id, 'dataset_id' : self.dataset_id, 'algorithm_param' : self.algorithm_param, 'creator' : self.creator}

"""
This class represents an entry out of the Recommendation table of the database.
"""
class Recommendation:
    def __init__(self, abtest_id, result_id, dataset_id, customer_id, item_number, attribute_customer, start_point, end_point):
        self.abtest_id = abtest_id
        self.result_id = result_id
        self.dataset_id = dataset_id
        self.customer_id = customer_id
        self.item_number = item_number
        self.attribute_customer = attribute_customer
        self.start_point = start_point
        self.end_point = end_point

    def to_dct(self):
        return {'abtest_id' : self.abtest_id, 'result_id' : self.result_id, 'dataset_id' : self.dataset_id,
                'customer_id' : self.customer_id, 'item_number' : self.item_number}


#Acces Classes
########################################################################################################################

dbconnect = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
datasetId = 0


"""
This class is for accesing the Datascientist table and the Admin table
"""

"""
This function gets all the datascientists in the database.
"""
def get_users():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password FROM DataScientist d, Authentication a WHERE d.username = a.username') #Haalt uit de database
    user_objects = list()
    for row in cursor:
        user_object = DataScientist(row[0], row[1], row[2], row[3], row[4])
        user_objects.append(user_object)

    return user_objects

"""
This function gets the datascientists with the given name out of the database
"""
def get_user(username):
    global dbconnect
    cursor = dbconnect.get_cursor()
    # Zoekt een user op zijn username
    cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.username=%s', (username))
    row = cursor.fetchone()
    if not row:
        return None

    return DataScientist(row[0], row[1], row[2], row[3], row[4])

"""
This function gets datascientists with the given email adress.
"""
def get_user_by_email(email):
    global dbconnect
    cursor = dbconnect.get_cursor()
    # Zoekt een user op zijn username
    cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.email=%s', (email))
    row = cursor.fetchone()
    if not row:
        return None

    return DataScientist(row[0], row[1], row[2], row[3], row[4])

"""
This function gets the datascientist, wchich is also an admin.
"""
def getAdmin(adminName):
    global dbconnect
    cursor = dbconnect.get_cursor()
    # Zoekt een user op zijn username
    cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d,\
     Authentication a, Admin ad WHERE d.username == a.username AND d.username=%s AND d.username = ad.username',
                   (adminName))
    row = cursor.fetchone()
    if not row:
        return None

    return DataScientist(row[0], row[1], row[2], row[3], row[4])

"""
This function adds the given user object to the database.
"""
def addUser(user_obj):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute('INSERT INTO Authentication(username, password) VALUES(%s,%s)',
                       (user_obj.username, user_obj.password))
        cursor.execute('INSERT INTO DataScientist(username, email, firstname, lastname) VALUES(%s,%s,%s,%s)',
                       (user_obj.username, user_obj.email, user_obj.firstname, user_obj.lastname))

        dbconnect.commit()
        return user_obj
    except:
        dbconnect.rollback()
        raise Exception("Unable to save the user!")

"""
This fucntion gets the item zith the given item id from the dataset.
"""
def getItem(item_id, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()

    # First get the itemnumber of an item where the attribute 'item_id' = item_id
    cursor.execute('SELECT item_number FROM Articles where dataset_id = %s and attribute = %s and val = %s LIMIT 1',
                   (str(dataset_id), 'article_id', str(item_id)))
    itemNumber = cursor.fetchone()[0]

    # Second, use the itemNumber to get all the attributes of an item
    cursor.execute(
        "SELECT dataset_id, item_number, attribute, val FROM Articles WHERE %s = item_number AND %s = dataset_id",
        (str(itemNumber), str(dataset_id)))

    attr = {}
    notEmpty = False
    dataset_id = 0
    for row in cursor:
        notEmpty = True
        dataset_id = row[0]
        attr[row[2]] = row[3]

    if not notEmpty:
        return None

    return Item(item_id, attr, dataset_id)

def getDatasets():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT dataset_id, dataset_name FROM Dataset")

    dataset_names = []
    for row in cursor:
        dataset_names.append((row[0], row[1]))

    return dataset_names

def getDatasetname(dataset_id):

    cursor = dbconnect.get_cursor()
    cursor.execute("select dataset_name from dataset where dataset_id = %s;", (str(dataset_id)))

    row = cursor.fetchone()
    if row is None:
        return None

    return row[0]


# def addArticles(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
def addArticles(file_name, dataset_id, types_list):
    global dbconnect
    #Duurt 1.30 min op deze manier
    print('start reading articles')
    data_articles = pd.read_csv(file_name)
    start = time.process_time()
    cursor = dbconnect.get_cursor()
    psycopg2.extensions.register_adapter(numpy.int64, psycopg2._psycopg.AsIs)
    insert_query = 'INSERT INTO Articles(item_number, val, attribute, type, dataset_id) VALUES %s'

    tuples_list = []
    index = 0
    for column in data_articles.columns:
        subset = data_articles[[column]].copy()
        subset['column'] = column
        subset['type'] = types_list['articles_types'][index]
        subset['dataset_id'] = dataset_id
        tuples = list(subset.to_records())
        tuples_list.extend(tuples)
        index += 1

    # data_articles.to_csv(file_name, index=False)
    # cursor.execute('COPY Customer FROM %s DELIMITER %s CSV HEADER', (str(file_name), ','))

    psycopg2.extras.execute_values(
        cursor, insert_query, tuples_list, template=None, page_size=100
    )
    cursor.execute('INSERT INTO Names(dataset_id, table_name, name) VALUES (%s, %s, %s);', (str(dataset_id), 'articles', types_list['articles_name_column']))
    dbconnect.commit()

    print("Articles: ", time.process_time() - start)
    print('end reading articles')

"""
This function returns the asked attribute of a given item. If the item exists
"""
def getItemAttribute(itemId, attr):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT item_number, attribute, val FROM Articles WHERE %s = item_number AND %s = attribute", (itemId, attr))

    row = cursor.fetchone()

    if not row:
        return None

    return [row[1], row[2]]


# def addCustomer(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
def addCustomers(file_name, dataset_id, types_list):
    global dbconnect
    cursor = dbconnect.get_cursor()
    start = time.process_time()
    print('start reading customers')
    cursor.execute("DROP INDEX IF EXISTS customer_id_idx;")
    dbconnect.commit()
    data_customers = pd.read_csv(file_name)
    psycopg2.extensions.register_adapter(numpy.int64, psycopg2._psycopg.AsIs)
    insert_query = 'INSERT INTO Customer(customer_number, val, attribute, type, dataset_id) VALUES %s;'

    tuples_list = []
    index = 0
    for column in data_customers.columns:
        subset = data_customers[[column]].copy()
        subset['column'] = column
        subset['type'] = types_list['customers_types'][index]
        subset['dataset_id'] = dataset_id
        tuples = list(subset.to_records())
        tuples_list.extend(tuples)
        index += 1

    # add default user
    tuples_list.append((-1, '-1', 'customer_id', 'default', dataset_id))

    # data_customers.to_csv(file_name, index=False)
    # cursor.execute('COPY Customer FROM %s DELIMITER %s CSV HEADER', (str(file_name), ','))
    psycopg2.extras.execute_values(
        cursor, insert_query, tuples_list, template=None, page_size=100
    )
    cursor.execute('INSERT INTO Names(dataset_id, table_name, name) VALUES (%s, %s, %s);', (str(dataset_id), 'customers', types_list['customers_name_column']))

    cursor.execute("CREATE INDEX customer_id_idx ON Customer (dataset_id);")

    dbconnect.commit()

    print("Customer: ", time.process_time() - start)
    print('end inserting customers')

"""
This function gets the customer with the given customer id out of the database.
"""
def getCustomer(customer_id, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()

    # First get the customerNumber of a customer where the attribute 'customer_id' = customer_id
    cursor.execute(
        'SELECT customer_number FROM Customer where dataset_id = %s and attribute = %s and val = %s LIMIT 1',
        (str(dataset_id), 'customer_id', str(customer_id)))
    customerNumber = cursor.fetchone()[0]

    # Second, use the Number to get all the attributes of an item
    cursor.execute("SELECT dataset_id, customer_number, attribute, val\
                    FROM Customer WHERE customer_number = %s AND dataset_id = %s", (str(customerNumber), str(dataset_id)))

    attr = {}
    notEmpty = False
    for row in cursor:
        notEmpty = True
        attr[row[2]] = row[3]

    return Customer(dataset_id, customer_id, attr)

"""
This function returns all the id's of the customers in the same dataset.
"""
def getCustomersIDs(dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    # cursor.execute("SELECT c1.customer_id, c1.attribute\
    #                 FROM Customer c1 WHERE c1.dataset_id = %s", (dataset_id))

    cursor.execute("SELECT c1.customer_id, c1.attribute\
                            FROM Customer c1 WHERE c1.dataset_id = %s", (dataset_id))

    dic = {}
    for row in cursor:
        dic[row[0]] = row[1]

    return dic


# def addArticles(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
def addPurchases(file_name, dataset_id):
    global dbconnect
    global datasetId
    print('start reading purchases')
    data_purchases = pd.read_csv(file_name)
    cursor = dbconnect.get_cursor()
    start = time.process_time()
    cursor.execute("DROP INDEX IF EXISTS interaction_index;")
    dbconnect.commit()
    cursor.execute("DROP INDEX IF EXISTS inter_price;")
    dbconnect.commit()

    cursor.execute('SELECT attribute FROM customer WHERE dataset_id = %s AND customer_number = -1 LIMIT 1', str(dataset_id))
    customer = cursor.fetchone()
    customer_attribute = customer[0]
    data_purchases['dataset_id'] = dataset_id
    data_purchases['attribute_customer'] = customer_attribute
    data_purchases = data_purchases.drop_duplicates()
    data_purchases.to_csv(file_name, index=False, header=False)

    f = open(file_name)
    cursor.copy_from(f, 'interaction', sep=',')
    dbconnect.commit()
    datasetId += 1

    cursor.execute("CREATE INDEX interaction_index ON Interaction(t_dat, customer_id, dataset_id);")
    dbconnect.commit()

    cursor.execute("CREATE INDEX inter_price ON Interaction(t_dat, customer_id, dataset_id);")
    dbconnect.commit()

    print("Purchases: ", time.process_time() - start)
    print('end reading purchases')

"""
This function gets the interaction out of the database that corresponds with the given attributes.
"""
def getInteraction(customer_id, item_id, time_date, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT customer_id, dataset_id, item_id, attribute_customer, t_dat, price \
                    FROM Interaction WHERE customer_id = %s AND item_id = %s AND t_dat = %s AND dataset_id = %s",
                     (str(customer_id), str(item_id), time_date, str(dataset_id)))

    row = cursor.fetchone()
    if not row:
        return None

    return Interaction(row[0], row[1], row[2], row[3], row[4], row[5])

def getNumberOfInteractions(dataset_id, curDate):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT count(item_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
                   (curDate, dataset_id))

    return cursor.fetchone()[0]

def getNumberOfActiveUsers(dataset_id, curDate):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT count(distinct customer_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
                   (curDate, dataset_id))

    return cursor.fetchone()[0]

def getResultIds(abtest_id, dataset_id):
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT result_id FROM Result WHERE abtest_id = %s AND dataset_id = %s;',(abtest_id, dataset_id))

    rows = cursor.fetchall()
    results = []
    for row in rows:
        results.append(row[0])

    return results

def getClickTroughRate(abtest_id, result_id,dataset_id, curDate):
    global dbconnect

    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT count(DISTINCT r.item_number) FROM Recommendation r, Interaction i WHERE r.abtest_id = %s AND r.result_id = %s AND %s BETWEEN r.start_point AND r.end_point'
                   ' AND i.dataset_id = %s AND i.t_dat = %s AND r.item_number = i.item_id;', (abtest_id, result_id, curDate, dataset_id, curDate))


    return cursor.fetchone()[0]

"""
Function to add an entry to the ABTest table
"""
def addAB_Test(abtest_id, result_id, start_point, end_point, stepsize, topk):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute('INSERT INTO ABTest(abtest_id, result_id, start_point, end_point, stepsize, topk) VALUES(%s,%s,%s,%s,%s,%s)',
                       (str(abtest_id), str(result_id), start_point, end_point, str(stepsize), topk))

        dbconnect.commit()
    except:
        dbconnect.rollback()
        raise Exception("Unable to save ABTest!")
"""
This function gets an AB-test from the database that corresponds with the given database.
"""
def getAB_Test(abtestId):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT abtest_id, result_id, start_point, end_point, stepsize, topk FROM ABTest WHERE abtest_id = %s', (str(abtestId),))

    res = []
    rows = None
    for row in cursor:
        res.append(row[1])
        rows = row

    if not rows:
        return None

    return AB_Test(rows[0], res, rows[2], rows[3], rows[4], rows[5])

"""
Function to add an entry to the Algorithm table
"""
def addAlgorithm(abtest_id, result_id, name, param_name, value):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute(
            'INSERT INTO Algorithm(abtest_id, result_id, name, param_name, value) VALUES(%s,%s,%s,%s,%s)',
            (str(abtest_id), str(result_id), name, param_name, str(value)))

        dbconnect.commit()
    except:
        dbconnect.rollback()
        raise Exception("Unable to save Algorithm!")

"""
This function gets the algorithm out of the database that corresponds to the goven attributes.
"""
def getAlgorithm(abtest_id, result_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT abtest_id, result_id, name, param_name, value \
                            FROM Algorithm WHERE abtest_id = %s AND result_id = %s",
                             (str(abtest_id), str(result_id)))

    res = {}
    rows = None
    for row in cursor:
        res[row[3]] = row[4]
        rows = row

    if not rows:
        return None

    return Algorithm(rows[0], rows[1], rows[2], res)

"""
This function gets the result from the database that has the same result id.
"""
def getResult(result_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT abtest_id, result_id, dataset_id, algorithm_param, creator \
                            FROM Result WHERE result_id = %s",(str(result_id),))

    row = cursor.fetchone()
    if not row:
        return None

    return Result(row[0], row[1], row[2], row[3], row[4])

def addResult(abtest_id, result_id, dataset_id, algorithm_param, creator):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute('INSERT INTO Result(abtest_id, result_id, dataset_id, algorithm_param, creator) VALUES(%s,%s,%s,%s,%s)',
                       (str(abtest_id), str(result_id), str(dataset_id), algorithm_param, creator))

        dbconnect.commit()
    except:
        dbconnect.rollback()
        raise Exception("Unable to save Result!")

def getRecommendation(result_id, customer_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT abtest_id, result_id, dataset_id, customer_id, item_number, attribute_customer, start_point, end_point \
                            FROM Recommendation WHERE result_id = %s AND customer_id = %s",
                              (result_id, customer_id))

    row = cursor.fetchone()
    if not row:
        return None

    return Recommendation(row[0], row[1], row[2], row[3], row[4],  row[5], row[6], row[7])

def addRecommendation(abtest_id, result_id, dataset_id, customer_id, item_number, attribute_customer, start_point, end_point):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute(
            'INSERT INTO Recommendation(abtest_id, result_id, dataset_id, customer_id, item_number, attribute_customer, start_point, end_point) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (str(abtest_id), str(result_id), dataset_id, customer_id, item_number, attribute_customer, start_point, end_point))

        dbconnect.commit()
    except:
        dbconnect.rollback()
        raise Exception("Unable to save Recommendation!")

def getPopularityItem(dataset_id, begin_date, end_date, top_k):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT action.item_id, COUNT(action.item_id) \
                   FROM Interaction action \
                   WHERE action.t_dat BETWEEN %s AND %s AND action.dataset_id = %s \
                   GROUP BY item_id \
                   ORDER BY COUNT(item_id) DESC \
                   LIMIT %s;", (begin_date, end_date, dataset_id, top_k)
                   )
    recommendations = cursor.fetchall()
    if len(recommendations) == 0:
        return None
    return recommendations

def getItemPurchases(dataset_id, item_id, date):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT count(item_id) \
                    FROM Interaction \
                    WHERE dataset_id = %s AND item_id = %s AND t_dat = %s;", (str(dataset_id), str(item_id), date))
    amount = cursor.fetchone()
    if amount:
        amount = amount[0]
    else:
        amount = None
    return amount

def getRecencyItem(dataset_id, interval_start, interval_end, top_k):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT distinct item_id, t_dat\
                   FROM Interaction \
                   WHERE t_dat BETWEEN %s AND %s AND dataset_id = %s \
                   ORDER BY t_dat DESC LIMIT %s;", (interval_start, interval_end, dataset_id, top_k))
    recommendations = cursor.fetchall()
    if len(recommendations) == 0:
        return None
    return recommendations

def addDataset(dataset_id, dataset_name):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute('INSERT INTO Dataset(dataset_id, dataset_name) VALUES(%s,%s)',
                       (str(dataset_id), str(dataset_name)))

        dbconnect.commit()
    except:
        dbconnect.rollback()
        raise Exception("Unable to save dataset!")


def getCustomerAndItemIDs(start, end, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT I.customer_id, I.item_id FROM Interaction I WHERE I.t_dat BETWEEN %s AND %s AND dataset_id = %s ORDER BY customer_id ASC; ", (start, end, dataset_id))
    rows = cursor.fetchall()
    results = []
    for row in rows:
        # row is expected to be a Tuple here
        results.append(row)
    return results

def getMaxDatasetID():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT MAX(dataset_id) \
                    FROM Dataset")

    row = cursor.fetchone()
    if row[0] is None:
        return 0

    return row[0]

def getMaxABTestID():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT MAX(abtest_id) \
                            FROM ABTest")

    row = cursor.fetchone()
    if row[0] is None:
        return 0

    return row[0]


def getMaxAlgorithmId():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT MAX(result_id) \
                            FROM Algorithm")

    row = cursor.fetchone()
    if row[0] is None:
        return 0

    return row[0]

def createDatasetIdIndex():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("DROP INDEX IF EXISTS db_id_idx;")
    cursor.execute("CREATE INDEX db_id_idx ON Dataset (dataset_id);")
    dbconnect.commit()

def getItemRecommendations(retrainDay, item_id, abtest_id, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    algorithmsList = []
    resultIDs = getResultIds(abtest_id, dataset_id)
    for id in resultIDs:
        cursor.execute('SELECT count(*) FROM Recommendation WHERE abtest_id = %s AND result_id = %s AND dataset_id = %s AND item_number = %s AND end_point = %s',
                       (str(abtest_id), str(id), str(dataset_id), str(item_id), retrainDay))
        amount = cursor.fetchone()[0]

        # For popularity and recency we need to multiply the amount of recommendations with the amount of active users
        # because we only save 1 record in the database
        algorithm = getAlgorithm(abtest_id, id)
        if algorithm.name == 'popularity' or algorithm.name == 'recency':
            amountActiveUsers = getNumberOfActiveUsers(dataset_id, retrainDay)
            amount = amount * amountActiveUsers
        algorithmsList.append(amount)

    return algorithmsList

def getRecommendationCorrectness(retrainDay, item_id, abtest_id, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    algorithmsList = []
    resultIDs = getResultIds(abtest_id, dataset_id)
    for result_id in resultIDs:
        algorithm = getAlgorithm(abtest_id, result_id)
        timeBetween = int(algorithm.params['retraininterval'])
        nextRetrainDay = retrainDay + timedelta(days=timeBetween)

        # Popularity and recency ==> count how many interactions there were on that day
        if algorithm.name == 'popularity' or algorithm.name == 'recency':
            cursor.execute("SELECT COUNT(*) FROM Interaction i WHERE i.item_id = %s AND i.dataset_id = %s AND i.t_dat BETWEEN %s AND %s "
                           "AND i.item_id IN (SELECT r.item_number FROM Recommendation r WHERE r.abtest_id = %s AND r.result_id = %s AND "
                            "r.dataset_id = %s AND r.item_number = %s AND r.end_point = %s);",
                           (str(item_id), str(dataset_id), retrainDay, nextRetrainDay, str(abtest_id), str(result_id), str(dataset_id), str(item_id), retrainDay))

        # ItemKNN ==> look at user specific recommendations and purchases
        elif algorithm.name == 'itemknn':
            cursor.execute("SELECT COUNT(*) FROM Interaction i WHERE i.item_id = %s AND i.dataset_id = %s AND i.t_dat BETWEEN %s AND %s "
                           "AND i.item_id IN (SELECT r.item_number FROM Recommendation r WHERE r.abtest_id = %s AND r.result_id = %s AND "
                            "r.dataset_id = %s AND r.item_number = %s AND r.end_point = %s AND r.customer_id = i.customer_id);",
                           (str(item_id), str(dataset_id), retrainDay, nextRetrainDay, str(abtest_id), str(result_id), str(dataset_id), str(item_id), retrainDay))

        amount = cursor.fetchone()[0]
        algorithmsList.append(amount)

    return algorithmsList


# """
# This function gets all the datascientists in the database.
# """
# def get_users():
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password FROM DataScientist d, Authentication a WHERE d.username = a.username') #Haalt uit de database
#     user_objects = list()
#     for row in cursor:
#         user_object = DataScientist(row[0], row[1], row[2], row[3], row[4])
#         user_objects.append(user_object)
#
#     return user_objects
#
# """
# This function gets the datascientists with the given name out of the database
# """
# def get_user(username):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     # Zoekt een user op zijn username
#     cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.username=%s', (username))
#     row = cursor.fetchone()
#     if not row:
#         return None
#
#     return DataScientist(row[0], row[1], row[2], row[3], row[4])
#
# """
# This function gets datascientists with the given email adress.
# """
# def get_user_by_email(email):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     # Zoekt een user op zijn username
#     cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.email=%s', (email))
#     row = cursor.fetchone()
#     if not row:
#         return None
#
#     return DataScientist(row[0], row[1], row[2], row[3], row[4])
#
# """
# This function gets the datascientist, wchich is also an admin.
# """
# def getAdmin(adminName):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     # Zoekt een user op zijn username
#     cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d,\
#      Authentication a, Admin ad WHERE d.username == a.username AND d.username=%s AND d.username = ad.username',
#                    (adminName))
#     row = cursor.fetchone()
#     if not row:
#         return None
#
#     return DataScientist(row[0], row[1], row[2], row[3], row[4])
#
# """
# This function adds the given user object to the database.
# """
# def add_user(user_obj):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     try:
#         cursor.execute('INSERT INTO Authentication(username, password) VALUES(%s,%s)',
#                        (user_obj.username, user_obj.password))
#         cursor.execute('INSERT INTO DataScientist(username, email, firstname, lastname) VALUES(%s,%s,%s,%s)',
#                        (user_obj.username, user_obj.email, user_obj.firstname, user_obj.lastname))
#
#         dbconnect.commit()
#         return user_obj
#     except:
#         dbconnect.rollback()
#         raise Exception("Unable to save the user!")
#
# """
# This fucntion gets the item zith the given item id from the dataset.
# """
# def getItem(itemNumber, dataset_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT dataset_id, item_number, attribute, val FROM Articles WHERE %s = item_number AND %s = dataset_id", (itemNumber, dataset_id))
#
#     attr = {}
#     notEmpty = False
#     dataset_id = 0
#     for row in cursor:
#         notEmpty = True
#         dataset_id = row[0]
#         attr[row[2]] = row[3]
#
#     if not notEmpty:
#         return None
#
#     return Item(itemNumber, attr, dataset_id)
#
# def getDatasets():
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT dataset_id, dataset_name FROM Dataset")
#
#     dataset_names = []
#     for row in cursor:
#         dataset_names.append((row[0], row[1]))
#
#     return dataset_names
#
# # def addArticles(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
# def addArticles(data_articles, dataset_id):
#     #Duurt 1.30 min op deze manier
#     print('start reading articles')
#     start = time.process_time()
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     psycopg2.extensions.register_adapter(numpy.int64, psycopg2._psycopg.AsIs)
#     insert_query = 'INSERT INTO Articles(item_number, val, attribute, type, dataset_id) VALUES %s'
#
#     tuples_list = []
#     for column in data_articles.columns:
#         subset = data_articles[[column]].copy()
#         subset['column'] = column
#         subset['type'] = data_articles.dtypes[column].name
#         subset['dataset_id'] = dataset_id
#         tuples = list(subset.to_records())
#         tuples_list.extend(tuples)
#
#     psycopg2.extras.execute_values(
#         cursor, insert_query, tuples_list, template=None, page_size=100
#     )
#     dbconnect.commit()
#
#     print("Articles: ", time.process_time() - start)
#     print('end reading articles')
#
# """
# This function returns the asked attribute of a given item. If the item exists
# """
# def getItemAttribute(itemId, attr):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT item_id, attribute, val FROM Dataset WHERE %s = item_id AND %s = attr", (itemId, attr))
#
#     row = cursor.fetchone()
#
#     if not row:
#         return None
#
#     return [row[1], row[2]]
#
#
# # def addCustomer(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
# def addCustomers(data_customers, columns_customers, dataset_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     start = time.process_time()
#     print('start reading customers')
#     insert_query = 'INSERT INTO Customer(customer_number, val, attribute, type, dataset_id) VALUES %s;'
#
#     tuples_list = []
#     for column in data_customers.columns:
#         subset = data_customers[[column]].copy()
#         subset['column'] = column
#         subset['type'] = data_customers.dtypes[column].name
#         subset['dataset_id'] = dataset_id
#         tuples = list(subset.to_records())
#         tuples_list.extend(tuples)
#
#     # add default user
#     tuples_list.append((-1, str(data_customers.iloc[1, 0]), str(columns_customers[0]), 'default', dataset_id))
#
#     print('end reading customers')
#     print(len(tuples_list))
#     print('start inserting customers')
#     psycopg2.extras.execute_values(
#         cursor, insert_query, tuples_list, template=None, page_size=100
#     )
#
#     dbconnect.commit()
#
#     print("Customer: ", time.process_time() - start)
#     print('end inserting customers')
#
# """
# This function gets the customer with the given customer id out of the database.
# """
# def getCustomer(customer_id, dataset_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT dataset_id, customer_id, attribute, val\
#                     FROM Customer WHERE customer_id = %s AND dataset_id = %s", (customer_id,  dataset_id))
#
#     attr = {}
#     notEmpty = False
#     for row in cursor:
#         notEmpty = True
#         attr[row[2]] = row[3]
#
#     return Customer(dataset_id, customer_id, attr)
#
# """
# This function returns all the id's of the customers in the same dataset.
# """
# def getCustomersIDs(dataset_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     # cursor.execute("SELECT c1.customer_id, c1.attribute\
#     #                 FROM Customer c1 WHERE c1.dataset_id = %s", (dataset_id))
#
#     cursor.execute("SELECT c1.customer_id, c1.attribute\
#                             FROM Customer c1 WHERE c1.dataset_id = %s", (dataset_id))
#
#     dic = {}
#     for row in cursor:
#         dic[row[0]] = row[1]
#
#     return dic
#
#
# # def addArticles(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
# def addPurchases(data_purchases, dataset_id):
#     global dbconnect
#     print('start reading purchases')
#     cursor = dbconnect.get_cursor()
#     start = time.process_time()
#     psycopg2.extensions.register_adapter(numpy.int64, psycopg2._psycopg.AsIs)
#     insert_query = 'INSERT INTO Interaction(t_dat, customer_id, item_id, price, dataset_id, attribute_customer)\
#                                VALUES %s'
#
#     cursor.execute('SELECT attribute FROM customer WHERE dataset_id = %s AND customer_number = -1 LIMIT 1', str(dataset_id))
#     customer = cursor.fetchone()
#     customer_attribute = customer[0]
#     print(customer_attribute)
#     data_purchases['dataset_id'] = dataset_id
#     data_purchases['attribute_customer'] = customer_attribute
#     data_purchases = data_purchases.drop_duplicates()
#     tuples_list = list(data_purchases.to_records(index=False))
#
#     psycopg2.extras.execute_values(
#         cursor, insert_query, tuples_list, template=None, page_size=100
#     )
#     dbconnect.commit()
#     global datasetId
#     datasetId += 1
#
#     cursor.execute("DROP INDEX IF EXISTS interaction_index;")
#     dbconnect.commit()
#     cursor.execute("CREATE INDEX interaction_index ON Interaction(t_dat, customer_id, dataset_id);")
#     dbconnect.commit()
#
#     cursor.execute("DROP INDEX IF EXISTS inter_price;")
#     dbconnect.commit()
#     cursor.execute("CREATE INDEX inter_price ON Interaction(t_dat, customer_id, dataset_id);")
#     dbconnect.commit()
#
#     print("Purchases: ", time.process_time() - start)
#     print('end reading purchases')
#
# """
# This function gets the interaction out of the database that corresponds with the given attributes.
# """
# def getInteraction(customer_id, item_id, time_date, dataset_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT customer_id, dataset_id, item_id, attribute_dataset, attribute_customer, t_dat, price \
#                     FROM Interaction WHERE customer_id = %s AND item_id = %s AND t_dat = %s AND dataset_id = %s",
#                      (str(customer_id), str(item_id), time_date, str(dataset_id)))
#
#     row = cursor.fetchone()
#     if not row:
#         return None
#
#     return Interaction(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
#
# def getNumberOfInteractions( dataset_id, curDate):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute('SELECT count(item_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
#                    (curDate, dataset_id))
#
#     return cursor.fetchone()[0]
#
# def getNumberOfActiveUsers(dataset_id, curDate):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute('SELECT count(distinct customer_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
#                    (curDate, dataset_id))
#
#     return cursor.fetchone()[0]
#
# def getResultIds(abtest_id, dataset_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute('SELECT result_id FROM Result WHERE abtest_id = %s AND dataset_id = %s;',(abtest_id, dataset_id))
#
#     rows = cursor.fetchall()
#     results = []
#     for row in rows:
#         results.append(row[0])
#
#     return results
#
# def getClickTroughRate(abtest_id, result_id,dataset_id, curDate):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute('SELECT count(DISTINCT r.item_id) FROM Recommendation r, Interaction i WHERE r.abtest_id = %s AND r.result_id = %s AND %s BETWEEN r.start_point AND r.end_point'
#                    ' AND i.dataset_id = %s AND i.t_dat = %s AND r.item_id = i.item_id;', (abtest_id, result_id, curDate, dataset_id, curDate))
#
#
#     return cursor.fetchone()[0]
#
# """
# Function to add an entry to the ABTest table
# """
# def addAB_Test(abtest_id, result_id, start_point, end_point, stepsize, topk):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     try:
#         cursor.execute('INSERT INTO ABTest(abtest_id, result_id, start_point, end_point, stepsize, topk) VALUES(%s,%s,%s,%s,%s,%s)',
#                        (str(abtest_id), str(result_id), start_point, end_point, str(stepsize), topk))
#
#         dbconnect.commit()
#     except:
#         dbconnect.rollback()
#         raise Exception("Unable to save ABTest!")
# """
# This function gets an AB-test from the database that corresponds with the given database.
# """
# def getAB_Test(abtestId):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute('SELECT abtest_id, result_id, start_point, end_point, stepsize, topk FROM ABTest WHERE abtest_id = %s', (str(abtestId),))
#
#     res = []
#     rows = None
#     for row in cursor:
#         res.append(row[1])
#         rows = row
#
#     if not rows:
#         return None
#
#     return AB_Test(rows[0], res, rows[2], rows[3], rows[4], rows[5])
#
# """
# Function to add an entry to the Algorithm table
# """
# def addAlgorithm(abtest_id, result_id, name, param_name, value):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     try:
#         cursor.execute(
#             'INSERT INTO Algorithm(abtest_id, result_id, name, param_name, value) VALUES(%s,%s,%s,%s,%s)',
#             (str(abtest_id), str(result_id), name, param_name, str(value)))
#
#         dbconnect.commit()
#     except:
#         dbconnect.rollback()
#         raise Exception("Unable to save Algorithm!")
#
# """
# This function gets the algorithm out of the database that corresponds to the goven attributes.
# """
# def getAlgorithm(abtest_id, result_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT abtest_id, result_id, name, param_name, value \
#                             FROM Algorithm WHERE abtest_id = %s AND result_id = %s",
#                              (str(abtest_id), str(result_id)))
#
#     res = {}
#     rows = None
#     for row in cursor:
#         res[row[3]] = row[4]
#         rows = row
#
#     if not rows:
#         return None
#
#     return Algorithm(rows[0], rows[1], rows[2], res)
#
# """
# This function gets the result from the database that has the same result id.
# """
#
# def getResult(result_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT abtest_id, result_id, dataset_id, algorithm_param, creator \
#                             FROM Result WHERE result_id = %s",
#                              (str(result_id)))
#
#     row = cursor.fetchone()
#     if not row:
#         return None
#
#     return Result(row[0], row[1], row[2], row[3], row[4])
#
# def addResult(abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param, creator):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     try:
#         cursor.execute('INSERT INTO Result( abtest_id, result_id, dataset_id, algorithm_param, creator) VALUES(%s,%s,%s,%s,%s)',
#                        (str(abtest_id), str(result_id), str(dataset_id), algorithm_param, creator))
#
#         dbconnect.commit()
#     except:
#         dbconnect.rollback()
#         raise Exception("Unable to save Result!")
#
# def getRecommendation(result_id, customer_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, start_point, end_point \
#                             FROM Recommendation WHERE result_id = %s AND customer_id = %s",
#                               (result_id, customer_id))
#
#     row = cursor.fetchone()
#     if not row:
#         return None
#
#     return Recommendation(row[0], row[1], row[2], row[3], row[4],  row[5], row[6], row[7], row[8])
#
# def addRecommendation(abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, start_point, end_point):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     try:
#         cursor.execute(
#             'INSERT INTO Recommendation( abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, '
#             'start_point, end_point) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
#             (abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, start_point, end_point))
#
#         dbconnect.commit()
#     except:
#         dbconnect.rollback()
#         raise Exception("Unable to save Recommendation!")
#
# def getPopularityItem(dataset_id, begin_date, end_date, top_k):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT action.item_id, COUNT(action.item_id) \
#                    FROM Interaction action \
#                    WHERE action.t_dat BETWEEN %s AND %s AND action.dataset_id = %s \
#                    GROUP BY item_id \
#                    ORDER BY COUNT(item_id) DESC \
#                    LIMIT %s;", (begin_date, end_date, dataset_id, top_k)
#                    )
#     recommendations = cursor.fetchall()
#     if len(recommendations) == 0:
#         return None
#     return recommendations
#
# def getRecencyItem(dataset_id, interval_start, interval_end, top_k):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT item_id\
#                    FROM Interaction \
#                    WHERE t_dat BETWEEN %s AND %s AND dataset_id = %s \
#                    ORDER BY t_dat DESC LIMIT %s;", (interval_start, interval_end, dataset_id, top_k))
#     recommendations = cursor.fetchall()
#     if len(recommendations) == 0:
#         return None
#     return recommendations
#
# def addDataset(dataset_id, dataset_name):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     try:
#         cursor.execute('INSERT INTO Dataset(dataset_id, dataset_name) VALUES(%s,%s)',
#                        (str(dataset_id), str(dataset_name)))
#
#         dbconnect.commit()
#     except:
#         dbconnect.rollback()
#         raise Exception("Unable to save dataset!")
#
#
# def getCustomerAndItemIDs(start, end, dataset_id):
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT I.customer_id, I.item_id FROM Interaction I WHERE I.t_dat BETWEEN %s AND %S AND dataset_id = %s ORDER BY customer_id DESC; ", (start, end, dataset_id))
#     rows = cursor.fetchall()
#     results = []
#     for row in rows:
#
#         # row is expected to be a Tuple here
#         results.append(row)
#
#     return results
#
# def getMaxDatasetID():
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT MAX(dataset_id) \
#                     FROM Dataset")
#
#     row = cursor.fetchone()
#     if row[0] is None:
#         return 0
#
#     return row[0]
#
# def getMaxABTestID():
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT MAX(abtest_id) \
#                             FROM ABTest")
#
#     row = cursor.fetchone()
#     if row[0] is None:
#         return 0
#
#     return row[0]
#
#
# def getMaxAlgorithmId():
#     global dbconnect
#     cursor = dbconnect.get_cursor()
#     cursor.execute("SELECT MAX(result_id) \
#                             FROM Algorithm")
#
#     row = cursor.fetchone()
#     if row[0] is None:
#         return 0
#
#     return row[0]
