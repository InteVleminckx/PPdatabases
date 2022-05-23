
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
    cursor = dbconnect.get_cursor()
    cursor.execute("DELETE FROM ABTest WHERE abtest_id = %s", (abtest_id))
    cursor.commit()

def startAB(abtest_id, dataset_id):
    abtest = getAB_Test(abtest_id)
    result_ids = abtest.result_id
    startpoint = str(abtest.start_point)
    endpoint = str(abtest.end_point)
    stepsize = abtest.stepsize
    topk = abtest.topk

    for result_id in result_ids:
        result = getResult(result_id)
        algorithm_param = result.algorithm_param
        algorithm = getAlgorithm(abtest_id, result_id)

        if algorithm.name == 'popularity':
            retraininterval = int(algorithm.params["retraininterval"])
            windowsize = int(algorithm.params["windowsize"])
            popAlgo = popularity.Popularity(dataset_id, abtest_id, result_id, startpoint, endpoint, stepsize, topk, windowsize, retraininterval, algorithm_param)
            popAlgo.recommend()

        elif algorithm.name == 'recency':
            retraininterval = int(algorithm.params["retraininterval"])
            recAlgo = recency.Recency(dataset_id, abtest_id, result_id, startpoint, endpoint, topk, stepsize, retraininterval, algorithm_param)
            recAlgo.recommend()

        elif algorithm.name == 'itemknn':
            retraininterval = int(algorithm.params["retraininterval"])
            windowsize = int(algorithm.params["windowsize"])
            k = int(algorithm.params['k'])
            normalize = bool(algorithm.params['normalize'])
            itemAlgo = itemknn.ItemKNN(dataset_id, abtest_id, result_id, startpoint, endpoint, topk, stepsize,
                                       normalize, k, windowsize, retraininterval, algorithm.params)
            itemAlgo.recommend()

def getAB_Pop_Active(abtest_id, dataset_id):
    dataset_id = 0
    abtest = getAB_Test(abtest_id)

    curDate = abtest.start_point

    items = list()
    users = list()
    while curDate <= abtest.end_point:
        curDate_str = str(curDate)[0:10]
        numberOfItems = getNumberOfInteractions(dataset_id, curDate_str)
        numberOfActiveUsers = getNumberOfActiveUsers(dataset_id, curDate_str)

        items.append({"date": curDate_str, "purchases": numberOfItems})
        users.append({"date": curDate_str, "active_users": numberOfActiveUsers})

        curDate += datetime.timedelta(days=1)

    sys.stdout = open("static/metrics1.js", "w")

    dictItems = jsn.dumps(items)
    dictUsers = jsn.dumps(users)

    print("var items = '{}' ".format(dictItems))
    print("var users = '{}' ".format(dictUsers))
    sys.stdout.close()

def getCTR(abtest_id, dataset_id):
    abtest = getAB_Test(abtest_id)

    curDate = abtest.start_point
    results = getResultIds(abtest_id, dataset_id)

    ctrs = []
    for result in results:
        ctr = []
        while curDate <= abtest.end_point:
            curDate_str = str(curDate)[0:10]


            algorithm = getAlgorithm(abtest_id, result)
            numberOfClicks = getClickTroughRate(abtest_id, result,dataset_id, curDate_str)
            ctr.append({"date": curDate_str, "clicks": numberOfClicks, "algo_name": algorithm.name, "params": algorithm.params})
            curDate += datetime.timedelta(days=1)

        ctrs.append(ctr)
        curDate = abtest.start_point


    sys.stdout = open("static/metrics2.js", "w")

    for i, clicks in enumerate(ctrs):
        print("var clicks" + str(i) + " = '{}' ".format(jsn.dumps(clicks)))

    sys.stdout.close()



def getABtestResults(abtest_id, dataset_id):

    abtest = getAB_Test(abtest_id)
    topk = abtest.topk
    start_point = abtest.start_point
    end_point = abtest.end_point
    f = open("ABtest.txt", "w")

    cursor = dbconnect.get_cursor()
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
            "SELECT item_number, end_point FROM Recommendation WHERE abtest_id = %s AND dataset_id = %s AND result_id= %s",
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

# def main():
#     getCTR(1,0, user_data_access)

# main()