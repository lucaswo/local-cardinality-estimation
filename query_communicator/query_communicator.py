import yaml


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

    def __init__(self, meta: str, query_number: int = 10, nullqueries: bool = False):
        '''

        :param meta: meta information, needed to generate queries
        :param nullqueries: decide whether to generate nullqueries or not, default: no nullqueries
        :param query_number: count of queries that are generated per meta file entry
        '''
        if not meta:
            raise ValueError('No meta file given, but at least needed!')
        else:
            self.meta = yaml.safe_load(meta)
            self.nullqueries = nullqueries
            self.query_number = query_number


    def get_queries(self)-> str:
        '''
        TODO: percentage of nullqueries adjustable -> only a 'nice to have' at first
        Function for generating queries and their cardinalities if nullqueries are allowed.
        :return:
        '''
    def get_nullfree_queries(self, iterations: int):
        '''
        Function for generation an evaluation of the queries when nullfree. Communication
        is bounded by a number of Iteration in order to avoid an endless process of generation an Evaluation.
        There will be less queries then deserved, if unavoidable.
        :return:
        #TODO: generate queries for each entry and evaluate them. Compare number of distinct queries to desired queries and generate new if needed
        '''

        # number of distinct queries
        q_count = 0
        print('%d queries have been generated!' % q_count)

    def produce_queries(self):
        '''
        Main function to produce the queries and return the correct csv file,
        depending if nullqueries are wanted or not.
        :return:
        '''
        #Just a first template or idea
        if self.nullqueries == True:
            self.get_queries()
        else:
            self.get_nullfree_queries()
