# Vectorizer
This submodule uses the output of the [postgres-evaluater](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/postgres-evaluator) submodule to encode the SQL query into a vector and also normalizes the cardinalities given. Vector and cardinalities are input to the [estimator](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/estimator) submodule.

## Usage
Normally this submodule is called from `main.py`, however you may want to use it separately:

1. First, you need a CSV file (semicolon separated) with the queries, meta data and estimated and true cardinalities. E.g. `queries_with_cardinalities.csv`:
```
querySetID;query;encodings;max_card;min_max_step;estimated_cardinality;true_cardinality
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<2 AND mi_idx.info_type_id=107 AND t.production_year>2009;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];197595;1152438
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id=1 AND mi_idx.info_type_id<80 AND t.production_year<=1894;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];30903;1416
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=1 AND mi_idx.info_type_id!=62 AND t.production_year<=2094;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];70814563;94395272
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id>=2 AND mi_idx.info_type_id>45 AND t.production_year<1939;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];652856;197336
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND mi_idx.info_type_id<=32 AND t.production_year<=1918;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];1733520;1054332
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id>=2 AND mi_idx.info_type_id<54 AND t.production_year<=2097;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];81368212;30387086
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=2 AND mi_idx.info_type_id>=38 AND t.production_year<1896;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];362;2501
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND mi_idx.info_type_id<=66 AND t.production_year=2026;[];134163798;[[1, 2, 1], [1, 113, 1], [1878, 2115, 1]];42743;14
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id=1 AND mk.keyword_id>=117023 AND t.production_year<=1894;[];63056995;[[1, 2, 1], [1, 236627, 1], [1878, 2115, 1]];436;26
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id>=1 AND mk.keyword_id<35239 AND t.production_year<=1896;[];63056995;[[1, 2, 1], [1, 236627, 1], [1878, 2115, 1]];18935;2117
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id<2 AND mk.keyword_id<=35888 AND t.production_year!=2020;[];63056995;[[1, 2, 1], [1, 236627, 1], [1878, 2115, 1]];14700094;40290318
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id=2 AND mk.keyword_id>196933 AND t.production_year=1907;[];63056995;[[1, 2, 1], [1, 236627, 1], [1878, 2115, 1]];101;2
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id!=1 AND mk.keyword_id<19712 AND t.production_year<1980;[];63056995;[[1, 2, 1], [1, 236627, 1], [1878, 2115, 1]];2728149;1552444
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id>1 AND mk.keyword_id<=186471 AND t.production_year<2110;[];63056995;[[1, 2, 1], [1, 236627, 1], [1878, 2115, 1]];24858350;14307838
```
> `encodings` and `min_max_step` are arrays in string representation
> `querySetID` is mandatory, since it is used for automatically determine the length of the output vector. All vectors of the same querySet must have the same length.

* Given one or more such CSV files:
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
   vectorizer.save("/path/to/directory/matrix", "csv")
   ```
   
   E.g.: `matrix.csv`:
   ```
      0,1,0,0,1,0,0,1,0.946902654867256666,0,1,0,0.554621848739495826,134163798,0.651576470484740322,0.745803338052605902
      0,0,0,1,0.5,1,0,0,0.707964601769911495,1,0,1,0.0714285714285714246,134163798,0.552436280887511844,0.387697419969840307
      0,1,0,1,0.5,1,1,0,0.548672566371681381,1,0,1,0.911764705882352922,134163798,0.9658556575333751,0.981214080678194711
      0,0,1,1,1,0,1,0,0.39823008849557523,1,0,0,0.260504201680672287,134163798,0.715437781548679874,0.651506384900475854
      0,0,0,1,1,1,0,1,0.283185840707964598,1,0,1,0.172268907563025209,134163798,0.767619189647782418,0.7410491653476593
      0,0,1,1,1,1,0,0,0.477876106194690287,1,0,1,0.924369747899159711,134163798,0.973278750577822982,0.920647733098342469
      0,1,0,1,1,0,1,1,0.336283185840707988,1,0,0,0.0798319327731092376,134163798,0.314815867372580604,0.418093768713123426
      0,0,0,1,1,1,0,1,0.584070796460177011,0,0,1,0.626050420168067223,134163798,0.569767811257714807,0.141016173481957524
      1,0,0,1,0.5,0,1,1,0.494546269022554497,1,0,1,0.0714285714285714246,63056995,0.338407275959206999,0.181413043100808496
      1,0,1,1,0.5,1,0,0,0.148922143288804737,1,0,1,0.0798319327731092376,63056995,0.548386100028571355,0.426389049816630394
      1,1,0,0,1,1,0,1,0.151664856504118289,1,1,0,0.600840336134453756,63056995,0.918918617255151005,0.975059073360462714
      1,0,0,1,1,0,1,0,0.832250757521331042,0,0,1,0.126050420168067223,63056995,0.256973066165060549,0.0385949089828031763
      1,1,1,0,0.5,1,0,0,0.0833041030820658723,1,0,0,0.432773109243697496,63056995,0.825139509620369638,0.793747135768320677
      1,0,1,0,0.5,1,0,1,0.7880377133632257,1,0,0,0.978991596638655426,63056995,0.948169897872308987,0.917412655803315658
   ```
* Whole code:
  ```python
   vectorizer = Vectorizer()
   vectorizer.add_queries_with_cardinalities("queries_with_cardinalities_1.csv")
   vectorizer.add_queries_with_cardinalities("queries_with_cardinalities_2.csv")
   vectors = vectorizer.vectorize()
   for vec in vectors:
      vectorized_query, cardinality_estimation, cardinality_true = vec[:-2], vec[-2], vec[-1]
   vectorizer.save("/path/to/directory/")
   ```