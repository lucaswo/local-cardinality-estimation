import os.path as path

from database_connector import DatabaseConnector
from .database_evaluator import DatabaseEvaluator
from .sql_generator import SQLGenerator


class QueryCommunicator:
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

    def get_queries(self, database_connector: DatabaseConnector, save_file_path: str, query_number: int):
        '''
        Function for generating queries and their cardinalities if nullqueries are allowed.
        Saves generated queries in ../assets/queries_with_cardinalities.csv
        :param query_number: number of queries to generate
        :param save_file_path: path to save the finished queries with their cardinalities
        :param database_connector: Handles the database connection to the desired database.
        :return:
        '''

        # intermediate file path for the csv from the generator, which will be evaluated and reduced afterwards
        inter_file_path = path.join(path.dirname(save_file_path), 'inter_' + path.basename(save_file_path))

        generator = SQLGenerator(config=self.meta)
        print("generate ", query_number, " queries")
        generator.generate_queries(qnumber=query_number, save_readable=inter_file_path.split(".")[0])

        evaluator = DatabaseEvaluator(input_file_path=inter_file_path, database_connector=database_connector)
        evaluator.get_cardinalities(eliminate_null_queries=False, save_file_path=save_file_path.split(".")[0],
                                    query_number=query_number)

    def get_nullfree_queries(self, query_number: int, save_file_path: str, database_connector: DatabaseConnector):
        '''
        Function that generates given number queries and their cardinalities which are not zero.
        There will be less queries then requested, if unavoidable.
        :param query_number: number of queries to generate
        :param save_file_path: path to save the finished queries with their cardinalities
        :param database_connector: Handles the database connection to the desired database.
        :return: list of remained Queries
        '''

        # generate 150% queries
        query_number_with_buffer = int(query_number * 2.0)

        # intermediate file path for the csv from the generator, which will be evaluated and reduced afterwards
        inter_file_path = path.join(path.dirname(save_file_path), 'inter_' + path.basename(save_file_path))

        # number of distinct queries
        generator = SQLGenerator(config=self.meta)
        generator.generate_queries(qnumber=query_number_with_buffer, save_readable=inter_file_path.split(".")[0])

        evaluator = DatabaseEvaluator(input_file_path=inter_file_path, database_connector=database_connector)
        evaluator.get_cardinalities(eliminate_null_queries=True, save_file_path=save_file_path.split(".")[0],
                                    query_number=query_number)

    def produce_queries(self, database_connector: DatabaseConnector, query_number: int = 10, nullqueries: bool = False,
                        save_file_path: str = 'assets/reduced_queries_with_cardinalities.csv'):
        '''
        Main function to produce the queries and return the correct csv file,
        depending if nullqueries are wanted or not

        :param save_file_path: Path to save the finished query file
        :param nullqueries: decide whether to generate nullqueries or not, default: no nullqueries
        :param query_number: count of queries that are generated per meta file entry
        :param database_connector: Connector for the database connection, depending on the database system you are using
        :return:
        '''

        if nullqueries:
            self.get_queries(save_file_path=save_file_path, query_number=query_number,
                             database_connector=database_connector)
        else:
            self.get_nullfree_queries(save_file_path=save_file_path, query_number=query_number,
                                      database_connector=database_connector)
