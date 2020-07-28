from postgres_evaluator import PostgresEvaluator
from sql_generator import SQLGenerator
import csv
import numpy as np
from typing import Tuple, Dict, List
from database_connector import DatabaseConnector


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

    def __init__(self, meta_file_path: str = '../assets/meta_information.yaml'):
        self.meta = meta_file_path

    def get_queries(self, query_number: int = 10, database_connector: DatabaseConnector) -> str:
        '''
        Function for generating queries and their cardinalities if nullqueries are allowed.
        Saves generated queries in ../assets/queries_with_cardinalities.csv
        :return:
        '''
        generator = SQLGenerator(config=self.meta)
        print("generate ", query_number, " queries")
        generator.generate_queries(qnumber=query_number, save_readable='../assets/null_including_queries')

        # TODO: save file path as parameter in evaluator, so save file path can be passed trough
        evaluator = PostgresEvaluator(input_file_name='null_including_queries.csv', database_connector=database_connector)
        evaluator.get_cardinalities()

    def get_nullfree_queries(self, query_number: int, save_file_path: str, database_connector: DatabaseConnector):
        '''
        Function that generates given number queries and their cardinalities which are not zero.
        There will be less queries then requested, if unavoidable.
        :param query_number: number of queries to generate
        :param save_file_path: path to save the finished queries with their cardinalities
        :return: list of remained Queries
        '''
        # generate 150% queries
        query_number_with_buffer = int(query_number * 1.5)

        # number of distinct queries
        generator = SQLGenerator(config=self.meta)
        generator.generate_queries(qnumber=query_number_with_buffer, save_readable='../assets/nullfree_queries')

        evaluator = PostgresEvaluator(input_file_name='nullfree_queries.csv', database_connector=database_connector)
        evaluator.get_cardinalities()
        reduced_queries = self.reduce_queries(query_number=query_number)

        self.write_queries(queries=reduced_queries, save_file_path=save_file_path)

        return reduced_queries

    def reduce_queries(self, query_number):
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
            if len(query_n) > query_number:
                query_n = query_n[query_number]
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

    def write_queries(self, queries: List, save_file_path: str = '../assets/reduced_queries_with_cardinalities.csv'):
        '''
        function for writing the csv file with the reduced queries
        :param reduced_q: list of queries to write in a csv file
        :param save_file_path: file path, where to save the file
        :return:
        '''
        with open(save_file_path, 'w') as file:
            writer = csv.writer(file, delimiter=';')
            for q in queries:
                writer.writerow(q)

    def produce_queries(self, query_number: int = 10, nullqueries: bool = False,
                        save_file_path: str = '../assets/reduced_queries_with_cardinalities.csv',
                        database_connector: DatabaseConnector):
        '''
        Main function to produce the queries and return the correct csv file,
        depending if nullqueries are wanted or not

        :param meta: meta information, needed to generate queries
        :param nullqueries: decide whether to generate nullqueries or not, default: no nullqueries
        :param query_number: count of queries that are generated per meta file entry
        :return:
        '''
        if nullqueries == True:
            self.get_queries(query_number=query_number, database_connector=database_connector)
        else:
            self.get_nullfree_queries(save_file_path=save_file_path, query_number=query_number,
                                      database_connector=database_connector)
