
from app import user_data_access

# from config import config_data
# from db_connection import DBConnection
# from user_data_acces import UserDataAcces
# connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
# user_data_access = UserDataAcces(connection)

import Popularity as popularity
import recency_algorithm as receny

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

        elif algorithm.name == "recency":
            retraininterval = int(algorithm.params["retraininterval"])
            recAlgo = receny.Recency(dataset_id, abtest_id, result_id, startpoint, endpoint, topk, stepsize, retraininterval, algorithm_param)
            recAlgo.recommend()


def getABtestResults(abtest_id, dataset_id):

    abtest = user_data_access.getAB_Test(abtest_id)
    topk = abtest.topk
    start_point = abtest.start_point
    end_point = abtest.end_point
    f = open("ABtest.txt", "w")

    cursor = user_data_access.dbconnect.get_cursor()
    cursor.execute('SELECT DISTINCT result_id FROM Result WHERE dataset_id = %s and abtest_id = %s', (str(dataset_id), str(abtest_id)))

    resultIdList = list()
    for row in cursor:
        resultIdList.append(row[0])


    # results = ['TOP-K', 'Current Date', 'Algorithm name','Result_id', 'Window']
    results = ['TOP-K', 'Current Date','Result_id', 'Algorithm name']
    for i in range(topk):
        results.append('Item' + str(i+1))

    f.write('[\n')
    for j in range(len(results)):
        f.write(str(results[j]))
        f.write('\n')
    f.write(']\n')
    f.write('start_point: ' + str(start_point)[0:10])
    f.write('\n')
    f.write('end_point: ' + str(end_point)[0:10])
    f.write('\n')
    f.write('topk: ' + str(topk))
    f.write('\n')

    itemEndPoints = list()
    for res in resultIdList:
        f.write('\n')
        f.write("result_id: " + str(res))
        f.write('\n')

        cursor.execute('SELECT name, param_name, value FROM Algorithm WHERE abtest_id = %s AND result_id = %s',(abtest_id, res))
        windowsize = 0
        name = ''
        for row in cursor:
            if row[0] == 'popularity':
                if row[1] == 'windowsize':
                    windowsize = int(row[2])

            name = row[0]
        f.write("name: " + name)
        f.write('\n')
        # f.write("windowsize: " + str(windowsize))
        # f.write('\n')

        cursor.execute(
            "SELECT item_id, end_point FROM Recommendation WHERE abtest_id = %s AND dataset_id = %s AND result_id= %s",
            (abtest_id, dataset_id, res))

        items = {}
        for row in cursor:
            date = str(row[1])[0:10]
            if date not in items:
                items[date] = []
            items[date].append(row[0])

        for key in items:
            f.write("current date: " + str(key))
            f.write('\n')
            f.write( "items: " + str(items[key]))
            f.write('\n')

    f.close()

#
# def getDate(date):
#     return int(date.year), int(date.day), int(date.day)

def main():
    getABtestResults(6, 0)

# main()