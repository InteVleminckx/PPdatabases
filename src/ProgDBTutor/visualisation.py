# import datetime
import json

from flask import request, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os
from user_data_acces import *
from Metrics import *
import sys

def getInfoVisualisationPage(abtest_id, dataset_id):
    cursor = dbconnect.get_cursor()
    cursor.execute("select start_point, end_point, stepsize, topk from abtest where abtest_id = %s limit 1;",
                   (str(abtest_id),))
    row = cursor.fetchone()

    if row is None:
        return None

    startPoint = str(row[0])[0:10]
    endPoint = str(row[1])[0:10]
    stepsize = str(row[2])
    topk = str(row[3])

    datasetName = getDatasetname(dataset_id)
    graphPurchasesAndUsers, totalUsers, totalPurch = getPurchasesAndActiveUsersOverTime(startPoint, endPoint)

    algorithms, ctr, arad, arpuad = getAlgorithms(abtest_id, dataset_id, startPoint, endPoint, stepsize)

    return {"abtest_id": abtest_id, "dataset_id": dataset_id,"startpoint": startPoint, "endpoint": endPoint, "datasetname": datasetName,
            "stepsize": stepsize, "topk": topk, "graphPurchAndUsers": graphPurchasesAndUsers, "totalUsers": totalUsers,
            "totalPurchases": totalPurch,
            "algorithms": algorithms, "ctr": ctr, "ar@d": arad, "arpu@d": arpuad}


def getPurchasesAndActiveUsersOverTime(start, end):
    cursor = dbconnect.get_cursor()
    cursor.execute(
        "select count(distinct customer_id), count(*), t_dat from interaction where t_dat between %s and %s group by t_dat order by t_dat;",
        (str(start), str(end)))

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


def getAlgorithms(abtest_id, dataset_id, startpoint, endpoint, stepsize):
    algorithmIDs = getAlgorithmIds(abtest_id, dataset_id)
    if algorithmIDs is None:
        return False

    algorithms = {}

    ctr = {}
    ard = {}
    argRevPr = {}
    for algorithmID in algorithmIDs:
        algo = getAlgorithm(abtest_id, algorithmID)
        algorithms[str(algorithmID)] = {"name": algo.name, "params": algo.params, "algorithm_id": algo.algorithm_id}
        ctr_, arad, argRev = getCTR(algorithmID, abtest_id, dataset_id, startpoint, endpoint, stepsize, algo.name)
        ctr[algorithmID] = {"name": algo.name, "algorithm_id": algo.algorithm_id, "values": ctr_, "type": "CTR"}
        ard[algorithmID] = {"name": algo.name, "algorithm_id": algo.algorithm_id, "values": arad, "type": "AR@D"}
        argRevPr[algorithmID] = {"name": algo.name, "algorithm_id": algo.algorithm_id, "values": argRev, "type": "ARPU@D"}

    return algorithms, ctr, ard, argRevPr


def getCTR(algorithm_id, abtest_id, dataset_id, startpoint, endpoint, stepsize, algoName):
    ctr = getClickThroughRate(startpoint, endpoint, abtest_id, algorithm_id, dataset_id, stepsize, algoName)
    arad, arpuad = getAR_and_ARPU(7, startpoint, endpoint, abtest_id, algorithm_id, dataset_id, int(stepsize), algoName)
    return ctr, arad, arpuad


def getTopkMostRecommendItemsPerAlgo(start, end, dataset_id, topk, abtest_id):
    algorithmIDs = getAlgorithmIds(abtest_id, dataset_id)
    if start == "":
        abtest = getAB_Test(abtest_id)
        start, end = str(abtest.start_point)[0:10], str(abtest.end_point)[0:10]

    topkReco = {}
    cursor = dbconnect.get_cursor()
    cursor.execute("select name from Names where dataset_id = %s and table_name = %s;", (str(dataset_id), 'articles'))
    name = cursor.fetchone()[0]
    names = []

    for algorithmID in algorithmIDs:
        recommendations = []
        algorithm = getAlgorithm(abtest_id, algorithmID)
        cursor.execute(
            "select item_number, count(item_number) from recommendation where abtest_id = %s and algorithm_id = %s and end_point between %s and %s group by item_number order by count(item_number) desc limit %s",
            (str(abtest_id), str(algorithmID), str(start), str(end), str(topk)))

        rows = cursor.fetchall()
        for row in rows:
            cursor.execute("select a1.val from Articles a1 where a1.attribute = %s and a1.dataset_id = %s and a1.item_number in "
                           "(select a2.item_number from Articles a2 where attribute = %s and val = %s)",
                           (name, str(dataset_id), 'article_id', str(row[0])))
            temp = cursor.fetchone()
            if temp:
                names.append(temp[0])

        # For popularity or recency we have to look at each day and compute the nr of active users
        if algorithm.name == 'popularity' or algorithm.name == 'recency':
            startPoint = datetime.strptime(start, '%Y-%m-%d')
            endPoint = datetime.strptime(end, '%Y-%m-%d')
            stepsize = timedelta(days=1)
            counter_rows = [0] * len(rows)

            # Loop over all the days
            while startPoint <= endPoint:
                nrActiveUsers = getNumberOfActiveUsers(dataset_id, startPoint)
                for i in range(len(rows)):
                    cursor.execute(
                        "select item_number, count(item_number) from recommendation where abtest_id = %s and algorithm_id = %s and end_point = %s and item_number = %s group by item_number order by count(item_number)",
                        (str(abtest_id), str(algorithmID), startPoint, str(rows[i][0]))
                    )
                    amount = cursor.fetchone()
                    if amount:
                        # This determines the amount we need to add to the current counter of the item
                        counter_rows[i] += amount[1] * nrActiveUsers
                startPoint += stepsize

            for j in range(len(rows)):
                recommendations.append({"item": str(rows[j][0]), "count": str(counter_rows[j]), "name": names[j]})

        elif algorithm.name == 'itemknn':
            for j in range(len(rows)):
                recommendations.append({"item": str(rows[j][0]), "count": str(rows[j][1]), "name": names[j]})

        topkReco[algorithmID] = {"name": algorithm.name, "algorithmID": algorithm.algorithm_id, "recommendations": recommendations}

    return topkReco


def getTopkMostPurchasedItems(start, end, dataset_id, topk, abtest_id):
    if start == "":
        abtest = getAB_Test(abtest_id)
        start, end = str(abtest.start_point)[0:10], str(abtest.end_point)[0:10]

    cursor = dbconnect.get_cursor()

    cursor.execute("select name from Names where dataset_id = %s and table_name = %s;", (str(dataset_id), 'articles'))
    name = cursor.fetchone()[0]
    names = []

    cursor.execute(
        "SELECT item_id, COUNT(item_id) FROM Interaction WHERE dataset_id = %s AND t_dat BETWEEN %s AND %s "
        "GROUP BY item_id ORDER BY COUNT(item_id) DESC LIMIT %s;", (str(dataset_id), start, end, str(topk)))

    purchases = []
    rows = cursor.fetchall()

    for row in rows:
        cursor.execute(
            "select a1.val from Articles a1 where a1.attribute = %s and a1.dataset_id = %s and a1.item_number in "
            "(select a2.item_number from Articles a2 where attribute = %s and val = %s)",
            (name, str(dataset_id), 'article_id', str(row[0])))
        temp = cursor.fetchone()
        if temp:
            names.append(temp[0])

    for i in range(len(rows)):
        purchases.append({'item': rows[i][0], 'count': rows[i][1], 'name': names[i]})

    return purchases


def getNumberUniqueActiveUsers(list_users):
    return len(list_users)


def getTotaleRevenue(start, end, dataset_id, abtest_id):
    if start == "":
        abtest = getAB_Test(abtest_id)
        start, end = str(abtest.start_point)[0:10], str(abtest.end_point)[0:10]

    cursor = dbconnect.get_cursor()

    cursor.execute(
        "select sum(price) from interaction where dataset_id = %s and t_dat between %s and %s",
        (str(dataset_id), str(start), str(end)))

    price = cursor.fetchone()[0]

    return str(round(float(price), 2))


def getListOfActiveUsers(start, end, dataset_id, abtest_id):
    if start == "":
        abtest = getAB_Test(abtest_id)
        start, end = str(abtest.start_point)[0:10], str(abtest.end_point)[0:10]

    cursor = dbconnect.get_cursor()

    cursor.execute(
        "select distinct customer_id from interaction where dataset_id = %s and t_dat between %s and %s",
        (str(dataset_id), str(start), str(end)))

    users = cursor.fetchall()
    userCount = getNumberUniqueActiveUsers(users)

    userInformation_ = []
    userInformation = {}
    for user in users:
        # totalPurch = getUsersTotalPurchases(dataset_id, user[0], cursor)
        # purchOverTime = getUsersPurchasesOverTime(start, end, dataset_id, user[0], cursor)
        # userCTR = getUsersCTR(start, end, dataset_id, user[0], cursor, abtest_id)
        userInformation[str(user[0])] = {"totalePurchases": 0, "purchasesOverTime": 0, "CTR": 0}

    userInformation = getUsersTotalPurchases(dataset_id, start, end, userInformation, cursor)
    userInformation = getUsersPurchasesOverTime(start, end, dataset_id, cursor, userInformation)
    userInformation = getUsersCTR(start, end, dataset_id, userInformation, cursor, abtest_id)

    sort0 = dict(sorted(userInformation.items(), key=lambda item: int(item[0]), reverse=False))
    userInformation_.append([key for key in sort0])

    sort1 = dict(sorted(userInformation.items(), key=lambda item: item[1]["totalePurchases"], reverse=True))
    userInformation_.append([key for key in sort1])

    sort2 = dict(sorted(userInformation.items(), key=lambda item: item[1]["purchasesOverTime"], reverse=True))
    userInformation_.append([key for key in sort2])

    sort3 = dict(sorted(userInformation.items(), key=lambda item: item[1]["CTR"], reverse=True))
    userInformation_.append([key for key in sort3])

    return userInformation, userInformation_, userCount


def getUsersTotalPurchases(dataset_id, start, end, userInformation, cursor):

    cursor.execute(
        "select count(i1.customer_id), i1.customer_id from interaction i1 where i1.dataset_id = %s and i1.customer_id "
        "in( select i2.customer_id from interaction i2 where i2.dataset_id = %s and i2.t_dat between %s and %s) group by customer_id;",
        (str(dataset_id), str(dataset_id), str(start), str(end)))

    purchases = cursor.fetchall()

    for purch in purchases:
        userInformation[str(purch[1])]["totalePurchases"] = int(purch[0])

    return userInformation


def getUsersPurchasesOverTime(start, end, dataset_id, cursor, userInformation):

    cursor.execute(
        "select count(i1.customer_id), i1.customer_id from interaction i1 where i1.dataset_id = %s and i1.t_dat between %s and %s and i1.customer_id "
        "in( select i2.customer_id from interaction i2 where i2.dataset_id = %s and i2.t_dat between %s and %s) group by customer_id;",
        (str(dataset_id), str(start), str(end), str(dataset_id), str(start), str(end)))

    purchases = cursor.fetchall()

    for purch in purchases:
        userInformation[str(purch[1])]["purchasesOverTime"] = int(purch[0])

    return userInformation


def getUsersCTR(start, end, dataset_id, userinformation, cursor, abtest_id):
    abtest = getAB_Test(abtest_id)
    curDate = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    stepsize_ = timedelta(days=int(abtest.stepsize))
    recommendationsCount = 0

    while curDate <= end:

        # Bij elke stepsize hebben we een nieuwe recommendation dus bekijken we ook de ctr
        recommendationsCount += 1

        date = str(curDate)[0:10]

        # bij recommendations is de stepsize gelijk aan het endpoint, we vragen dus eerst alle recommendations op
        cursor.execute(
            'select customer_id, item_number from recommendation where dataset_id = %s and abtest_id = %s and end_point = %s',
            (str(dataset_id), str(abtest_id), date))

        recommendations = cursor.fetchall()
        if recommendations is None:
            continue

        # Nu gaan we alle interactions opvragen waar deze recommendations voor gedaan zijn
        cursor.execute(
            'select customer_id, item_id from interaction where dataset_id = %s and t_dat between %s and %s',
            (str(dataset_id), date, str(curDate + (timedelta(days=int(abtest.stepsize) - 1)))[0:10]))
        interactions = cursor.fetchall()

        dirInteraction = {}
        dirRecommendations = {}

        # We zetten alle items samen per customer id
        for id, item in interactions:

            if id not in dirInteraction:
                dirInteraction[str(id)] = [item]
            else:
                dirInteraction[str(id)].append(item)

        # We zetten alle recommendations samen per customer id
        for id, item in recommendations:

            if id not in dirRecommendations:
                dirRecommendations[str(id)] = [item]
            else:
                dirRecommendations[str(id)].append(item)

        # We lopen over de interactions
        for id, items in dirInteraction.items():

            # We controleren of de id bestaan in de recommendation
            if id in dirRecommendations:
                # We controleren of de aankopen van de user in de recommendations zitten
                if any(reco in items for reco in dirRecommendations[id]):
                    # Zit in zijn recommendation dus we doen de count + 1
                    userinformation[str(id)]["CTR"] += 1
                    break
            else:
                if "-1" in dirRecommendations:
                    if any(reco in items for reco in dirRecommendations["-1"]):
                        # Zit in zijn recommendation dus we doen de count + 1
                        userinformation[str(id)]["CTR"] += 1
                        break

        curDate += timedelta(days=1)

    for id, values in userinformation.items():
        values["CTR"] = round(values["CTR"] / recommendationsCount, 2)

    # print(userinformation)
    return userinformation
