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
class Inetraction:
    def __init__(self, customer_id, dataset_id, item_id, atribute_id, time_data, price):
        self.customer_id = customer_id
        self.dataset_id = dataset_id
        self.item_id = item_id
        self.atribute_id = atribute_id
        self.time_date = time_date
        self.price = price

    def to_dct(self):
        return {'customer_id' : self.customer_id, 'dataset_id' : dataset_id, ' item_id' : self.item_id, 'attribute_id' : self.atribute_id,
                 'time_date' : self.time_date, 'price' : self.price}

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
         Authentication a, Admin ad WHERE d.username == a.username AND d.username=%s AND d.username = ad.username',(username))
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



#this class is for accesing the Dataset table
class DatasetAcces:
    dataset_id = 1

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
            notEmpty = true
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

#This class is for accesing the customer table in the database.
class CustomerAcces:
    def __init__(self):
        self.dbconnect = dbconnect


    def getCustomer(self, customer_id):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT dataset_id, customer_id, FN, Active, club_member_status, fashion_news_frequency, age, postal_code\
                        FROM Customer WHERE customer_id = %s LIMIT 1", (customer_id))

        row = cursor.fetchone()
        if not row:
            return None

        return Customer(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])





