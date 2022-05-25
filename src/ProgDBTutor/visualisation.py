# import datetime
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

    algorithms, ctr, arad, arpuad = getAlgortihms(abtest_id, dataset_id, startPoint, endPoint, stepsize)

    return {"abtest_id": abtest_id, "startpoint":startPoint, "endpoint":endPoint, "datasetname": datasetName,
            "stepsize": stepsize, "topk": topk, "graphPurchAndUsers" : graphPurchasesAndUsers, "totalUsers": totalUsers, "totalPurchases": totalPurch,
            "algorithms": algorithms, "ctr": ctr, "ar@d": arad, "arpu@d": arpuad}

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


def getAlgortihms(abtest_id, dataset_id, startpoint, endpoint, stepsize):
    results = getResultIds(abtest_id, dataset_id)
    if results is None:
        return False

    algorithms = {}

    ctr = {}
    ard = {}
    argRevPr = {}
    for result in results:
        algo = getAlgorithm(abtest_id, result)
        algorithms[str(result)] = {"name": algo.name, "params": algo.params, "result_id": algo.result_id}
        ctr_, arad, argRev = getCTR(result, abtest_id, dataset_id, startpoint, endpoint, stepsize)
        ctr[result] = {"name": algo.name, "result_id": algo.result_id, "values": ctr_, "type": "CTR"}
        ard[result] = {"name": algo.name, "result_id": algo.result_id, "values": arad, "type": "AR@D"}
        argRevPr[result] = {"name": algo.name, "result_id": algo.result_id, "values": argRev, "type": "AR@D"}

    return algorithms, ctr, ard, argRevPr

def getCTR(result_id, abtest_id, dataset_id, startpoint, endpoint, stepsize):

    curDate = datetime.strptime(startpoint, "%Y-%m-%d")
    end = datetime.strptime(endpoint, "%Y-%m-%d")
    # print("oke")
    prevDate = curDate

    ctr = getClickThroughRate(startpoint, endpoint, abtest_id, result_id, dataset_id, stepsize)
    arad, arpuad = getAR_and_ARPU(7, startpoint, endpoint, abtest_id, result_id, dataset_id, int(stepsize))
    # while curDate <= end:
        # print("oke")
        # print(curDate)
        # res = getClickThroughRate(prevDate, curDate, abtest_id, result_id, dataset_id)
        # arad, avrgRev = getAR_and_ARPU(7, curDate, abtest_id, result_id, dataset_id)
        # ctr[str(curDate)[0:10]] = res
        # ard[str(curDate)[0:10]] = arad[0]
        # argRev[str(curDate)[0:10]] = avrgRev[0]
        # prevDate = curDate + timedelta(days=1)
        # curDate += stepsize

    return ctr, arad, arpuad