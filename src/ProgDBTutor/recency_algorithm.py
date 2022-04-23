from config import config_data
from db_connection import DBConnection

connection = DBConnection(dbname=config_data['dbname'], dbuser=config_data['dbuser'])


class Recency:

    def __init__(self, dbconnect, _start, _end, K: int, stepSize: int):
        self.top_k = K
        self.stepSize = stepSize
        self.start = _start
        self.end = _end
        self.db = dbconnect

    def getData(self):
        cursor = self.db.get_cursor()

        # expected date format: YYYY-MM-DD HH:MM:SS
        # selects the item_id between the interval and only selects the first k items
        topK_items = cursor.execute(f"SELECT item_id FROM Interaction WHERE t_dat BETWEEN {self.interval_start} AND {self.interval_end} ORDER BY t_dat ASC LIMIT {self.top_k}")





