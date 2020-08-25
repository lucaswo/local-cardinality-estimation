# MetaCollector
This module uses the output of the QueryParser and adds additional meta information from the database which is needed to generate the SQL-Queries. For the connection to the DBMS the DatabaseConnector is used.

## Usage
Normally this submodule is called from main.py, however you may want to use it separately:

1. You need a DatabaseConnector with an established connection to the DBMS.

2. You need the output of the QueryParser like:

    ```
   0:
      join_attributes:
      - t.id=mc.movie_id
      - t.id=mi_idx.movie_id
      selection_attributes:
      - mc.company_type_id
      - mi_idx.info_type_id
      - t.production_year
      table_names:
      - - movie_companies
        - mc
      - - movie_info_idx
        - mi_idx
      - - title
        - t
   1:
      join_attributes:
      - t.id=mc.movie_id
      - t.id=mk.movie_id
      selection_attributes:
      - mc.company_type_id
      - mk.keyword_id
      - t.production_year
      table_names:
      - - movie_companies
        - mc
      - - movie_keyword
        - mk
      - - title
        - t
   ```

3. You can save the results to file like:

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
        - ''
      - - info_type_id
        - mi_idx
        - integer
        - - 1
          - 113
          - 1
        - {}
        - ''
      - - production_year
        - t
        - integer
        - - 1874
          - 2115
          - 1
        - {}
        - ''
      join_attributes:
      - t.id=mc.movie_id
      - t.id=mi_idx.movie_id
      max_card: 134952836
      table_names:
      - - movie_companies
        - mc
      - - movie_info_idx
        - mi_idx
      - - title
        - t
    ```
