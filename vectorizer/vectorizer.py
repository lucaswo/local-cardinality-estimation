import numpy as np
from sklearn.preprocessing import LabelEncoder
import time
import os.path
import csv
from ast import literal_eval
from tqdm import tqdm

from typing import List, Tuple, Dict

class Vectorizer:
    """Constructs a vector consisting of operator code and normalized value for each predicate in the sql query set with set_query method."""
    
    def __init__(self):
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
        self.vectorization_tasks = [] # may become a SimpleQueue in case of multithreading
        self.vectorization_results = []

    def add_queries_with_cardinalities(self, queries_with_cardinalities_path):
        """
        Reads CSV file with fomrat (querySetID;query;encodings;max_card;min_max_step) whereas min_max_step is a dictionary of the format 
        {'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]} and encodings is an empty dictionary if only integer values are processed.
        Read queries are added to the list of vectorisation tasks. Attention: queries must have sorted predicates.

        :param queries_with_cardinalities_path: path to a CSV file containing all queries and their estimated and true cardinalities 
        """

        with open(queries_with_cardinalities_path) as f:
            next(f) # skip header
            reader = csv.reader(f, delimiter=';')
            for querySetID, query, encodings, max_card, min_max_step, estimated_cardinality, true_cardinality in reader:
                
                expressions = query.split("WHERE", maxsplit=1)[1].split("AND")
                assert self.n_max_expressions > len(expressions), f"Too many expressions concatinated by 'AND' in query! {query}"

                query_parsed = [self.__parse_expression(expression) for expression in expressions]

                self.vectorization_tasks.append((
                    int(querySetID),
                    query_parsed,
                    literal_eval(encodings),
                    int(max_card),
                    literal_eval(min_max_step),
                    int(estimated_cardinality),
                    int(true_cardinality)
                    ))


    def vectorize(self) -> List[np.array]:
        """
        Vectorizes all vectorization tasks added.
        
        :return: List of np.array vectors whereas each row contains the vectorized query and appended estimated and true cardinality (in this order) 
        """

        while len(self.vectorization_tasks) > 0:
            _, query, encodings, max_card, min_max_step, estimated_cardinality, true_cardinality = self.vectorization_tasks.pop(0)

            n_total_columns = len(min_max_step)
            vector = np.zeros(n_total_columns * self.n_max_expressions + 2) # constant 2 for estimated_cardinality and true_cardinality

            # vectorize query
            for idx, query in enumerate(query): # requires sorted predicates
                predicate, operator, value = query
                value_normalzed = self.__normalize(predicate, min_max_step, encodings, value)

                end_idx = idx * self.n_max_expressions + self.operator_code_length
                vector[idx*self.n_max_expressions:end_idx] = self.operators[operator]
                vector[end_idx] = value_normalzed
                
            # normalize cardinalities
            vector[-2] = self.__min_max_normalize(estimated_cardinality, max_card)
            vector[-1] = self.__min_max_normalize(true_cardinality, max_card)

            self.vectorization_results.append(vector)
        return self.vectorization_results

    def __parse_expression(self, expression: str) -> Tuple[str, str, int]:
        """
        Parses the given expression. Returns parse result: predicate, operator and value.

        :param expression: an exptression of a WHERE clause (are usually seperated by AND/ OR) e.g. 'kind_id != 8'
        :return: a triple with predicate, operator and value

        """

        expression = expression.strip().strip(';')
        predicate, operator, value = expression.split(" ")
        return predicate, operator, int(value)


    def __normalize(self, predicate: str, min_max_steps: Dict[str, Tuple[int, int, int]], encodings: Dict[int, str], value: int) -> float:
        """
        Normalizes the value according to min-max statistics of the given predicate. If an encoding is avaiable for the predicate it is used.
        Normalization will result in value of range (0,1].
        
        :param predicate: attribute of the value
        :param min_max_steps: dictionary of all min, max, step values for each predicate
        :param encodings: dictionary, which maps predicates to encoders
        :param value: the value to be normalized
        :return: the normalized value
        """

        min_val, max_val, step = min_max_steps[predicate]
        if predicate in encodings.keys():
            value = encodings[predicate].transform([int(value)])[0]
        else:
            value = max(min_val, float(value))
        return (value - min_val + step) / (max_val - min_val + step)
    

    def __min_max_normalize(self, value, max_cardinality, min_value = 0) -> float:
        """
        Executes a min max normalization
        
        :param value: the value to be normailzed
        :param max_cardinality: maximal cardinality of the query set. Its logarithm is the max value for normalization
        :param min_value: minimal value as lower limit. Default is 0
        :return: the normalized value
        """

        max_value = np.log(max_cardinality)
        value = np.log(value)
        return float(value - min_value)/(max_value - min_value)

    def save(self, path: str):
        """
        Stores the SQL query and corresponding vector at given path as NPY and TXT file. Prepends a timestamp

        :param path: path to a directory for saving
        """

        timestr = time.strftime("%Y%m%d_%H%M%S")
        np.save( os.path.join(path, f"{timestr}_vector.npy"), np.array(self.vectorization_results) )
        np.savetxt( os.path.join(path, f"{timestr}_vector.csv"), np.array(self.vectorization_results), delimiter=',', fmt="%.18g")

def vectorize_query_original(query: str, min_max: Dict[str, Tuple[int, int, int]], encoders: Dict[str, LabelEncoder]) -> np.array:
    """
    Copy-pasted method of the original implementation for testing purposes
    
    :param query: the query to vectorize
    :param min_max: dictionary of all min, max, step values for each predicate
    :param encoders: dictionary, which maps predicates to encoders
    :return: the normalized vector without cardinalities
    """

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

    # small vectorization test
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities("/mnt/data/study/Forschungspraktikum/project/local-cardinality-estimation/vectorizer/fake_queries_with_cardinalities_test.csv")
    for vec in vectorizer.vectorize():
        vector_vectorizer, card_est, card_norm = vec[:-2], vec[-2], vec[-1]
        assert np.allclose(vector_vectorizer, vector_truth),  f"{vector_vectorizer} not close \n{vector_truth}"
        assert card_norm == normalized_cardinality, f"{card_norm} is not queal {normalized_cardinality}"

    # bigger vectorization test
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities("/mnt/data/study/Forschungspraktikum/project/local-cardinality-estimation/vectorizer/fake_queries_with_cardinalities_test_bigger.csv")
    vectorizer.add_queries_with_cardinalities("/mnt/data/study/Forschungspraktikum/project/local-cardinality-estimation/vectorizer/fake_queries_with_cardinalities_test.csv")
    for vec in vectorizer.vectorize():
        vector_vectorizer, cardinality_estimation, cardinality_true = vec[:-2], vec[-2], vec[-1]
    vectorizer.save("/mnt/data/programming/tmp/")

if __name__ == "__main__":
    vectorizer_tests()


    



