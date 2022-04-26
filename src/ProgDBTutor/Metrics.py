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

        query = (
            "SELECT count(DISTINCT customer_id) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate))

    def getClickThroughRate(self, startDate=None, endDate=None):
        if startDate is None and endDate is None:
            startDate = self.start
            endDate = self.end

        """
        voor elke ACTIEVE consumer: kijk of die in die tijdsperiode minstens 1 aankoop hebben gemaakt die ook 
        recommended was. Stel dat consumer 1, 5 dingen kocht, en minstens 1 daarvan is van de recommendation
        dan zet je de CTR voor die user op 1.        
        """
        # NUMBER OF ACTIVE USERS WHO BOUGHT AT LEAST 1 RECOMMENDED ITEM
        # TODO make sure R1 is the Recommendation we want to test by making WHERE some_id = some_other_id
        query1 = (
            "CREATE VIEW Active_Users AS SELECT DISTINCT I1.customer_id FROM Interaction I1 WHERE t_dat BETWEEN %s AND %s; \
             CREATE VIEW Recommendations AS SELECT DISTINCT R1.item_id FROM Recommendation R1; \
                SELECT count(DISTINCT I.customer_id) FROM Interaction I \
            WHERE I.customer_id IN (SELECT * FROM Active_Users) AND I.item_id IN (SELECT * FROM Recommendations) AND I.t_dat BETWEEN %s AND %s ;",
            (startDate, endDate, startDate, endDate))

        # NUMBER OF ALL ACTIVE USERS
        query2 = (
            "SELECT count(DISTINCT I.customer_id) FROM Interaction I WHERE t_dat BETWEEN %s AND %s ;",
            (startDate, endDate))

        # Click Through Rate = query1 / query2
        CTR = None
        pass

    def getAttributionRate(self, days, endDate):
        # hardcoded 7 or 30 days
        if days not in [7, 30]:
            days = 7

        startDate = str(datetime.strptime(endDate, '%Y-%m-%d') - timedelta(days=days))

        """
        voor elke ACTIEVE consumer: kijk of die in die tijdsperiode aankopen hebben gemaakt die ook 
        recommended waren. Stel dat consumer 1, 5 dingen kocht, en 1 daarvan is van de recommendation
        dan zet je de Attribution Rate voor die user op 1/5  
        """
        # NUMBER OF PURCHASES WHERE ITEM WAS RECOMMENDED
        # TODO make sure R1 is the Recommendation we want to test by making WHERE some_id = some_other_id
        query1 = (
            "CREATE VIEW Recommendations AS SELECT DISTINCT R1.item_id FROM Recommendation R1; \
             SELECT count(I.item_id) FROM Interaction I WHERE I.item_id in (SELECT * FROM Recommendations) AND I.t_dat BETWEEN %s AND %s ;",
            (startDate, endDate))

        # NUMBER OF ALL PURCHASES
        query2 = (
            "SELECT count(I.item_id) FROM Interaction I WHERE I.t_dat BETWEEN %s AND %s ;",
            (startDate, endDate))

        # Attribution Rate = query1 / query2
        AR = None
        pass

    def getAverageRevenuePerUser(self, days, endDate):
        # hardcoded 7 or 30 days
        if days not in [7, 30]:
            days = 7

        startDate = str(datetime.strptime(endDate, '%Y-%m-%d') - timedelta(days=days))

        """
        Voor elke aankoop die is gemaakt en die ook in de top k recommended zat, vraag de prijs op en tel
        prijzen van al die items bij elkaar op
        """
        # SUM OF PRICES OF ALL ITEMS BOUGHS WHERE ITEM WAS ALSO RECOMMENDED
        # TODO make sure R1 is the Recommendation we want to test by making WHERE some_id = some_other_id
        query1 = ("CREATE VIEW Recommendations AS SELECT DISTINCT R1.item_id FROM Recommendation R1; \
            SELECT sum(I.price) FROM Interaction I WHERE I.item_id in (SELECT * FROM Recommendations) AND I.t_dat BETWEEN %s AND %s ;",
                  (startDate, endDate))

        # Average Revenue Per User
        ARPU = None
        pass
