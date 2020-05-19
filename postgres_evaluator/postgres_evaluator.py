from typing import List, Tuple, Dict

import psycopg2 as postgres
import yaml

# TODO: Dokumentation für SQL aus CSV/SQL-file laden ergänzen
# TODO: gegen Fehler absichern, entsprechende Meldungen machen
# TODO: hardgecodete Filenamen ersetzen, CSV-Varianten ergänzen

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

    def __init__(self, config: dict = None, debug: bool = True):
        """
        Initializer for the PostgresEvaluator

        Configuration options for the database are optionally passed via a config dict.
        It must contain at least the dbname, the username and the password.
        Additionally the host and the port can be given if there not default (host: localhost, port: 5432).

        :param config: if given: it has to be a dictionary with at least db_name, user and password and optionally host
            and port (default to host: localhost, port: 5432 if not given)
            if not given: the config file 'config.yaml' is used for these settings
        :param debug: boolean whether to print additional information while processing
        """

        if config is None:
            with open("config.yaml") as file:
                config = yaml.safe_load(file)

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

        with open('queries.sql', 'r') as f:
            sqlFile = f.read()
        self.sqlQueries = list(filter(None,sqlFile.split('\n')))

        self.explainQueries = []
        for query in self.sqlQueries:
            tmp = query.split('COUNT(*)')
            explainQuery = "EXPLAIN " + tmp[0] + "*" + tmp[1]
            self.explainQueries.append(explainQuery)

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

    def get_true_cardinalities(self):
        cardinalities = []
        for query in self.sqlQueries:
            if self.debug:
                print("Executing: {}".format(query))
            self.cur.execute(query)
            output = self.cur.fetchone()
            trueCardi = output[0]
            if self.debug:
                print("true cardinality ('count(*)'): {}".format(trueCardi))
            cardinalities.append(trueCardi)
        return cardinalities

    def get_estimated_cardinalities(self):
        cardinalities = []
        for query in self.explainQueries:
            if self.debug:
                print("Executing: {}".format(query))
            self.cur.execute(query)

            output = self.cur.fetchone()
            startIndex = output[0].index("rows=")
            endIndex = output[0].index("width=")
            estiCardi = output[0][startIndex+5:endIndex-1]

            if self.debug:
                print("estimated cardinality: {}".format(estiCardi))
            cardinalities.append(estiCardi)
        return cardinalities

    def save_cardinalities(self, ec, tc):

        with open("queries_with_cardinalities.txt",'w') as f:
            if self.debug:
                print("Save queries and corresponing cardinalities (firstly estimated, secondly true) on 'queries_with_cardinalities.txt'")
            for idx, q in enumerate(self.sqlQueries):
                entry = q + ' '+ str(ec[idx]) + ' '+ str(tc[idx])+'\n'
                f.write(entry)


    def get_cardinalities(self):

        self.open_database_connection()
        estimatedCardinalities = self.get_estimated_cardinalities()
        trueCardinalities = self.get_true_cardinalities()
        self.save_cardinalities(estimatedCardinalities, trueCardinalities)
        self.close_database_connection()


pc = PostgresEvaluator()
pc.get_cardinalities()
