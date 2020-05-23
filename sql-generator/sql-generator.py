from typing import Tuple, Dict, List
import yaml
import random
import csv
import datetime
class SQLGenarator:
    '''
    Class for generating SQL queries. Uses Meta Information from MetaCollector Step before.
    '''

    def __init__(self, config:str=None):
        """
        Initializer of the SQL Generator. Reads the needed parameters from the meta-information.yaml generated from the
        MetaCollector which was possibly executed before.

        It's also possible to pass an own meta.yaml file to skip the metaCollector Step.

        :param config: Config file which contains columns with their datatypes, tables, join_attributes, encodings,maximum cardinality
        min and max values of the columns with the step size.
        If None: meta-information.yaml generated from MetaCollector is used
        """

        if config is None:
            with open('meta_information.yaml','r') as file:
                self.q_set = yaml.safe_load(file)
                print(self.q_set,'\n',type(self.q_set))

        else:
            with open(config,'r') as file:
                self.q_set = yaml.safe_load(file)
                print(self.q_set, '\n', type(self.q_set))

        for key,gen_params in self.q_set.items():

            if gen_params['columns'] is None:
                self.columns = []
            else:
                self.columns = gen_params['columns']

            if gen_params['table_names'] is None or len(gen_params['table_names'])== 0:
                raise ValueError('There has to be at least one table!')

            if len(gen_params['columns']) != len(gen_params['min_max_step']):
                raise IndexError('For every given Column there has to be exactly one min_max_step definitition!')

            if gen_params['join_attributes'] is None and len(gen_params['tables'] > 1):
                raise ValueError('There are tables to join but no join attributes are given!')



    def write_sql(self, queries:List[Tuple[int,str]], file:str):
        with open(file,'w+') as f:
            for q in queries:
                f.write(q[1]+'\n')


    def random_operator_value(self,range:List,val_type:str,encoding:dict = None) -> Tuple:
        '''
        Function for random operator and value creation from a list of allowed operators and a range of values


        :param range: Min_max Value range and stepsize of a given column from meta_information
        :param type: Type of column, can be either integer or enumeration. when enumeration, then an encoding dict has to be given
        :return: Tuple consisting of operator and value
        '''

        # avoid values that zeroize the cardinality -> val<min (if val =min) or val>max (if val=max)
        val = None

        while (val == range[0] and op== '<') or (val == range[1] and op== '>') or not val:
            op = random.choice(['<','>','=','<=','>=','!='])

            # create value according to datatype of column -> integer or string (then encoding dict given)
            if val_type == 'integer':
                val = random.randrange(start=range[0], stop=range[1] + 1, step=range[2])
            else:
                val = random.choice(encoding.values())

        return (op,val)


    def generate_queries(self,number:int=10,save_readable:Tuple[bool,str]=[True,'../assets/queries.sql']):
        '''
        Generates given number of SQL Queries with given meta-information.
        Function, which models the hole process of query generation

        :param self:
        :param save_readable: If True: Saves the generated SQL queries into a human friendly readable txt file
        :param number: Number of generated queries per meta-entry
        :return: list with queries as String
        '''
        all_queries = []
        header = ['querySetID','query','encodings','max_card','min_max_step']

        with open('../assets/queries.csv','w') as file:
            writer = csv.DictWriter(file,delimiter= ';',fieldnames=header)
            writer.writeheader()

            for key,value in self.q_set.items():
                # generate queries until there are 'number' of unique queries
                queries = []
                while len(queries)< number:
                    #sort columns by name
                    columns = sorted(value['columns'],key = lambda index : index[0])
                    comparison = []
                    
                    for col in columns:
                        op,val = self.random_operator_value(value['min_max_step'][col[0]],val_type=col[2])
                        comparison.append({'col':col, 'op':op,'val':val})

                    #not formatted yet
                    # TODO: find duplicates and replace them
                    sql = 'SELECT COUNT(*) FROM {} WHERE {} AND {}'.format(','.join('{} {}'.format(v[0],v[1])for v in value['table_names']),
                                                                       ' AND '.join(value['join_attributes']),
                                                                       ' AND '.join('{}.{}{}{}'.format(c['col'][1],c['col'][0],c['op'],c['val']) for c in comparison))

                    if sql not in queries:
                        writer.writerow({'querySetID':key,'query':sql,'encodings':value['encodings'],'max_card':value['max_card'][0],'min_max_step':value['min_max_step']})

                    print(key,sql)
                    queries.append((key,sql))
                    queries=list(set(queries))

                all_queries+=queries

        #save as .sql in a readable format with choosen name
        if save_readable[0]:
            self.write_sql(all_queries,save_readable[1])


        return queries


gen = SQLGenarator(config='../assets/meta_information.yaml')
gen.generate_queries()

