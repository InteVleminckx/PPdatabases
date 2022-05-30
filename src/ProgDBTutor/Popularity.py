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
#import time as tm

#from config import config_data
#from db_connection import DBConnection
from user_data_acces import *
from rq import get_current_job
from Metrics import amountRecommendationDays
from copy import copy

class Popularity:

    def __init__(self, dataset_id, abtest_id, algorithm_id, startPoint, endPoint, stepsize, topk, window, retrainInterval):
        """
        Initialize all the required variables to run the ABTest
        for variables regarding timestamps, instantiate them as a datetime object to perform operations on them
        """
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
        self.algorithm_id = algorithm_id
        self.simulationTime = None
        self.currentModel = None
        self.estimated = False

    def popularity(self, algorithm_id):
        """
        Function will calculate when to retrain/recommend and call the appropriate functions
        """
        begin_time = datetime.now()

        # obtain all variables required to run the algorithm
        nextRetrain = self.currentDate  # next retrain interval
        nextRecommend = self.currentDate
        simulationStep = timedelta(days=1)

        # keep going for the entire ABTest interval
        while self.currentDate <= self.endPoint:

            # retrain every {retrainInterval} days
            if self.currentDate == nextRetrain:
                self.retrain()
                nextRetrain += self.retrainInterval

            # recommend every {stepSize} days
            if self.currentDate == nextRecommend:
                self.recommend()
                nextRecommend += self.stepsize
                if not self.estimated:
                    self.estimated = True
                    recomDays = amountRecommendationDays(copy(self.startPoint), copy(self.endPoint), copy(self.stepsize))
                    job = get_current_job(dbconnect)
                    time_difference_ms = datetime.now() - begin_time
                    time_difference = time_difference_ms.total_seconds() * recomDays
                    job.meta['times'][algorithm_id] = time_difference
                    print(job.meta)
                    job.save()

            # repeat for each day and not for each stepSize
            self.currentDate += simulationStep

    def retrain(self):
        """
        Retrain the algorithm: Do this for all active users together
        :return: /
        """

        # train window is from {windowSize} before current date until now
        trainWindow = (str(self.currentDate - self.window)[0:10], str(self.currentDate)[0:10])
        self.currentModel = getPopularityItem(self.dataset_id, *trainWindow, self.topk)

    def recommend(self):
        """
        Look at the latest recommendation model and add the top k
        recommendations for all users in the database
        :return: /
        """
        recommendWindow = (str(self.currentDate - self.stepsize)[0:10], str(self.currentDate)[0:10])

        # A model must exist
        if self.currentModel is not None:
            for item_id, count in self.currentModel:
                addRecommendation(self.abtest_id, self.algorithm_id, self.dataset_id, -1, str(item_id),
                                  *recommendWindow)


# DEBUG ONLY
def main():
    algo = Popularity(0, 100, 0, "2020-01-01", "2020-02-15", 1, 10, 2, 3)
    algo.recommend()

# main()
