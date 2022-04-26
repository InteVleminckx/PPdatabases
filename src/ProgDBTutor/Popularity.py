"""
SELECT article_id, COUNT(article_id)
FROM purchases t
WHERE t.t_date between '2020-01-01' and '2020-01-18'
GROUP BY article_id
ORDER BY COUNT(article_id) DESC
LIMIT 2;
"""
# from app import user_data_access

import datetime
# from app import user_data_access
import time as tm

from config import config_data
from db_connection import DBConnection
from user_data_acces import UserDataAcces
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
user_data_access = UserDataAcces(connection)

class Popularity:

    def __init__(self, dataset_id, abtest_id, result_id, startPoint, endPoint, stepsize, topk, window, retrainInterval, algorithm_param):
        self.startPoint = datetime.datetime.strptime(startPoint, '%Y-%m-%d %H:%M:%S')
        self.endPoint = datetime.datetime.strptime(endPoint, '%Y-%m-%d %H:%M:%S')
        self.stepsize = datetime.timedelta(days=stepsize)
        self.intStep = stepsize
        self.topk = topk
        self.window = datetime.timedelta(days=window)
        self.retrainInterval = datetime.timedelta(days=retrainInterval)
        self.currentDate = self.startPoint
        self.recommendations = dict()
        self.dataset_id = dataset_id
        self.abtest_id = abtest_id
        self.result_id = result_id
        self.algorithm_param = algorithm_param
        self.simulationTime = None

    def simulate(self):
        nextRetrainInterval = self.currentDate

        start_time = tm.process_time()
        while self.currentDate <= self.endPoint:
            if self.currentDate >= nextRetrainInterval:
                self.train()
                nextRetrainInterval += self.retrainInterval

            self.currentDate += self.stepsize

            if self.simulationTime is None:
                oneStep = tm.process_time() - start_time
                oneStep /= self.intStep
                days = (self.endPoint - self.startPoint).days
                self.simulationTime = float("{0:.4f}".format(oneStep * days))
                print("Excpected calculation time = " + str(self.simulationTime) + " seconds.")

    def recommend(self):
        self.simulate()

    def train(self):
        trainWindow = (str(self.currentDate-self.window)[0:10], str(self.currentDate)[0:10])
        recommendations = user_data_access.getPopularityItem(self.dataset_id, *trainWindow, self.topk)
        if recommendations is not None:
            for item_id, count in recommendations:
                item = user_data_access.getItem(str(item_id), self.dataset_id)
                attribute_dataset = list(item.attributes.keys())[0]
                attribute_costumer = list(user_data_access.getCustomer(-1, self.dataset_id).attributes)[0]
                user_data_access.addRecommendation(self.abtest_id, self.result_id, self.dataset_id, -1, str(item_id),
                                                       attribute_dataset, attribute_costumer, *trainWindow)

    # def getdate(self, date):
    # 
    #     year, month, day = "", "", ""
    # 
    #     first, second = True, False
    # 
    #     for letter in date:
    #         if first and not second:
    #             if letter == '-':
    #                 second = True
    #             else:
    #                 year += letter
    # 
    #         elif first and second:
    #             if letter == "-":
    #                 second = False
    #                 first = False
    #             else:
    #                 month += letter
    # 
    #         else:
    #             day += letter
    # 
    #     return int(year), int(month), int(day)

def main():

    algo = Popularity(0, 100, 0, "2020-01-01", "2020-02-15", 1, 10, 2, 3, "window_size")
    algo.recommend()

# main()