def vectoize_query_original(query_str, min_max, encoders):
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

def vectorize_query_test(query_str, min_max, encoders):
    # assert new Vectorizer(...).vectorize(...) == vectorize_query_original(...)
    pass
     

from sklearn.preprocessing import LabelEncoder
class Vectorizer:
    def __init__(self):
        pass

    def vectorize(self,query_str, min_max, encoders):
        pass

# see example file for SQL query examples

#meta data:
# for each column:
    # col[X] = (column_name, data_type)
    # min_max holds (min_value, max_value, 1) for each columns value range
    # encoders is dictonary. Only cols not of type integer have an encoder (LabelEncoder) mapped

