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


def getClickThroughRate(startDate, endDate, abtestID, resultID, datasetID):
    if startDate is None and endDate is None:
        startDate = start
        endDate = end

    cursor = connection.get_cursor()

    startDate = str(startDate)[0:10]
    endDate = str(endDate)[0:10]

    print(endDate, abtestID, resultID, datasetID)

    cursor.execute('select distinct customer_id from interaction where t_dat between %s and %s limit 2;',
                   (str(startDate), str(endDate)))
    rows = cursor.fetchall()
    if rows is None:
        return None

    for row in rows:
        print(row[0])
        cursor.execute(
            "select item_number from recommendation where ( abtest_id = %s and result_id = %s and dataset_id = %s and (customer_id = -1 or customer_id = %s) and start_point < %s and %s <= end_point);",
            (str(abtestID), str(resultID), str(datasetID), str(row[0]), str(endDate), str(endDate)))

        print(cursor.query)
        recos = cursor.fetchall()
        print(recos)
        # for reco in recos:
        #     print(reco)
        print('\n')

    # """
    # voor elke ACTIEVE consumer: kijk of die in die tijdsperiode minstens 1 aankoop hebben gemaakt die ook
    # recommended was. Stel dat consumer 1, 5 dingen kocht, en minstens 1 daarvan is van de recommendation
    # dan zet je de CTR voor die user op 1.
    # """
    # # NUMBER OF ACTIVE USERS WHO BOUGHT AT LEAST 1 RECOMMENDED ITEM
    # # TODO make sure R1 is the Recommendation we want to test by making WHERE some_id = some_other_id -> OK NOW
    # cursor.execute(
    #     "CREATE VIEW Active_Users AS SELECT DISTINCT I1.customer_id FROM Interaction I1 WHERE t_dat BETWEEN %s AND %s ; \
    #      CREATE VIEW Recommendations AS SELECT DISTINCT R1.item_number FROM Recommendation R1 WHERE R1.abtest_id = %s \
    #     and R1.result_id = %s and R1.dataset_id = %s and R1.start_point = %s and R1.end_point = %s; \
    #         SELECT count(DISTINCT I.customer_id) FROM Interaction I \
    #     WHERE I.customer_id IN (SELECT * FROM Active_Users) AND I.item_id IN (SELECT * FROM Recommendations) AND I.t_dat BETWEEN %s AND %s ; \
    #      DROP VIEW Active_Users ; \
    #      DROP VIEW Recommendations ; ",
    #     (startDate, endDate, abtestID, resultID, datasetID, startDate, endDate, startDate, endDate))
    #
    # if cursor is None:
    #     return 0
    # query1 = cursor.fetchone()[0]
    #
    # # NUMBER OF ALL ACTIVE USERS
    # query2 = getNrOfActiveUsers(startDate, endDate)
    #
    # # can't divide by None or by 0
    # if query2 is None or query2 == 0:
    #     return 0
    #
    # # Click Through Rate = query1 / query2
    # CTR = query1 / query2
    # return CTR


def getAttributionRate(days, endDate, abtestID, resultID, datasetID):
    # hardcoded 7 or 30 days
    if days not in [7, 30]:
        days = 7

    startDate = str(datetime.strptime(endDate, '%Y-%m-%d') - timedelta(days=days))

    cursor = connection.get_cursor()

    """
    voor elke ACTIEVE consumer: kijk of die in die tijdsperiode aankopen hebben gemaakt die ook 
    recommended waren. Stel dat consumer 1, 5 dingen kocht, en 1 daarvan is van de recommendation
    dan zet je de Attribution Rate voor die user op 1/5  
    """
    # NUMBER OF PURCHASES WHERE ITEM WAS RECOMMENDED
    # TODO make sure R1 is the Recommendation we want to test by making WHERE some_id = some_other_id
    cursor.execute(
        "CREATE VIEW Recommendations AS SELECT DISTINCT R1.item_number FROM Recommendation R1 WHERE R1.abtest_id = %s \
        and R1.result_id = %s and R1.dataset_id = %s and R1.start_point = %s and R1.end_point = %s; \
        SELECT count(I.item_id) FROM Interaction I WHERE I.item_id in (SELECT * FROM Recommendations) AND I.t_dat BETWEEN %s AND %s ; \
        DROP VIEW Recommendations ; ",
        (abtestID, resultID, datasetID, startDate, endDate, startDate, endDate))

    if cursor is None:
        return 0
    query1 = cursor.fetchone()[0]

    # NUMBER OF ALL PURCHASES
    cursor.execute(
        "SELECT count(I.item_id) FROM Interaction I WHERE I.t_dat BETWEEN %s AND %s ;",
        (startDate, endDate))

    if cursor is None:
        return 0
    query2 = cursor.fetchone()[0]

    # can't divide by None or by 0
    if query2 is None or query2 == 0:
        return 0

    # Attribution Rate = query1 / query2
    AR = query1 / query2
    return AR


def getAverageRevenuePerUser(days, endDate, abtestID, resultID, datasetID):
    # hardcoded 7 or 30 days
    if days not in [7, 30]:
        days = 7

    startDate = str(datetime.strptime(endDate, '%Y-%m-%d') - timedelta(days=days))

    cursor = connection.get_cursor()

    """
    Voor elke aankoop die is gemaakt en die ook in de top k recommended zat, vraag de prijs op en tel
    prijzen van al die items bij elkaar op
    """
    # SUM OF PRICES OF ALL ITEMS BOUGHS WHERE ITEM WAS ALSO RECOMMENDED
    # TODO make sure R1 is the Recommendation we want to test by making WHERE some_id = some_other_id
    cursor.execute("CREATE VIEW Recommendations AS SELECT DISTINCT R1.item_number FROM Recommendation R1 WHERE R1.abtest_id = %s \
        and R1.result_id = %s and R1.dataset_id = %s and R1.start_point = %s and R1.end_point = %s; \
        SELECT sum(I.price) FROM Interaction I WHERE I.item_id in (SELECT * FROM Recommendations) AND I.t_dat BETWEEN %s AND %s ; \
         DROP VIEW Recommendations ; ",
                   (abtestID, resultID, datasetID, startDate, endDate, startDate, endDate))

    if cursor is None:
        return 0
    query1 = cursor.fetchone()[0]

    query2 = getNrOfActiveUsers(startDate, endDate)

    # can't divide by None or by 0
    if query2 is None or query2 == 0:
        return 0

    # Average Revenue Per User = query1 / query2
    ARPU = query1 / query2
    return ARPU


nrOfPurchases = getNrOfPurchases(start, end)
print(nrOfPurchases)

nrOfActiveUsers = getNrOfActiveUsers(start, end)
print(nrOfActiveUsers)

# CTR = test.getClickThroughRate(start, end, 1, 1, 1)
# print(CTR)

# AR = test.getAttributionRate(start, end, 1, 1, 1)
# print(AR)

# ARPU = test.getAverageRevenuePerUser(start, end, 1, 1, 1)
# print(ARPU)
