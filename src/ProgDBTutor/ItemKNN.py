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

        self.currentModel = None

    # function will calculate when to retrain and how long it takes
    def iknn(self):
        """
        recommends items in the current interval for each step
        """
        ########################################################################################################################
        # delta's in timestamp days
        deltaStepsize = timedelta(days=self.stepSize)

        nextRetrain = self.currentDate  # next retrain interval
        nextRecommend = self.currentDate
        start_time = tm.process_time()
        simulationStep = timedelta(days=1)

        cursor = dbconnect.get_cursor()
        cursor.execute("select t_dat from interaction where dataset_id = %s order by t_dat limit 1;",
                       (str(self.datasetID),))

        startDateDataset = cursor.fetchone()[0]
        startDateDataset = datetime.strptime(str(startDateDataset)[0:10], "%Y-%m-%d")

        cursor.execute("select t_dat from interaction where dataset_id = %s order by t_dat desc limit 1;",
                       (str(self.datasetID),))

        endDateDataset = cursor.fetchone()[0]
        endDateDataset = datetime.strptime(str(endDateDataset)[0:10], "%Y-%m-%d")

        Allinteractions = getCustomerAndItemIDs(str(startDateDataset)[0:10], str(endDateDataset)[0:10], self.datasetID)
        user_ids, item_ids = zip(*Allinteractions)
        unique_item_ids = list(set(item_ids))

        while self.currentDate <= self.end:

            if self.currentDate == nextRetrain:
                self.retrain(unique_item_ids)
                nextRetrain += self.retrainInterval

            if self.currentDate == nextRecommend:
                self.recommend(startDateDataset, self.currentDate)
                nextRecommend += deltaStepsize

            self.currentDate += simulationStep

        ########################################################################################################################

        # while self.currentDate <= self.end:
        #
        #     if self.currentDate >= nextRetrain:
        #         self.reTrain(self.start, self.currentDate)
        #         nextRetrain = nextRetrain + self.retrainInterval
        #
        #     self.currentDate += deltaStepsize
        #
        #     if self.simulationTime is None:
        #         oneStep = tm.process_time() - start_time
        #         oneStep /= self.stepSize
        #         days = (self.end - self.start).days
        #         self.simulationTime = float("{0:.4f}".format(oneStep * days))
        #         print("Excpected calculation time = " + str(self.simulationTime) + " seconds.")

    def retrain(self, unique_item_ids):

        trainingWindow = (str(self.currentDate - self.windowSize)[0:10], str(self.currentDate)[0:10])

        self.currentModel = ItemKNNAlgorithm(k=self.K, normalize=self.normalize)

        """ MUST BE LIST OF TUPLES"""
        interactions = getCustomerAndItemIDs(trainingWindow[0], trainingWindow[1], self.datasetID)

        self.currentModel.train(interactions, unique_item_ids=unique_item_ids)

    def recommend(self, startDateDataset, currentDate):
        # this one is slower, but requires far less memory than the other
        # alg = ItemKNNIterative(k=k, normalize=normalize)

        # This one is faster, but requires more memory
        interactions = getCustomerAndItemIDs(str(startDateDataset)[0:10], str(currentDate)[0:10], self.datasetID)
        user_ids, item_ids = zip(*interactions)
        unique_user_ids = list(set(user_ids))

        amt_users = len(unique_user_ids)
        histories = self.history_from_subset_interactions(interactions, amt_users=amt_users)
        # # this will be a list
        recommendations = self.currentModel.recommend_all(histories, self.top_k)
        recommendations = dict(zip(unique_user_ids, recommendations))

        insert_query = 'INSERT INTO Recommendation(abtest_id, result_id, dataset_id, customer_id, item_number, attribute_customer, start_point, end_point) VALUES %s'
        cursor = dbconnect.get_cursor()
        attribute_costumer = list(getCustomer(-1, self.datasetID).attributes)[0]
        tuples_list = []

        recommendationsInterval = (str(currentDate-timedelta(days=self.stepSize))[0:10], str(currentDate)[0:10])

        if recommendations is not None:

            """ DO SOMETHING HERE """
            for customer_id in recommendations:
                recommendations_ = recommendations[customer_id]
                for item_id in recommendations_:
                    # attribute_dataset = list(item.attributes.keys())[0]
                    tuples_list.append((self.ABTestID, self.resultID, self.datasetID, customer_id, str(item_id),
                                        attribute_costumer, *recommendationsInterval))

            psycopg2.extras.execute_values(
                cursor, insert_query, tuples_list, template=None, page_size=100
            )
            dbconnect.commit()

    # function retrains the algorithm
    # def reTrain(self, start, end):
    #     """
    #     reTrain will move the start and end date accordingly to the retrain interval
    #     then it will get the recommendations for that interval
    #     """
    #
    #     trainWindow = (str(self.currentDate - self.windowSize)[0:10], str(self.currentDate)[0:10])
    #     recommendationDictionary = self.iknn(*trainWindow)
    #
    #     insert_query = 'INSERT INTO Recommendation(abtest_id, result_id, dataset_id, customer_id, item_number, attribute_customer, start_point, end_point) VALUES %s'
    #     cursor = dbconnect.get_cursor()
    #     attribute_costumer = list(getCustomer(-1, self.datasetID).attributes)[0]
    #     tuples_list = []
    #
    #     if recommendationDictionary is not None:
    #
    #         """ DO SOMETHING HERE """
    #         for customer_id in recommendationDictionary:
    #             recommendations = recommendationDictionary[customer_id]
    #             for item_id in recommendations:
    #                 # attribute_dataset = list(item.attributes.keys())[0]
    #                 tuples_list.append((self.ABTestID, self.resultID, self.datasetID, customer_id, str(item_id),
    #                                     attribute_costumer, start, end))
    #                 # addRecommendation(self.ABTestID, self.resultID, self.datasetID, customer_id, str(item_id),
    #                 #                   attribute_costumer, start, end)
    #
    #         psycopg2.extras.execute_values(
    #             cursor, insert_query, tuples_list, template=None, page_size=100
    #         )
    #         dbconnect.commit()

    def history_from_subset_interactions(self, interactions, amt_users=5) -> List[List]:
        """ Take the history of the first users in the dataset and return as list of lists """
        user_histories = dict()
        for user_id, item_id in interactions:
            if len(user_histories) < amt_users:
                user_histories[user_id] = list()

            if user_id in user_histories:
                user_histories[user_id].append(item_id)

        return list(user_histories.values())
