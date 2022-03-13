import csv

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
#         # Hier database maken ==> CREATE TABLE Item()
#
#         createTableQuery = "CREATE TABLE Item ()"
#
#         with open('employee_birthday.txt') as csv_file:
#             csv_reader = csv.reader(csv_file, delimiter=',')
#             line_count = 0
#             for row in csv_reader:
#                 if line_count == 0:
#                     print(f'Column names are {", ".join(row)}')
#                     line_count += 1
#                 else:
#                     print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
#                     line_count += 1
#             print(f'Processed {line_count} lines.')



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
        #Zoekt een user op zijn username
        cursor.execute('SELECT d.firstname, d.lastname, d.username, d.email, a.password  FROM DataScientist d, Authentication a WHERE d.username == a.username AND d.username=%s', (username))
        row = cursor.fetchone()
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
