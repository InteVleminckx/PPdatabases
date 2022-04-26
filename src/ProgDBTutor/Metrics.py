from config import config_data
from db_connection import DBConnection
from user_data_acces import UserDataAcces

from datetime import datetime
from datetime import timedelta

import time as tm

connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
user_data_access = UserDataAcces(connection)

class Metrics:

    def __init__(self, startDate, endDate):
        self.start = startDate
        self.end = endDate

    # METRIC: Purchases
    def getNrOfPurchases(self, startDate=None, endDate=None):
        if startDate is None and endDate is None:
            startDate = self.start
            endDate = self.end

        query = ("SELECT count(*) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate))

    # METRIC: Active Users
    def getNrOfActiveUsers(self, startDate=None, endDate=None):
        if startDate is None and endDate is None:
            startDate = self.start
            endDate = self.end

        query = ("SELECT count(DISTINCT customer_id) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate))

    def getClickThroughRate(self, startDate=None, endDate=None):
        if startDate is None and endDate is None:
            startDate = self.start
            endDate = self.end

        """
        voor elke ACTIEVE consumer: kijk of die in die tijdsperiode minstens 1 aankoop hebben gemaakt die ook 
        recommended was. Stel dat consumer 1, 5 dingen kocht, en minstens 1 daarvan is van de recommendation
        dan zet je de CTR voor die user op 1.        
        """
        # ACTIVE USERS
        query1 = (
        "CREATE VIEW Active_Users AS SELECT DISTINCT customer_id FROM Interaction WHERE t_dat BETWEEN %s AND %s;",
        (startDate, endDate))

        # NUMBER OF PURCHASES
        query = ("SELECT count(*) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate))
        pass

    def getAttributionRate(self, startDate=None, endDate=None):
        if startDate is None and endDate is None:
            startDate = self.start
            endDate = self.end

        """
        voor elke ACTIEVE consumer: kijk of die in die tijdsperiode aankopen hebben gemaakt die ook 
        recommended waren. Stel dat consumer 1, 5 dingen kocht, en 1 daarvan is van de recommendation
        dan zet je de Attribution Rate voor die user op 1/5  
        """
        # ACTIVE USERS
        query1 = (
        "CREATE VIEW Active_Users AS SELECT DISTINCT customer_id FROM Interaction WHERE t_dat BETWEEN %s AND %s;",
        (startDate, endDate))

        pass

    def getAverageRevenuePerUser(self):
        """
        Voor elke aankoop die is gemaakt en die ook in de top k recommended zat, vraag de prijs op en tel
        prijzen van al die items bij elkaar op
        """
        pass
