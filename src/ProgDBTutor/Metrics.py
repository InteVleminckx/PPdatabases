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

    def getClickThroughRate(self):
        pass

    def getAttributionRate(self):
        pass

    def getAverageRevenuePerUser(self):
        pass
