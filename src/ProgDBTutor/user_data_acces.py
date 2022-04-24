import pandas
# import os
class DataScientist:
    def __init__(self, firstname, lastname, username, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.email = email
        self.password = password

    def to_dct(self):
        return {'firstname': self.firstname, 'lastname': self.lastname, 'username': self.username,'email': self.email, 'password': self.password}


class Item:
    def __init__(self, itemId, atributesAndVals, dataset_id):
        self.id = itemId
        self.attr = atributesAndVals
        self.inDataset = dataset_id


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
        return DataScientist(row[0], row[1], row[2], row[3], row[4])

    def get_user_by_email(self):
        pass

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



class DatasetAcces:
    dataset_id = 1

    def __init__(self, dbconnect):
            self.dbconnect = dbconnect
            self.datasetId = dataset_id
            cursor = self.dbconnect.get_cursor()

            df = pd.read_csv('/home/app/PPDB-Template-App/CSVFiles/articles.csv')
            amountRows = len(df.index)
            amountColumns = len(df.columns)

            for row in range(amountRows):
                for column in range(amountColumns):
                    print(df.iloc[row, column])
                    cursor.execute('INSERT INTO Dataset(dataset_id, item_id, attribute, value) VALUES(%d, %d, %s, %s)',
                    (int(self.dataset_id), int(df.iloc[row, 0]), str(df.iloc[0, column]), str(df.iloc[row, column])))

            dataset_id += 1



    def getItem(self, itemId):
         cursor = self.dbconnect.get_cursor()
         cursor.execute("SELECT item_id, attribute, val FROM Dataset WHERE %s = item_id"% itemId)

         #TODO maybe check if cursor is empty and raise an error if so

         attr = {}
         for row in cursor:
            attr[row[1]] = row[2]

         return Item(itemId, attr, self.dataset_id)

    #TODO implement if needed
    def getItems(self):
        pass

    def getItemAttribute(self, itemId, attr):
        cursor = self.dbconnect.get_cursor()
        cursor.execute("SELECT item_id, attribute, val FROM Dataset WHERE %s = item_id AND %s = attr"% itemId, attr)

        row = cursor.fetchone()
        return [row[1], row[2]]



