import datetime
import json

from flask import request, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os
from user_data_acces import *
from Metrics import *


def getInfoVisualisationPage(abtest_id, dataset_id):
    cursor = dbconnect.get_cursor()
    cursor.execute("select start_point, end_point, stepsize, topk from abtest where abtest_id = %s limit 1;", (str(abtest_id),))
    row = cursor.fetchone()

    if row is None:
        return None

    startPoint = str(row[0])[0:10]
    endPoint = str(row[1])[0:10]
    stepsize = str(row[2])
    topk = str(row[3])

    datasetName = getDatasetname(dataset_id)
    graphPurchasesAndUsers,totalUsers, totalPurch = getPurchasesAndActiveUsersOverTime(startPoint, endPoint)

    algorithms = getAlgortihms(abtest_id)

    return {"abtest_id": abtest_id, "startpoint":startPoint, "endpoint":endPoint, "datasetname": datasetName,
            "stepsize": stepsize, "topk": topk, "graphPurchAndUsers" : graphPurchasesAndUsers, "totalUsers": totalUsers, "totalPurchases": totalPurch,
            "algorithms": algorithms}


def getPurchasesAndActiveUsersOverTime(start, end):

    cursor = dbconnect.get_cursor()
    cursor.execute("select count(distinct customer_id), count(*), t_dat from interaction where t_dat between %s and %s group by t_dat order by t_dat;",(str(start), str(end)))

    rows = cursor.fetchall()
    if rows is None:
        return None

    info = {}
    totalusers = 0
    totalPurch = 0
    for row in rows:
        info[str(row[2])[0:10]] = {"purchases": str(row[1]), "users": str(row[0])}
        totalusers += int(row[0])
        totalPurch += int(row[1])

    return info, str(totalusers), str(totalPurch)


def getAlgortihms(abtest_id):
    cursor = dbconnect.get_cursor()
    cursor.execute("select result_id from abtest where abtest_id = %s", (str(abtest_id),))

    results = cursor.fetchall()
    if results is None:
        return False

    algorithms = {}

    for result in results:
        algo = getAlgorithm(abtest_id, result[0])
        print(algo.params)
        algorithms[str(result[0])] = {"name": algo.name, "params": algo.params, "result_id": algo.result_id}

    return algorithms