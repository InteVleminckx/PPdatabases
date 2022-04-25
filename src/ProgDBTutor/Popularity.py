"""
SELECT article_id, COUNT(article_id)
FROM purchases t
WHERE t.t_date between '2020-01-01' and '2020-01-18'
GROUP BY article_id
ORDER BY COUNT(article_id) DESC
LIMIT 2;
"""
# from app import user_data_access

import datetime

#TODO: Deze imports mogen later weg, we kunnen de import van app.py hiervoor dan gebruiken
# Had deze staan omdat ik dan enkel deze file kon runnen zonder afhankelijk te zijn van de app.py
from config import config_data
from db_connection import DBConnection
from user_data_acces import UserDataAcces
connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])
user_data_access = UserDataAcces(connection)

class Popularity:

    def __init__(self, dataset_id, startPoint, endPoint, stepsize, topk, window, retrainInterval):
        self.startPoint = datetime.date(*self.getdate(startPoint))
        self.endPoint = enddate = datetime.date(*self.getdate(endPoint))
        self.stepsize = datetime.timedelta(days=stepsize)
        self.topk = topk
        self.window = datetime.timedelta(days=window)
        self.retrainInterval = datetime.timedelta(days=retrainInterval)
        self.currentDate = self.startPoint
        self.recommendations = dict()
        self.dataset_id = dataset_id

    def simulate(self):
        nextRetrainInterval = self.currentDate
        while self.currentDate <= self.endPoint:
            if self.currentDate >= nextRetrainInterval:
                self.train()
                nextRetrainInterval += self.retrainInterval

            self.currentDate += self.stepsize

    def recommend(self):
        self.simulate()

    def train(self):
        trainWindow = (str(self.currentDate-self.window), str(self.currentDate))
        recommendations = user_data_access.getPopularity(self.dataset_id, *trainWindow, self.topk)
        if recommendations is not None:
            list_ = []
            for item_id, number_purchases in recommendations:
                list_.append(item_id)

        #TODO: niet vergeten dat dit moet worden toegevoegd worden aan de recommendations van een user
            self.recommendations[trainWindow] = list_


        #TODO: Van wat ik er van denk is dat we een volledige AB test moeten opslagen per user
        # Maar ook dat telkens elke keer een topk wordt berekent binnen de windowsize deze opgeslagen moet worden per use

    def getdate(self, date):

        year, month, day = "", "", ""

        first, second = True, False

        for letter in date:
            if first and not second:
                if letter == '-':
                    second = True
                else:
                    year += letter

            elif first and second:
                if letter == "-":
                    second = False
                    first = False
                else:
                    month += letter

            else:
                day += letter

        return int(year), int(month), int(day)

def main():

    algo = Popularity(0, "2022-03-01", "2022-05-01", 1, 5, 14, 7)
    algo.recommend()
    print("")

main()