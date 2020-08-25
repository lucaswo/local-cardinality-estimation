# Database Evaluator
This sub(sub)module is part of the [query communicator](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/query_communicator) and uses the output from the [sql-generator](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/query_communicator/sql_generator) submodule to evaluate the generated queries against a database (currently only PostgreSQL is supported) und get the corresponding estimated and true cardinality of each query. Queries and cardinalities are input to the [vectorizer](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/vectorizer) submodule.

## Usage
Usually this submodule is called from the [query communicator](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/query_communicator) and does not communicate directly with the main.py, however you may want to use it seperatly:

1. First, you need a CSV file (semicolon separated) with the queries and meta data.

```
querySetID;query;encodings;max_card;min_max_step
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<2 AND mi_idx.info_type_id>=30 AND t.production_year>=2050;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<1 AND mi_idx.info_type_id=71 AND t.production_year<=2109;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<2 AND mi_idx.info_type_id=107 AND t.production_year>2009;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id=1 AND mi_idx.info_type_id<80 AND t.production_year<=1894;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=1 AND mi_idx.info_type_id!=62 AND t.production_year<=2094;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id>=2 AND mi_idx.info_type_id>45 AND t.production_year<1939;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND mi_idx.info_type_id<=32 AND t.production_year<=1918;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id>=2 AND mi_idx.info_type_id<54 AND t.production_year<=2097;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=2 AND mi_idx.info_type_id>=38 AND t.production_year<1896;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
0;SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mi_idx.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND mi_idx.info_type_id<=66 AND t.production_year=2026;{};134163798;{'company_type_id': [1, 2, 1], 'info_type_id': [1, 113, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id=1 AND mk.keyword_id>=117023 AND t.production_year<=1894;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id<1 AND mk.keyword_id>=134591 AND t.production_year<2015;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id>=1 AND mk.keyword_id<35239 AND t.production_year<=1896;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id<2 AND mk.keyword_id<=35888 AND t.production_year!=2020;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id<=1 AND mk.keyword_id=20641 AND t.production_year=1889;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id>2 AND mk.keyword_id!=104628 AND t.production_year>=1940;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id=1 AND mk.keyword_id!=176282 AND t.production_year=2055;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id=2 AND mk.keyword_id>196933 AND t.production_year=1907;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id!=1 AND mk.keyword_id<19712 AND t.production_year<1980;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
1;SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mc.movie_id AND t.id=mk.movie_id AND mc.company_type_id>1 AND mk.keyword_id<=186471 AND t.production_year<2110;{};63056995;{'company_type_id': [1, 2, 1], 'keyword_id': [1, 236627, 1], 'production_year': [1878, 2115, 1]}
```

Alternativly also a SQL-file with just the queries would work as input, but be aware that you have to add the meta data later then for further processing.  

2. Initialize the Database Evaluator and call the get_cardinalities() function. 

```python
evaluator = DatabaseEvaluator(input_file_path=inter_file_path, database_connector=database_connector)
evaluator.get_cardinalities(eliminate_null_queries=False, save_file_path=save_file_path.split(".")[0],
                            query_number=query_number)
   ```

Note, that *inter_file_path* holding just the same string as *save_file_path* with a additional "inter_"-praefix (file used in the SQL-Generator module).  Per default all intermediate products are saved in the asset folder. Be also beware of the hints in the parent module (QueryCommunicator) [documentation](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/blob/master/query_communicator/README.md).
