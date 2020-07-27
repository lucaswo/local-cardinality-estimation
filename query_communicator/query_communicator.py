from query_communicator.postgres_evaluator.postgres_evaluator import PostgresEvaluator
from query_communicator.sql_generator.sql_generator import SQLGenerator
import csv
import numpy as np
from typing import Tuple, Dict, List




class QueryCommunicator():
    '''
    Class for oberserving the generation and evaluation of queries, in order to have
    nullqueryfree set of queries if needed.
    Manages the communication between Evaluator and SQL Generator
    to get the required amount of queries if possible.
    The SQL_Generator itself is not able to find nullqueries, that are caused by a valid combination of attributes,
    which just don't match any data of the database.
    Vice Versa, the Evaluator is not able to generate new queries, if there are nullqueries.
    '''

    def __init__(self, meta: str = '../assets/meta_information.yaml', query_number: int = 10,
                 nullqueries: bool = False):
        '''

        :param meta: meta information, needed to generate queries
        :param nullqueries: decide whether to generate nullqueries or not, default: no nullqueries
        :param query_number: count of queries that are generated per meta file entry
        '''
        if not meta:
            raise ValueError('No meta file given, but at least needed!')
        else:
            self.meta = meta
            self.nullqueries = nullqueries
            self.query_number = query_number

    def get_queries(self) -> str:
        '''
        Function for generating queries and their cardinalities if nullqueries are allowed.
        Saves generated queries in ../assets/queries_with_cardinalities.csv
        :return:
        '''
        generator = SQLGenerator(config=self.meta)
        print("generate ", self.query_number, " queries")
        generator.generate_queries(qnumber=self.query_number, save_readable='null_including_queries')

        evaluator = PostgresEvaluator(input_file_name='null_including_queries.csv')
        evaluator.get_cardinalities()

    def get_nullfree_queries(self, save_file_path: str):
        '''
        Function for generation an evaluation of the queries when nullfree. Communication
        is bounded by a number of Iteration in order to avoid an endless process of generation an Evaluation.
        There will be less queries then deserved, if unavoidable.
        :return: list of remained Queries
        '''
        # generate 150% queries
        generate = int(self.query_number * 1.5)

        # number of distinct queries
        generator = SQLGenerator(config=self.meta)
        generator.generate_queries(qnumber=generate, save_readable='nullfree_queries')

        evaluator = PostgresEvaluator(input_file_name='nullfree_queries.csv')
        evaluator.get_cardinalities()
        reduced_queries = self.reduce_queries()

        self.write_queries(reduced_q=reduced_queries, save_file_path=save_file_path)

        return reduced_queries

    def reduce_queries(self):
        '''
        Reduces genrated queries to the requested number of queries
        :return:DataFrame with reduced query sets
        '''
        with open('../assets/queries_with_cardinalities.csv', 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            queries = np.array([r for r in csv_reader])
            setIDs = set(queries[1:, 0])
            reduced_queries = []
            reduced_queries.append(queries[0].tolist())
        for id in setIDs:
            query_n = np.where(queries[:, 0] == id)
            if len(query_n) > self.query_number:
                query_n = query_n[:self.query_number]
                rq = [queries.tolist()[i] for i in query_n[0].tolist()]
                for q in rq:
                    reduced_queries.append(q)
                print('%d queries have been generated for query set %d!' % (len(query_n[0]), int(id)))
            else:
                rq = [queries.tolist()[i] for i in query_n[0].tolist()]
                for q in rq:
                    reduced_queries.append(q)
                print('%d queries have been generated for query set %d!' % (len(query_n[0]), int(id)))

        return reduced_queries

    def write_queries(self, reduced_q: List, save_file_path: str = '../assets/reduced_queries_with_cardinalities.csv'):
        '''
        function for writing the csv file with the reduced queries
        :param reduced_q: list of queries to write in a csv file
        :param save_file_path: file path, where to save the file
        :return:
        '''
        with open(save_file_path, 'w') as file:
            writer = csv.writer(file, delimiter=';')
            for q in reduced_q:
                writer.writerow(q)

    def produce_queries(self,save_file_path:str = '../assets/reduced_queries_with_cardinalities.csv'):
        '''
        Main function to produce the queries and return the correct csv file,
        depending if nullqueries are wanted or not.
        :return:
        '''
        if self.nullqueries == True:
            self.get_queries()
        else:
            self.get_nullfree_queries(save_file_path=save_file_path)

