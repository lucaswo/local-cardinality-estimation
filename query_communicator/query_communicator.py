import yaml
from postgres_evaluator import postgres_evaluator
from sql_generator import sql_generator
import pandas as pd


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

    def __init__(self, meta: str = '../assets/meta_information.yaml', query_number: int = 10, nullqueries: bool = False):
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
        TODO: percentage of nullqueries adjustable -> only a 'nice to have' at first
        Function for generating queries and their cardinalities if nullqueries are allowed.
        :return:
        '''
        generator = sql_generator.SQLGenarator(config=self.meta)
        generator.generate_queries(qnumber=self.query_number, save_readable='../assets/null_including_queries.sql')

        with open('../postgres_evaluator/config.yaml', 'r') as c:
            config = yaml.safe_load(c)

        # TODO: test if it works with the DB Connection, then uncommend
        # evaluator = postgres_evaluator.PostgresEvaluator(config=config)
        # evaluator.get_cardinalities()


    def get_nullfree_queries(self, outputfile: str = '../assets/reduced_queries_with_cardinalities.csv'):
        '''
        Function for generation an evaluation of the queries when nullfree. Communication
        is bounded by a number of Iteration in order to avoid an endless process of generation an Evaluation.
        There will be less queries then deserved, if unavoidable.
        :return: reduced Queries as DataFrame
        '''
        # generate 150% queries
        generate = int(self.query_number * 1.5)
        # number of distinct queries

        generator = sql_generator.SQLGenarator(config=self.meta)
        generator.generate_queries(qnumber=generate, save_readable='../assets/nullfree_queries.sql')
        # TODO: change code in PG Evaluator, that a config file can be chosen, instead of loading a config file and giving th dict to the Evaluator
        with open('../postgres_evaluator/config.yaml','r') as c:
            config = yaml.safe_load(c)

        #TODO: test if it works with the DB Connection, then uncommend
        #evaluator = postgres_evaluator.PostgresEvaluator(config=config)
        #evaluator.get_cardinalities()
        reduced_queries = self.reduce_queries()

        if outputfile:
            reduced_queries.to_csv(outputfile)
        else:
            reduced_queries.to_csv('../assets/reduced_queries_with_cardinalities.csv')

        return reduced_queries

    def reduce_queries(self):
        '''
        Reduces genrated queries to the requested number of queries
        :return:DataFrame with reduced query sets
        '''
        queries = pd.read_csv('../assets/queries_with_cardinalities.csv',delimiter=';')
        setIDs = set(queries.querySetID.to_list())
        reduced_queries = pd.DataFrame(columns=queries.columns)

        for id in setIDs:
            df = queries[queries['querySetID'] == id]
            if len(df) > self.query_number:
                df = df[:self.query_number]
                reduced_queries = reduced_queries.append(df)
                print('%d queries have been generated for query set %d!' % (len(df), id))
            else:
                reduced_queries = reduced_queries.append(df)
                print('%d queries have been generated for query set %d!' % (len(df), id))

        return reduced_queries

    def produce_queries(self):
        '''
        Main function to produce the queries and return the correct csv file,
        depending if nullqueries are wanted or not.
        :return:
        '''
        # Just a first template or idea
        if self.nullqueries == True:
            self.get_queries()
        else:
            self.get_nullfree_queries()


com = QueryCommunicator()
com.produce_queries()