from config import config_data
from db_connection import DBConnection
from user_data_acces import *

from datetime import datetime
from datetime import timedelta

from user_data_acces import *

connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
# user_data_access = UserDataAcces(connection)


"""TEST"""
start = "2020-01-01 20:00:00"
end = "2020-02-01 20:00:00"


# METRIC: Purchases
def getNrOfPurchases(startDate=None, endDate=None):
    if startDate is None and endDate is None:
        startDate = start
        endDate = end

    cursor = connection.get_cursor()

    # "SELECT count(*) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate)
    cursor.execute("SELECT count(*) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate))

    if cursor is None:
        return cursor
    return cursor.fetchone()[0]


# METRIC: Active Users
def getNrOfActiveUsers(startDate=None, endDate=None):
    if startDate is None and endDate is None:
        startDate = start
        endDate = end

    cursor = connection.get_cursor()

    # "SELECT count(DISTINCT customer_id) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate)
    cursor.execute("SELECT count(DISTINCT customer_id) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;",
                   (startDate, endDate))

    if cursor is None:
        return cursor
    return cursor.fetchone()[0]


def getClickThroughRate(startDate, endDate, abtestID, resultID, datasetID, stepsize):
    cursor = connection.get_cursor()
    print("startctr")

    cursor.execute(
        'select i.t_dat, i.customer_id, i.item_id from interaction i where i.dataset_id = %s and i.t_dat between %s and %s and exists(select * from recommendation r where'
        ' r.item_number = i.item_id and ( r.customer_id = i.customer_id  or r.customer_id = -1) and r.start_point < i.t_dat and i.t_dat <= r.end_point  and r.abtest_id = %s and r.result_id = %s and r.dataset_id = %s) '
        'order by customer_id;',
        (str(datasetID), str(startDate), str(endDate), str(abtestID), str(resultID), str(datasetID))
    )

    interactions = cursor.fetchall()

    info_recommendation = {}

    for interaction in interactions:
        if str(interaction[0])[0:10] not in info_recommendation:
            info_recommendation[str(interaction[0])[0:10]] = {}

        if str(interaction[1]) not in info_recommendation[str(interaction[0])[0:10]]:
            info_recommendation[str(interaction[0])[0:10]][str(interaction[1])] = []

        info_recommendation[str(interaction[0])[0:10]][str(interaction[1])].append(str(interaction[2]))

    # print(info_recommendation)

    cursor.execute(
        'select t_dat, customer_id, item_id from interaction where t_dat between %s and %s and dataset_id = %s;',
        (str(startDate), str(endDate), str(datasetID)))

    interactions = cursor.fetchall()

    info_interactions = {}

    for interaction in interactions:
        if str(interaction[0])[0:10] not in info_interactions:
            info_interactions[str(interaction[0])[0:10]] = {}

        if str(interaction[1]) not in info_interactions[str(interaction[0])[0:10]]:
            info_interactions[str(interaction[0])[0:10]][str(interaction[1])] = []

        info_interactions[str(interaction[0])[0:10]][str(interaction[1])].append(str(interaction[2]))

    # print(info_interactions)

    ctr = {}

    curDate = datetime.strptime(startDate, "%Y-%m-%d")
    end = datetime.strptime(endDate, "%Y-%m-%d")
    stepsize_ = timedelta(days=int(stepsize))

    while curDate <= end:

        ctrCount = 0
        if int(stepsize) > 1:

            start = curDate - stepsize_

            while start <= curDate:
                count_ = 0
                date = str(start)[0:10]
                if date in info_recommendation:
                    actv_cus = len(info_interactions[date])
                    for customer, items in info_interactions[date].items():
                        # We controleren eerst of de de user al in de recommendations zit, zoja check de items nog
                        # Moeten ook nog de datum controleren
                        if date in info_recommendation:
                            if str(customer) in info_recommendation[date]:
                                # nu nog de items controleren
                                for item in items:
                                    if str(item) in info_recommendation[date][str(customer)]:
                                        count_ += 1

                    ctrCount += count_ / actv_cus

                start += timedelta(days=1)

            ctr[str(curDate)[0:10]] = (round(ctrCount / int(stepsize), 2))

        else:
            date = str(curDate)[0:10]
            actv_cus = 1
            if date in info_recommendation:
                actv_cus = len(info_interactions[date])
                for customer, items in info_interactions[date].items():
                    # We controleren eerst of de de user al in de recommendations zit, zoja check de items nog
                    # Moeten ook nog de datum controleren
                    if date in info_recommendation:
                        if str(customer) in info_recommendation[date]:
                            # nu nog de items controleren
                            for item in items:
                                if str(item) in info_recommendation[date][str(customer)]:
                                    ctrCount += 1

            ctr[date] = (round(ctrCount / actv_cus, 2))

        curDate += stepsize_

    return ctr


def getAR_and_ARPU(days, startDate, endDate, abtestID, resultID, datasetID, stepSize):
    # hardcoded 7 or 30 days
    if days not in [7, 30]:
        days = 7

    startDate = str(startDate)[0:10]
    endDate = str(endDate)[0:10]

    cursor = connection.get_cursor()
    print("startander")
    intervalDates = []

    # initial values: date2 is altijd voor date1
    date1 = endDate
    date2 = str(datetime.strptime(str(date1)[0:10], '%Y-%m-%d') - timedelta(days=days))[0:10]
    _end = datetime.strptime(str(startDate)[0:10], '%Y-%m-%d') - timedelta(days=days)

    while _end <= datetime.strptime(str(date2)[0:10], '%Y-%m-%d'):
        intervalDates.append([date2, date1])

        # update
        date1 = str(datetime.strptime(str(date1)[0:10], '%Y-%m-%d') - timedelta(days=stepSize))[0:10]
        date2 = str(datetime.strptime(str(date2)[0:10], '%Y-%m-%d') - timedelta(days=stepSize))[0:10]

    # returnList[0] is de ARPU voor alle users
    # returnList[1] is een dict met als keys de customer id en values de ARPU voor een user
    returnARPU = [0, {}]
    returnAR = [0, {}]

    cursor.execute(
        'select i.t_dat, i.customer_id, i.item_id, i.price from interaction i where i.dataset_id = %s and i.t_dat between %s and %s and exists(select * from recommendation r where'
        ' r.item_number = i.item_id and ( r.customer_id = i.customer_id  or r.customer_id = -1) and r.start_point < i.t_dat and i.t_dat <= r.end_point  and r.abtest_id = %s and r.result_id = %s and r.dataset_id = %s) '
        'order by customer_id;',
        (str(datasetID), str(startDate), str(endDate), str(abtestID), str(resultID), str(datasetID))
    )
    recommended_purchases = cursor.fetchall()

    cursor.execute(
        'select i.t_dat, i.customer_id, i.item_id, i.price from interaction i where i.dataset_id = %s and i.t_dat between %s and %s and not exists(select * from recommendation r where'
        ' r.item_number = i.item_id and ( r.customer_id = i.customer_id  or r.customer_id = -1) and r.start_point < i.t_dat and i.t_dat <= r.end_point  and r.abtest_id = %s and r.result_id = %s and r.dataset_id = %s) '
        'order by i.customer_id, i.t_dat;',
        (str(datasetID), str(startDate), str(endDate), str(abtestID), str(resultID), str(datasetID))
    )
    not_recommended_purchases = cursor.fetchall()

    # {customer_id: [[item_id], [t_dat], [was_recommended], [price]]}
    DATA = {}

    for row in recommended_purchases:

        # als entry nog niet bestaat -> maak een nieuwe entry
        if row[1] not in DATA:
            DATA[row[1]] = [[], [], [], []]

        # voeg data toe aan de entry
        DATA[row[1]][3].append(row[3])  # price
        DATA[row[1]][0].append(row[2])  # item_id
        DATA[row[1]][1].append(row[0])  # date
        DATA[row[1]][2].append(True)  # bool: was_recommended

    for row in not_recommended_purchases:

        # als entry nog niet bestaat -> maak een nieuwe entry
        if row[1] not in DATA:
            DATA[row[1]] = [[], [], [], []]

        # voeg data toe aan de entry
        DATA[row[1]][3].append(0)  # price = 0 because not recommended
        DATA[row[1]][0].append(row[2])  # item_id
        DATA[row[1]][1].append(row[0])  # date
        DATA[row[1]][2].append(False)  # bool: was_recommended

    returnValue = []

    for interval in intervalDates:
        AR = 0
        ARPU = 0
        nrOfPurchases = 0

        # ga over alle customers
        for key, value in DATA.items():
            # ga over de data van een bepaalde customer

            for i in range(len(value[0])):
                t_dat = datetime.strptime(str(value[1][i])[0:10], '%Y-%m-%d')

                # als die customer een aankoop heeft binnen het interval -> doe er iets mee
                if datetime.strptime(str(interval[0])[0:10], '%Y-%m-%d') < t_dat <= datetime.strptime(
                        str(interval[1])[0:10], '%Y-%m-%d'):
                    nrOfPurchases += 1

                    # als de item recommended was
                    if value[2][i]:
                        AR += 1
                        ARPU += value[3][i]  # items[3] holds the price of the purchase

        if nrOfPurchases != 0:
            AR = AR / nrOfPurchases
            ARPU = ARPU / nrOfPurchases

        returnValue.append([interval, AR, ARPU])

    """
    returnValue is een lijst van lijsten.
    in elke lijst zit op 
    index 0: het interval
    index 1: de Attribution Rate voor dat interval
    index 2: de Average Revenue Per User voor dat interval
    """

    arad = {}
    arpuad = {}

    returnValue.reverse()

    for value in returnValue:
        arad[value[0][1]] = round(value[1], 2)
        arpuad[value[0][1]] = value[2]

    # print(arad)
    # print(arpuad)

    return arad, arpuad