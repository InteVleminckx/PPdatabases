import numpy as np
import scipy.sparse

from .algorithm import Algorithm


class ItemKNNAlgorithm(Algorithm):
    """ Item based nearest neighbors recommendation algorithm """
    def __init__(self, k=20, normalize=False):
        super().__init__()
        self.k = k
        self.normalize = normalize

    def fit(self, X: scipy.sparse.csr_matrix):
        """ Train algorithm with interaction matrix X """
        # Input checking
        X.eliminate_zeros()
        assert np.all(X.data == 1), "X should only contain binary values"

        m, n = X.shape

        # Cosine similarity is dot product between l2 normalized vectors
        norms = np.sqrt(np.asarray(X.sum(axis=0)).flatten())
        safe_norms = norms.copy()
        safe_norms[safe_norms == 0] = 1
        diag_div = scipy.sparse.diags(1 / safe_norms)
        del safe_norms, norms
        X = X @ diag_div
        del diag_div
        sim = (X.T @ X).tocsr()

        # Set diagonal to 0, because we don't want to support self similarity
        sim.setdiag(0)

        # can speed up top_k per row selection
        sim.eliminate_zeros()

        # take top-k nearest neighbors per row
        if self.k:
            for row in range(n):
                start, end = sim.indptr[row], sim.indptr[row + 1]
                if end - start <= self.k:
                    continue

                values = sim.data[start:end]
                not_top_k_indices = np.argpartition(values, -self.k)[:-self.k]
                sim.data[start + not_top_k_indices] = 0

        sim.eliminate_zeros()
        sim.sort_indices()

        # normalize per row
        if self.normalize:
            row_sums = np.asarray(sim.sum(axis=1)).flatten()
            row_sums[row_sums == 0] = 1
            diag_div_matrix = scipy.sparse.diags(1 / row_sums)
            sim = diag_div_matrix @ sim

        self.B_ = sim

        return self

    def predict(self, X):
        assert hasattr(self, "B_"), "fit needs to be called before predict"
        X.eliminate_zeros()
        assert np.all(X.data == 1), "X should only contain binary values"

        # predictions are sum of nearest neighbor similarity scores
        return X @ self.B_


class ItemKNNIterativeAlgorithm(ItemKNNAlgorithm):
    """ Reduce memory requirement by taking top K per row immediately. """
    def fit(self, X: scipy.sparse.csr_matrix):
        # Input checking
        X.eliminate_zeros()
        assert np.all(X.data == 1), "X should only contain binary values"

        m, n = X.shape

        norms = np.sqrt(np.asarray(X.sum(axis=0)).flatten())
        safe_norms = norms.copy()
        safe_norms[safe_norms == 0] = 1
        diag_div = scipy.sparse.diags(1 / safe_norms)
        del safe_norms
        X = X @ diag_div
        del diag_div

        XT = X.T.tocsr()

        data = list()
        row_ind = list()
        col_ind = list()
        for i in range(n):
            if norms[i] == 0:
                continue

            num = (XT[i] @ X).toarray().flatten()
            num[i] = 0

            cols, = num.nonzero()
            values = num[cols]

            if self.k < len(cols):
                top_k_indices = np.argpartition(values, -self.k)[-self.k:]
                cols = cols[top_k_indices]
                values = values[top_k_indices]

            if self.normalize:
                total = values.sum()
                if total == 0:
                    total = 1   # safe divide
                values = values / total

            col_ind.append(cols)
            rows = np.repeat(i, len(cols))
            row_ind.append(rows)
            data.append(values)

        data = np.concatenate(data, axis=0)
        row_ind = np.concatenate(row_ind, axis=0)
        col_ind = np.concatenate(col_ind, axis=0)
        sim = scipy.sparse.csr_matrix((data, (row_ind, col_ind)), shape=(n, n), dtype=np.float32)

        self.B_ = sim

        return self
