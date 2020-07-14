import numpy as np
import csv
from ast import literal_eval
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

    def __init__(self):
        """
        Intitialises the Vectorizer object by defining available operators.
        """

        self.operator_code_length = len(next(iter(Vectorizer.operators.values())))        
        self.querySetID_meta = {}
        self.vectorization_tasks = [] # may become a SimpleQueue in case of multithreading
        self.vectorization_results = []

    def add_queries_with_cardinalities(self, queries_with_cardinalities_path: str):
        """
        Reads CSV file with format (querySetID;query;encodings;max_card;min_max_step;estimated_cardinality;true_cardinality) whereas min_max_step is an array of the format 
        [[1, 2, 1], [1, 113, 1], [1878, 2115, 1]] sorted by lexicographic order of corresponding predicates and encodings is an empty array if only integer values are processed. 
        For a querySetID all predicates are collected and sorted in lexicographical order to provide correct indices (e.g. in encodings & min_max_value) for a given predicate.
        Read queries are added to the list of vectorisation tasks.

        :param queries_with_cardinalities_path: path to a CSV file containing all queries and their estimated and true cardinalities 
        """

        with open(queries_with_cardinalities_path) as f:
            next(f) # skip header
            reader = csv.reader(f, delimiter=';')
            for querySetID, query, encodings, max_card, min_max_step, estimated_cardinality, true_cardinality in reader:
                
                querySetID = int(querySetID)
                if querySetID not in self.querySetID_meta:
                    self.querySetID_meta[querySetID] = {"predicates":[], "min_max_step":[], "n_max_expressions":0, "encodings":[]}

                expressions = query.split("WHERE", maxsplit=1)[1].split("AND")
                # Matches join statements within WHERE clausel in a general manner. 
                # E.g.: a=b a=abc is matched as join statement, but a="b" a='b' a=9 not (for all numbers and letters respectivley)
                join_matcher = re.compile(r'.+\s*=\s*[^\d"\']*$')
                expressions = [expr for expr in expressions if not join_matcher.match(expr)]

                query_parsed = [self.__parse_expression(expression) for expression in expressions]
                
                if len(query_parsed) > self.querySetID_meta[querySetID]["n_max_expressions"]:
                    self.querySetID_meta[querySetID]["n_max_expressions"] = len(query_parsed)

                for predicate in [x[0] for x in query_parsed]:
                    if predicate not in self.querySetID_meta[querySetID]["predicates"]:
                        self.querySetID_meta[querySetID]["predicates"].append(predicate)

                if self.querySetID_meta[querySetID]["encodings"] == []:
                    enc = literal_eval(encodings)
                    if enc == []:
                        self.querySetID_meta[querySetID]["encodings"] = None
                
                if self.querySetID_meta[querySetID]["min_max_step"] == []:
                    self.querySetID_meta[querySetID]["min_max_step"] = literal_eval(min_max_step)
        
                self.vectorization_tasks.append((
                    querySetID,
                    query_parsed,
                    int(max_card),
                    int(estimated_cardinality),
                    int(true_cardinality)
                    ))
        
        # sort all predicates for a querySetID to correctly retrieve the index within encodings and min_max_step
        for querySetID, meta in self.querySetID_meta.items():
            meta["predicates"].sort()


    def vectorize(self) -> List[np.array]:
        """
        Vectorizes all vectorization tasks added.
        
        :return: List of np.array vectors whereas each row contains the vectorized query and appended maximal, estimated and true cardinality (in this order) 
        """

        while len(self.vectorization_tasks) > 0:
            querySetID, query, max_card, estimated_cardinality, true_cardinality = self.vectorization_tasks.pop(0)
            n_max_expressions = self.querySetID_meta[querySetID]["n_max_expressions"]

            vector = np.zeros(n_max_expressions * (self.operator_code_length + 1) + 3) # constant 1 for each value; constant 3 for max_cardinality, estimated_cardinality, true_cardinality

            # vectorize query
            for predicate, operator, value in query:
                idx = self.querySetID_meta[querySetID]["predicates"].index(predicate)
                value_normalzed = self.__normalize(querySetID, predicate, value)

                end_idx = idx * (self.operator_code_length + 1) + self.operator_code_length
                vector[idx*(self.operator_code_length+1):end_idx] = Vectorizer.operators[operator]
                vector[end_idx] = value_normalzed
                
            # normalize/set cardinality information
            vector[-3] = max_card
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


    def __normalize(self, querySetID: int, predicate: str, value: int) -> float:
        """
        Normalizes the value according to min-max statistics of the given predicate and the querySetID. If an encoding is avaiable for the predicate it is used.
        Normalization will result in value of range (0,1].
        
        :param querySetID: id of the querySet to get the meta data for the given predicate
        :param predicate: attribute of the value
        :param value: the value to be normalized
        :return: the normalized value
        """

        predicate_idx = self.querySetID_meta[querySetID]["predicates"].index(predicate)
        min_val, max_val, step = self.querySetID_meta[querySetID]["min_max_step"][predicate_idx]
        encoding = self.querySetID_meta[querySetID]["encodings"]
        
        encoded_value = value
        if encoding is not None:
            encoding = encoding[predicate_idx]
            if value in encoding.keys():
                encoded_value = encoding[value]
        
        if value == encoded_value:
            encoded_value = max(min_val, float(value))
            
        return (encoded_value - min_val + step) / (max_val - min_val + step)
    

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

    def save(self, path: str, filetypes : str): #TODO
        """
        Stores the SQL query and corresponding vector at given path as NPY and TXT file.

        :param path: path to a directory for saving
        :param filetypes: string of file types must contain "csv" or "npy"
        """
        
        assert "npy" in filetypes or  "csv" in filetypes, "Valid file extention must be given. filetypes argument must contain 'csv' and/or 'npy'"
        if "npy" in filetypes: 
            np.save(f"{path}.npy", np.array(self.vectorization_results))
        if "csv" in filetypes:
            np.savetxt(f"{path}.csv", np.array(self.vectorization_results), delimiter=',', fmt="%.18g")

def vectorize_query_original(query: str, min_max: Dict[str, Tuple[int, int, int]], encoders: List[Dict[str, int]]) -> np.array:
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
    
    # not quite the original anymore due to query file adaptions
    join_matcher = re.compile(r'.+\s*=\s*[^\d"\']*$')
    exps = []
    for exp in predicates.split("AND"):
        exp = exp.strip()
        if join_matcher.match(exp):
            continue
        exps.append(exp)
    exps.sort()

    for i, exp in enumerate(exps):
        pred, op, value = exp.split(" ")
        # FIXME Ignore encoders...
        # if pred in encoders.keys(): 
        #     #value = encoders[pred].transform([value.replace("'", "")])[0]
        #     value = encoders[pred].transform([int(value)])[0]
        # else:
        value = max(min_max[i][0], float(value))
        vector[i*4:i*4+3] = operators[op]
        vector[i*4+3] = (value-min_max[i][0]+min_max[i][2]) / (min_max[i][1]-min_max[i][0]+min_max[i][2])
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
    # alphabetically sorted
    min_max_step = ([[1, 2, 1], [1, 113, 1], [1878, 2115, 1]], 
                    [[1, 2, 1], [1, 236627, 1], [1878, 2115, 1]])
    encoders = []

    # original implementation copy-pasted test
    original_vectors = []
    for i in range(len(sql_queries)):
        for query in sql_queries[i]:
            original_vectors.append(vectorize_query_original(query, min_max_step[i], encoders))
    original_vectors = np.array(original_vectors)

    # small vectorization test
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities("assets/queries_with_cardinalities.csv")
    vectorizer.add_queries_with_cardinalities("assets/queries_with_cardinalities.csv") # duplicated to sumulate adding of two query files
    vectorizer_vectors = np.array(vectorizer.vectorize())
    vectorizer_vectors = vectorizer_vectors[len(vectorizer_vectors)//2:,:]

    print(sql_queries[0][0])
    print(vectorizer_vectors[0,1:-3], len(vectorizer_vectors[0,1:-3]))
    print(original_vectors[0], len(original_vectors[0]))

    assert np.allclose(vectorizer_vectors[:,1:-3], original_vectors),  f"{vectorizer_vectors[:,1:-3]} not close \n{original_vectors}"
    #vector_vectorizer, card_est, card_norm = vec[:-2], vec[-2], vec[-1]
    #assert card_norm == normalized_cardinality, f"{card_norm} is not queal {normalized_cardinality}"
    vectorizer.save("/mnt/data/programming/tmp/asset_queries_with_cardinalites_vectors", "csv") # will store duplicated results, due to indentical second query file 

if __name__ == "__main__":
    vectorizer_tests()


    



