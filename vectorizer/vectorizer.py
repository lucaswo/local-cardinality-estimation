import numpy as np
from sklearn.preprocessing import LabelEncoder
from typing import List, Tuple, Dict
import time
import os.path
import yaml
import csv

# Proposal: Do not call the vectorizer for each single query string, but collect them and then execute them parallelized

class Vectorizer:
    """Constructs a vector consisting of operator code and normalized value for each predicate in the sql query set with set_query method."""
    
    def __init__(self, yaml_path):
        """ Intitialises the Vectorizer object by defining available operators and maximum numbers of expressions allowed within a query. Returns the obejct."""

        self.n_max_expressions = 4
        self.operators = {
            "=": [0,0,1],
            ">": [0,1,0],
            "<": [1,0,0],
            "<=": [1,0,1],
            ">=": [0,1,1],
            "!=": [1,1,0],
            "IS": [0,0,1]
        }
        self.operator_code_length = len(next(iter(self.operators.values())))
        self.query = None
        self.cardinality_estimation_postgres = None
        self.cardinality_truth = None
        self.vector = None
        self.yaml_path = yaml_path

    def get_max_cardinality(self, query_csv_path):
        """Stores and returns the max_cardinality of the current query"""

        max_card_yaml_key = -1
        with open(query_csv_path, 'r', encoding='utf8') as f:
            for row in csv.DictReader(f):
                if row["query"] == self.query:
                    max_card_yaml_key = row["key"]
                    break
        if max_card_yaml_key != -1:
            with open(self.yaml_path, 'r', encoding='utf8') as f:
                self.meta = yaml.safe_load(f)

            max_card = self.meta[max_card_yaml_key]['max_card']
            self.max_cardinality = max_card
            return max_card
        else:
            raise ValueError("Query not found within csv file!")
    


    def set_query(self, query: str, min_max: Dict[str, Tuple[int, int, int]], encoders: Dict[str, LabelEncoder]):
        """Reads a new query for another vectorisation task. Avoids Vectorizer object switch."""

        self.query = query
        self.expressions = query.split("WHERE", maxsplit=1)[1].split("AND")
        assert self.n_max_expressions > len(self.expressions), f"Too many expressions concatinated by 'AND' in query!"

        self.min_max_step = min_max
        self.predicates = list(self.min_max_step.keys())
        self.encoders = encoders
        self.n_total_columns = len(min_max)
        self.vector = np.zeros(self.n_total_columns * self.n_max_expressions)


    def add_query(self):
        #TODO
        print("Not yet implemented!")


    def vectorize_batch(self):
        #TODO
        print("Not yet implemented!")
        

    def __parse_expression(self, expression: str) -> Tuple[str, str, int]:
        """Parses the given expression. Returns parse result: predicate, operator and value"""
        expression = expression.strip().strip(';')
        predicate, operator, value = expression.split(" ")
        return predicate, operator, int(value)


    def __normalize(self, predicate: str, value: int) -> float:
        """Normalizes the value according to min-max statistics of the given predicate.
        Normalization will never result in value of range (0,1]. Returns normalized value."""

        min_val, max_val, step = self.min_max_step[predicate]
        if predicate in self.encoders.keys():
            value = self.encoders[predicate].transform([int(value)])[0]
        else:
            value = max(min_val, float(value))
        return (value - min_val + step) / (max_val - min_val + step)
    

    def __min_max_normalize(self, value, max_cardinality, min_value = 0):
        """Executes a min max normalisation"""

        max_value = np.log(max_cardinality)
        value = np.log(value)
        return (value - min_value)/(max_value - min_value)


    def vectorize(self, cardinality_estimation_postgres, cardinality_truth, max_card=None) -> np.ndarray:
        """Vectorizes the query given. Returns the a triple containing (vector, estimated cardinality, true cardinality). If cardinalities not set beforehand None or old value is returned."""

        for expression in self.expressions:
            predicate, operator, value = self.__parse_expression(expression)
            normalized_value = self.__normalize(predicate, value)

            idx = self.predicates.index(predicate)
            end_idx = idx * self.n_max_expressions + self.operator_code_length
            self.vector[idx*self.n_max_expressions:end_idx] = self.operators[operator]
            self.vector[end_idx] = normalized_value

        if max_card is None:
            max_card = self.max_cardinality
        self.cardinality_truth = self.__min_max_normalize(cardinality_truth, max_card)
        self.cardinality_estimation_postgres = cardinality_estimation_postgres
        return self.vector, self.cardinality_estimation_postgres, self.cardinality_truth

    def save(self, path: str):
        """Stores the SQL query and corresponding vector at given path"""

        timestr = time.strftime("%Y%m%d_%H%M%S")
        np.save( os.path.join(path, f"{timestr}_vector.npy"), self.vector )
        np.savetxt( os.path.join(path, f"{timestr}_vector.txt"), self.vector )
        with open( os.path.join(path, f"{timestr}_query.sql"), "a" ) as f:
            f.write(self.query + "\n")




def vectorize_query_original(query: str, min_max: Dict[str, Tuple[int, int, int]], encoders: Dict[str, LabelEncoder]):
    """Copy-pasted method of the original implementation for testing purposes"""

    query = query.replace("NULL", "-1").replace("IS NOT", "!=").replace(";", "")
    total_columns = len(min_max)
    vector = np.zeros(total_columns*4)
    predicates = query.split("WHERE", maxsplit=1)[1]
    operators = {
        "=": [0,0,1],
        ">": [0,1,0],
        "<": [1,0,0],
        "<=": [1,0,1],
        ">=": [0,1,1],
        "!=": [1,1,0],
        "IS": [0,0,1]
    }
    
    for exp in predicates.split("AND"):
        exp = exp.strip()
        pred, op, value = exp.split(" ")
        if pred in encoders.keys():
            #value = encoders[pred].transform([value.replace("'", "")])[0]
            value = encoders[pred].transform([int(value)])[0]
        else:
            value = max(min_max[pred][0], float(value))
        idx = list(min_max.keys()).index(pred)
        vector[idx*4:idx*4+3] = operators[op]
        vector[idx*4+3] = (value-min_max[pred][0]+min_max[pred][2])/                           (min_max[pred][1]-min_max[pred][0]+min_max[pred][2])
    return vector

def vectorizer_tests():
    """Test method to compare the original implementation with jupyter notebook output (truth) or with the Vectorizer implementation. Succeeds if no assertion throws an error."""

    # OUTPUT
    # Setting up view...

    # cols, max_card
    # [('kind_id', 'integer'), ('person_id', 'integer'), ('role_id', 'integer')] (62143897,)

    # mm, encs
    # {'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)} {}
    # Generating test queries...

    # SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE kind_id != 8;

    # vector
    # [1. 1. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0.]

    # SQL_queries_t, data_test, y_test, postgres_est
    # ['SELECT * FROM title t1,cast_info t2 WHERE t1.id=t2.movie_id AND kind_id != 8;'] [[1. 1. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0.]] [62143871] [63475836]

    # N, y
    # [17.94496317] [0.99999998] # was sadly rounded... but is ok as approximation




    sql_query = "SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE kind_id != 8;"
    min_max_step = {'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)}
    encoders = {}
    vector_truth = np.array([1,1,0,1,0,0,0,0,0,0,0,0], dtype=float)
    max_card = (62143897,)[0]
    postgres_cardinality_estimate = 63475836
    cardinality = 62143871
    normalized_cardinality = 0.999999976685163

    # original implementation copy-pasted test
    vector_original = vectorize_query_original(sql_query, min_max_step, encoders)
    assert np.allclose(vector_original, vector_truth)

    # vectorization test
    vectorizer = Vectorizer("/mnt/data/study/Forschungspraktikum/project/local-cardinality-estimation/vectorizer/meta_information.yaml")
    vectorizer.set_query(sql_query, min_max_step, encoders)
    vector_vectorizer, card_est, card_norm = vectorizer.vectorize(postgres_cardinality_estimate, cardinality, None)
    assert np.allclose(vector_vectorizer, vector_truth),  f"{vector_vectorizer} not close \n{vector_truth}"
    assert card_est == postgres_cardinality_estimate, f"{card_est} is not queal {postgres_cardinality_estimate}"
    assert card_norm == normalized_cardinality, f"{card_norm} is not queal {normalized_cardinality}"
    vectorizer.save("/mnt/data/programming/tmp/")

    # TODO: batch test

# meta data:
# for each column:
    # col[X] = (column_name, data_type)
    # min_max holds (min_value, max_value, 1) for each columns value range
    # encoders is dictonary. Only cols not of type integer have an encoder (LabelEncoder) mapped

if __name__ == "__main__":
    vectorizer_tests()


    



