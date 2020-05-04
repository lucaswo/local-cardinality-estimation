from typing import Tuple, Dict
import yaml
import random


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
                gen_params = yaml.safe_load(file)
                print(gen_params)

        else:
            with open(config,'r') as file:
                gen_params = yaml.safe_load(file)

        if gen_params['columns'] is None:
            self.columns = []
        else:
            self.columns = gen_params['columns']

        if gen_params['tables'] is None or len(gen_params['tables'])== 0:
            raise ValueError('There has to be at least one table!')

        if len(gen_params['columns']) != len(gen_params['min_max_step']):
            raise IndexError('For every given Column there has to be exactly one min_max_step definitition!')

        if gen_params['join_attributes'] is None and len(gen_params['tables'] > 1):
            raise ValueError('There are tables to join but no join attributes given!')

        self.encodings = gen_params['encodings']
        self.join_attributes = gen_params['join_attributes']
        self.max_card = gen_params['max_card']
        self.min_max_step = gen_params['min_max_step']
        self.tables = gen_params['tables']

    def random_operator(self):
        '''
        Function for random operator creation from a list of allowed operators
        :return: Operator from possible solutions: ['<','>','=','<=','>=']
        '''
        return random.choice(['<','>','=','<=','>=','!='])

    def random_value(self,range):
        # TODO What to Do with other dtypes than Integer or double, float etc? Does'nt exist in joblight queries
        '''
        Function for finding a random value in the given min_max range.

        :param range: Min_max Value range and stepsize of a given column
        :return: random legit value from range given with min, max and step size
        '''
        value = random.randrange(range[0],range[1],range[2])
        return value


    def generate_queries(self,number:int=10,save_readable:Tuple[bool,str]=[True,'queries.txt']):
        '''
        Generates given number of SQL Queries with given meta-information.
        Function, which models the hole process of query generation

        :param self:
        :param save_readable: If True: Saves the generated SQL queries into a human friendly readable txt file
        :return: list with queries as String
        '''
        queries = []
        for q in range(number):
            compairison_num = random.randint(1,len(self.columns))
            compairisons = []
            columns = self.columns
            for i in compairison_num:
                col = random.choice(columns)
                columns.remove(col)
                op = self.random_operator()
                val = self.random_value(self.min_max_step)
                compairisons.append((col,op,val))

                #TODO: List, needed for the joblight csv format
                #TODO: get belonging table of the
                # column from meta data(does not exist now) and change col[0] to '.'join([col[2],col[0]])
            #not formatted yet
            sql = 'SELECT COUNT(*) FROM {} WHERE {} {}'.format(','.join(c[0] for c in self.columns))
            queries.append(sql)

        return []


gen = SQLGenarator()
gen.generate_queries()

