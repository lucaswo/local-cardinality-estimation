from typing import Tuple, Dict, List
import yaml
import random
import csv
import datetime


class SQLGenarator:
    '''
    Class for generating SQL queries. Uses Meta Information from MetaCollector Step before.
    '''

    def __init__(self, config: str = None, debug:bool=False):
        """
        Initializer of the SQL Generator. Reads the needed parameters from the meta-information.yaml generated from the
        MetaCollector which was possibly executed before.

        It's also possible to pass an own meta.yaml file to skip the metaCollector Step.

        :param config: Config file which contains columns with their datatypes, tables, join_attributes, encodings,maximum cardinality
        min and max values of the columns with the step size.
        If None: meta-information.yaml generated from MetaCollector is used
        """

        if config is None:
            with open('meta_information.yaml', 'r') as file:
                self.q_set = yaml.safe_load(file)
                if debug == True:
                    print(self.q_set, '\n', type(self.q_set))
        else:
            with open(config, 'r') as file:
                self.q_set = yaml.safe_load(file)
                if debug == True:
                    print(self.q_set, '\n', type(self.q_set))

        for key, gen_params in self.q_set.items():

            if gen_params['columns'] is None:
                self.columns = []
            else:
                self.columns = gen_params['columns']

            if gen_params['table_names'] is None or len(gen_params['table_names']) == 0:
                raise ValueError('There has to be at least one table!')

            if gen_params['join_attributes'] is None and len(gen_params['tables'] > 1):
                raise ValueError('There are tables to join but no join attributes are given!')

    def write_sql(self, queries: List[Tuple[int, str]], file: str):
        with open(file, 'w+') as f:
            for q in queries:
                f.write(q[1] + '\n')

    def random_operator_value(self, range: List[int], val_type: str, encoding: dict = None) -> Tuple[str, str or int]:
        '''
        Function for random operator and value creation from a list of allowed operators and a range of values


        :param range: Min_max Value range and stepsize of a given column from meta_information
        :param type: Type of column, can be either integer or enumeration. when enumeration, then an encoding dict has to be given
        :return: Tuple consisting of operator and value as string or int
        '''

        # avoid values that zeroize the cardinality -> val<min (if val =min) or val>max (if val=max)
        val = None

        while (val == range[0] and op == '<') or (val == range[1] and op == '>') or not val:
            op = random.choice(['<', '>', '=', '<=', '>=', '!='])

            # create value according to datatype of column -> integer or string (then encoding dict given)
            if val_type == 'integer':
                val = random.randrange(start=range[0], stop=range[1] + 1, step=range[2])
            else:
                val = random.choice(encoding.values())

        return (op, val)

    def max_query_number(self,desired_number,entry):
        q_count = 1
        for min_max in entry:
            col = min_max[3]
            # count of possible values
            range = (col[1]-col[0]+1)/col[2]

            # max entries * number of operators -2 for <min or >max
            max = (range*6)-2
            q_count*=max

        if q_count < desired_number:
            raise ValueError('There are less queries to generate than desired! Maximum Quantity: %d < %d'%(q_count,desired_number))

        return q_count

    def generate_queries(self, qnumber: int = 10, save_readable: str = '../assets/queries.sql'):
        '''
        Generates given number of SQL Queries with given meta-information.
        Function, which models the hole process of query generation

        :param self:
        :param save_readable:Saves the generated SQL queries into a human friendly readable .sql file
        :param qnumber: Number of generated queries per meta-entry
        :return: list with queries as String
        '''


        all_queries = []
        header = ['querySetID', 'query', 'encodings', 'max_card', 'min_max_step']

        with open('../assets/queries.csv', 'w') as file:
            writer = csv.DictWriter(file, delimiter=';', fieldnames=header)
            writer.writeheader()

            for key, value in self.q_set.items():
                #calculate maximum number of possible queries, throw error if qnumber is higher
                print('Maximum Number of Queries to generate for entry %d: %d'%(key,self.max_query_number(qnumber,value['columns'])))
                # generate queries until there are 'number' of unique queries
                queries = []
                while len(queries) < qnumber:
                    # sort columns by name
                    columns = sorted(value['columns'], key=lambda index: index[0])
                    comparison = []

                    for col in columns:
                        op, val = self.random_operator_value(col[3], val_type=col[2])
                        comparison.append({'col': col, 'op': op, 'val': val})

                    # not formatted yet
                    # TODO: find duplicates and replace them
                    sql = 'SELECT COUNT(*) FROM {} WHERE {} AND {}'.format(
                        ','.join('{} {}'.format(v[0], v[1]) for v in value['table_names']),
                        ' AND '.join(value['join_attributes']),
                        ' AND '.join('{table}.{attr}{op}{val}'.format(table=c['col'][1], attr=c['col'][0], op=c['op'],
                                                                      val=c['val']) for c in comparison))

                    if sql not in queries:
                        writer.writerow({'querySetID': key, 'query': sql, 'encodings': [enc[4] for enc in value['columns']],
                                         'max_card': value['max_card'][0], 'min_max_step': [m[3] for m in value['columns']]})

                    queries.append((key, sql))
                    queries = list(set(queries))

                all_queries += queries

        # save as .sql in a readable format with choosen name
        self.write_sql(all_queries, save_readable)

        return queries

if __name__ == "__main__":
    gen = SQLGenarator(config='../assets/meta_information.yaml',debug=True)
    gen.generate_queries()
