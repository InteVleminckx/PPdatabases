import time

import pandas as pd
import numpy
from psycopg2.extensions import register_adapter #, AsIs
import psycopg2.extras
from config import config_data
from db_connection import DBConnection
from datetime import timedelta #, datetime

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
        return {'firstname': self.firstname, 'lastname': self.lastname, 'username': self.username, 'email': self.email,
                'password': self.password}


"""
This class represents an item out of the database
"""
class Item:
    def __init__(self, item_number, atributesAndVals, dataset_id):
        self.item_number = item_number
        self.attributes = atributesAndVals
        self.dataset_id = dataset_id

    def to_dct(self):
        return {'number': self.item_number, 'attributes': self.attributes, 'datasetId': self.dataset_id}


"""
This class represents a customer from the Customer table
"""

class Customer:
    def __init__(self, dataset_id, customer_id, attributes):
        self.dataset_id = dataset_id
        self.customer_id = customer_id
        self.attributes = attributes

    def to_dct(self):
        return {'dataset_id': self.dataset_id, 'customer_id': self.customer_id, 'attributes': self.attributes}


"""
This class represents an interaction in the Interaction table
"""
class Interaction:
    def __init__(self, customer_id, dataset_id, item_number, time_date, price):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.item_number = item_number
        self.time_date = time_date
        self.price = price

    def to_dct(self):
        return {'customer_id': self.customer_id, 'dataset_id': self.dataset_id, 'item_number': self.item_number,
                'time_date': self.time_date, 'price': self.price}


"""
This class represents an entry out of the AB_Test table
"""
class AB_Test:
    def __init__(self, test_id, algorithm_id, start_point, end_point, stepsize, topk, creator, dataset_id):
        self.test_id = test_id
        self.algorithm_id = algorithm_id
        self.start_point = start_point
        self.end_point = end_point
        self.stepsize = stepsize
        self.topk = topk
        self.creator = creator
        self.dataset_id = dataset_id

    def to_dct(self):
        return {'test_id': self.test_id, 'algorithm_id': self.algorithm_id, 'start_point': self.start_point,
                'end_point': self.end_point,
                'stepsize': self.stepsize, 'topK': self.topk, 'creator': self.creator, 'dataset_id': self.dataset_id}


"""
This class represents an entry out of the Algorithm table in the database.
"""
class Algorithm:
    def __init__(self, abtest_id, algorithm_id, name, params):
        self.abtest_id = abtest_id
        self.algorithm_id = algorithm_id
        self.name = name
        self.params = params

    def to_dct(self):
        return {'abtest_id': self.abtest_id, 'algorithm_id': self.algorithm_id, 'name': self.name,
                'parameters': self.params}


"""
This class represents an entry out of the Recommendation table of the database.
"""
class Recommendation:
    def __init__(self, abtest_id, algorithm_id, dataset_id, customer_id, item_number, start_point, end_point):
        self.abtest_id = abtest_id
        self.algorithm_id = algorithm_id
        self.dataset_id = dataset_id
        self.customer_id = customer_id
        self.item_number = item_number
        self.start_point = start_point
        self.end_point = end_point

    def to_dct(self):
        return {'abtest_id': self.abtest_id, 'algorithm_id': self.algorithm_id, 'dataset_id': self.dataset_id,
                'customer_id': self.customer_id, 'item_number': self.item_number, 'start_point': self.start_point,
                'end_point': self.end_point}


# Access Classes
########################################################################################################################

dbconnect = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
datasetId = 0

"""
This function gets all the datascientists in the database.
"""
def get_users():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute(
        'SELECT d.firstname, d.lastname, d.username, d.email, a.password FROM DataScientist d, Authentication a WHERE d.username = a.username')  # Haalt uit de database
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
    cursor.execute(
        'SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username = a.username AND d.username = %s',
        (username))
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
    cursor.execute(
        'SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username = a.username AND d.email = %s',
        (email))
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
     Authentication a, Admin ad WHERE d.username = a.username AND d.username = %s AND d.username = ad.username',
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
        cursor.execute('INSERT INTO DataScientist(username, email, firstname, lastname) VALUES(%s,%s,%s,%s)',
                       (user_obj.username, user_obj.email, user_obj.firstname, user_obj.lastname))
        cursor.execute('INSERT INTO Authentication(username, password) VALUES(%s,%s)',
                       (user_obj.username, user_obj.password))
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


"""
This function returns the names of the datasets
"""
def getDatasets():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT dataset_id, dataset_name FROM Dataset")

    dataset_names = []
    for row in cursor:
        dataset_names.append((row[0], row[1]))

    return dataset_names


"""
This function returns the name of a certain dataset when provided with an id
"""
def getDatasetname(dataset_id):
    cursor = dbconnect.get_cursor()
    cursor.execute("select dataset_name from dataset where dataset_id = %s;", (str(dataset_id)))

    row = cursor.fetchone()
    if row is None:
        return None

    return row[0]


"""
This function adds Articles to the database for a certain dataset
"""
def addArticles(file_name, dataset_id, types_list):
    global dbconnect
    # Duurt 1.30 min op deze manier
    print('start reading articles')
    print(file_name)
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

    psycopg2.extras.execute_values(
        cursor, insert_query, tuples_list, template=None, page_size=100
    )
    cursor.execute('INSERT INTO Names(dataset_id, table_name, name) VALUES (%s, %s, %s);',
                   (str(dataset_id), 'articles', types_list['articles_name_column']))
    dbconnect.commit()

    print("Articles: ", time.process_time() - start)
    print('end reading articles')


"""
This function returns the asked attribute of a given item. If the item exists
"""
def getItemAttribute(itemId, attr):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT item_number, attribute, val FROM Articles WHERE %s = item_number AND %s = attribute",
                   (itemId, attr))

    row = cursor.fetchone()

    if not row:
        return None

    return [row[1], row[2]]


"""
This function adds Customers to the database for a certain dataset
"""
def addCustomers(file_name, dataset_id, types_list):
    global dbconnect
    cursor = dbconnect.get_cursor()
    start = time.process_time()
    print('start reading customers')
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

    psycopg2.extras.execute_values(
        cursor, insert_query, tuples_list, template=None, page_size=100
    )
    cursor.execute('INSERT INTO Names(dataset_id, table_name, name) VALUES (%s, %s, %s);',
                   (str(dataset_id), 'customers', types_list['customers_name_column']))

    cursor.execute("CREATE INDEX IF NOT EXISTS customer_id_idx ON Customer (dataset_id);")
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
                    FROM Customer WHERE customer_number = %s AND dataset_id = %s",
                   (str(customerNumber), str(dataset_id)))

    attr = {}
    for row in cursor:
        attr[row[2]] = row[3]

    return Customer(dataset_id, customer_id, attr)


"""
This function returns all the id's of the customers in the same dataset.
"""
def getCustomersIDs(dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()

    cursor.execute("SELECT c1.customer_id, c1.attribute\
                            FROM Customer c1 WHERE c1.dataset_id = %s", (dataset_id))

    dic = {}
    for row in cursor:
        dic[row[0]] = row[1]

    return dic


"""
This function adds Purchases to the database for a certain dataset
"""
def addPurchases(file_name, dataset_id):
    global dbconnect
    global datasetId
    print('start reading purchases')
    data_purchases = pd.read_csv(file_name)
    cursor = dbconnect.get_cursor()
    start = time.process_time()
    dbconnect.commit()

    data_purchases['dataset_id'] = dataset_id
    data_purchases = data_purchases.drop_duplicates()
    data_purchases.to_csv(file_name, index=False, header=False)

    f = open(file_name)
    cursor.copy_from(f, 'interaction', sep=',')
    dbconnect.commit()
    datasetId += 1

    cursor.execute("CREATE INDEX IF NOT EXISTS interaction_index ON Interaction(t_dat, customer_id, dataset_id);")
    dbconnect.commit()

    print("Purchases: ", time.process_time() - start)
    print('end reading purchases')


"""
This function gets the interaction out of the database that corresponds with the given attributes.
"""
def getInteraction(customer_id, item_id, time_date, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT customer_id, dataset_id, item_id, t_dat, price \
                    FROM Interaction WHERE customer_id = %s AND item_id = %s AND t_dat = %s AND dataset_id = %s",
                   (str(customer_id), str(item_id), time_date, str(dataset_id)))

    row = cursor.fetchone()
    if not row:
        return None

    return Interaction(row[0], row[1], row[2], row[3], row[4])


"""
This function returns the number of interactions for a certain day
"""
def getNumberOfInteractions(dataset_id, curDate):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT count(item_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
                   (curDate, dataset_id))

    return cursor.fetchone()[0]


"""
This function retusn the number of active users for a certain day
"""
def getNumberOfActiveUsers(dataset_id, curDate):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT count(distinct customer_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
                   (curDate, dataset_id))

    return cursor.fetchone()[0]


"""
This function returns the id's of all Algorithms that belong to that ABTest
"""
def getAlgorithmIds(abtest_id, dataset_id):
    cursor = dbconnect.get_cursor()
    cursor.execute('SELECT algorithm_id FROM ABTest WHERE abtest_id = %s AND dataset_id = %s;', (abtest_id, dataset_id))

    rows = cursor.fetchall()
    algorithms = []
    for row in rows:
        algorithms.append(row[0])

    return algorithms


"""
This function returns the CTR for a certain day
"""
def getClickTroughRate(abtest_id, algorithm_id, dataset_id, curDate):
    global dbconnect

    cursor = dbconnect.get_cursor()
    cursor.execute(
        'SELECT count(DISTINCT r.item_number) FROM Recommendation r, Interaction i WHERE r.abtest_id = %s AND r.algorithm_id = %s AND %s BETWEEN r.start_point AND r.end_point'
        ' AND i.dataset_id = %s AND i.t_dat = %s AND r.item_number = i.item_id;',
        (abtest_id, algorithm_id, curDate, dataset_id, curDate))

    return cursor.fetchone()[0]


"""
Function to add an entry to the ABTest table
"""
def addAB_Test(abtest_id, algorithm_id, start_point, end_point, stepsize, topk, creator, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute(
            'INSERT INTO ABTest(abtest_id, algorithm_id, start_point, end_point, stepsize, topk, creator, dataset_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (str(abtest_id), str(algorithm_id), start_point, end_point, str(stepsize), topk, creator, str(dataset_id)))
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
    cursor.execute(
        'SELECT abtest_id, algorithm_id, start_point, end_point, stepsize, topk, creator, dataset_id FROM ABTest WHERE abtest_id = %s',
        (str(abtestId),))

    res = []
    rows = None
    for row in cursor:
        res.append(row[1])
        rows = row

    if not rows:
        return None

    return AB_Test(rows[0], res, rows[2], rows[3], rows[4], rows[5], rows[6], rows[7])


"""
Function to add an entry to the Algorithm table
"""
def addAlgorithm(abtest_id, algorithm_id, name, param_name, value):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute(
            'INSERT INTO Algorithm(abtest_id, algorithm_id, name, param_name, value) VALUES(%s,%s,%s,%s,%s)',
            (str(abtest_id), str(algorithm_id), name, param_name, str(value)))
        dbconnect.commit()
    except:
        dbconnect.rollback()
        raise Exception("Unable to save Algorithm!")


"""
This function gets the algorithm out of the database that corresponds to the goven attributes.
"""
def getAlgorithm(abtest_id, algorithm_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT abtest_id, algorithm_id, name, param_name, value \
                            FROM Algorithm WHERE abtest_id = %s AND algorithm_id = %s",
                   (str(abtest_id), str(algorithm_id)))

    res = {}
    rows = None
    for row in cursor:
        res[row[3]] = row[4]
        rows = row

    if not rows:
        return None

    return Algorithm(rows[0], rows[1], rows[2], res)


"""
This function returns a recommendation for a certain user in a certain algorithm
"""
def getRecommendation(algorithm_id, customer_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT abtest_id, algorithm_id, dataset_id, customer_id, item_number, start_point, end_point \
                            FROM Recommendation WHERE algorithm_id = %s AND customer_id = %s",
                   (algorithm_id, customer_id))

    row = cursor.fetchone()
    if not row:
        return None

    return Recommendation(row[0], row[1], row[2], row[3], row[4], row[5], row[6])


"""
This function adds a recommendation in the database (called only from Algorithm class objects)
"""
def addRecommendation(abtest_id, algorithm_id, dataset_id, customer_id, item_number, start_point, end_point):
    global dbconnect
    cursor = dbconnect.get_cursor()
    try:
        cursor.execute(
            'INSERT INTO Recommendation(abtest_id, algorithm_id, dataset_id, customer_id, item_number, start_point, end_point) VALUES(%s,%s,%s,%s,%s,%s,%s)',
            (str(abtest_id), str(algorithm_id), dataset_id, customer_id, item_number, start_point, end_point))
        dbconnect.commit()
    except:
        dbconnect.rollback()
        raise Exception("Unable to save Recommendation!")


"""
This function generates the top k items for the popularity algorithm in an interval
"""
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


"""
This function returns the count of how many times the provided item was purchased on a certain day
"""
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


"""
This function generated the top k items for the recency algorithm in an interval
"""
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


"""
This function adds a dataset to the database
"""
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


"""
This function returns all customer id's and item id's belonging to them between an interval
"""
def getCustomerAndItemIDs(start, end, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute(
        "SELECT I.customer_id, I.item_id FROM Interaction I WHERE I.t_dat BETWEEN %s AND %s AND dataset_id = %s ORDER BY customer_id ASC; ",
        (start, end, dataset_id))
    rows = cursor.fetchall()
    results = []
    for row in rows:
        results.append(row)
    return results


"""
This function returns the current highest dataset ID (We need this information to generate new MAX id's)
"""
def getMaxDatasetID():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT MAX(dataset_id) \
                    FROM Dataset")

    row = cursor.fetchone()
    if row[0] is None:
        return 0

    return row[0]


"""
This function returns the current highest ABTest ID (We need this information to generate new MAX id's)
"""
def getMaxABTestID():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT MAX(abtest_id) \
                            FROM ABTest")

    row = cursor.fetchone()
    if row[0] is None:
        return 0

    return row[0]


"""
This function returns the current highest Algorithm ID (We need this information to generate new MAX id's)
"""
def getMaxAlgorithmId():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("SELECT MAX(algorithm_id) \
                            FROM Algorithm")

    row = cursor.fetchone()
    if row[0] is None:
        return 0

    return row[0]


"""
This function makes dataset id index for the current dataset
"""
def createDatasetIdIndex():
    global dbconnect
    cursor = dbconnect.get_cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS db_id_idx ON Dataset (dataset_id);")
    dbconnect.commit()


"""
This function returns a list with integers that represent how often an item was recommended by an algorithm
"""
def getItemRecommendations(recommendDay, item_id, abtest_id, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    algorithmsList = []
    algorithmIDs = getAlgorithmIds(abtest_id, dataset_id)
    for id in algorithmIDs:
        cursor.execute(
            'SELECT count(*) FROM Recommendation WHERE abtest_id = %s AND algorithm_id = %s AND dataset_id = %s AND item_number = %s AND end_point = %s',
            (str(abtest_id), str(id), str(dataset_id), str(item_id), recommendDay))
        amount = cursor.fetchone()[0]

        # For popularity and recency we need to multiply the amount of recommendations with the amount of active users
        # because we only save 1 record in the database
        algorithm = getAlgorithm(abtest_id, id)
        if algorithm.name == 'popularity' or algorithm.name == 'recency':
            amountActiveUsers = getNumberOfActiveUsers(dataset_id, recommendDay)
            amount = amount * amountActiveUsers
        algorithmsList.append(amount)

    return algorithmsList


"""
This function does a quick check to verify whether the recommendations are well executed
"""
def getRecommendationCorrectness(recommendDay, item_id, abtest_id, dataset_id):
    global dbconnect
    cursor = dbconnect.get_cursor()
    algorithmsList = []
    algorithmIDs = getAlgorithmIds(abtest_id, dataset_id)
    abtest = getAB_Test(abtest_id)
    stepsize = int(abtest.stepsize)

    for algorithm_id in algorithmIDs:
        algorithm = getAlgorithm(abtest_id, algorithm_id)
        nextRecommendDay = recommendDay + timedelta(days=stepsize)

        # Popularity and recency ==> count how many interactions there were on that day
        if algorithm.name == 'popularity' or algorithm.name == 'recency':
            cursor.execute(
                "SELECT COUNT(*) FROM Interaction i WHERE i.item_id = %s AND i.dataset_id = %s AND i.t_dat BETWEEN %s AND %s "
                "AND i.item_id IN (SELECT r.item_number FROM Recommendation r WHERE r.abtest_id = %s AND r.algorithm_id = %s AND "
                "r.dataset_id = %s AND r.item_number = %s AND r.end_point = %s);",
                (str(item_id), str(dataset_id), recommendDay, nextRecommendDay, str(abtest_id), str(algorithm_id),
                 str(dataset_id), str(item_id), recommendDay))

        # ItemKNN ==> look at user specific recommendations and purchases
        elif algorithm.name == 'itemknn':
            cursor.execute(
                "SELECT COUNT(*) FROM Interaction i WHERE i.item_id = %s AND i.dataset_id = %s AND i.t_dat BETWEEN %s AND %s "
                "AND i.item_id IN (SELECT r.item_number FROM Recommendation r WHERE r.abtest_id = %s AND r.algorithm_id = %s AND "
                "r.dataset_id = %s AND r.item_number = %s AND r.end_point = %s AND r.customer_id = i.customer_id);",
                (str(item_id), str(dataset_id), recommendDay, nextRecommendDay, str(abtest_id), str(algorithm_id),
                 str(dataset_id), str(item_id), recommendDay))

        amount = cursor.fetchone()[0]
        algorithmsList.append(amount)

    return algorithmsList
