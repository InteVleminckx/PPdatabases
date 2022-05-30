# from config import config_data
# from db_connection import DBConnection
# from user_data_acces import *

from datetime import datetime
# from datetime import timedelta

from user_data_acces import *

# Metrics are separated from other queries, so we need to connect to the database here
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])


# METRIC: Purchases
def getNrOfPurchases(startDate, endDate):
    """
    :return: number of purchases made from {startDate} to {endDate}
    """
    cursor = connection.get_cursor()
    cursor.execute("SELECT count(*) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;", (startDate, endDate))

    if cursor is None:
        return cursor
    return cursor.fetchone()[0]


# METRIC: Active Users
def getNrOfActiveUsers(startDate, endDate):
    """
    Active users are users who bought at least 1 item in the interval
    :return: number of active users made from {startDate} to {endDate}
    """
    cursor = connection.get_cursor()
    cursor.execute("SELECT count(DISTINCT customer_id) FROM Interaction WHERE t_dat BETWEEN %s AND %s ;",
                   (startDate, endDate))

    if cursor is None:
        return cursor
    return cursor.fetchone()[0]


def getClickThroughRate(startDate, endDate, abtestID, algorithmID, datasetID, stepsize, algoName):
    """
    Generate the CTR for each step for the entire ABTest
    :precondition: The Algorithms must have run
    :return: a Dictionary with {key=date, value=CTR for that date}
    """
    cursor = connection.get_cursor()
    print("startctr")

    ctr = {}

    # gather information about the time interval
    curDate = datetime.strptime(startDate, "%Y-%m-%d")
    end = datetime.strptime(endDate, "%Y-%m-%d")
    stepsize_ = timedelta(days=int(stepsize))

    # For each stepsize, we have a new recommendation so we also generate a new CTR
    # To make it easier, we split the CTR in 2 (popularity + recency) and (itemknn)
    while curDate <= end:

        # Popularity or Recency
        if algoName != 'itemknn':
            date = str(curDate)[0:10]

            # There are recommendations for each stepsize so we can just request them from the database
            cursor.execute(
                'select item_number from recommendation where dataset_id = %s and abtest_id = %s and algorithm_id = %s and end_point = %s',
                (str(datasetID), str(abtestID), str(algorithmID), date))

            # get recommendations, if there aren't any, then the CTR will be 0 for that day
            recommendations = cursor.fetchall()
            if recommendations is None:
                ctr[date] = 0
                continue

            # Now request all interactions from the same interval as the recommendation
            cursor.execute(
                'select customer_id, item_id from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            # Now request all active users, again in that same interval
            cursor.execute(
                'select count(distinct customer_id) from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))

            activeUsers = int(cursor.fetchone()[0])

            # save all interactions
            dirInteraction = {}

            # save the interactions in a Dict like this {key=customer_id, value=list(purchases)}
            for id, item in interactions:
                if id not in dirInteraction:
                    dirInteraction[id] = [item]
                else:
                    dirInteraction[id].append(item)

            # count holds the amount of users that bought at least 1 recommendation
            count = 0

            # Loop over all pruchases of the user
            for id, items in dirInteraction.items():
                # Check if any of the purchases in also recommended
                if any(reco[0] in items for reco in recommendations):
                    # if so, we increase the count
                    count += 1

            # the ctr for that day will be the number of users who bought a recommendation
            # divided by the total amount of active users (in that time interval)
            ctr[date] = round(count / activeUsers, 2)

        # ItemKNN
        else:
            date = str(curDate)[0:10]

            # There are recommendations for each stepsize so we can just request them from the database
            cursor.execute(
                'select customer_id, item_number from recommendation where dataset_id = %s and abtest_id = %s and algorithm_id = %s and end_point = %s',
                (str(datasetID), str(abtestID), str(algorithmID), date))

            # get recommendations, if there aren't any, then the CTR will be 0 for that day
            recommendations = cursor.fetchall()
            if recommendations is None:
                ctr[date] = 0
                continue

            # Now request all interactions from the same interval as the recommendation
            cursor.execute(
                'select customer_id, item_id from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            # Now request all active users, again in that same interval
            cursor.execute(
                'select count(distinct customer_id) from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepsize) - 1)))[0:10]))

            activeUsers = int(cursor.fetchone()[0])

            # Since ItemKNN works with recommendations specific for users,
            # save the interactions separately from the recommendations
            # Both dictionaries will have the key=customer_id so we can do a very fast check
            # to see if a recommendation was bought or not
            dirInteraction = {}
            dirRecommendations = {}

            # Insert items in the dict {key=customer_id, value=list(purchases)}
            for id, item in interactions:

                if id not in dirInteraction:
                    dirInteraction[id] = [item]
                else:
                    dirInteraction[id].append(item)

            # Insert items in the dict {key=customer_id, value=list(recommendations)}
            for id, item in recommendations:

                if id not in dirRecommendations:
                    dirRecommendations[id] = [item]
                else:
                    dirRecommendations[id].append(item)

            # count holds the amount of users that bought at least 1 recommendation
            count = 0

            # Loop over all Purchases
            for id, items in dirInteraction.items():
                # Check if there are recommendations for a certain user
                if id in dirRecommendations:
                    # Check if the user bought at least 1 recommendation
                    if any(reco in items for reco in dirRecommendations[id]):
                        # If so, increase the count by 1
                        count += 1

            # the ctr for that day will be the number of users who bought a recommendation
            # divided by the total amount of active users (in that time interval)
            ctr[date] = round(count / activeUsers, 2)

        curDate += stepsize_

    return ctr


def getAR_and_ARPU(days, startDate, endDate, abtestID, algorithmID, datasetID, stepSize, algoName):
    """
    Generate the Attribution Rate and the Average Revenue per User in the same function
    We do this to avoid a lot of code duplication
    :return: 2 Dictionary's with {key=date, value=AR/ARPU for that date}
    """

    # hardcoded 7 or 30 days
    if days not in [7, 30]:
        days = 7

    cursor = connection.get_cursor()
    print("startAR"), print("startARPU")

    ar = {}
    arpu = {}

    # gather information about the time interval
    curDate = datetime.strptime(startDate, "%Y-%m-%d")
    end = datetime.strptime(endDate, "%Y-%m-%d")
    stepsize_ = timedelta(days=int(stepSize))

    # loop over the ABTest
    while curDate <= end:

        # Popularity or Recency
        if algoName != 'itemknn':
            date = str(curDate)[0:10]
            _7days = str(curDate - timedelta(days=7))[0:10]

            # initialize useful values
            tempDate = curDate
            moveOn = False
            recommendations = []

            # go over {days} days and find all recommendations. This is needed because recommendations aren't
            # per stepsize here size D is hardcoded to 7 or 30 and the stepsize doesn't need to be either of that
            for i in range(days):

                cursor.execute(
                    'select item_number from recommendation where dataset_id = %s and abtest_id = %s and algorithm_id = %s and end_point = %s',
                    (str(datasetID), str(abtestID), str(algorithmID), tempDate))

                tempDate = tempDate - timedelta(days=1)

                # Check if there are recommendations for that day and if so, add them to the list
                _recommendations = cursor.fetchall()
                if _recommendations is None:
                    continue

                moveOn = True
                for recommendation in _recommendations:
                    recommendations.append(recommendation[0])

            # if no recommendations are found at all for the last {days} days, don't proceed
            if not moveOn:
                ar[date] = 0
                arpu[date] = 0
                continue

            recommendations = list(set(recommendations))

            # If there are recommendations, we request the interactions over the same interval
            cursor.execute(
                'select customer_id, item_id, price from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepSize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            dirInteraction = {}

            # Make a Dict for the interactions {key=customer_id, value=list( list(items) , list(prizes) )}
            for id, item, price in interactions:
                if id not in dirInteraction:
                    dirInteraction[id] = [[item], [price]]
                else:
                    dirInteraction[id][0].append(item)
                    dirInteraction[id][1].append(price)

            count = 0
            price = 0
            nrOfInteractions = 0

            # Loop over all interactions
            for id_, items in dirInteraction.items():
                nrOfInteractions += len(items[0])

                # Loop over the purchases of a specific user
                for i in range(len(items[0])):
                    # If it was recommended, increase count by 1 and price by whatever the price of the item is
                    if items[0][i] in recommendations:
                        count += 1
                        price += items[1][i]

            # AR is the number of recommended items bought divided by all purchases
            # ARPU is the price of all recommended items bought divided by all purchases
            ar[date] = round(count / nrOfInteractions, 2)
            arpu[date] = price / nrOfInteractions

        # ItemKNN
        else:
            date = str(curDate)[0:10]
            _7days = str(curDate - timedelta(days=7))[0:10]

            # initialize useful values
            tempDate = curDate
            moveOn = False
            recommendations = []

            # go over {days} days and find all recommendations. This is needed because recommendations aren't
            # per stepsize here size D is hardcoded to 7 or 30 and the stepsize doesn't need to be either of that
            for i in range(days):

                cursor.execute(
                    'select customer_id, item_number from recommendation where dataset_id = %s and abtest_id = %s and algorithm_id = %s and end_point = %s',
                    (str(datasetID), str(abtestID), str(algorithmID), tempDate))

                tempDate = tempDate - timedelta(days=1)

                # Check if there are recommendations for that day and if so, add them to the list
                _recommendations = cursor.fetchall()
                if _recommendations is None:
                    continue

                moveOn = True

                if _recommendations not in recommendations:
                    recommendations.append(_recommendations)

            # if no recommendations are found at all for the last {days} days, don't proceed
            if not moveOn:
                ar[date] = 0
                arpu[date] = 0
                continue

            # If there are recommendations, we request the interactions over the same interval
            cursor.execute(
                'select customer_id, item_id, price from interaction where dataset_id = %s and t_dat between %s and %s',
                (str(datasetID), date, str(curDate + (timedelta(days=int(stepSize) - 1)))[0:10]))
            interactions = cursor.fetchall()

            # make 2 seperate Dict's for the interactions and for the recommendations
            # with as key=customer_id
            dirInteraction = {}
            dirRecommendations = {}

            # Make a Dict for the interactions {key=customer_id, value=list( list(items) , list(prizes) )}
            for id, item, price in interactions:
                if id not in dirInteraction:
                    dirInteraction[id] = [[item], [price]]
                else:
                    dirInteraction[id][0].append(item)
                    dirInteraction[id][1].append(price)

            # Save the recommendations in a Dict but Loop over all models first
            for recom in recommendations:
                for id, item in recom:
                    if id not in dirRecommendations:
                        dirRecommendations[id] = [item]
                    else:
                        dirRecommendations[id].append(item)

            count = 0
            price = 0
            nrOfInteractions = 0

            # Loop over all interactions
            for id_, items in dirInteraction.items():
                nrOfInteractions += len(items[0])

                # Check if there are recommendations for a certain user
                if id_ in dirRecommendations:

                    # Loop over the items of the user
                    for i in range(len(items[0])):

                        # If a recommended item was also bought, increase count+price
                        if items[0][i] in dirRecommendations[id_]:
                            count += 1
                            price += items[1][i]

            # AR is the number of recommended items bought divided by all purchases
            # ARPU is the price of all recommended items bought divided by all purchases
            ar[date] = round(count / nrOfInteractions, 2)
            arpu[date] = price / nrOfInteractions

        curDate += stepsize_

    return ar, arpu

"""Function that returns the amount of recommendation days based the start and end date and the stepsize"""
def amountRecommendationDays(startPoint, endPoint, stepsize):
    amount = 0
    while startPoint <= endPoint:
        amount += 1
        startPoint += stepsize
    return amount
