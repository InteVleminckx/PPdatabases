from config import config_data
from db_connection import DBConnection
from user_data_acces import *

from datetime import datetime
from datetime import timedelta

import time as tm


class Recency:

    def __init__(self, dataset_id, abtest_id, algorithm_id, _start, _end, K: int, stepSize: int, retrainInterval):
        self.top_k = K
        self.stepSize = timedelta(days=stepSize)
        self.retrainInterval = timedelta(days=retrainInterval)
        self.start = datetime.strptime(_start, '%Y-%m-%d %H:%M:%S')
        self.end = datetime.strptime(_end, '%Y-%m-%d %H:%M:%S')
        self.simulationTime = None
        self.currentDate = self.start
        self.currentModel = None

        self.datasetID = dataset_id
        self.ABTestID = abtest_id
        self.algorithmID = algorithm_id

    def recency(self):

        nextRetrain = self.currentDate
        nextRecommend = self.currentDate
        simulationStep = timedelta(days=1)

        while self.currentDate <= self.end:

            if self.currentDate == nextRetrain:
                self.train()
                nextRetrain += self.retrainInterval

            if self.currentDate == nextRecommend:
                self.recommend()
                nextRecommend += self.stepSize

            self.currentDate += simulationStep

    def train(self):
        trainWindow = (str(self.start)[0:10], str(self.currentDate)[0:10])
        self.currentModel = getRecencyItem(self.datasetID, *trainWindow, self.top_k)

    def recommend(self):
        recommendWindow = (str(self.start)[0:10], str(self.currentDate)[0:10])

        if self.currentModel is not None:
            for item_id in self.currentModel:
                addRecommendation(self.ABTestID, self.algorithmID, self.datasetID, -1, item_id[0], *recommendWindow)

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
