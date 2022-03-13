class DataScientist:
    def __init__(self, firstname, lastname, username, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.email = email
        self.password = password

    def to_dct(self):
        return {'firstname': self.firstname, 'lastname': self.lastname, 'username': self.username,'email': self.email, 'password': self.password}


class UserDataAcces:
    def __init__(self, dbconnect):
        self.dbconnect = dbconnect

    def get_users(self):
        cursor = self.dbconnect.get_cursor()
        cursor.execute('SELECT firstname, lastname, username, email, password FROM Users') #Haalt uit de database
        user_objects = list()
        for row in cursor:
            user_object = User(row[0], row[1], row[2], row[3], row[4])
            user_objects.append(user_object)

        return user_objects

    def get_user(self, username):
        cursor = self.dbconnect.get_cursor()
        #Zoekt een user op zijn email
        cursor.execute('SELECT firstname, lastname, username, email, password FROM Users WHERE email=%s', (email,))
        row = cursor.fetchone()
        return User(row[0], row[1], row[2], row[3], row[4])

    def add_user(self, user_obj):
        cursor = self.dbconnect.get_cursor()
        try:
            cursor.execute('INSERT INTO Users(firstname, lastname, username, email, password) VALUES(%s,%s,%s,%s,%s)',
                           (user_obj.firstname, user_obj.lastname, user_obj.username, user_obj.email, user_obj.password))
            self.dbconnect.commit()
            return user_obj
        except:
            self.dbconnect.rollback()
            raise Exception("Unable to save the user!")

