import numpy as np
from sklearn.preprocessing import LabelEncoder

# TODO: Documentation
# TODO: Type Hinting: : e.g. List[Tuple[str, str]]
# Proposal: Do not call the vectorizer for each single query string, but collect them and then execute them parallelized

def vectorize_query_original(query_str, min_max, encoders):
    query_str = query_str.replace("NULL", "-1").replace("IS NOT", "!=").replace(";", "")
    total_columns = len(min_max)
    vector = np.zeros(total_columns*4)
    predicates = query_str.split("WHERE", maxsplit=1)[1]
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

class Vectorizer:
    """Constructs a vector consisting of operator code and normalized value for each predicate in the given sql query"""
    
    def __init__(self,query_str, min_max, encoders):
        self.n_max_expressions = 4
        self.expressions = query_str.split("WHERE", maxsplit=1)[1].split("AND")
        assert self.n_max_expressions > self.expressions, f"Too many expressions concatinated by 'AND' given in query!"

        self.min_max_step = min_max
        self.predicates = list(self.min_max_step.keys())
        self.encoders = encoders
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
        self.n_total_columns = len(min_max)
        self.vector = np.zeros(self.n_total_columns * self.n_max_expressions)

    def __parse_expression(self, expression):
        expression = expression.strip().strip(';')
        predicate, operator, value = expression.split(" ")
        return predicate, operator, value

    def __normalize(self, predicate, value):
        min_val, max_val, step = self.min_max_step[predicate]
        if predicate in self.encoders.keys():
            value = self.encoders[predicate].transform([int(value)])[0]
        else:
            value = max(min_val, float(value))
        return (value - min_val + step) / (max_val - min_val + step)
    
    def vectorize(self):
        for expression in self.expressions:
            predicate, operator, value = self.__parse_expression(expression)
            normalized_value = self.__normalize(predicate, value)

            idx = self.predicates.index(predicate)
            end_idx = idx * self.n_max_expressions + self.operator_code_length
            self.vector[idx*self.n_max_expressions:end_idx] = self.operators[operator]
            self.vector[end_idx] = normalized_value
        return self.vector


def vectorize_query_test():
    sql_query = "SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE person_id <= 2559751 AND kind_id <= 2;"
    min_max_step = {'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)}
    encoders = {}
    vector_truth = np.array([1,0,1,0.25,1,0,1,0.4111042,0,0,0,0], dtype=float)
    vector_original = vectorize_query_original(sql_query, min_max_step, encoders)
    assert np.allclose(vector_original, vector_truth)

    vector_vectorizer = Vectorizer(sql_query, min_max_step, encoders).vectorize()
    assert np.allclose(vector_vectorizer, vector_truth),  f"{vector_vectorizer} not close \n{vector_truth}"


# meta data:
# for each column:
    # col[X] = (column_name, data_type)
    # min_max holds (min_value, max_value, 1) for each columns value range
    # encoders is dictonary. Only cols not of type integer have an encoder (LabelEncoder) mapped
# SQL query examples
# Postgres allows inner joins by where clauses:
# SELECT * FROM title t1,cast_info t2 WHERE t1.id=t2.movie_id AND person_id < 2006305 AND role_id >= 1 AND kind_id < 2;
if __name__ == "__main__":
    vectorize_query_test()


    



