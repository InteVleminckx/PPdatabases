from typing import List, Tuple

import numpy as np
import scipy.sparse


class Algorithm:
    """ Base class for recommendation algorithms """
    def fit(self, X: scipy.sparse.csr_matrix):
        """ The actual training of the algorithm """
        raise NotImplementedError()

    def predict(self, X: scipy.sparse.csr_matrix):
        """ Scoring function of algorithm """
        raise NotImplementedError()

    def _id_to_index(self, ids):
        return np.array([self.item_id_to_index_mapping_[item_id] for item_id in ids])

    def _index_to_id(self, indices):
        return self.index_to_item_id_mapping_[np.asarray(indices)]

    @property
    def n(self):
        """ The number of items """
        return self.index_to_item_id_mapping_.shape[0]

    def _interaction_to_matrix(self, interactions, unique_item_ids=None):
        """ Convert interaction list to sparse matrix format and store item id mappings. """
        user_ids, item_ids = zip(*interactions)
        user_ids = np.array(user_ids)
        item_ids = np.array(item_ids)

        # remap ids to prevent zero rows/columns
        _, user_indices = np.unique(user_ids, return_inverse=True)

        item_indices = None
        if unique_item_ids is None:
            item_id_mapping, item_indices = np.unique(item_ids, return_inverse=True)
        else:
            item_id_mapping = np.array(unique_item_ids)

        self.item_id_to_index_mapping_ = {item_id: index for index, item_id in enumerate(item_id_mapping)}

        if item_indices is None:
            item_indices = self._id_to_index(item_ids)

        # to revert back to original ids
        self.index_to_item_id_mapping_ = item_id_mapping

        max_user = user_indices.max() + 1
        max_item = len(item_id_mapping)

        values = np.ones(item_indices.shape[0], dtype=np.int8)
        X = scipy.sparse.csr_matrix((values, (user_indices, item_indices)), dtype=np.int32, shape=(max_user, max_item))

        # duplicates are added together -> make binary again
        X.sum_duplicates()
        X[X > 1] = 1

        return X

    def train(self, interactions: List[Tuple], unique_item_ids=None):
        """ Trains the algorithm from pairs of (user, item) interactions.
        Optionally can provide a global list of item ids to uniformly perform mapping. """
        X = self._interaction_to_matrix(interactions, unique_item_ids=unique_item_ids)
        self.fit(X)
        return self

    def recommend(self, history: List, top_k: int, retarget=True) -> List:
        """ Compute recommendations based on a list of historical item ids. """
        return self.recommend_all([history], top_k=top_k, retarget=retarget)[0]

    def recommend_all(self, histories: List[List], top_k: int, retarget=True) -> List[List]:
        """ Compute recommendations based on a list of historical item ids for multiple users """
        # Build sparse matrix
        row_ind = list()
        col_ind = list()
        for row, history in enumerate(histories):
            row_ind.append(np.repeat(row, len(history)))
            col_ind.append(np.asarray(history))

        row_ind = np.concatenate(row_ind, axis=0)
        col_ind = self._id_to_index(np.concatenate(col_ind, axis=0))
        data = np.ones(col_ind.shape[0])
        X = scipy.sparse.csr_matrix((data, (row_ind, col_ind)), shape=(len(histories), self.n), dtype=np.int32)

        X.sum_duplicates()
        X[X > 1] = 1

        # Compute predictions
        predictions = self.predict(X)

        if not retarget:
            predictions -= 10000 * X

        # Turn into recommendations
        recommendations = list()
        for row in range(predictions.shape[0]):
            start, end = predictions.indptr[row], predictions.indptr[row + 1]

            scores = predictions.data[start:end]
            indices = predictions.indices[start:end]

            if len(scores) < top_k:
                top_k_score_indices = np.arange(len(scores))
            else:
                top_k_score_indices = np.argpartition(scores, -top_k)[-top_k:][::-1]

            top_k_indices = indices[top_k_score_indices]
            top_k_ids = self._index_to_id(top_k_indices)
            recommendations.append(list(top_k_ids))

        return recommendations