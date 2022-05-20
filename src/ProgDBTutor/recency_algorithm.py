from config import config_data
from db_connection import DBConnection
from user_data_acces import *

from datetime import datetime
from datetime import timedelta

import time as tm

class Recency:

    def __init__(self, dataset_id, abtest_id, result_id, _start, _end, K: int, stepSize: int, retrainInterval,
                 algorithm_parameters):
        self.top_k = K
        self.stepSize = stepSize
        self.retrainInterval = retrainInterval
        self.start = datetime.strptime(_start, '%Y-%m-%d %H:%M:%S')
        self.end = datetime.strptime(_end, '%Y-%m-%d %H:%M:%S')
        self.simulationTime = None

        self.datasetID = dataset_id
        self.ABTestID = abtest_id
        self.resultID = result_id

        self.parameters = algorithm_parameters

    # function will calculate when to retrain and how long it takes
    def recommend(self):
        """
        recommends items in the current interval for each step
        """
        # format YYYY-MM-DD HH:MM:SS
        # try:
        #     start = datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S')
        #     end = datetime.strptime(self.end, '%Y-%m-%d %H:%M:%S')
        #
        # # format YYYY-MM-DD
        # except:
        #     start = datetime.strptime(self.start, '%Y-%m-%d')
        #     end = datetime.strptime(self.end, '%Y-%m-%d')

        # delta's in timestamp days
        deltaStepsize = timedelta(days=self.stepSize)
        deltaRetrainInterval = timedelta(days=self.retrainInterval)

        nextRetrain = self.start  # next retrain interval
        dateToCheck = self.start  # current date

        start_time = tm.process_time()

        while dateToCheck <= self.end:

            if dateToCheck >= nextRetrain:
                self.reTrain(self.start, dateToCheck)
                nextRetrain = nextRetrain + deltaRetrainInterval

            dateToCheck = dateToCheck + deltaStepsize

            if self.simulationTime is None:
                oneStep = tm.process_time() - start_time
                oneStep /= self.stepSize
                days = (self.end - self.start).days
                self.simulationTime = float("{0:.4f}".format(oneStep * days))
                print("Excpected calculation time = " + str(self.simulationTime) + " seconds.")

    # function retrains the algorithm
    def reTrain(self, start, end):
        """
        reTrain will move the start and end date accordingly to the retrain interval
        then it will get the recommendations for that interval
        """

        # i = 1
        # print("RECENCY")
        recommendations = getRecencyItem(self.datasetID, start, end, self.top_k)
        if recommendations is not None:
            for item_id in recommendations:
                # print(i)
                # i += 1
                attribute_costumer = list(getCustomer(-1, self.datasetID).attributes)[0]
                addRecommendation(self.ABTestID, self.resultID, self.datasetID, -1, str(item_id[0]), attribute_costumer, start, end)


# TESTCODE
#
# # start: 1 juli 2020
# startDate = "2020-07-01 00:00:01"
#
# # end: 14 juli 2020
# endDate = "2020-07-14 23:59:59"
#
# # topK
# k = 5
#
# # stepSize: 1 week (geeft meest recente dingen binnen die week)
# step = 1
#
# # retrain interval (retrain every 7 days)
# retrain = 7
#
# recency = Recency(connection, startDate, endDate, k, step, retrain)
# recency.recommend()
#
# # 1 week later (1 retrain interval so retrain)
# recency.reTrain()
