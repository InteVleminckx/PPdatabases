from app import user_data_access

# from config import config_data
# from db_connection import DBConnection
# from user_data_acces import UserDataAcces
# connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
# user_data_access = UserDataAcces(connection)

import Popularity as popularity

def startAB(abtest_id, dataset_id=None):
    abtest = user_data_access.getAB_Test(abtest_id)
    result_ids = abtest.result_id
    startpoint = str(abtest.start_point)
    endpoint = str(abtest.end_point)
    stepsize = abtest.stepsize
    topk = abtest.topk


    for result_id in result_ids:
        result = user_data_access.getResult(result_id)
        algorithm_param = result.algorithm_param
        algorithm = user_data_access.getAlgorithm(abtest_id, result_id)

        if algorithm.name == "popularity":
            retraininterval = int(algorithm.params["retraininterval"])
            windowsize = int(algorithm.params["windowsize"])
            popAlgo = popularity.Popularity(dataset_id, abtest_id, result_id, startpoint, endpoint, stepsize, topk, windowsize, retraininterval, algorithm_param)
            popAlgo.recommend()


def main():
    startAB(1, 0)

# main()