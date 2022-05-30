import datetime
import json as jsn
import sys
from user_data_acces import *
from config import config_data
from db_connection import DBConnection
from user_data_acces import *
import Popularity as popularity
import recency_algorithm as recency
import ItemKNN as itemknn

def deleteABTest(abtest_id):
    """
    Function to delete an ABTest from the database
    :param abtest_id: the id of the ABTest we need to delete
    :return: /
    """
    cursor = dbconnect.get_cursor()
    cursor.execute("DELETE FROM ABTest WHERE abtest_id = %s", (abtest_id))
    cursor.commit()

def startAB(abtest_id, dataset_id):
    """
    Function to an ABTest with the appropriate algorithm or algorithms
    :param abtest_id: the id of the ABTest we want to run
    :param dataset_id: the id of the dataset where the ABTest belongs to
    :return: /
    """

    # obtain general information about the ABTest
    abtest = getAB_Test(abtest_id)
    algorithm_ids = abtest.algorithm_id
    startpoint = str(abtest.start_point)
    endpoint = str(abtest.end_point)
    stepsize = abtest.stepsize
    topk = abtest.topk

    # run each algorithm separately so we can compare them later
    for algorithm_id in algorithm_ids:
        algorithm = getAlgorithm(abtest_id, algorithm_id)

        # Popularity Algorithm
        if algorithm.name == 'popularity':
            retraininterval = int(algorithm.params["retraininterval"])
            windowsize = int(algorithm.params["windowsize"])
            popAlgo = popularity.Popularity(dataset_id, abtest_id, algorithm_id, startpoint, endpoint, stepsize, topk, windowsize, retraininterval)
            popAlgo.popularity(algorithm_id)

        # Recency Algorithm
        elif algorithm.name == 'recency':
            retraininterval = int(algorithm.params["retraininterval"])
            recAlgo = recency.Recency(dataset_id, abtest_id, algorithm_id, startpoint, endpoint, topk, stepsize, retraininterval)
            recAlgo.recency(algorithm_id)

        # ItemKNN Algorithm
        elif algorithm.name == 'itemknn':
            retraininterval = int(algorithm.params["retraininterval"])
            windowsize = int(algorithm.params["window"])
            k = int(algorithm.params['k'])
            normalize = bool(algorithm.params['normalize'])
            itemAlgo = itemknn.ItemKNN(dataset_id, abtest_id, algorithm_id, startpoint, endpoint, topk, stepsize,
                                       normalize, k, windowsize, retraininterval)
            itemAlgo.iknn(algorithm_id)

def getCTR(abtest_id, dataset_id):
    """
    Function unused (for debug only)
    """
    abtest = getAB_Test(abtest_id)
    curDate = abtest.start_point
    algorithm_ids = getAlgorithmIds(abtest_id, dataset_id)
    ctrs = []

    # Loop over the algorithms
    for algorithm_id in algorithm_ids:
        ctr = []
        while curDate <= abtest.end_point:
            curDate_str = str(curDate)[0:10]
            algorithm = getAlgorithm(abtest_id, algorithm_id)
            # Determine click through rate
            numberOfClicks = getClickTroughRate(abtest_id, algorithm_id, dataset_id, curDate_str)
            ctr.append({"date": curDate_str, "clicks": numberOfClicks, "algo_name": algorithm.name, "params": algorithm.params})
            curDate += datetime.timedelta(days=1)

        ctrs.append(ctr)
        curDate = abtest.start_point

    sys.stdout = open("static/metrics2.js", "w")
    for i, clicks in enumerate(ctrs):
        print("var clicks" + str(i) + " = '{}' ".format(jsn.dumps(clicks)))
    sys.stdout.close()