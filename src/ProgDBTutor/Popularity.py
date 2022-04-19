"""
SELECT article_id, COUNT(article_id)
FROM purchases t
WHERE t.t_date between '2020-01-01' and '2020-01-18'
GROUP BY article_id
ORDER BY COUNT(article_id) DESC
LIMIT 2;
"""
import datetime


class Popularity:

    def __init__(self, begin, end, stepsize, topk, retrainInterval, window):
        self.begin = begin
        self.end = end
        self.stepsize = stepsize
        self.topk = topk
        self.retrainInterval = retrainInterval
        self.window = window
        self.recommendations = list()

    def train(self, curDate):

        # we gaan opnieuw data verzamelen binnen de window size
        startWindow = curDate - datetime.timedelta(days=self.window)

        """
        Doe het volgende:
            Neem het volgende uit de database
             SELECT *
             FROM purchases
             WHERE t_date between startWindow and curDate
            
            Slaag deze data opnieuw op in de database (in een andere table)
            
            training is gedaan en kunnen weer verder gaan
            
            We gaan nu alle recommendations bekijken voor dit window 
        """
        self.getRecommedation(startWindow, curDate)

    def getRecommedation(self, startWindow, curDate):

        delta = datetime.timedelta(days=self.stepsize)

        while (startWindow <= curDate):
            print(startWindow, end="\n")

            startWindow += delta
            """
            hier gaan we dan telkens de top k berekenen voor de huidige stepsize
            """

            startStep = startStep - startWindow

            """SELECT article_id, COUNT(article_id)
            FROM tabel_waar_alle_recommendations_in_komen_van_het_training_interval t
            WHERE t.t_date between startStep and startWindow
            GROUP BY article_id
            ORDER BY COUNT(article_id) DESC
            LIMIT self.topk;
            
            Deze top k gaan we dan ook weer telkens opslagen zodat we dit later kunnen gebruiken voor visualisatie 
            """

    def recommend(self):

        startdate = datetime.date(*self.getdate(self.begin))
        enddate = datetime.date(*self.getdate(self.end))
        delta = datetime.timedelta(days=self.stepsize)

        retrainCounter = 0

        # We lopen van het begin tot het einde over de dates
        while (startdate <= enddate):
            # Dan gaan we een
            print(startdate, end="\n")

            if self.retrainInterval == retrainCounter:
                self.train(startdate)
                retrainCounter = 0


            retrainCounter += 1
            startdate += delta

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

    algo = Popularity("2020-11-12", "2020-11-13", 1, 5, 7, 14)
    algo.recommend()

main()