import time

import pandas
import numpy
from psycopg2.extensions import register_adapter, AsIs
import psycopg2.extras

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
    def __init__(self, itemId, atributesAndVals, dataset_id):
        self.item_id = itemId
        self.attributes = atributesAndVals
        self.dataset_id = dataset_id

    def to_dct(self):
        return {'id' : self.item_id, 'attributes' : self.attributes, 'datasetId' : self.dataset_id}

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
    def __init__(self, customer_id, dataset_id, item_id, attribute_dataset, attribute_customer, time_date, price):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.item_id = item_id
        self.attribute_dataset = attribute_dataset
        self.attribute_customer =attribute_customer
        self.time_date = time_date
        self.price = price

    def to_dct(self):
        return {'customer_id' : self.customer_id, 'dataset_id' : self.dataset_id, ' item_id' : self.item_id,
                'attribute_dataset' : self.attribute_dataset, ' attribute_customer' : self.attribute_customer,
                 'time_date' : self.time_date, 'price' : self.price}

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
    def __init__(self, abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param, creator):
        self.abtest_id = abtest_id
        self.result_id = result_id
        self.dataset_id = dataset_id
        self.item_id = item_id
        self.attribute_dataset = attribute_dataset
        self. algorithm_param = algorithm_param
        self.creator = creator

    def to_dct(self):
        return {'abtest_id' : self.abtest_id, 'result_id' : self.result_id, 'dataset_id' : self.dataset_id, 'item_id' : self.item_id,
                'attribute_dataset' : self.attribute_dataset, 'algorithm_param' : self.algorithm_param, 'creator' : self.creator}

"""
This class represents an entry out of the Recommendation table of the database.
"""
class Recommendation:
    def __init__(self, abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, start_point, end_point):
        self.abtest_id = abtest_id
        self.result_id = result_id
        self.dataset_id = dataset_id
        self.customer_id = customer_id
        self.item_id = item_id
        self.attribute_dataset = attribute_dataset
        self.attribute_customer = attribute_customer
        self.start_point = start_point
        self.end_point = end_point

    def to_dct(self):
        return {'abtest_id' : self.abtest_id, 'result_id' : self.result_id, 'dataset_id' : self.dataset_id,
                'customer_id' : self.customer_id, 'item_id' : self.item_id, 'attribute' : self.attribute}


#Acces Classes
########################################################################################################################

"""
This class is for accesing the Datascientist table and the Admin table
"""
class UserDataAcces:
    def __init__(self, dbconnect):
        self.dbconnect = dbconnect
        self.datasetId = 0


    """
    This function gets all the datascientists in the database.
    """
    def get_users(self):
        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password FROM DataScientist d, Authentication a WHERE d.username = a.username') #Haalt uit de database
        user_objects = list()
        for row in cursor:
            user_object = DataScientist(row[0], row[1], row[2], row[3], row[4])
            user_objects.append(user_object)

        return user_objects

    """
    This function gets the datascientists with the given name out of the database
    """
    def get_user(self, username):
        cursor = self.dbconnect.get_cursor()
        # Zoekt een user op zijn username
        cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.username=%s', (username))
        row = cursor.fetchone()
        if not row:
            return None

        return DataScientist(row[0], row[1], row[2], row[3], row[4])

    """
    This function gets datascientists with the given email adress.
    """
    def get_user_by_email(self, email):
        cursor = self.dbconnect.get_cursor()
        # Zoekt een user op zijn username
        cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.email=%s', (email))
        row = cursor.fetchone()
        if not row:
            return None

        return DataScientist(row[0], row[1], row[2], row[3], row[4])

    """
    This function gets the datascientist, wchich is also an admin.
    """
    def getAdmin(self, adminName):
        cursor = self.dbconnect.get_cursor()
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
    def add_user(self, user_obj):
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute('INSERT INTO Authentication(username, password) VALUES(%s,%s)',
                           (user_obj.username, user_obj.password))
            cursor.execute('INSERT INTO DataScientist(username, email, firstname, lastname) VALUES(%s,%s,%s,%s)',
                           (user_obj.username, user_obj.email, user_obj.firstname, user_obj.lastname))

            self.dbconnect.commit()
            return user_obj
        except:
            self.dbconnect.rollback()
            raise Exception("Unable to save the user!")

    """
    This fucntion gets the item zith the given item id from the dataset.
    """
    def getItem(self, itemId, dataset_id):
         cursor = self.dbconnect.get_cursor()
         cursor.execute("SELECT dataset_id, item_id, attribute, val FROM Dataset WHERE %s = item_id AND %s = dataset_id", (itemId, dataset_id))

         attr = {}
         notEmpty = False
         dataset_id = 0
         for row in cursor:
            notEmpty = True
            dataset_id = row[0]
            attr[row[2]] = row[3]

         if not notEmpty:
            return None

         return Item(itemId, attr, dataset_id)


    # def addArticles(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
    def addArticles(self, data_articles, columns_articles):
        #Duurt 1.30 min op deze manier
        start = time.process_time()
        cursor = self.dbconnect.get_cursor()
        insert_query = 'INSERT INTO Articles(item_number, val, attribute, type, dataset_id) VALUES %s'

        print('start reading articles')

        # isinstance(value, (int, numpy.integer))
        # value = int(value) if isinstance(value, (int, numpy.integer)) else value

        tuples_list = []
        for column in data_articles.columns:
            subset = data_articles[[column]].copy()
            subset['column'] = column
            #TODO: zorg ervoor da hier het juiste type geselecteerd wordt en we zo dan het juiste type kunnen toewijden
            subset['type'] = str(data_articles.dtypes[column])
            subset['dataset_id'] = self.datasetId
            tuples = list(subset.to_records())
            tuples_list.extend(tuples)

        # for row in range(0, len(data_articles.index)):
        #     for column in range(1, len(data_articles.columns)):
        #         if str(data_articles.iloc[row, column]) == 'nan':
        #             data_articles.iloc[row, column] = ''
        #
        #         files = (self.datasetId,
        #                         int(data_articles.iloc[row, 0]),
        #                         str(columns_articles[column]),
        #                         str(data_articles.iloc[row, column]))
        #
        #         tuples_list.append(files)

        print(len(tuples_list))
        print('start inserting articles')
        psycopg2.extras.execute_values(
            cursor, insert_query, tuples_list, template=None, page_size=100
        )
        self.dbconnect.commit()

        print("Articles: ", time.process_time() - start)
        print('end reading articles')

    """
    This function returns the asked attribute of a given item. If the item exists
    """
    def getItemAttribute(self, itemId, attr):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT item_id, attribute, val FROM Dataset WHERE %s = item_id AND %s = attr", (itemId, attr))

        row = cursor.fetchone()

        if not row:
            return None

        return [row[1], row[2]]


    # def addCustomer(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
    def addCustomers(self, data_customers, columns_customers):
        #duurt 6 min
        cursor = self.dbconnect.get_cursor()
        start = time.process_time()
        print('start reading customers')
        insert_query = 'INSERT INTO Customer(dataset_id, customer_id, attribute , val) VALUES %s;'
        execute = []

        tuples_list = []
        for column in data_customers.columns:
            subset = data_customers[[column]].copy()
            subset['column'] = column
            subset['type'] = str(data_customers.dtypes[column])
            subset['dataset_id'] = self.datasetId
            tuples = list(subset.to_records())
            tuples_list.extend(tuples)

        #             file = (self.datasetId,
        #                             -1,
        #                             str(columns_customers[column]),
        #                             str(data_customers.iloc[row, column]))
        #             execute.append(file)
        #         addedDefault = True
        #         print("Added default costumer")

        # add default user
        tuples_list.append((-1, str(columns_customers[0]), str(data_customers.iloc[1, 0]), 'default', self.datasetId))

        psycopg2.extras.execute_values(
            cursor, insert_query, execute, template=None, page_size=100
        )

        self.dbconnect.commit()

        print(len(tuples_list))
        print("Customer: ", time.process_time() - start)
        print('end reading customers')

    """
    This function gets the customer with the given customer id out of the database.
    """
    def getCustomer(self, customer_id, dataset_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT dataset_id, customer_id,attribute, val\
                        FROM Customer WHERE customer_id = %s AND dataset_id = %s", (customer_id,  dataset_id))

        attr = {}
        notEmpty = False
        for row in cursor:
            notEmpty = True
            attr[row[2]] = row[3]

        return Customer(dataset_id, customer_id, attr)

    """
    This function returns all the id's of the customers in the same dataset.
    """
    def getCustomersIDs(self, dataset_id):
        cursor = self.dbconnect.get_cursor()
        # cursor.execute("SELECT c1.customer_id, c1.attribute\
        #                 FROM Customer c1 WHERE c1.dataset_id = %s", (dataset_id))

        cursor.execute("SELECT c1.customer_id, c1.attribute\
                                FROM Customer c1 WHERE c1.dataset_id = %s", (dataset_id))

        dic = {}
        for row in cursor:
            dic[row[0]] = row[1]

        return dic


    # def addArticles(self,dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code):
    def addPurchases(self, data_purchases):
        # data_purchases = data_purchases.drop_duplicates()
        #57 minuten
        cursor = self.dbconnect.get_cursor()
        start = time.process_time()
        print('start reading purchases')

        execute = []
        created = set()
        insert_query = 'INSERT INTO Interaction(customer_id, dataset_id, item_id, attribute_dataset, attribute_customer, t_dat, price)\
                                   VALUES %s'

        tuples_list = []
        for column in data_purchases.columns:
            subset = data_purchases[[column]].copy()
            subset['column'] = column
            subset['type'] = data_purchases.dtypes[column]  # dtype is configurable in your webapplication and should come from there.
            subset['dataset_id'] = self.datasetId
            tuples = list(subset.to_records())
            tuples_list.extend(tuples)

        # for row in range(0, len(data_purchases.index)):
        #     item_id = str(data_purchases.iloc[row, 2])
        #     customer_id = int(data_purchases.iloc[row, 1])
        #
        #     item = self.getItem(item_id, self.datasetId)
        #     attribute_dataset = list(item.attributes)[0]
        #     customer = self.getCustomer(customer_id, self.datasetId)
        #     attribute_customer = list(customer.attributes)[0]
        #
        #     if (item_id, customer_id) in created:
        #         continue
        #
        #     created.add((item_id, customer_id))
        #     execute.append((str(customer_id), str(self.datasetId), str(item_id), attribute_dataset, attribute_customer, data_purchases.iloc[row, 0], data_purchases.iloc[row, 3]))
        #
        # psycopg2.extras.execute_values(
        #     cursor, insert_query, execute, template=None, page_size=100
        # )
        #
        # self.dbconnect.commit()
        print(len(tuples_list))
        print("Purchases: ", time.process_time() - start)
        self.datasetId += 1
        print('end reading purchases')

    """
    This function gets the interaction out of the database that corresponds with the given attributes.
    """
    def getInteraction(self, customer_id, item_id, time_date, dataset_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT customer_id, dataset_id, item_id, attribute_dataset, attribute_customer, t_dat, price \
                        FROM Interaction WHERE customer_id = %s AND item_id = %s AND t_dat = %s AND dataset_id = %s",
                         (str(customer_id), str(item_id), time_date, str(dataset_id)))

        row = cursor.fetchone()
        if not row:
            return None

        return Interaction(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

    def getNumberOfInteractions(self, dataset_id, curDate):
        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT count(item_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
                       (curDate, dataset_id))

        return cursor.fetchone()[0]

    def getNumberOfActiveUsers(self, dataset_id, curDate):
        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT count(distinct customer_id) FROM Interaction WHERE t_dat = %s AND dataset_id = %s;',
                       (curDate, dataset_id))

        return cursor.fetchone()[0]

    def getResultIds(self, abtest_id, dataset_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT result_id FROM Result WHERE abtest_id = %s AND dataset_id = %s;',(abtest_id, dataset_id))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(row[0])

        return results

    def getClickTroughRate(self, abtest_id, result_id,dataset_id, curDate):

        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT count(DISTINCT r.item_id) FROM Recommendation r, Interaction i WHERE r.abtest_id = %s AND r.result_id = %s AND %s BETWEEN r.start_point AND r.end_point'
                       ' AND i.dataset_id = %s AND i.t_dat = %s AND r.item_id = i.item_id;', (abtest_id, result_id, curDate, dataset_id, curDate))


        return cursor.fetchone()[0]

    """
    Function to add an entry to the ABTest table
    """
    def addAB_Test(self, abtest_id, result_id, start_point, end_point, stepsize, topk):
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute('INSERT INTO ABTest(abtest_id, result_id, start_point, end_point, stepsize, topk) VALUES(%s,%s,%s,%s,%s,%s)',
                           (str(abtest_id), str(result_id), start_point, end_point, str(stepsize), topk))

            self.dbconnect.commit()
        except:
            self.dbconnect.rollback()
            raise Exception("Unable to save ABTest!")
    """
    This function gets an AB-test from the database that corresponds with the given database.
    """
    def getAB_Test(self, abtestId):
        cursor = self.dbconnect.get_cursor()
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
    def addAlgorithm(self, abtest_id, result_id, name, param_name, value):
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute(
                'INSERT INTO Algorithm(abtest_id, result_id, name, param_name, value) VALUES(%s,%s,%s,%s,%s)',
                (str(abtest_id), str(result_id), name, param_name, str(value)))

            self.dbconnect.commit()
        except:
            self.dbconnect.rollback()
            raise Exception("Unable to save Algorithm!")

    """
    This function gets the algorithm out of the database that corresponds to the goven attributes.
    """
    def getAlgorithm(self, abtest_id, result_id):
        cursor = self.dbconnect.get_cursor()
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
    def getResult(self, result_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param, creator \
                                FROM Result WHERE result_id = %s",
                                 (str(result_id)))

        row = cursor.fetchone()
        if not row:
            return None

        return Result(row[0], row[1], row[2], row[3], row[4],  row[5], row[6])

    def addResult(self, abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param, creator):
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute('INSERT INTO Result( abtest_id, result_id, dataset_id, item_id, attribute_dataset, '
                           'algorithm_param, creator) VALUES(%s,%s,%s,%s,%s,%s,%s)',
                           (str(abtest_id), str(result_id), str(dataset_id), str(item_id), attribute_dataset, algorithm_param, creator))

            self.dbconnect.commit()
        except:
            self.dbconnect.rollback()
            raise Exception("Unable to save Result!")

    def getRecommendation(self, result_id, customer_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, start_point, end_point \
                                FROM Recommendation WHERE result_id = %s AND customer_id = %s",
                                  (result_id, customer_id))

        row = cursor.fetchone()
        if not row:
            return None

        return Recommendation(row[0], row[1], row[2], row[3], row[4],  row[5], row[6], row[7], row[8])

    def addRecommendation(self, abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, start_point, end_point):
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute(
                'INSERT INTO Recommendation( abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, '
                'start_point, end_point) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (abtest_id, result_id, dataset_id, customer_id, item_id, attribute_dataset, attribute_customer, start_point, end_point))

            self.dbconnect.commit()
        except:
            self.dbconnect.rollback()
            raise Exception("Unable to save Recommendation!")

    def getPopularityItem(self, dataset_id, begin_date, end_date, top_k):
        cursor = self.dbconnect.get_cursor()
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

    def getRecencyItem(self, dataset_id, interval_start, interval_end, top_k):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT item_id\
                       FROM Interaction \
                       WHERE t_dat BETWEEN %s AND %s AND dataset_id = %s \
                       ORDER BY t_dat DESC LIMIT %s;", (interval_start, interval_end, dataset_id, top_k))
        recommendations = cursor.fetchall()
        if len(recommendations) == 0:
            return None
        return recommendations

    def getMaxDatasetID(self):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT MAX(dataset_id) \
                        FROM Dataset")

        row = cursor.fetchone()
        if row[0] is None:
            return 0

        return row[0]

    def getMaxABTestID(self):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT MAX(abtest_id) \
                                FROM ABTest")

        row = cursor.fetchone()
        if row[0] is None:
            return 0

        return row[0]


    def getMaxAlgorithmId(self):

        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT MAX(result_id) \
                                FROM Algorithm")

        row = cursor.fetchone()
        if row[0] is None:
            return 0

        return row[0]

    def createGraph(self):
        cursor = self.dbconnect.get_cursor()
        abtest = self.getAB_Test(self.getMaxABTestID())

    def createGraph(self):
        cursor = self.dbconnect.get_cursor()
        abtest_id = 0
        f = open("chart.js", "w")
        f.write('<script>\nconst labels = [\n')
        f.close()
