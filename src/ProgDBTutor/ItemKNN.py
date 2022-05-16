from config import config_data
from db_connection import DBConnection
from user_data_acces import *

from datetime import datetime
from datetime import timedelta
import time as tm
from typing import List

from itemKNN.src.algorithm.iknn import ItemKNNAlgorithm, ItemKNNIterativeAlgorithm


class ItemKNN:

    def __init__(self, dataset_id: int, abtest_id: int, result_id: int, _start, _end, top_k: int, stepSize: int,
                 normalize: bool, K: int, window: int, retrainInterval: int, algorithm_parameters):
        self.datasetID = dataset_id
        self.ABTestID = abtest_id
        self.resultID = result_id

        self.start = datetime.strptime(_start, '%Y-%m-%d %H:%M:%S')
        self.end = datetime.strptime(_end, '%Y-%m-%d %H:%M:%S')
        self.top_k = top_k
        self.stepSize = stepSize
        self.normalize = normalize
        self.K = K
        self.windowSize = timedelta(days=window)
        self.retrainInterval = timedelta(days=retrainInterval)

        self.currentDate = self.start

        self.parameters = algorithm_parameters
        self.simulationTime = None

    def iknn(self, start, end):
        # this one is slower, but requires far less memory than the other
        # alg = ItemKNNIterative(k=k, normalize=normalize)

        # This one is faster, but requires more memory
        alg = ItemKNNAlgorithm(k=self.K, normalize=self.normalize)

        """ MUST BE LIST OF TUPLES"""
        interactions = getCustomerAndItemIDs(start, end, self.datasetID)

        """ PARSE DATA FROM TUPLES """
        user_ids, item_ids = zip(*interactions)
        unique_item_ids = list(set(item_ids))
        unique_user_ids = list(set(user_ids))

        alg.train(interactions, unique_item_ids=unique_item_ids)

        amt_users = 5
        amt_users = len(unique_user_ids)

        histories = self.history_from_subset_interactions(interactions, amt_users=amt_users)

        # this will be a list
        recommendations = alg.recommend_all(histories, self.top_k)

        return dict(zip(unique_user_ids, recommendations))

    # function will calculate when to retrain and how long it takes
    def recommend(self):
        """
        recommends items in the current interval for each step
        """

        # delta's in timestamp days
        deltaStepsize = timedelta(days=self.stepSize)

        nextRetrain = self.currentDate  # next retrain interval

        start_time = tm.process_time()

        while self.currentDate <= self.end:

            if self.currentDate >= nextRetrain:
                self.reTrain(self.start, self.currentDate)
                nextRetrain = nextRetrain + self.retrainInterval

            self.currentDate += deltaStepsize

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

        trainWindow = (str(self.currentDate - self.windowSize)[0:10], str(self.currentDate)[0:10])
        recommendationDictionary = self.iknn(*trainWindow)
        if recommendationDictionary is not None:

            """ DO SOMETHING HERE """
            for customer_id, recommendations in recommendationDictionary:
                for item_id in recommendations:
                    item = getItem(str(item_id), self.datasetID)
                    # attribute_dataset = list(item.attributes.keys())[0]
                    attribute_costumer = list(getCustomer(-1, self.datasetID).attributes)[0]
                    addRecommendation(self.ABTestID, self.resultID, self.datasetID, -1, str(item_id),
                                      attribute_costumer, start, end)

    def history_from_subset_interactions(self, interactions, amt_users=5) -> List[List]:
        """ Take the history of the first users in the dataset and return as list of lists """
        user_histories = dict()
        for user_id, item_id in interactions:
            if len(user_histories) < amt_users:
                user_histories[user_id] = list()

            if user_id in user_histories:
                user_histories[user_id].append(item_id)

        return list(user_histories.values())
