# Vectorizer
This submodule uses the output of the [postgres-evaluater](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/postgres-evaluator) submodule to encode the SQL query into a vector and also normalizes the cardinalities given. Vector and cardinalities are input to the [estimator](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/estimator) submodule.

## Usage
This submodule is called from `main.py`

### Loop Mode
1. Instantiate an Vectorizer class: `vectorizer = Vectorizer("path/to/meta.yaml")`
2. Within a loop:
   1. Call `set_query`, `set_cardinality_estimation`, `set_cardinality_truth`
   2. Call `vectorize`