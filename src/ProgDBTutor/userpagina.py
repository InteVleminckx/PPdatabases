from user_data_acces import *
import datetime

def getUserInformation(abtest_id, dataset_id, user_id):
    algoritmes = getAlgoritmes(abtest_id)
    startAB, endAB = getAbInterval(abtest_id)
    historyUser = getPurchases(user_id, dataset_id, startAB, endAB)
    recommendationsPerInterval = getRecommendations(abtest_id, dataset_id, user_id)
    colors = ["#9FE3FE", "#9CD0FE", "#9DBEFE", "#9CB5FE", "#9CB5FE", "#C2A5FF", "#D69DFF", "#DF9BFD", "#ED9BEB", "#F49CD3",
             "#FEABB1", "#FECF9F", "#F7FCA8", "#D3FFA7", "#BEFEC4", "#BEFEC4"]

    maxcolor = len(colors)

    recosSort = []
    for key in recommendationsPerInterval:
        recosSort.append(key)

    recosSort.sort(key=lambda date: datetime.datetime.strptime(date[0], '%Y-%m-%d'))
    colorCount = 0
    gesorteerdeRecommendations = []
    it = 0
    for algoritme in algoritmes:
        resultCount = 0
        for reco in recosSort:
            if algoritme["result_id"] == reco[1]:
                if it == 0:
                    gesorteerdeRecommendations.append([[algoritme["name"], colors[colorCount], reco[0], recommendationsPerInterval[reco]]])
                else:
                    if resultCount > len(gesorteerdeRecommendations)-1:
                        gesorteerdeRecommendations.append(
                            [[algoritme["name"], colors[colorCount], reco[0], recommendationsPerInterval[reco]]])
                    else:
                        gesorteerdeRecommendations[resultCount].append([algoritme["name"], colors[colorCount], reco[0], recommendationsPerInterval[reco]])
                resultCount += 1

        colorCount += 1
        if colorCount == maxcolor:
            colorCount = 0
        it = 1

    historyUserAndRec = []
    for reco in gesorteerdeRecommendations:
        ls = []
        for item in historyUser:
            breaked = False
            for algo in reco:
                if str(item) in algo[3]:
                    ls.append([str(item), True])
                    breaked = True
                    break

            if not breaked:
                ls.append([str(item), False])

        historyUserAndRec.append(ls)

    for reco in gesorteerdeRecommendations:
        for i in range(len(reco)):
            cur = reco[i][3]
            new = []
            items = []
            for j in range(len(cur)):
                items.append(cur[j])
                if (j+1) % 3 == 0:
                    new.append(items)
                    items = []
            if len(items) > 0:
                new.append(items)
            reco[i][3] = new

    return gesorteerdeRecommendations, historyUserAndRec, startAB + " — " + endAB

def getAlgoritmes(abtest_id):
    cursor = dbconnect.get_cursor()

    cursor.execute("select result_id, name from algorithm where abtest_id = %s group by result_id, name;",
                   (str(abtest_id)))
    algoritmes = []
    rows = cursor.fetchall()

    if rows is None:
        return None

    for row in rows:
        algoritmes.append({"name": row[1], "result_id": row[0]})

    return algoritmes


def getAbInterval(abtest_id):
    cursor = dbconnect.get_cursor()

    cursor.execute("select start_point, end_point from abtest where abtest_id = %s limit 1;", (str(abtest_id)))
    interval = cursor.fetchone()
    if interval is None:
        return None

    start = str(interval[0])[0:10]
    end = str(interval[1])[0:10]
    return start, end


def getPurchases(user_id, dataset_id, start, end):
    cursor = dbconnect.get_cursor()
    cursor.execute(
        "select item_id from interaction where dataset_id = %s and customer_id = %s and t_dat between %s and %s;",
        (str(dataset_id), str(user_id), str(start), str(end)))
    rows = cursor.fetchall()
    items = []

    if rows is None:
        return None

    for row in rows:
        items.append(row[0])

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

    for interval in intervals:
        recosPerInterval[(str(interval[1])[0:10], interval[0])] = []

    for recommendation in recommendations:
        recosPerInterval[(str(recommendation[2])[0:10], recommendation[0])].append(str(recommendation[1]))

    return recosPerInterval
