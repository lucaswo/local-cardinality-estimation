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

        :param config: Dictionary which contains columns with their datatypes, tables, join_attributes, encodings,maximum cardinality
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
        with open(file,'w') as f:
            for q in queries:
                f.write(q[1]+'\n')

    def write_csv(self,key:int,value:Dict,compairison:List[Dict]):
        '''
        Function for writing the generated query into a csv file
        :param value: Dict Entry from Meta File
        :param key: integer for query_setID
        :param compairison: Attribute values for query
        :return:
        '''
        with open('queries.csv',mode ='a') as f:
            writer = csv.writer(f,delimiter=';')
            tables = ','.join('{} {}'.format(v[0],v[1])for v in value['table_names'])
            joins = ','.join(value['join_attributes'])
            att1 = '{}.{}'.format(compairison[0]['col'][1],compairison[0]['col'][0])+','+compairison[0]['op']+','+str(compairison[0]['val'])
            try:
                att2= '{}.{}'.format(compairison[1]['col'][1],compairison[1]['col'][0])+','+compairison[1]['op']+','+str(compairison[1]['val'])
            except:
                att2=''
            try:
                att3 = '{}.{}'.format(compairison[2]['col'][1],compairison[2]['col'][0])+','+compairison[2]['op']+','+str(compairison[2]['val'])
            except:
                 att3=''
            writer.writerow([key,tables,joins,att1,att2,att3])

    def random_operator(self):
        '''
        Function for random operator creation from a list of allowed operators
        :return: Operator from possible solutions: ['<','>','=','<=','>=']
        '''
        return random.choice(['<','>','=','<=','>=','!='])

    def random_value(self,range:List,type:str,encoding:dict = None) -> int:
        # TODO What to Do with other dtypes than Integer or double, float etc? Does'nt exist in joblight queries
        '''
        Function for finding a random value in the given min_max range.

        :param range: Min_max Value range and stepsize of a given column
        :param type: Type of column, can be either integer or enumeration. when enumeration, then an encoding dict has to be given
        :return: random legit value from range given with min, max and step size

        '''
        if type == 'integer':
            return random.randrange(start=range[0],stop=range[1]+1,step=range[2])

        else:
            return random.choice(encoding.keys())


    def generate_queries(self,number:int=10,save_readable:Tuple[bool,str]=[True,'queries.sql']):
        '''
        Generates given number of SQL Queries with given meta-information.
        Function, which models the hole process of query generation

        :param self:
        :param save_readable: If True: Saves the generated SQL queries into a human friendly readable txt file
        :param number: Number of generated queries per meta-entry
        :return: list with queries as String
        '''
        queries = []
        with open('queries.csv','w') as file:
            writer = csv.writer(file,delimiter= ';')
            writer.writerow(['querySetID','tables','join_attributes','attr_1,attr_2','attr_3'])
        for key,value in self.q_set.items():

            for q in range(number):
                #sort columns by name
                columns = sorted(value['columns'],key = lambda index : index[0])
                comparison = []
                for col in columns:
                    # if val = max  and op = >, the cardinality will be zero, same with min and < --> pretend such cases?
                    op = self.random_operator()
                    val = self.random_value(value['min_max_step'][col[0]],type=col[2])
                    comparison.append({'col':col, 'op':op,'val':val})


                #not formatted yet
                # TODO: find duplicates and replace them
                sql = 'SELECT COUNT(*) FROM {} WHERE {} AND {};'.format(','.join('{} {}'.format(v[0],v[1])for v in value['table_names']),
                                                                   ' AND '.join(value['join_attributes']),
                                                                   ' AND '.join('{}.{}{}{}'.format(c['col'][1],c['col'][0],c['op'],c['val']) for c in comparison))
                self.write_csv(key,value,comparison)

                print(key,sql)
                queries.append((key,sql))
        if save_readable[0]:
            self.write_sql(queries,save_readable[1])


        return queries


gen = SQLGenarator()
gen.generate_queries()

