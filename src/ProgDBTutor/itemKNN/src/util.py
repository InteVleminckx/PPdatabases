import pandas as pd


def parse_interactions(path, user_col: str, item_col: str):
    """ Creates list of tuples (user, item) for interactions in csv dataset.
    Only to be used for debugging, not in application (fetch interactions from database) """
    interactions = pd.read_csv(path, usecols=[user_col, item_col])
    A = list(zip(interactions[user_col], interactions[item_col]))
    return A
