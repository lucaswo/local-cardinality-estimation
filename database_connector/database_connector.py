from enum import Enum
from typing import Dict

import yaml


class Database(Enum):
    """
    Enum for the different supported databases. If you use MySQL, then use MARIADB as value here.
    """

    NONE = None
    POSTGRES = "postgres"
    SQLITE = "sqlite"
    MARIADB = "mariadb"  # also MySQL


class DatabaseConnector:
    """
    Class for DatabaseConnector.
    """

    conn = None
    cur = None

    database = None

    debug: bool = None

    def __init__(self, database: Database, debug: bool = False):
        """
        Initializer for the DatabaseConnector

        :param debug: boolean whether to print additional information while processing
        """

        self.debug = debug
        self.database = database

    def connect(self, config: Dict = None, config_file_path: str = None, sqlite_file_path: str = None):
        """
        Wrapper method for connecting to the selected database.

        :param config: if given: It has to be a dictionary with at least db_name, user and password and optionally
            host and port (default to host: localhost, port: 5432 if not given) for PostgreSQL or it has to be a
            dictionary with at least database, user and password and optionally host and port (default to host:
            localhost, port: 3306 if not given) for MariaDB.
            if not given: The config file path is needed and used for these settings.
        :param config_file_path: Path to the config file for PostgreSQL or MariaDB.
        :param sqlite_file_path: Path to the SQLite database file.
        """

        if (config is None and config_file_path is None and (
                self.database == Database.POSTGRES or self.database == Database.MARIADB)) or (
                sqlite_file_path is None and self.database == Database.SQLITE):
            raise ValueError("Please read the documentation. You need to give either config or config_file_path or "
                             "sqlite_file_path!")

        if self.database == Database.POSTGRES:
            self.connect_to_postgres(config=config, config_file_path=config_file_path)
        elif self.database == Database.SQLITE:
            self.connect_to_sqlite(database_file_path=sqlite_file_path)
        elif self.database == Database.MARIADB:
            self.connect_to_mariadb(config=config, config_file_path=config_file_path)
        else:
            raise ValueError("No valid database selected!")

    def connect_to_postgres(self, config: Dict = None, config_file_path: str = "config.yaml"):
        """
        Connect to the postgres database with the given config.

        :param config: if given: it has to be a dictionary with at least db_name, user and password and optionally host
            and port (default to host: localhost, port: 5432 if not given)
            if not given: the config file 'config.yaml' is used for these settings
        :param config_file_path: path for the config-file -> only necessary if no config is given; needs to point on a
            .yaml/.yml file
        """
        import psycopg2 as postgres

        if config is None:
            with open(config_file_path) as file:
                config = yaml.safe_load(file)

        if config["db_name"] is None or config["db_name"] == "":
            raise ValueError("Value for db_name is needed! You can provide it with the config dict or in config.yaml!")
        if config["user"] is None or config["user"] == "":
            raise ValueError("Value for user is needed! You can provide it with the config dict or in config.yaml!")
        if config["password"] is None or config["password"] == "":
            raise ValueError("Value for password is needed! You can provide it with the config dict or in config.yaml!")

        db_name = config["db_name"]
        db_user = config["user"]
        db_password = config["password"]
        db_host = config["host"] if (config["host"] is not None and config["host"] != "") else "localhost"
        db_port = config["port"] if (config["port"] is not None and config["port"] != "") else "5432"

        if self.debug:
            print("Connecting to postgres with dbname = {}, user = {}, host = {}, port = {}".format(db_name, db_user,
                                                                                                    db_host, db_port))
        self.conn = postgres.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
        self.conn.set_session(autocommit=True)
        self.cur = self.conn.cursor()

    def connect_to_mariadb(self, config: Dict = None, config_file_path: str = "config.yaml"):
        """
        Connect to the postgres database with the given config.

        :param config: if given: it has to be a dictionary with at least db_name, user and password and optionally host
            and port (default to host: localhost, port: 3306 if not given)
            if not given: the config file 'config.yaml' is used for these settings
        :param config_file_path: path for the config-file -> only necessary if no config is given; needs to point on a
            .yaml/.yml file
        """
        import mariadb

        if config is None:
            with open(config_file_path) as file:
                config = yaml.safe_load(file)

        if config["database"] is None or config["database"] == "":
            raise ValueError(
                "Value for db_name is needed! You can provide it with the config dict or in config.yaml!")
        if config["user"] is None or config["user"] == "":
            raise ValueError("Value for user is needed! You can provide it with the config dict or in config.yaml!")
        if config["password"] is None or config["password"] == "":
            raise ValueError(
                "Value for password is needed! You can provide it with the config dict or in config.yaml!")

        database = config["database"]
        user = config["user"]
        password = config["password"]
        host = config["host"] if (config["host"] is not None and config["host"] != "") else "localhost"
        port = config["port"] if (config["port"] is not None and config["port"] != "") else "3306"

        if self.debug:
            print(
                "Connecting to MariaDB with database = {}, user = {}, host = {}, port = {}".format(database, user, host,
                                                                                                   port))
        self.conn = mariadb.connect(database=database, user=user, password=password, host=host, port=port)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def connect_to_sqlite(self, database_file_path: str):
        """
        Open connection to a sqlite database.

        :param database_file_path: The path to the sqlite database file.
        """
        import sqlite3 as sqlite

        if not database_file_path:
            raise ValueError("The path to the sqlite database file is needed!")

        if self.debug:
            print("Connecting to sqlite in {}".format(database_file_path))
        self.conn = sqlite.connect(database_file_path)
        self.conn.isolation_level = None
        self.cur = self.conn.cursor()

    def close_database_connection(self):
        """
        close  the connection to the database

        :return: void
        """

        if not self.conn:
            print("There is no database-connection to close. Make sure to establish a connection to the database before"
                  " trying to close it.")
        else:
            if self.debug:
                print("Closing connection to database.")
            self.conn.close()

    def execute(self, sql_string: str):
        """
        Method for executing a SQL-Query.

        :param sql_string: The SQL-Query to execute
        """

        if not sql_string:
            raise ValueError("The SQL-String must not be empty!")
        if not self.cur:
            raise ConnectionError("The database-connection may not have been initialized correctly. Make sure to call "
                                  "'open_database_connection' before this method.")

        if self.debug:
            print("Executing: {}".format(sql_string))
        self.cur.execute(sql_string)

    def fetchall(self):
        """
        Wrapper for fetchall method.
        """

        if not self.cur:
            raise ConnectionError("The database-connection may not have been initialized correctly. Make sure to call "
                                  "'open_database_connection' before this method.")

        return self.cur.fetchall()

    def fetchone(self):
        """
        Wrapper for fetchone method.
        """

        if not self.cur:
            raise ConnectionError("The database-connection may not have been initialized correctly. Make sure to call "
                                  "'open_database_connection' before this method.")

        return self.cur.fetchone()
