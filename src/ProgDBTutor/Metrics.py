from config import config_data
from db_connection import DBConnection
from user_data_acces import *

from datetime import datetime
from datetime import timedelta

from user_data_acces import *

connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])


# user_data_access = UserDataAcces(connection)


# METRIC: Purchases
def getNrOfPurchases(startDate, endDate):
    cursor = connection.get_cursor()

    # "SELECT count(*) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate)
    cursor.execute("SELECT count(*) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate))

    if cursor is None:
        return cursor
    return cursor.fetchone()[0]


# METRIC: Active Users
def getNrOfActiveUsers(startDate, endDate):
    cursor = connection.get_cursor()

    # "SELECT count(DISTINCT customer_id) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate)
    cursor.execute("SELECT count(DISTINCT customer_id) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;",
                   (startDate, endDate))

    if cursor is None:
        return cursor
    return cursor.fetchone()[0]


def getClickThroughRate(startDate, endDate, abtestID, resultID, datasetID, stepsize, algoName):
    cursor = connection.get_cursor()
    print("startctr")

    ctr = {}

    curDate = datetime.strptime(startDate, "%Y-%m-%d")
    end = datetime.strptime(endDate, "%Y-%m-%d")
    stepsize_ = timedelta(days=int(stepsize))

    while curDate <= end:

        # Bij elke stepsize hebben we een nieuwe recommendation dus bekijken we ook de ctr

        # Om het ons makkelijker te maken gaan we dit opslitsen in een geval waar we als algo pop of rec hebben of als algo itemknn
        if algoName != 'itemknn':
            date = str(curDate)[0:10]
            # bij recommendations is de stepsize gelijk aan het endpoint, we vragen dus eerst alle recommendations op
            cursor.execute(
                'select item_number from recommendation where dataset_id = %s and abtest_id = %s and result_id = %s and end_point = %s',
                (str(datasetID), str(abtestID), str(resultID), date))

            recommendations = cursor.fetchall()
            if recommendations is None:
                ctr[date] = 0
                continue

            # Nu gaan we alle interactions opvragen waar deze recommendations voor gedaan zijn
            cursor.execute(
                'select customer_id, item_id from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            # We vragen het aantal actieve gebruikers op
            cursor.execute(
                'select count(distinct customer_id) from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))

            activeUsers = int(cursor.fetchone()[0])

            dirInteraction = {}

            # We zetten alle aankopen samen per user
            for id, item in interactions:
                if id not in dirInteraction:
                    dirInteraction[id] = [item]
                else:
                    dirInteraction[id].append(item)

            count = 0

            # We gaan over alle interaction per gebruiker
            for id, items in dirInteraction.items():
                # We controleren of een van de gekochte items van de gebruiker in zijn recommendation zit
                if any(reco[0] in items for reco in recommendations):
                    # We doen de count omhoog
                    count += 1

            ctr[date] = round(count / activeUsers, 2)

        else:
            date = str(curDate)[0:10]

            # bij recommendations is de stepsize gelijk aan het endpoint, we vragen dus eerst alle recommendations op
            cursor.execute(
                'select customer_id, item_number from recommendation where dataset_id = %s and abtest_id = %s and result_id = %s and end_point = %s',
                (str(datasetID), str(abtestID), str(resultID), date))

            recommendations = cursor.fetchall()
            if recommendations is None:
                ctr[date] = 0
                continue

            # Nu gaan we alle interactions opvragen waar deze recommendations voor gedaan zijn
            cursor.execute(
                'select customer_id, item_id from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            # We vragen het aantal actieve users op
            cursor.execute(
                'select count(distinct customer_id) from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))

            activeUsers = int(cursor.fetchone()[0])

            dirInteraction = {}
            dirRecommendations = {}

            # We zetten alle items samen per customer id
            for id, item in interactions:

                if id not in dirInteraction:
                    dirInteraction[id] = [item]
                else:
                    dirInteraction[id].append(item)

            # We zetten alle recommendations samen per customer id
            for id, item in recommendations:

                if id not in dirRecommendations:
                    dirRecommendations[id] = [item]
                else:
                    dirRecommendations[id].append(item)

            count = 0

            # We lopen over de interactions
            for id, items in dirInteraction.items():

                # We controleren of de id bestaan in de recommendation
                if id in dirRecommendations:
                    # We controleren of de aankopen van de user in de recommendations zitten
                    if any(reco in items for reco in dirRecommendations[id]):
                        # Zit in zijn recommendation dus we doen de count + 1
                        count += 1

            ctr[date] = round(count / activeUsers, 2)

        curDate += stepsize_

    return ctr


def getAR_and_ARPU(days, startDate, endDate, abtestID, resultID, datasetID, stepSize, algoName):
    # hardcoded 7 or 30 days
    if days not in [7, 30]:
        days = 7

    cursor = connection.get_cursor()
    print("startAR"), print("startARPU")

    ar = {}
    arpu = {}

    curDate = datetime.strptime(startDate, "%Y-%m-%d")
    end = datetime.strptime(endDate, "%Y-%m-%d")
    stepsize_ = timedelta(days=int(stepSize))

    while curDate <= end:

        # Bij elke stepsize hebben we een nieuwe recommendation dus bekijken we ook de ctr

        # Om het ons makkelijker te maken gaan we dit opslitsen in een geval waar we als algo pop of rec hebben of als algo itemknn
        if algoName != 'itemknn':
            date = str(curDate)[0:10]
            _7days = str(curDate - timedelta(days=7))[0:10]

            # bij recommendations is de stepsize gelijk aan het endpoint, we vragen dus eerst alle recommendations op
            tempDate = curDate
            moveOn = False
            recommendations = []

            # ga over 7 dagen en zoek recommendations
            for i in range(7):

                cursor.execute(
                    'select item_number from recommendation where dataset_id = %s and abtest_id = %s and result_id = %s and end_point = %s',
                    (str(datasetID), str(abtestID), str(resultID), tempDate))

                # ga een dag lager
                tempDate = tempDate - timedelta(days=1)

                # kijk of er voor die dag recommendations bestaan
                _recommendations = cursor.fetchall()
                if _recommendations is None:
                    continue

                # voeg de recommendations voor die dag toe aan de lijst van alle recommendations
                moveOn = True
                for recommendation in _recommendations:
                    recommendations.append(recommendation[0])

            if not moveOn:
                ar[date] = 0
                arpu[date] = 0
                continue

            recommendations = list(set(recommendations))

            # Nu gaan we alle interactions opvragen waar deze recommendations voor gedaan zijn
            cursor.execute(
                'select customer_id, item_id, price from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepSize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            dirInteraction = {}

            # We zetten alle aankopen samen per user
            for id, item, price in interactions:
                if id not in dirInteraction:
                    dirInteraction[id] = [[item], [price]]
                else:
                    dirInteraction[id][0].append(item)
                    dirInteraction[id][1].append(price)

            count = 0
            price = 0
            nrOfInteractions = 0

            # ga over de items van alle users
            for id_, items in dirInteraction.items():
                nrOfInteractions += len(items[0])

                # ga over de items van 1 specifieke user
                for i in range(len(items[0])):
                    # als dat item gerecommend was, verhoog count en price
                    if items[0][i] in recommendations:
                        count += 1
                        price += items[1][i]

            ar[date] = round(count / nrOfInteractions, 2)
            arpu[date] = price / nrOfInteractions

        else:
            date = str(curDate)[0:10]
            _7days = str(curDate - timedelta(days=7))[0:10]

            # bij recommendations is de stepsize gelijk aan het endpoint, we vragen dus eerst alle recommendations op
            tempDate = curDate
            moveOn = False
            recommendations = []

            # ga over 7 dagen en zoek recommendations
            for i in range(7):

                cursor.execute(
                    'select customer_id, item_number from recommendation where dataset_id = %s and abtest_id = %s and result_id = %s and end_point = %s',
                    (str(datasetID), str(abtestID), str(resultID), tempDate))

                # ga een dag lager
                tempDate = tempDate - timedelta(days=1)

                # kijk of er voor die dag recommendations bestaan
                _recommendations = cursor.fetchall()
                if _recommendations is None:
                    continue

                # voeg de recommendations voor die dag toe aan de lijst van alle recommendations
                moveOn = True

                if _recommendations not in recommendations:
                    recommendations.append(_recommendations)

                # recommendations.append(_recommendations)

            if not moveOn:
                ar[date] = 0
                arpu[date] = 0
                continue

            # recommendations = list(set(recommendations))

            # Nu gaan we alle interactions opvragen waar deze recommendations voor gedaan zijn
            cursor.execute(
                'select customer_id, item_id, price from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepSize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            dirInteraction = {}
            dirRecommendations = {}

            # We zetten alle items samen per customer id
            for id, item, price in interactions:

                if id not in dirInteraction:
                    dirInteraction[id] = [[item], [price]]
                else:
                    dirInteraction[id][0].append(item)
                    dirInteraction[id][1].append(price)

            # er kunnen meerdere recommendation modellen zijn.
            for recom in recommendations:
                # print(recom)
                for id, item in recom:

                    if id not in dirRecommendations:
                        dirRecommendations[id] = [item]
                    else:
                        dirRecommendations[id].append(item)

            count = 0
            price = 0
            nrOfInteractions = 0

            # ga over alle items van alle users
            for id_, items in dirInteraction.items():
                nrOfInteractions += len(items[0])

                # kijk of er voor die user recommendations zijn
                if id_ in dirRecommendations:

                    # ga over de items van een specifieke user
                    for i in range(len(items[0])):

                        # als dat item gerecommend was, verhoog count en price
                        if items[0][i] in dirRecommendations[id_]:
                            count += 1
                            price += items[1][i]

            ar[date] = round(count / nrOfInteractions, 2)
            arpu[date] = price / nrOfInteractions

        curDate += stepsize_

    return ar, arpu


# def getAR_and_ARPU(days, startDate, endDate, abtestID, resultID, datasetID, stepSize, algoName):
#     # hardcoded 7 or 30 days
#     if days not in [7, 30]:
#         days = 7
#
#     startDate = str(startDate)[0:10]
#     endDate = str(endDate)[0:10]
#
#     cursor = connection.get_cursor()
#     print("startAR_ARPU")
#     intervalDates = []
#
#     # initial values: date2 is altijd voor date1
#     date1 = endDate
#     date2 = str(datetime.strptime(str(date1)[0:10], '%Y-%m-%d') - timedelta(days=days))[0:10]
#     _end = datetime.strptime(str(startDate)[0:10], '%Y-%m-%d') - timedelta(days=days)
#
#     while _end <= datetime.strptime(str(date2)[0:10], '%Y-%m-%d'):
#         intervalDates.append([date2, date1])
#
#         # update
#         date1 = str(datetime.strptime(str(date1)[0:10], '%Y-%m-%d') - timedelta(days=stepSize))[0:10]
#         date2 = str(datetime.strptime(str(date2)[0:10], '%Y-%m-%d') - timedelta(days=stepSize))[0:10]
#
#     # get all purchases that were recommended
#     cursor.execute(
#         'select i.t_dat, i.customer_id, i.item_id, i.price from interaction i where i.dataset_id = %s and i.t_dat between %s and %s and exists(select * from recommendation r where'
#         ' r.item_number = i.item_id and ( r.customer_id = i.customer_id  or r.customer_id = -1) and r.start_point < i.t_dat and i.t_dat <= r.end_point  and r.abtest_id = %s and r.result_id = %s and r.dataset_id = %s) '
#         'order by customer_id;',
#         (str(datasetID), str(startDate), str(endDate), str(abtestID), str(resultID), str(datasetID))
#     )
#     recommended_purchases = cursor.fetchall()
#
#     # get all purchases that were not recommended
#     cursor.execute(
#         'select i.t_dat, i.customer_id, i.item_id, i.price from interaction i where i.dataset_id = %s and i.t_dat between %s and %s and not exists(select * from recommendation r where'
#         ' r.item_number = i.item_id and ( r.customer_id = i.customer_id  or r.customer_id = -1) and r.start_point < i.t_dat and i.t_dat <= r.end_point  and r.abtest_id = %s and r.result_id = %s and r.dataset_id = %s) '
#         'order by i.customer_id, i.t_dat;',
#         (str(datasetID), str(startDate), str(endDate), str(abtestID), str(resultID), str(datasetID))
#     )
#     not_recommended_purchases = cursor.fetchall()
#
#     # {customer_id: [[item_id], [t_dat], [was_recommended], [price]]}
#     DATA = {}
#
#     for row in recommended_purchases:
#
#         # als entry nog niet bestaat -> maak een nieuwe entry
#         if row[1] not in DATA:
#             DATA[row[1]] = [[], [], [], []]
#
#         # voeg data toe aan de entry
#         DATA[row[1]][3].append(row[3])  # price
#         DATA[row[1]][0].append(row[2])  # item_id
#         DATA[row[1]][1].append(row[0])  # date
#         DATA[row[1]][2].append(True)  # bool: was_recommended
#
#     for row in not_recommended_purchases:
#
#         # als entry nog niet bestaat -> maak een nieuwe entry
#         if row[1] not in DATA:
#             DATA[row[1]] = [[], [], [], []]
#
#         # voeg data toe aan de entry
#         DATA[row[1]][3].append(0)  # price = 0 because not recommended
#         DATA[row[1]][0].append(row[2])  # item_id
#         DATA[row[1]][1].append(row[0])  # date
#         DATA[row[1]][2].append(False)  # bool: was_recommended
#
#     returnValue = []
#
#     for interval in intervalDates:
#         AR = 0
#         ARPU = 0
#         nrOfPurchases = 0
#
#         # ga over alle customers
#         for key, value in DATA.items():
#             # ga over de data van een bepaalde customer
#
#             for i in range(len(value[0])):
#                 t_dat = datetime.strptime(str(value[1][i])[0:10], '%Y-%m-%d')
#
#                 # als die customer een aankoop heeft binnen het interval -> doe er iets mee
#                 if datetime.strptime(str(interval[0])[0:10], '%Y-%m-%d') < t_dat <= datetime.strptime(
#                         str(interval[1])[0:10], '%Y-%m-%d'):
#                     nrOfPurchases += 1
#
#                     # als de item recommended was
#                     if value[2][i]:
#                         AR += 1
#                         ARPU += value[3][i]  # items[3] holds the price of the purchase
#
#         if nrOfPurchases != 0:
#             AR = AR / nrOfPurchases
#             ARPU = ARPU / nrOfPurchases
#
#         returnValue.append([interval, AR, ARPU])
#
#     """
#     returnValue is een lijst van lijsten.
#     in elke lijst zit op
#     index 0: het interval
#     index 1: de Attribution Rate voor dat interval
#     index 2: de Average Revenue Per User voor dat interval
#     """
#
#     arad = {}
#     arpuad = {}
#
#     returnValue.reverse()
#
#     for value in returnValue:
#         arad[value[0][1]] = round(value[1], 2)
#         arpuad[value[0][1]] = value[2]
#
#     # print(arad)
#     # print(arpuad)
#
#     return arad, arpuad
