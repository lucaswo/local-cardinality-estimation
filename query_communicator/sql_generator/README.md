# SQL Generator
 This  is a sub(sub)module for genrating sql queries, given a meta_information file.
 It's typically called from the [Query communicator](https://gitlab.hrz.tu-chemnitz.de/ddsg/ml4sys/local-cardinality-estimation/-/tree/master/query_communicator),
 which manages the hole process of generating queries and evaluating them.
 However, you can use the geneartor seperately to genrate queries without duplicates. 
    

## Usage
1. To initialize the generator, you need a meta_information file in .yaml file format.
The file contains the columns you want to join, the attributes you want to select, the stepsize and min/max values of the columns,
and so on. 
You can have more than one entry to generate queries. 
Note, that in the end there will be an own model for every entry in the meta_file and query_set respectively.
    
    1. If you want to generate more than one query set, note that there has to be an own entry with own ID
in the meta file
    1. the columns will need a synonym as second argument

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

2. Given the meta File:
    1. Instantiate a new sql-generator with meta File
        ```python 
       generator = SQLGenarator(config='meta_information_test.yaml')
        ```
    1. Generate the desired number of queries. Note that the default is 10(queries per entry in meta file)
        ```python
       generator.generate_queries(qnumber=100, save_readable = 'queries')
        ```
       You also have the possibility to specify the filename for the queries.
       Note that you just specify the name (e.g.'movie_queries') and not hte format. 
       The Generator will safe a csv file (usable for vectorizer) and a human readable sql file with the specified name 
       in the assets directory.
       Default is *queries.csv/queries.sql*.
       
    
    