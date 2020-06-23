import numpy as np
from sklearn.preprocessing import LabelEncoder
import time
import os.path
import csv
from ast import literal_eval
from tqdm import tqdm
import itertools

from typing import List, Tuple, Dict
import re

class Vectorizer:
    """Constructs a vector consisting of operator code and normalized value for each predicate in the sql query set with set_query method."""
    
    operators = {
            "=": [0,0,1],
            ">": [0,1,0],
            "<": [1,0,0],
            "<=": [1,0,1],
            ">=": [0,1,1],
            "!=": [1,1,0],
            "IS": [0,0,1]
    }

    def __init__(self, n_max_expressions: int):
        """
        Intitialises the Vectorizer object by defining available operators and maximum numbers of expressions allowed within a query. Returns the obejct.
        
        :param n_max_expressions maximal number of expression allowed to process to conform with the fixed vector length used for each predictor model.
        """

        self.n_max_expressions = n_max_expressions
        self.operator_code_length = len(next(iter(Vectorizer.operators.values())))
        self.vectorization_tasks = [] # may become a SimpleQueue in case of multithreading
        self.vectorization_results = []

    def add_queries_with_cardinalities(self, queries_with_cardinalities_path: str):
        """
        Reads CSV file with format (querySetID;query;encodings;max_card;min_max_step) whereas min_max_step is a dictionary of the format 
        {'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]} and encodings is an empty dictionary if only integer values are processed.
        Read queries are added to the list of vectorisation tasks. Attention: queries must have sorted predicates.

        :param queries_with_cardinalities_path: path to a CSV file containing all queries and their estimated and true cardinalities 
        """

        with open(queries_with_cardinalities_path) as f:
            next(f) # skip header
            reader = csv.reader(f, delimiter=';')
            for querySetID, query, encodings, max_card, min_max_step, estimated_cardinality, true_cardinality in reader:
                
                expressions = query.split("WHERE", maxsplit=1)[1].split("AND")
                join_matcher = re.compile(r'.+\..*id\s*=\s*.+\..*id\s*')
                expressions = [expr for expr in expressions if not join_matcher.match(expr)]
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
            querySetID, query, encodings, max_card, min_max_step, estimated_cardinality, true_cardinality = self.vectorization_tasks.pop(0)

            n_total_columns = len(min_max_step)
            vector = np.zeros(n_total_columns * self.n_max_expressions + 2) # constant 2 for estimated_cardinality, true_cardinality

            # vectorize query
            for idx, query in enumerate(query): # requires sorted predicates
                predicate, operator, value = query
                value_normalzed = self.__normalize(predicate, min_max_step, encodings, value)

                end_idx = idx * self.n_max_expressions + self.operator_code_length
                vector[idx*self.n_max_expressions:end_idx] = Vectorizer.operators[operator]
                vector[end_idx] = value_normalzed
                
            # normalize cardinalities
            vector[-2] = self.__min_max_normalize(estimated_cardinality, max_card)
            vector[-1] = self.__min_max_normalize(true_cardinality, max_card)

            vector = np.insert(vector, 0, querySetID, axis=0)

            self.vectorization_results.append(vector)
        return self.vectorization_results

    def __parse_expression(self, expression: str) -> Tuple[str, str, int]:
        """
        Parses the given expression. Parsing does not rely on spaces before and after operator, since these could be omitted within a query. Returns parse result: predicate, operator and value.

        :param expression: an exptression of a WHERE clause (are usually seperated by AND/ OR) e.g. 'kind_id != 8'
        :return: a triple with predicate, operator and value

        """

        expression = expression.strip().strip(';')
        ops = sorted(self.operators.keys(), key=len, reverse=True)
        for op in ops:
            if op in expression:
                predicate, value = expression.split(op)
                operator = op
                break
        return predicate.strip(), operator.strip(), int(value)


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
        if '.' in predicate: 
            predicate = predicate.split('.')[1]
        min_val, max_val, step = min_max_steps[predicate]
        if predicate in encodings.keys():
            value = encodings[predicate].transform([int(value)])[0]
        else:
            value = max(min_val, float(value))
        return (value - min_val + step) / (max_val - min_val + step)
    

    def __min_max_normalize(self, value: float, max_cardinality: int, min_value: int = 0) -> float:
        """
        Executes a min max normalization
        
        :param value: the value to be normalized
        :param max_cardinality: maximal cardinality of the query set. Its logarithm is the max value for normalization
        :param min_value: minimal value as lower limit. Default is 0
        :return: the normalized value
        """

        max_value = np.log(max_cardinality)
        value = np.log(value)
        return float(value - min_value)/(max_value - min_value)

    def save(self, path: str, filename : str):
        """
        Stores the SQL query and corresponding vector at given path as NPY and TXT file.

        :param path: path to a directory for saving
        :param filename: filename without extension e.g. "queries_with_cardinalites_vectors"
        """

        np.save(os.path.join(path, f"{filename}.npy"), np.array(self.vectorization_results) )
        np.savetxt( os.path.join(path, f"{filename}.csv"), np.array(self.vectorization_results), delimiter=',', fmt="%.18g", header="querySetID, [vector], estimated_cardinality, true cardinality")

def vectorize_query_original(query: str, min_max: Dict[str, Tuple[int, int, int]], encoders: Dict[str, LabelEncoder]) -> np.array:
    """
    Copy-pasted method of the original implementation for testing purposes; Only added Join detection
    
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
    
    join_matcher = re.compile(r'.+\..*id\s*=\s*.+\..*id\s*')
    for exp in predicates.split("AND"):
        exp = exp.strip()
        if join_matcher.match(exp):
            continue
        pred, op, value = exp.split(" ")
        if '.' in pred: 
            pred = pred.split('.')[1]
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

    sql_queries = (
        ["SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id < 2 AND mi_idx.info_type_id = 107 AND t.production_year > 2009;",
            "SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id = 1 AND mi_idx.info_type_id < 80 AND t.production_year <= 1894;",
            "SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id <= 1 AND mi_idx.info_type_id != 62 AND t.production_year <= 2094;",
            "SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id >= 2 AND mi_idx.info_type_id > 45 AND t.production_year < 1939;",
            "SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id = 2 AND mi_idx.info_type_id <= 32 AND t.production_year <= 1918;",
            "SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id >= 2 AND mi_idx.info_type_id < 54 AND t.production_year <= 2097;",
            "SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id <= 2 AND mi_idx.info_type_id >= 38 AND t.production_year < 1896;",
            "SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id = 2 AND mi_idx.info_type_id <= 66 AND t.production_year = 2026;",]
        ,
        ["SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id = 1 AND mk.keyword_id >= 117023 AND t.production_year <= 1894;", 
            "SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id >= 1 AND mk.keyword_id < 35239 AND t.production_year <= 1896;", 
            "SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id < 2 AND mk.keyword_id <= 35888 AND t.production_year != 2020;", 
            "SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id = 2 AND mk.keyword_id > 196933 AND t.production_year = 1907;", 
            "SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id != 1 AND mk.keyword_id < 19712 AND t.production_year < 1980;", 
            "SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id > 1 AND mk.keyword_id <= 186471 AND t.production_year < 2110;"]
        )
    min_max_step = ({'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}, 
                    {'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]})
    encoders = {}

    # original implementation copy-pasted test
    original_vectors = []
    for i in range(len(sql_queries)):
        for query in sql_queries[i]:
            original_vectors.append(vectorize_query_original(query, min_max_step[i], encoders))
    original_vectors = np.array(original_vectors)

    # small vectorization test
    vectorizer = Vectorizer(4)
    vectorizer.add_queries_with_cardinalities("assets/queries_with_cardinalities.csv")
    vectorizer_vectors = np.array(vectorizer.vectorize())
    assert np.allclose(vectorizer_vectors[:,1:-3], original_vectors),  f"{vectorizer_vectors[:,1:-3]} not close \n{original_vectors}"
    #vector_vectorizer, card_est, card_norm = vec[:-2], vec[-2], vec[-1]
    #assert card_norm == normalized_cardinality, f"{card_norm} is not queal {normalized_cardinality}"
    vectorizer.save("/mnt/data/programming/tmp/", "asset_queries_with_cardinalites_vectors")

if __name__ == "__main__":
    vectorizer_tests()


    



