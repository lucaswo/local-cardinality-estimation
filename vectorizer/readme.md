# Vectorizer
This submodule uses the output of the [postgres-evaluater](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/postgres-evaluator) submodule to encode the SQL query into a vector and also normalizes the cardinalities given. Vector and cardinalities are input to the [estimator](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/estimator) submodule.

## Usage
Normally this submodule is called from `main.py`, however you may want to use it separately:

1. First, you need a CSV file (semicolon separated) with the queries, meta data and estimated and true cardinalities. E.g. `queries_with_cardinalities.csv`:
```
querySetID;query;encodings;max_card;min_max_step;estimated_cardinality;true_cardinality
999;SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE person_id != 62656 AND kind_id = 1;{};62143897;{'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)};6347836;63143871
777;SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE role_id = 4 AND kind_id > 5;{};62143897;{'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)};65836;61143871
999;SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE kind_id <= 8 AND person_id > 111;{};62143897;{'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)};636;4214
777;SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE person_id >= 6226;{};62143897;{'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)};65836;52143871
777;SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE role_id = 10;{};62143897;{'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)};634756;1478
999;SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE person_id >= 26526 AND kind_id > 3 AND role_id = 5;{};62143897;{'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)};475836;82171
999;SELECT COALESCE(SUM(count), 0) FROM tmpview_cube WHERE kind_id = 8;{};62143897;{'kind_id': (1, 8, 1), 'person_id': (1, 6226526, 1), 'role_id': (1, 11, 1)};634736;143871
```
> `encodings` and `min_max_step` are dictionaries in string representation
> `querySetID` is not mandatory, since it is not used by the vectorizer i.e. each line could also start by a leading `';'`

2. Given one or more such CSV files:
   1. Instantiate a new vectorizer
   ```python
   vectorizer = Vectorizer()
   ```
   2. Add as many CSV files with queries, meta data and cardinalities as you want
   ```python
   vectorizer.add_queries_with_cardinalities("queries_with_cardinalities_1.csv")
   vectorizer.add_queries_with_cardinalities("queries_with_cardinalities_2.csv")
   ```
   3. Vectorize all queries within the CSV files and normalize the cardinalities
   ```python
   vectors = vectorizer.vectorize()
   ```
   4. The resulting matrix contains for each row the vector, normalized estimated cardinality and normalized true cardinality
   ```python
   for vec in vectors:
      vectorized_query, cardinality_estimation, cardinality_true = vec[:-2], vec[-2], vec[-1]
   ```
   5. You may now want to save the matrix as `.npy` and `.csv` file
   ```python
   vectorizer.save("/path/to/directory/")
   ```
   E.g.: `matrix.csv`:
   ```
   1,1,0,0.0100627540943376767,0,0,1,0.125,0,0,0,0,0.872870251903713812,1.00088956294163434
   0,0,1,0.363636363636363646,0,1,0,0.625,0,0,0,0,0.618274998565575662,0.999095958743106749
   1,0,1,1,0,1,0,1.78269551913860144e-05,0,0,0,0,0.359722029019480971,0.465098061991732536
   0,1,1,0.000999915522716840824,0,0,0,0,0,0,0,0,0.618274998565575662,0.99022310799082347
   0,0,1,0.909090909090909061,0,0,0,0,0,0,0,0,0.744554102625487046,0.40671273777879452
   0,1,1,0.00426016048114149018,0,1,0,0.375,0,0,1,0.45454545454545453,0.728495701543812491,0.63062585370190849
   0,0,1,1,0,0,0,0,0,0,0,0,0.744552346775326779,0.661838769414114569
   1,1,0,1,0,0,0,0,0,0,0,0,1.0011817624038688,0.99999997668516305
   ```
3. Whole code:
  ```python
   vectorizer = Vectorizer()
   vectorizer.add_queries_with_cardinalities("queries_with_cardinalities_1.csv")
   vectorizer.add_queries_with_cardinalities("queries_with_cardinalities_2.csv")
   vectors = vectorizer.vectorize()
   for vec in vectors:
      vectorized_query, cardinality_estimation, cardinality_true = vec[:-2], vec[-2], vec[-1]
   vectorizer.save("/path/to/directory/")
   ```
   