from typing import Tuple
import psycopg2 as postgres
import yaml
import csv


class PostgresEvaluator:
    """
    Class for PostgresEvaluator. Using psycopg2 to establish a connection to the postgres database.
    Evaluate true and estimated cardinalities from q given query list and save them.
    """

    db_name: str = None
    db_user: str = None
    db_password: str = None
    db_host: str = None
    db_port: str = None

    conn = None
    cur = None

    debug: bool = None

    def __init__(self, config_path: str = 'postgres_evaluator/config.yaml', debug: bool = True, input_file_name: str = 'queries.csv'):
        """
        Initializer for the PostgresEvaluator

        Configuration options for the database are optionally passed via a config dict.
        It must contain at least the dbname, the username and the password.
        Additionally the host and the port can be given if there not default (host: localhost, port: 5432).

        :param config: if given: it has to be a dictionary with at least db_name, user and password and optionally host
            and port (default to host: localhost, port: 5432 if not given)
            if not given: the config file 'config.yaml' is used for these settings
        :param debug: boolean whether to print additional information while processing
        :param input_file_name: name of the file used for the sql query import, have to be .csv or .sql and located in the asset folder
        """

        config: dict = None
        with open(config_path, 'r') as c:
            config = yaml.safe_load(c)

        if config["db_name"] is None or config["db_name"] == "":
            raise ValueError("Value for db_name is needed! You can provide it with the config dict or in config.yaml!")
        if config["user"] is None or config["user"] == "":
            raise ValueError("Value for user is needed! You can provide it with the config dict or in config.yaml!")
        if config["password"] is None or config["password"] == "":
            raise ValueError("Value for password is needed! You can provide it with the config dict or in config.yaml!")

        self.db_name = config["db_name"]
        self.db_user = config["user"]
        self.db_password = config["password"]
        self.db_host = config["host"] if (config["host"] is not None and config["host"] != "") else None
        self.db_port = config["port"] if (config["port"] is not None and config["port"] != "") else None

        self.debug = debug

        self.query_data = []
        path = "../assets/" + input_file_name
        self.import_sql_queries(path)

    def open_database_connection(self):
        """
        connect to the postgres database with the information given in the initialization
        :return: void
        """

        if self.debug:
            print("Connecting to postgres with dbname = {}, user = {}, host = {}, port = {}".format(self.db_name,
                                                                                                    self.db_user,
                                                                                                    self.db_host,
                                                                                                    self.db_port))
        self.conn = postgres.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,
                                     host=self.db_host, port=self.db_port)
        self.conn.set_session(autocommit=True)
        self.cur = self.conn.cursor()

    def close_database_connection(self):
        """
        close the connection to the database
        :return: void
        """

        if not self.conn:
            print("There is no database-connection to close. Make sure to establish a connection to the database before"
                  " trying to close it.")
        else:
            if self.debug:
                print("Closing connection to postgres")
            self.conn.close()

    def import_sql_queries(self, path):
        """
        load the queries from sql or csv file, wich is provided by the sql_generator submodule
        :param path: path to the file with the given queries (per default in asset folder), relative to the postgres_evaluator folder
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

    def get_true_cardinalities(self):
        """
        execute the given queries against the database and calculate the true cardinality from each query
        :return: void
        """
        for query_as_dict in self.query_data:
            if self.debug:
                 print("Executing: {}".format(query_as_dict['query']))
            self.cur.execute(query_as_dict['query'])
            output = self.cur.fetchone()
            true_cardi = output[0]
            if self.debug:
                print("true cardinality ('count(*)'): {}".format(true_cardi))
            query_as_dict['true_cardinality'] = true_cardi

    def get_estimated_cardinalities(self):
        """
        execute the adapted queries against the database and calculate the postgres cardinality estimation for each query
        :return: void
        """
        self.generate_explain_queries()
        for query_as_dict in self.query_data:
            if self.debug:
                print("Executing: {}".format(query_as_dict['explain_query']))
            self.cur.execute(query_as_dict['explain_query'])

            output = self.cur.fetchone()
            start_index = output[0].index("rows=")
            end_index = output[0].index("width=")
            esti_cardi = output[0][start_index + 5:end_index - 1]

            if self.debug:
                print("estimated cardinality: {}".format(esti_cardi))
            query_as_dict['estimated_cardinality'] = esti_cardi

    def save_cardinalities(self, save_readable: Tuple[bool, str] = [True, '../assets/queries_with_cardinalities.txt'],
                           eliminate_null_queries: bool = True):
        """
        execute the adapted queries against the database and calculate the postgres cardinality estimation for each query

        :param eliminate_null_queries: if True only queries with true cardinality > 0 will be saved
        :param save_readable: if True: save queries and corresponing cardinalities human readable in an separate text file, per default as assets/queries_with_cardinalities.txt

        :return: void
        """
        if save_readable[0]:
            with open(save_readable[1], 'w') as f:
                if self.debug:
                    print(
                        "Save human readable queries and corresponing cardinalities (firstly estimated, secondly true) on ",
                        save_readable[1])
                for query_as_dict in self.query_data:
                    entry = f"{query_as_dict['query']} {query_as_dict['estimated_cardinality']} {query_as_dict['true_cardinality']}\n";

                    f.write(entry)

        header = ['querySetID', 'query', 'encodings', 'max_card', 'min_max_step', 'estimated_cardinality',
                  'true_cardinality']
        with open('../assets/queries_with_cardinalities.csv', 'w', newline='') as csvfile:
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
                    if ordered_copy['true_cardinality'] != None and ordered_copy['true_cardinality'] > 0:
                        querywriter.writerow(ordered_copy)
                        querycounter += 1
                else:
                    querywriter.writerow(ordered_copy)
                    querycounter += 1
        if self.debug:
            print("Added estimated and true cardinalities to query list")

    def get_cardinalities(self):
        """
        function that manage the whole process of cardinality estimation/calculation
        :return: void
        """
        self.open_database_connection()
        self.get_estimated_cardinalities()
        self.get_true_cardinalities()
        self.save_cardinalities()
        self.close_database_connection()

if __name__ == "__main__":
    pc = PostgresEvaluator()
    pc.get_cardinalities()
