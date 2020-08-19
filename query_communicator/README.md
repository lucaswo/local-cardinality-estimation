# Query Communicator
This Module takes the Meta-Information, produced from [Meta_Collector](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/meta_collector)
It organizes the the generation and Evaluation of the queries, that are needed for the model training.
For that, it firstly generates random queries, given the information from the meta informations and secondly it fetches the true cardinality for the queries.

Normally, this module is a part of the hole process pipeline, called from the 'main.py' and must not be used as a standalone.
Anyway, if you want to use it seperatly, here are the needed instructions and explanations.

## Usage
1. Set up database connection 
For generating queries with their cardinality, you will need a Connection to the Database. Therefore, use the Module [DatabaseConnector](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/database_connector)
Initialize Connection:
You will need a config file (.yaml) from your Database to initialize the connection.
*Example File*
```
# Postgres
db_name: "imdb"
user: "postgres"
password: "postgres"
host: "localhost"
port: "5432"
```
Then call the folling functions:
```python
db_conn = DatabaseConnector(database=Database.POSTGRES)
db_conn.connect(config_file_path=config_file_path)
```
Choose the Database you use as parameter.

2. Set up the Communicator
To iniatialize the Communicator, you need a valid .yaml File as input with the corresponding meta Information.

The input file should look like this:
*Example file*
 ```
0:
  columns:
  - - company_type_id
    - mc
    - integer
    - - 1
      - 2
      - 1
    - {}
  - - info_type_id
    - mi_idx
    - integer
    - - 1
      - 113
      - 1
    - {}
  - - production_year
    - t
    - integer
    - - 1874
      - 2115
      - 1
    - {}
  join_attributes:
  - t.id=mc.movie_id
  - t.id=mi_idx.movie_id
  max_card:
  - 134163798
  table_names:
  - - movie_companies
    - mc
  - - movie_info_idx
    - mi_idx
  - - title
    - t
```
As you can see, you must specify the tables and corresponding columns you want to join. Normally this file should be generated in the course of the *main.py* execution. For more information on that process of collection meta information and the result file of that, look here: [Meta_Collector](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/meta_collector)

Now you can initialize the communicator and let it produce the queries:

```python
communicator = QueryCommunicator(meta_file_path=input_file_path)
communicator.produce_queries(query_number=query_number, nullqueries=nullqueries, save_file_path=save_file_path,
                                 database_connector=db_conn)
```
You have to specify...
	- the meta file described above
	- if you want to have queries with cardinality 0 in your trainingset or not, default is False
	- number of Queries you want to generate per QuerySet (-ID) in the Meta File
	- The Database connection enabled before

**HINT for query generation:**
Sometimes you want to generate more queries than possible, in that case the number of queries will be turned down to the maximum.

Anyway, if you want to eliminate queries with cardinality zero, it's possible you get less queries then requestet. 
The Submodule *SQLGenerator* will generate 200% queries. During the evaluation, evrything with cardinality 0 or the queries that are to much, will be ignored. Sometimes there are only a few queries whose cardinality is not zero in the generated Queries. So the desired number is not reachable. You will get a feedback from the module, how many queries were generated for each SetID.

3. Close Database Connection
```python
db_conn.close_database_connection()
```


