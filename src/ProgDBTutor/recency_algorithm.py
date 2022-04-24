from config import config_data
from db_connection import DBConnection

from datetime import datetime
from datetime import timedelta

connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])


class Recency:

    def __init__(self, dbconnect, _start, _end, K: int, stepSize: int, retrainInterval):
        self.top_k = K
        self.stepSize = stepSize
        self.retrainInterval = retrainInterval
        self.start = _start
        self.end = _end
        self.db = dbconnect

    def getData(self, interval_start, interval_end):
        """
        gets the wanted data for a certain step out of the database and stores it away
        :param interval_start: start of the interval
        :param interval_end: end of the interval
        """
        cursor = self.db.get_cursor()

        # expected date format: YYYY-MM-DD HH:MM:SS
        # selects the item_id between the interval and only selects the first k items
        topK_items = cursor.execute(
            f"SELECT item_id FROM Interaction WHERE t_dat BETWEEN {interval_start} AND {interval_end} ORDER BY t_dat DESC LIMIT {self.top_k}").fetchall()

        # TODO STORE DATA

    def recommend(self):
        """
        recommends items in the current interval for each step
        """
        start = datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(self.end, '%Y-%m-%d %H:%M:%S')
        delta = timedelta(days=self.stepSize)

        dateToCheck = start
        while dateToCheck <= end:

            # get the date for each step
            self.getData(str(dateToCheck), str(dateToCheck + delta))
            dateToCheck = dateToCheck + delta


    def reTrain(self):
        """
        reTrain will move the start and end date accordingly to the retrain interval
        then it will get the recommendations for that interval
        """

        # set start equal to end since we already recommended everything for the interval before
        self.start = self.end

        # set end to the amount of days in the retrainInterval later
        self.end = str(datetime.strptime(self.end, '%Y-%m-%d %H:%M:%S') + timedelta(days=self.retrainInterval))

        # recommend recent items in this new interval
        self.recommend()


# TESTCODE

# start: 1 juli 2020
startDate = "2020-07-01 00:00:01"

# end: 14 juli 2020
endDate = "2020-07-14 23:59:59"

# topK
k = 5

# stepSize: 1 week (geeft meest recente dingen binnen die week)
step = 1

# retrain interval (retrain every 7 days)
retrain = 7

recency = Recency(connection, startDate, endDate, k, step, retrain)
recency.recommend()

# 1 week later (1 retrain interval so retrain)
recency.reTrain()
