# from config import config_data
# from db_connection import DBConnection
from user_data_acces import *

from datetime import datetime
from datetime import timedelta
# import time as tm
from typing import List
from rq import get_current_job
from itemKNN.src.algorithm.iknn import ItemKNNAlgorithm, ItemKNNIterativeAlgorithm
from Metrics import amountRecommendationDays
from copy import copy

class ItemKNN:

    def __init__(self, dataset_id: int, abtest_id: int, algorithm_id: int, _start, _end, top_k: int, stepSize: int,
                 normalize: bool, K: int, window: int, retrainInterval: int):
        """
        Initialize all the required variables to run the ABTest
        for variables regarding timestamps, instantiate them as a datetime object to perform operations on them
        """

        self.datasetID = dataset_id
        self.ABTestID = abtest_id
        self.algorithmID = algorithm_id
        self.start = datetime.strptime(_start, '%Y-%m-%d %H:%M:%S')
        self.end = datetime.strptime(_end, '%Y-%m-%d %H:%M:%S')
        self.top_k = top_k
        self.stepSize = stepSize
        self.normalize = normalize
        self.K = K
        self.windowSize = timedelta(days=window)
        self.retrainInterval = timedelta(days=retrainInterval)
        self.currentDate = self.start
        self.simulationTime = None
        self.currentModel = None
        self.estimated = False

    def iknn(self, algorithm_id):
        """
        Function will calculate when to retrain/recommend and call the appropriate functions
        """
        begin_time = datetime.now()

        # delta's in timestamp days
        deltaStepsize = timedelta(days=self.stepSize)

        # obtain all variables required to run the algorithm
        nextRetrain = self.currentDate
        nextRecommend = self.currentDate
        simulationStep = timedelta(days=1)

        # get the start of the dataset
        cursor = dbconnect.get_cursor()
        cursor.execute("select t_dat from interaction where dataset_id = %s order by t_dat limit 1;",
                       (str(self.datasetID),))

        startDateDataset = cursor.fetchone()[0]
        startDateDataset = datetime.strptime(str(startDateDataset)[0:10], "%Y-%m-%d")

        # get the end of the dataset
        cursor.execute("select t_dat from interaction where dataset_id = %s order by t_dat desc limit 1;",
                       (str(self.datasetID),))
        endDateDataset = cursor.fetchone()[0]
        endDateDataset = datetime.strptime(str(endDateDataset)[0:10], "%Y-%m-%d")

        # get all the interactions from the beginning to the end of the entire dataset
        Allinteractions = getCustomerAndItemIDs(str(startDateDataset)[0:10], str(endDateDataset)[0:10], self.datasetID)
        user_ids, item_ids = zip(*Allinteractions)
        unique_item_ids = list(set(item_ids))

        # Use the fast Algorithm and not the Iterative Algorithm
        self.currentModel = ItemKNNAlgorithm(k=self.K, normalize=self.normalize)

        # keep going for the entire ABTest interval
        while self.currentDate <= self.end:

            # retrain every {retrainInterval} days
            if self.currentDate == nextRetrain:
                self.retrain(unique_item_ids)
                nextRetrain += self.retrainInterval

            # recommend every {stepSize} days
            if self.currentDate == nextRecommend:
                self.recommend(startDateDataset, self.currentDate)
                nextRecommend += deltaStepsize
                # Compute the time to process one stepsize ==> use that for estimation
                if not self.estimated:
                    self.estimated = True
                    recomDays = amountRecommendationDays(copy(self.start), copy(self.end), deltaStepsize)
                    job = get_current_job(dbconnect)
                    time_difference_ms = datetime.now() - begin_time
                    time_difference = time_difference_ms.total_seconds() * recomDays
                    job.meta['times'][algorithm_id] = time_difference
                    print(job.meta)
                    job.save()

            # repeat for each day and not for each stepSize
            self.currentDate += simulationStep

    def retrain(self, unique_item_ids):
        """
        Retrain the algorithm: Do this for each active user
        :param unique_item_ids: a List of all item id's from the beginning and end of the dataset
        :return: /
        """

        # obtain window and interactions between that window
        trainingWindow = (str(self.currentDate - self.windowSize)[0:10], str(self.currentDate)[0:10])
        interactions = getCustomerAndItemIDs(trainingWindow[0], trainingWindow[1], self.datasetID)

        # train on this window with the received interactions
        self.currentModel.train(interactions, unique_item_ids=unique_item_ids)

    def recommend(self, startDateDataset, currentDate):
        """
        Function recommends items based on the previous generated model in the retrain function
        and inserts the recommendation in the database so it can be used later in the visualization
        :param startDateDataset: startDate of the dataset (datetime object)
        :param currentDate: current date in the simulation (datetime object)
        :return: /
        """

        # get all interactions from the beginning of the dataset until now
        interactions = getCustomerAndItemIDs(str(startDateDataset)[0:10], str(currentDate)[0:10], self.datasetID)
        user_ids, item_ids = zip(*interactions)
        unique_user_ids = list(set(user_ids))

        # get the purchase history for each user
        amt_users = len(unique_user_ids)
        histories = self.history_from_subset_interactions(interactions, amt_users=amt_users)

        # generate recommendations for each user individually
        recommendations = self.currentModel.recommend_all(histories, self.top_k)
        recommendations = dict(zip(unique_user_ids, recommendations))

        # query that we use later to insert all values at once
        insert_query = 'INSERT INTO Recommendation(abtest_id, algorithm_id, dataset_id, customer_id, item_number, start_point, end_point) VALUES %s'
        cursor = dbconnect.get_cursor()
        tuples_list = []

        # interval of the recommendation: required for saving the recommendation in the database
        recommendationsInterval = (str(currentDate-timedelta(days=self.stepSize))[0:10], str(currentDate)[0:10])

        # extra check just incase
        if recommendations is not None:

            # create tuples with recommendations for each user
            for customer_id in recommendations:
                recommendations_ = recommendations[customer_id]
                for item_id in recommendations_:
                    tuples_list.append((self.ABTestID, self.algorithmID, self.datasetID, customer_id, str(item_id),
                                        *recommendationsInterval))

            # insert all the tuples in the database
            psycopg2.extras.execute_values(
                cursor, insert_query, tuples_list, template=None, page_size=100
            )
            dbconnect.commit()

    def history_from_subset_interactions(self, interactions, amt_users=5) -> List[List]:
        """
        Take the history of the first users in the dataset and return as list of lists
        :return: list of users with their purchase history
        """
        user_histories = dict()
        for user_id, item_id in interactions:
            if len(user_histories) < amt_users:
                user_histories[user_id] = list()

            if user_id in user_histories:
                user_histories[user_id].append(item_id)

        return list(user_histories.values())
