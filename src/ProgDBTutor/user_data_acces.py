import pandas

# This class is to hold an datascientist out of the database
class DataScientist:
    def __init__(self, firstname, lastname, username, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.email = email
        self.password = password

    def to_dct(self):
        return {'firstname': self.firstname, 'lastname': self.lastname, 'username': self.username,'email': self.email, 'password': self.password}

#This class represents an item out of the database
class Item:
    def __init__(self, itemId, atributesAndVals, dataset_id):
        self.item_id = itemId
        self.attr = atributesAndVals
        self.dataset_id = dataset_id

    def to_dct(self):
        return {'id' : self.id, 'attributes' : self.attr, 'datasetId' : self.inDataset}

#This class represents a customer from the Customer table
class Customer:
    def __init__(self, dataset_id, customer_id, fn, isActive, status, freq, age, postCode):
        self.dataset_id = dataset_id
        self.customer_id = customer_id
        self.fn = fn
        self.isActive = isActive
        self.memberStatus = status
        self.fashNwsFreq = freq
        self.age = age
        self.postCode = postCode

    def to_dct(self):
        return {'dataset_id' : self.dataset_id, 'customer_id' : self.customer_id, 'FN' : self.fn , 'acitve' : self.isActive,
                'status' : self.memberStatus, 'frequency' : self.fashNwsFreq, 'age' : self.age, 'postcode' : self.postCode}

#This class represents an interaction in the Interaction table
class Interaction:
    def __init__(self, customer_id, dataset_id, item_id, atribute, time_date, price):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.item_id = item_id
        self.atribute = atribute
        self.time_date = time_date
        self.price = price

    def to_dct(self):
        return {'customer_id' : self.customer_id, 'dataset_id' : self.dataset_id, ' item_id' : self.item_id,
                'attribute_id' : self.atribute_id,
                 'time_date' : self.time_date, 'price' : self.price}


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

class Algorithm:
    def __init__(self, abtest_id, result_id, name, param_name, value):
        self.abtest_id= abtest_id
        self.result_id = result_id
        self.name = name
        self.param_name = param_name
        self.value = value

    def to_dct(self):
        return {'abtest_id' : self.abtest_id, 'result_id' : self.result_id, 'name' : self.name, 'param_name' : self.param_name,
                'value' : self.value}

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

class Recommendation:
    def __init__(self, abtest_id, result_id, dataset_id, customer_id, item_id, attribute):
        self.abtest_id = abtest_id
        self.result_id = result_id
        self.dataset_id = dataset_id
        self.customer_id = customer_id
        self.item_id = item_id
        self.attribute = attribute

    def to_dct(self):
        return {'abtest_id' : self.abtest_id, 'result_id' : self.result_id, 'dataset_id' : self.dataset_id,
                'customer_id' : self.customer_id, 'item_id' : self.item_id, 'attribute' : self.attribute}

#Acces Classes
########################################################################################################################

#This class is for accesing the Datascientist table and the Admin table
class UserDataAcces:
    def __init__(self, dbconnect):
        self.dbconnect = dbconnect
        """ cursor = self.dbconnect.get_cursor()

        df = pd.read_csv('/home/app/PPDB-Template-App/CSVFiles/articles.csv')
        amountRows = len(df.index)
        amountColumns = len(df.columns)
        dataset_id = 0

        for row in range(amountRows):
            for column in range(amountColumns):
                print(df.iloc[row, column])
                cursor.execute('INSERT INTO Dataset(dataset_id, item_id, attribute, value) VALUES(%d, %d, %s, %s)',
                (int(dataset_id), int(df.iloc[row, 0]), str(df.iloc[0, column]), str(df.iloc[row, column]))) """

    def get_users(self):
        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password FROM DataScientist d, Authentication a WHERE d.username = a.username') #Haalt uit de database
        user_objects = list()
        for row in cursor:
            user_object = DataScientist(row[0], row[1], row[2], row[3], row[4])
            user_objects.append(user_object)

        return user_objects

    def get_user(self, username):
        cursor = self.dbconnect.get_cursor()
        # Zoekt een user op zijn username
        cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.username=%s', (username))
        row = cursor.fetchone()
        if not row:
            return None

        return DataScientist(row[0], row[1], row[2], row[3], row[4])

    def get_user_by_email(self, email):
        cursor = self.dbconnect.get_cursor()
        # Zoekt een user op zijn username
        cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.email=%s', (email))
        row = cursor.fetchone()
        if not row:
            return None

        return DataScientist(row[0], row[1], row[2], row[3], row[4])

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

    def __init__(self, dbconnect):
            self.dbconnect = dbconnect
            """ self.datasetId = dataset_id
            cursor = self.dbconnect.get_cursor()

            df = pd.read_csv('/home/app/PPDB-Template-App/CSVFiles/articles.csv')
            amountRows = len(df.index)
            amountColumns = len(df.columns)

            for row in range(amountRows):
                for column in range(amountColumns):
                    print(df.iloc[row, column])
                    cursor.execute('INSERT INTO Dataset(dataset_id, item_id, attribute, value) VALUES(%d, %d, %s, %s)',
                    (int(self.dataset_id), int(df.iloc[row, 0]), str(df.iloc[0, column]), str(df.iloc[row, column])))

            dataset_id += 1 """



    def getItem(self, itemId):
         cursor = self.dbconnect.get_cursor()
         cursor.execute("SELECT dataset_id, item_id, attribute, val FROM Dataset WHERE %s = item_id", (itemId))

         #TODO maybe check if cursor is empty and raise an error if so


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

    #TODO implement if needed
    def getItems(self):
        pass

    #This function returns the asked attribute of a given item. If the item exists
    def getItemAttribute(self, itemId, attr):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT item_id, attribute, val FROM Dataset WHERE %s = item_id AND %s = attr", (itemId, attr))

        row = cursor.fetchone()

        if not row:
            return None

        return [row[1], row[2]]


    def getCustomer(self, customer_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code\
                        FROM Customer WHERE customer_id = %s LIMIT 1", (customer_id))

        row = cursor.fetchone()
        if not row:
            return None

        return Customer(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    def getInteraction(self, customer_id, item_id, time_date):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT customer_id, dataset_id, item_id, attribute, t_dat, price \
                        FROM Interaction WHERE customer_id = %s AND item_id = %s AND t_dat = %s LIMIT 1",
                         (customer_id, item_id, time_date))

        row = cursor.fetchone()
        if not row:
            return None

        return Interaction(row[0], row[1], row[2], row[3], row[4], row[5])

    def getAB_Test(self, abtestId, resultId):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT abtest_id, result_id, start_point, end_point, stepsize, topk \
                        FROM ABTest WHERE abtest_id = %s AND result_id = %s", (abtestId, resultId))

        row = cursor.fetchone()
        if not row:
            return None

        return AB_Test(row[0], row[1], row[2], row[3], row[4], row[5])

    def getAlgorithm(self, abtest_id, result_id, param_name):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT abtest_id, result_id, name, param_name, value \
                                FROM ABTest WHERE abtest_id = %s AND result_id = %s AND param_name = %s",
                                 (abtest_id, result_id, param_name))

        row = cursor.fetchone()
        if not row:
            return None

        return Algorithm(row[0], row[1], row[2], row[3], row[4])


    def getResult(self, result_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param \
                                FROM Result WHERE result_id = %s",
                                 (result_id))

        row = cursor.fetchone()
        if not row:
            return None

        return Result(row[0], row[1], row[2], row[3], row[4],  row[5], row[6])

    def getRecommendation(self,result_id, customer_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param \
                                FROM Recommendation WHERE result_id = %s AND customer_id = %s",
                                  (result_id, customer_id))

        row = cursor.fetchone()
        if not row:
            return None

        return Recommendation(row[0], row[1], row[2], row[3], row[4],  row[5])

