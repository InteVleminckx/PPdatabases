# from app import user_data_access

from config import config_data
from db_connection import DBConnection
from user_data_acces import UserDataAcces
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
user_data_access = UserDataAcces(connection)

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


def getABtestResults(abtest_id, dataset_id):

    abtest = user_data_access.getAB_Test(abtest_id)
    topk = abtest.topk
    start_point = abtest.start_point
    date_tuple = getDate(start_point)

    #TODO: uit algorithm: name en param_name (zoeken op abtest_id en result_id)
    # uit recommendation: item_ids en end_point (zoeken op abtest_id, result_id en dataset_id)

    cursor = user_data_access.dbconnect.get_cursor()
    cursor.execute('SELECT DISTINCT result_id FROM Result WHERE dataset_id = %s', (str(dataset_id)))
    results = [['TOP-K', 'Current Date', 'Result_id', 'Algorithm name', 'Window']]
    for i in range(topk):
        results[0].append('Item' + str(i+1))

    algorithm = []

    resultIdList = list()
    for row in cursor:
        resultIdList.append(row[0])

    print(resultIdList)

    itemEndPoints = list()
    for res in resultIdList:
        cursor.execute("SELECT item_id, end_point FROM Recommendation WHERE abtest_id = %s AND dataset_id = %s AND result_id= %s", (abtest_id, dataset_id, res))
        for row in cursor:
            itemEndPoints.append([row[0], getDate(row[1])])

    print(itemEndPoints)
    return results

def getDate(date):
    return int(date.year), int(date.day), int(date.day)

def main():
    getABtestResults(1, 0)

main()