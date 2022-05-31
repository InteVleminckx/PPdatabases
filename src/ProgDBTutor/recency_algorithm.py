from user_data_acces import *

from datetime import datetime
from datetime import timedelta
from rq import get_current_job
from Metrics import amountRecommendationDays
from copy import copy

class Recency:

    def __init__(self, dataset_id, abtest_id, algorithm_id, _start, _end, K: int, stepSize: int, retrainInterval):
        """
        Initialize all the required variables to run the ABTest
        for variables regarding timestamps, instantiate them as a datetime object to perform operations on them
        """
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
        self.estimated = False

    def recency(self, algorithm_id):
        """
        Function will calculate when to retrain/recommend and call the appropriate functions
        """
        begin_time = datetime.now()

        # obtain all variables required to run the algorithm
        nextRetrain = self.currentDate
        nextRecommend = self.currentDate
        simulationStep = timedelta(days=1)

        # keep going for the entire ABTest interval
        while self.currentDate <= self.end:

            # retrain every {retrainInterval} days
            if self.currentDate == nextRetrain:
                self.train()
                nextRetrain += self.retrainInterval

            # recommend every {stepSize} days
            if self.currentDate == nextRecommend:
                self.recommend()
                nextRecommend += self.stepSize
                # Compute the time to process one stepsize ==> use that for estimation
                if not self.estimated:
                    self.estimated = True
                    recomDays = amountRecommendationDays(copy(self.start), copy(self.end), copy(self.stepSize))
                    job = get_current_job(dbconnect)
                    time_difference_ms = datetime.now() - begin_time
                    time_difference = time_difference_ms.total_seconds() * recomDays
                    job.meta['times'][algorithm_id] = time_difference
                    print(job.meta)
                    job.save()

            # repeat for each day and not for each stepSize
            self.currentDate += simulationStep

    def train(self):
        """
        Retrain the algorithm: Do this for all active users together
        :return: /
        """
        # train window is from the beginning of the dataset until now
        trainWindow = (str(self.start)[0:10], str(self.currentDate)[0:10])
        self.currentModel = getRecencyItem(self.datasetID, *trainWindow, self.top_k)

    def recommend(self):
        """
        Look at the latest recommendation model and add the top k
        recommendations for all users in the database
        :return: /
        """
        recommendWindow = (str(self.start)[0:10], str(self.currentDate)[0:10])

        # A model must exist
        if self.currentModel is not None:
            for item_id in self.currentModel:
                addRecommendation(self.ABTestID, self.algorithmID, self.datasetID, -1, item_id[0], *recommendWindow)
