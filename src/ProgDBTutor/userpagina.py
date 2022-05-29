import json

from user_data_acces import *
import datetime


def getUserInformation(abtest_id, dataset_id, user_id):
    """
    This function tries to obtain all the inforation for a user
    :param abtest_id: the ABTest id for which we need the information
    :param dataset_id: the id of the data to which the user belongs
    :param user_id: the user from the dataset
    :return: json objects that hold all the relevant information
    """

    algoritmes = getAlgoritmes(abtest_id)
    startAB, endAB, steps, topk = getAbInterval(abtest_id)
    historyUser = getPurchases(user_id, dataset_id, startAB, endAB)
    recommendationsPerInterval = getRecommendations(abtest_id, dataset_id, user_id)
    colors = ['#9FE3FE', '#9CD0FE', '#9DBEFE', '#9CB5FE', '#9CB5FE', '#C2A5FF', '#D69DFF', '#DF9BFD', '#ED9BEB',
              '#F49CD3',
              '#FEABB1', '#FECF9F', '#F7FCA8', '#D3FFA7', '#BEFEC4', '#BEFEC4']

    maxcolor = len(colors)
    colorsID = {}
    ids_algoritmes = set()

    for key in recommendationsPerInterval:
        ids_algoritmes.add(key[1])

    # We gaan per stepsize de recommendations groeperen, we doen de "simulatie" na te bootsen
    # We intend to group the recommendations per stepsize, essentially 'simulating' the simulation
    startDate = datetime.datetime.strptime(startAB, "%Y-%m-%d")
    endDate = datetime.datetime.strptime(endAB, "%Y-%m-%d")
    stepsize = datetime.timedelta(days=steps)
    simulationStep = datetime.timedelta(days=1)

    recommendations = {}
    history = {}
    purchases = {}
    dates = []
    nextRecommend = startDate
    itemsPerStep = []

    colorCount = 0

    # Loop over the entire simulation
    while startDate <= endDate:

        # First thing we do is group all the purchases for the user for this current stepsize
        date = str(startDate)[0:10]

        if date in historyUser:
            itemsPerStep.extend(historyUser[date])
        if startDate == nextRecommend:

            # Now that we have all the purchases for a user, we need to check for each algorithm
            # whether a purchased item was in this list
            history[date] = list()
            recommendations[date] = list()
            purchases[date] = list()
            dates.append(date)
            print("enter")
            for algorithm_id in ids_algoritmes:
                if date in historyUser:
                    for item in itemsPerStep:
                        if (date, algorithm_id) in recommendationsPerInterval:
                            for recItems in recommendationsPerInterval[(date, algorithm_id)]:
                                if str(item[0]) == str(recItems[0]):
                                    breaked = False
                                    for item_ in history[date]:
                                        if item_["name"] == str(item[1]):
                                            item_["purchased"] = True
                                            breaked = True
                                            break
                                    if not breaked:
                                        history[date].append(
                                            {"name": str(item[1]), "purchased": True, "url": str(item[2]), "item_id": str(item[0])})
                                else:
                                    breaked = False
                                    for item_ in history[date]:
                                        if item_["name"] == str(item[1]):
                                            breaked = True
                                            break
                                    if not breaked:
                                        history[date].append(
                                            {"name": str(item[1]), "purchased": False, "url": str(item[2]), "item_id": str(item[0])})

                if (date, algorithm_id) in recommendationsPerInterval:
                    recos = recommendationsPerInterval[(date, algorithm_id)]
                    name = algoritmes[algorithm_id]
                    recos_ = [item[1] for item in recos]
                    recommendations[date].append({"name": name, "algorithm_id": algorithm_id, "recommendations": recos,
                                                  "color": colors[colorCount % len(colors)]})
                    count = 0
                    for reco in recos:
                        for item in itemsPerStep:
                            if str(reco[0]) == str(item[0]):
                                count += 1
                                print("oke")
                    purchases[date].append({"name": name, "count": count, "color": colors[colorCount % len(colors)]})

                else:
                    name = algoritmes[algorithm_id]
                    recommendations[date].append({"name": name, "algorithm_id": algorithm_id, "recommendations": [],
                                                  "color": colors[colorCount % len(colors)]})
                    purchases[date].append({"name": name, "count": 0, "color": colors[colorCount % len(colors)]})

                colorCount += 1

            itemsPerStep = []
            nextRecommend += stepsize
            colorCount = 0

        startDate += simulationStep

    jsPur = json.dumps(purchases)
    jsReco = json.dumps(recommendations)
    jsHistory = json.dumps(history)
    jsDates = json.dumps(dates)
    topk_ = []
    for i in range(topk + 1):
        topk_.append(i)
    jsTopk = json.dumps(topk_)

    print(jsReco)
    print(jsHistory)
    print(startAB)
    print(endAB)
    print(jsPur)
    print(jsTopk)
    print(jsDates)

    return jsReco, jsHistory, startAB + " — " + endAB, jsPur, jsTopk, jsDates


def getAlgoritmes(abtest_id):
    """
    Function to get all Algorithms that are used in the ABTest
    :return: all algorithms
    """
    cursor = dbconnect.get_cursor()

    cursor.execute("select algorithm_id, name from algorithm where abtest_id = %s group by algorithm_id, name;",
                   (str(abtest_id),))
    algoritmes = {}
    rows = cursor.fetchall()

    if rows is None:
        return None

    for row in rows:
        algoritmes[row[0]] = row[1]
        # algoritmes.append({"name": row[1], "algorithm_id": row[0]})

    return algoritmes


def getAbInterval(abtest_id):
    """
    Obtain all the information regarding the interval, stepsize and top k for the ABTest
    :return: a tuple of the information
    """
    cursor = dbconnect.get_cursor()

    cursor.execute("select start_point, end_point, stepsize, topk from abtest where abtest_id = %s limit 1;",
                   (str(abtest_id),))
    interval = cursor.fetchone()
    if interval is None:
        return None

    start = str(interval[0])[0:10]
    end = str(interval[1])[0:10]
    stepsize = interval[2]
    topk = interval[3]
    return start, end, stepsize, topk


def getPurchases(user_id, dataset_id, start, end):
    """
    Get all purchases that a user made between an interval (the name of the pictures)
    :return: list of all the picture names that the user bought
    """
    cursor = dbconnect.get_cursor()
    cursor.execute(
        "select item_id, t_dat from interaction where dataset_id = %s and customer_id = %s and t_dat between %s and %s;",
        (str(dataset_id), str(user_id), str(start), str(end)))
    rows = cursor.fetchall()

    if rows is None:
        return None

    cursor.execute("select name from names where dataset_id = %s and table_name = 'articles';", (str(dataset_id),))
    name = cursor.fetchone()[0]
    if name is None:
        return None

    items = {}
    rows = list(set(rows))

    for row in rows:
        item = getItem(row[0], dataset_id).attributes
        val = ""
        if "image_url" in item:
            val = item["image_url"]
        name_ = item[name]
        if str(row[1])[0:10] not in items:
            items[str(row[1])[0:10]] = [(row[0], name_, val)]
        else:
            items[str(row[1])[0:10]].append((row[0], name_, val))

    return items


def getRecommendations(abtest_id, dataset_id, customer_id):
    """
    Get all the recommendations for the users (the name of the pictures)
    :return: list of all the picture names for the recommended items
    """
    cursor = dbconnect.get_cursor()
    cursor.execute(
        "select algorithm_id, item_number, end_point from recommendation where abtest_id = %s and dataset_id = %s and (customer_id = -1 or customer_id = %s);",
        (str(abtest_id), str(dataset_id), str(customer_id)))
    recommendations = cursor.fetchall()
    cursor.execute(
        "select algorithm_id, end_point from recommendation where abtest_id = %s and dataset_id = %s and (customer_id = -1 or customer_id = %s) group by algorithm_id, end_point;",
        (str(abtest_id), str(dataset_id), str(customer_id)))
    intervals = cursor.fetchall()
    recosPerInterval = dict()

    if recommendations is None:
        return None

    cursor.execute("select name from names where dataset_id = %s and table_name = 'articles';", (str(dataset_id),))
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
