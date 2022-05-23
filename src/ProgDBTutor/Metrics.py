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
    # startDate = str(startDate)[0:10]
    # endDate = str(endDate)[0:10]

    # print(endDate, abtestID, resultID, datasetID)

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

    cursor.execute('select t_dat, customer_id, item_id from interaction where t_dat between %s and %s and dataset_id = %s;',
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

                    ctrCount += count_/actv_cus

                start += timedelta(days=1)

            ctr[str(curDate)[0:10]] = (round(ctrCount/int(stepsize),2))

        else:
            date = str(curDate)[0:10]
            actv_cus = 1
            if date in info_recommendation:
                actv_cus = len(info_interactions[date])
                for customer, items in info_interactions[date].items():
                    #We controleren eerst of de de user al in de recommendations zit, zoja check de items nog
                    #Moeten ook nog de datum controleren
                    if date in info_recommendation:
                        if str(customer) in info_recommendation[date]:
                            #nu nog de items controleren
                            for item in items:
                                if str(item) in info_recommendation[date][str(customer)]:
                                    ctrCount += 1

            ctr[date] = (round(ctrCount/actv_cus, 2))

        curDate += stepsize_

    return ctr
    

def getAR_and_ARPU(days, endDate, abtestID, resultID, datasetID):
    return (0, 0), (0, 0)

    # hardcoded 7 or 30 days
    if days not in [7, 30]:
        days = 7

    startDate = str(datetime.strptime(str(endDate)[0:10], '%Y-%m-%d') - timedelta(days=days))[0:10]
    endDate = str(endDate)[0:10]

    cursor = connection.get_cursor()

    # customer_id's of all active customers from interval [startDate+1 , endDate] (geen dubbele startDate's)
    cursor.execute("SELECT DISTINCT i.customer_id FROM Interaction i \
                        WHERE i.t_dat BETWEEN %s AND %s",
                   (str(startDate), str(endDate)))

    if cursor is None:
        return None
    customerIDs = cursor.fetchall()

    # returnList[0] is de ARPU voor alle users
    # returnList[1] is een dict met als keys de customer id en values de ARPU voor een user
    returnARPU = [0, {}]
    returnAR = [0, {}]

    for ID in customerIDs:
        # print(abtestID, resultID, datasetID, startDate, endDate, ID[0])
        # geef het aantal voorgestelde aankopen van die user over het interval
        cursor.execute("SELECT r1.item_number FROM Recommendation r1 \
                            WHERE r1.abtest_id = %s AND r1.result_id = %s AND r1.dataset_id = %s \
                            AND r1.start_point < %s AND r1.end_point >= %s \
                            AND (r1.customer_id = %s OR r1.customer_id = -1); ",
                       (str(abtestID), str(resultID), str(datasetID), str(startDate), str(endDate), str(ID[0])))

        recommendations = cursor.fetchall()

        # geef het aantal aankopen van die user over het interval + prijs van elke aankoop
        cursor.execute("SELECT i.item_id, i.price FROM Interaction i \
                            WHERE i.customer_id = %s AND i.dataset_id = %s AND i.t_dat BETWEEN %s AND %s; ",
                       (str(ID[0]), str(datasetID), str(startDate), str(endDate)))

        purchases = cursor.fetchall()

        customer_ARPU = 0
        customer_AR = 0
        # print(purchases, recommendations)
        for row in purchases:
            for reco in recommendations:
                if row[0] == reco[0]:
                    customer_ARPU += row[1]
                    customer_AR += 1

        # getal tussen 0 en 1
        customer_ARPU = customer_ARPU / len(purchases)
        customer_AR = customer_AR / len(purchases)

        returnARPU[1][ID[0]] = customer_ARPU
        returnAR[1][ID[0]] = customer_AR

    # calculate general values
    ARPU = 0

    for key, value in returnARPU[1].items():
        ARPU += returnARPU[1][key]
    ARPU = ARPU / len(returnARPU[1])

    returnARPU[0] = ARPU

    AR = 0

    for key, value in returnAR[1].items():
        AR += returnAR[1][key]
    AR = round(AR / len(returnAR[1]), 2)

    returnAR[0] = AR

    return returnAR, returnARPU

# nrOfPurchases = getNrOfPurchases(start, end)
# print(nrOfPurchases)
#
# nrOfActiveUsers = getNrOfActiveUsers(start, end)
# print(nrOfActiveUsers)

# CTR = test.getClickThroughRate(start, end, 1, 1, 1)
# print(CTR)

# AR = test.getAttributionRate(start, end, 1, 1, 1)
# print(AR)

# ARPU = test.getAverageRevenuePerUser(start, end, 1, 1, 1)
# print(ARPU)
