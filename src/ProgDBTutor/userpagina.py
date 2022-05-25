import json

from user_data_acces import *
import datetime

def getUserInformation(abtest_id, dataset_id, user_id):
    algoritmes = getAlgoritmes(abtest_id)
    startAB, endAB, steps, topk = getAbInterval(abtest_id)
    historyUser = getPurchases(user_id, dataset_id, startAB, endAB)
    recommendationsPerInterval = getRecommendations(abtest_id, dataset_id, user_id)
    colors = ['#9FE3FE', '#9CD0FE', '#9DBEFE', '#9CB5FE', '#9CB5FE', '#C2A5FF', '#D69DFF', '#DF9BFD', '#ED9BEB', '#F49CD3',
             '#FEABB1', '#FECF9F', '#F7FCA8', '#D3FFA7', '#BEFEC4', '#BEFEC4']

    maxcolor = len(colors)
    colorsID = {}
    recosSort = {}

    for key in recommendationsPerInterval:
        if key[1] in recosSort:
            recosSort[key[1]].append(key[0])
        else:
            recosSort[key[1]] = [key[0]]
    j = 1
    for key in recosSort:
        recosSort[key].sort()
        recosSort[key].reverse()
        colorsID[j] = colors[(j-1)%maxcolor]
        j += 1

    # We gaan per stepsize de recommendations groeperen, we doen de "simulatie" na te bootsen
    startDate = datetime.datetime.strptime(startAB, "%Y-%m-%d")
    endDate = datetime.datetime.strptime(endAB, "%Y-%m-%d")
    stepsize = datetime.timedelta(days=steps)

    recommendations = []
    history = []
    purchases = []

    while startDate <= endDate:
        colorCount = 0
        stepReco = []
        hisUser = [None] * len(historyUser)
        purch = {}

        for reco in recosSort:
            for date in recosSort[reco]:
                if startDate < datetime.datetime.strptime(date, "%Y-%m-%d"):
                    continue
                else:
                    reco_ = recommendationsPerInterval[(date, reco)]
                    name = algoritmes[reco]
                    recosname = [item[1] for item in reco_]
                    stepReco.append({"name": name, "date": str(startDate)[0:10], "recommendations" : recosname, "result_id": reco, "color": colorsID[reco]})

                    for i, his in enumerate(historyUser):
                        if (name, reco) not in purch:
                            purch[(name, reco)] = [0, colorsID[reco]]
                        if [str(his[0]), his[2]] in reco_:

                            purch[(name, reco)][0] += 1
                            hisUser[i] = {"item": str(his[2]), "url": his[1], "purchased":True}
                        else:
                            if hisUser[i] is None:
                                hisUser[i] = {"item": str(his[2]), "url": his[1], "purchased": False}
                    break

            colorCount += 1
            if colorCount == maxcolor:
                colorCount = 0

        stepReco.sort(key=lambda x:x["result_id"])
        recommendations.append(stepReco)
        history.append(hisUser)
        purch = dict(sorted(purch.items(), key=lambda x:x[0][1]))
        purch_ = []
        for pur in purch:
            purch_.append([pur[0], purch[pur][0], purch[pur][1]])
        purchases.append(purch_)
        startDate += stepsize


    jsPur = json.dumps(purchases)
    jsReco = json.dumps(recommendations)
    jsHistory = json.dumps(history)
    topk_ = []
    for i in range(topk+1):
        topk_.append(i)
    jsTopk = json.dumps(topk_)
    return jsReco, jsHistory, startAB + " — " + endAB, jsPur, jsTopk

def getAlgoritmes(abtest_id):
    cursor = dbconnect.get_cursor()

    cursor.execute("select result_id, name from algorithm where abtest_id = %s group by result_id, name;",
                   (str(abtest_id),))
    algoritmes = {}
    rows = cursor.fetchall()

    if rows is None:
        return None

    for row in rows:
        algoritmes[row[0]] = row[1]
        # algoritmes.append({"name": row[1], "result_id": row[0]})

    return algoritmes


def getAbInterval(abtest_id):
    cursor = dbconnect.get_cursor()

    cursor.execute("select start_point, end_point, stepsize, topk from abtest where abtest_id = %s limit 1;", (str(abtest_id),))
    interval = cursor.fetchone()
    if interval is None:
        return None

    start = str(interval[0])[0:10]
    end = str(interval[1])[0:10]
    stepsize = interval[2]
    topk = interval[3]
    return start, end, stepsize, topk


def getPurchases(user_id, dataset_id, start, end):
    cursor = dbconnect.get_cursor()
    cursor.execute(
        "select item_id from interaction where dataset_id = %s and customer_id = %s and t_dat between %s and %s;",
        (str(dataset_id), str(user_id), str(start), str(end)))
    rows = cursor.fetchall()
    items = []

    if rows is None:
        return None

    cursor.execute("select name from names where dataset_id = %s and table_name = 'articles';",(str(dataset_id),))
    name = cursor.fetchone()[0]
    if name is None:
        return None
    for row in rows:
        item = getItem(row[0], dataset_id).attributes
        val = ""
        if "image_url" in item:
            val = item["image_url"]
        name_ = item[name]
        items.append([row[0], val, name_])

    return items


def getRecommendations(abtest_id, dataset_id, customer_id):
    cursor = dbconnect.get_cursor()
    cursor.execute(
        "select result_id, item_number, end_point from recommendation where abtest_id = %s and dataset_id = %s and (customer_id = -1 or customer_id = %s);",
        (str(abtest_id), str(dataset_id), str(customer_id)))
    recommendations = cursor.fetchall()
    cursor.execute(
        "select result_id, end_point from recommendation where abtest_id = %s and dataset_id = %s and (customer_id = -1 or customer_id = %s) group by result_id, end_point;",
        (str(abtest_id), str(dataset_id), str(customer_id)))
    intervals = cursor.fetchall()
    recosPerInterval = dict()

    if recommendations is None:
        return None

    cursor.execute("select name from names where dataset_id = %s and table_name = 'articles';",(str(dataset_id),))
    name = cursor.fetchone()[0]
    if name is None:
        return None

    for interval in intervals:
        recosPerInterval[(str(interval[1])[0:10], interval[0])] = []

    for recommendation in recommendations:
        item = getItem(recommendation[1], dataset_id).attributes
        name_ = item[name]
        recosPerInterval[(str(recommendation[2])[0:10], recommendation[0])].append([str(recommendation[1]), name_])

    return recosPerInterval
