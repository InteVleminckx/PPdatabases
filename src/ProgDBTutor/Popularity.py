"""
SELECT article_id, COUNT(article_id)
FROM purchases t
WHERE t.t_date between '2020-01-01' and '2020-01-18'
GROUP BY article_id
ORDER BY COUNT(article_id) DESC
LIMIT 2;
"""
# from app import user_data_access

from datetime import datetime, timedelta
# from app import user_data_access
import time as tm

from config import config_data
from db_connection import DBConnection
from user_data_acces import *


class Popularity:

    def __init__(self, dataset_id, abtest_id, result_id, startPoint, endPoint, stepsize, topk, window, retrainInterval,
                 algorithm_param):
        self.startPoint = datetime.strptime(startPoint, '%Y-%m-%d %H:%M:%S')
        self.endPoint = datetime.strptime(endPoint, '%Y-%m-%d %H:%M:%S')
        self.stepsize = timedelta(days=stepsize)
        self.intStep = stepsize
        self.topk = topk
        self.window = timedelta(days=window)
        self.retrainInterval = timedelta(days=retrainInterval)
        self.currentDate = self.startPoint
        self.recommendations = dict()
        self.dataset_id = dataset_id
        self.abtest_id = abtest_id
        self.result_id = result_id
        self.algorithm_param = algorithm_param
        self.simulationTime = None
        self.currentModel = None


    def popularity(self):

        nextRetrain = self.currentDate  # next retrain interval
        nextRecommend = self.currentDate
        simulationStep = timedelta(days=1)

        while self.currentDate <= self.endPoint:

            if self.currentDate == nextRetrain:
                self.retrain()
                nextRetrain += self.retrainInterval

            if self.currentDate == nextRecommend:
                self.recommend()
                nextRecommend += self.stepsize

            self.currentDate += simulationStep

    def retrain(self):
        trainWindow = (str(self.currentDate - self.window)[0:10], str(self.currentDate)[0:10])
        self.currentModel = getPopularityItem(self.dataset_id, *trainWindow, self.topk) 
        
    def recommend(self):
        recommendWindow = (str(self.currentDate - self.stepsize)[0:10], str(self.currentDate)[0:10])

        if self.currentModel is not None:
            for item_id, count in self.currentModel:
                attribute_costumer = list(getCustomer(-1, self.dataset_id).attributes)[0]
                addRecommendation(self.abtest_id, self.result_id, self.dataset_id, -1, str(item_id), attribute_costumer,
                                  *recommendWindow)

    # def simulate(self):
    #     nextRetrainInterval = self.currentDate
    #
    #     start_time = tm.process_time()
    #     while self.currentDate <= self.endPoint:
    #         if self.currentDate >= nextRetrainInterval:
    #             self.train()
    #             nextRetrainInterval += self.retrainInterval
    #
    #         self.currentDate += self.stepsize
    #
    #         if self.simulationTime is None:
    #             oneStep = tm.process_time() - start_time
    #             oneStep /= self.intStep
    #             days = (self.endPoint - self.startPoint).days
    #             self.simulationTime = float("{0:.4f}".format(oneStep * days))
    #             print("Excpected calculation time = " + str(self.simulationTime) + " seconds.")
    #
    # def recommend(self):
    #     self.simulate()
    #
    # def train(self):
    #     trainWindow = (str(self.currentDate - self.window)[0:10], str(self.currentDate)[0:10])
    #     recommendations = getPopularityItem(self.dataset_id, *trainWindow, self.topk)
    #     if recommendations is not None:
    #         for item_id, count in recommendations:
    #             attribute_costumer = list(getCustomer(-1, self.dataset_id).attributes)[0]
    #             addRecommendation(self.abtest_id, self.result_id, self.dataset_id, -1, str(item_id), attribute_costumer,
    #                               *trainWindow)


def main():
    algo = Popularity(0, 100, 0, "2020-01-01", "2020-02-15", 1, 10, 2, 3, "window_size")
    algo.recommend()

# main()
