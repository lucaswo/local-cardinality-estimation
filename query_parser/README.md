# QueryParser
This module parses a given query file and extracts the information for the joins. Based on the different joins the QueryParser creates different QuerySets with their QuerySetIDs.

## Usage
Normally this module is called from `main.py`, however you may want to use it separately:

 1. You need a file containing sql queries. There are some possibilities to format such a file:
    
    1.1 An sql file can have the following two formats:
         
        SELECT COUNT(*) FROM movie_companies mc,title t,movie_info_idx mi_idx WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id=112 AND mc.company_type_id=2;
        
        or 
        
        SELECT COUNT(*) From movie_companies mc INNER JOIN title t On (t.id=mc.movie_id) Inner JOIN movie_info_idx mi_idx on (t.id=mi_idx.movie_id) WHERE mi_idx.info_type_id=112 AND mc.company_type_id=2;

    1.2 A csv file can have the following formats (Where '#' is the outer_separator and ',' the inner_separator. These separators can be customized):
        
        movie_companies mc,title t,movie_info_idx mi_idx#t.id=mc.movie_id,t.id=mi_idx.movie_id#mi_idx.info_type_id,=,112,mc.company_type_id,=,2#715
        
    1.3 A tsv file is the same as a csv file, but with tab or '\t' as inner_separator.
    
 2. The result is saved as .yaml file like:
    
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
       