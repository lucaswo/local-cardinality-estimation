import csv

from database_connector import DatabaseConnector
from progressbar import ProgressBar,Bar,Counter,Timer


class DatabaseEvaluator:
    """
    Class for DatabaseEvaluator. Using psycopg2 to establish a connection to the postgres database.
    Evaluate true and estimated cardinalities from q given query list and save them.
    """

    db_conn: DatabaseConnector = None
    debug: bool = None

    def __init__(self, database_connector: DatabaseConnector, debug: bool = True,
                 input_file_path: str = 'assets/queries.csv'):
        """
        Initializer for the DatabaseEvaluator

        Configuration options for the database are optionally passed via a config dict.
        It must contain at least the dbname, the username and the password.
        Additionally the host and the port can be given if there not default (host: localhost, port: 5432).

        :param debug: boolean whether to print additional information while processing
        :param input_file_path: name of the file used for the sql query import, have to be .csv or .sql and located in
            the asset folder
        :param database_connector: Handles the database connection to the desired database.
        """

        self.db_conn = database_connector
        self.debug = debug

        self.query_data = []
        self.import_sql_queries(input_file_path)

    def import_sql_queries(self, path):
        """
        load the queries from sql or csv file, which is provided by the sql_generator submodule
        :param path: path to the file with the given queries (per default in asset folder), relative to the
            database_evaluator folder
        :return: void
        """

        if self.debug:
            print("try to load queries from ", path)
        if path.endswith(".sql"):
            print("Be aware that the resulting csv file will be incomplete and not suitable for further processing.")
            with open(path, 'r') as f:
                input_file = f.read()
                sql_queries = list(filter(None, input_file.split('\n')))
                for query in sql_queries:
                    self.query_data.append({"query": query})
        elif path.endswith(".csv"):
            with open(path, newline='') as f:
                # DictReader uses first line as keyNames
                queryreader = csv.DictReader(f, delimiter=';')
                for row in queryreader:
                    self.query_data.append(row)

        else:
            print("There was no sql or csv file to import the queries found, no further processing possible.")
            self.query_data = []

    def generate_explain_queries(self):
        """
        generate EXPLAIN sql statements for cardinality estimation
        :return: void
        """

        for query_as_dict in self.query_data:
            tmp = query_as_dict['query'].split('COUNT(*)')
            explain_query = "EXPLAIN " + tmp[0] + "*" + tmp[1]
            query_as_dict['explain_query'] = explain_query

    def get_true_cardinalities(self, query_number, eliminate_null_queries: bool):
        """
        execute the given queries against the database and calculate the true cardinality from each query
        :param query_number: desired number of queries, if reached before query list (extended for nullquery reduction)
            is comletly processed earlier abort for evaluation time savings
        :param eliminate_null_queries: if True only queries with true cardinality > 0 will be saved
        :return: void
        """
        max_value = int(self.query_data[-1]['querySetID']) + 1
        print('Evaluating %d Query sets for the true cardinalities.' % max_value)

        for current_query_set_id in range(max_value):
            query_list_i = list(filter(lambda i: i['querySetID'] == str(current_query_set_id),self.query_data))
            query_counter: int = 0

            with ProgressBar(widgets=['Query Set %d/%d ' % (current_query_set_id + 1, max_value), Bar(),
                            ' ', Counter(format='%(value)d/%(max_value)d'), ' ', Timer()],
                             max_value=query_number, redirect_stdout=True) as bar:
                for query_as_dict in query_list_i:
                    if query_counter < query_number:
                        bar.update(query_counter + 1)
                        self.db_conn.execute(query_as_dict['query'])
                        output = self.db_conn.fetchone()
                        true_cardi = output[0]
                        if eliminate_null_queries and true_cardi != 0:
                            query_counter += 1
                        elif not eliminate_null_queries:
                            query_counter += 1
                        if self.debug:
                            print("true cardinality ('count(*)'): {}".format(true_cardi))

                        self.query_data[self.query_data.index(query_as_dict)]['true_cardinality'] = true_cardi



    def get_estimated_cardinalities(self, query_number: int):
        """
        execute the adapted queries against the database and calculate the postgres cardinality estimation for each query
        :param query_number: desired number of queries, if reached before query list (extended for nullquery reduction)
            is comletly processed earlier abort for evaluation time savings
        :return: void
        """

        self.generate_explain_queries()
        for query_as_dict in self.query_data:
            self.db_conn.execute(query_as_dict['explain_query'])
            # TODO: Variants for MARIADB an SQLITE missing, self.db_conn.database gives database Enum value
            output = self.db_conn.fetchone()
            start_index = output[0].index("rows=")
            end_index = output[0].index("width=")
            esti_cardi = output[0][start_index + 5:end_index - 1]

            if self.debug:
                print("estimated cardinality: {}".format(esti_cardi))
            query_as_dict['estimated_cardinality'] = esti_cardi

    def save_cardinalities(self, save_readable: bool = True, save_file_path: str = 'assets/queries_with_cardinalities',
                           eliminate_null_queries: bool = True):
        """
        execute the adapted queries against the database and calculate the postgres cardinality estimation for each
            query
        :param eliminate_null_queries: if True only queries with true cardinality > 0 will be saved
        :param save_readable: if True: save queries and corresponing cardinalities human readable in an separate text
            file, per default as assets/queries_with_cardinalities.txt
        :param save_file_path: path to save the finished queries with their cardinalities
        :return: void
        """

        # delete queries with estimated but without true cardinalities (because evaluation of true cardinalities was aborted on satisfied number of queries)
        query_data_copy: list = []
        for query_as_dict in self.query_data:
            if ("estimated_cardinality" in query_as_dict) and ("true_cardinality" in query_as_dict):
                query_data_copy.append(query_as_dict)
        self.query_data = query_data_copy

        if save_readable:
            with open(save_file_path + '.txt', 'w') as f:
                if self.debug:
                    print("Save human readable queries and corresponing cardinalities(firstly estimated, secondly "
                          "true) on ", save_file_path + '.txt')
                for query_as_dict in self.query_data:
                    entry = f"{query_as_dict['query']} {query_as_dict['estimated_cardinality']} " \
                            f"{query_as_dict['true_cardinality']}\n"

                    f.write(entry)

        header = ['querySetID', 'query', 'encodings', 'max_card', 'min_max_step', 'estimated_cardinality',
                  'true_cardinality']
        with open(save_file_path + '.csv', 'w', newline='') as csvfile:
            querywriter = csv.DictWriter(csvfile, delimiter=';', fieldnames=header)
            querywriter.writeheader()
            querycounter = 0
            for query_as_dict in self.query_data:
                ordered_copy = {'querySetID': query_as_dict.get('querySetID'),
                                'query': query_as_dict.get('query'),
                                'encodings': query_as_dict.get('encodings'),
                                'max_card': query_as_dict.get('max_card'),
                                'min_max_step': query_as_dict.get('min_max_step'),
                                'estimated_cardinality': query_as_dict.get('estimated_cardinality'),
                                'true_cardinality': query_as_dict.get('true_cardinality')}
                if eliminate_null_queries:
                    if ordered_copy['true_cardinality'] is not None and ordered_copy['true_cardinality'] > 0:
                        querywriter.writerow(ordered_copy)
                        querycounter += 1
                else:
                    querywriter.writerow(ordered_copy)
                    querycounter += 1
        if self.debug:
            print("Added estimated and true cardinalities to query list")

    def get_cardinalities(self, query_number: int, eliminate_null_queries: bool = True,
                          save_file_path: str = 'assets/queries_with_cardinalities'):
        """
        function that manage the whole process of cardinality estimation/calculation
        :param query_number: desired number of queries, if reached before query list (extended for nullquery reduction)
            is comletly processed earlier abort for evaluation time savings
        :param eliminate_null_queries: if True only queries with true cardinality > 0 will be saved
        :param save_file_path: path to save the finished queries with their cardinalities
        :return: void
        """

        self.get_true_cardinalities(query_number=query_number, eliminate_null_queries=eliminate_null_queries)
        self.get_estimated_cardinalities(query_number)
        self.save_cardinalities(eliminate_null_queries=eliminate_null_queries, save_readable=True,
                                save_file_path=save_file_path)
