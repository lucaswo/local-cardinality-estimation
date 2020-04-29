from typing import List, Tuple, Dict

import psycopg2 as postgres
import yaml
from sklearn.preprocessing import LabelEncoder


class MetaCollector:
    """
    Class for MetaCollector. Using psycopg2 to establish a connection to the postgres database and setup tables with
    meta data.
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
        Initializer for the MetaCollector

        Configuration options are optionally passed via a config dict.
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
        close  the connection to the database

        :return: void
        """

        if not self.conn:
            print("There is no database-connection to close. Make sure to establish a connection to the database before"
                  " trying to close it.")
        else:
            if self.debug:
                print("Closing connection to postgres")
            self.conn.close()

    def setup_view(self, table_names: List[str], columns: List[str], join_atts: List[Tuple[str, str]] = None,
                   cube: bool = False) -> (List[Tuple[str, str]], int):
        """
        create the tables tmpview and if cube==True also tmpview_cube containing the metadata for the given tables
        joined on the attributes and projected on the columns

        :param table_names: tables to join
        :param columns: columns to project on
        :param join_atts: attributes to join the tables on -> is optional, because there is no join if there is only one
            table and so there is no join-attribute needed in that case
        :param cube: boolean whether to create the *_cube table, too
        :return: first: a list of tuples containing the name and the datatype for the columns, each as string
            second: the maximal cardinality as integer
        """

        if not self.cur:
            raise ConnectionError("The database-connection may not have been initialized correctly. Make sure to call "
                                  "'open_database_connection' befrore this method.")

        # drops maybe already existing tables with metadata
        sql = """DROP TABLE IF EXISTS tmpview; DROP TABLE IF EXISTS tmpview_cube;"""
        if self.debug:
            print("Executing: {}".format(sql))
        self.cur.execute(sql)

        # get column-name and datatype for the requested columns of the corresponding tables
        sql = """SELECT column_name, data_type FROM information_schema.columns 
                     WHERE table_schema = 'public' AND table_name IN ('{}') 
                     AND column_name IN ('{}') ORDER BY 1;""".format("','".join(table_names), "','".join(columns))
        if self.debug:
            print("Executing: {}".format(sql))
        self.cur.execute(sql)

        # get all remaining rows from the result set
        columns_types = self.cur.fetchall()

        # create table with the tuples for the given tables (join-result if
        # more than one table) with projection on the given columns
        if len(table_names) > 1:
            sql = """CREATE TABLE tmpview AS (SELECT {} FROM {} WHERE {});""".format(
                ",".join(["coalesce({col},'-1') AS {col}".format(col=col[0]) if "character" in col[1]
                          else "{col}".format(col=col[0]) for col in columns_types]),
                ",".join(["{} t{}".format(tab, i + 1) for i, tab in enumerate(table_names)]),
                " AND ".join(["t{}.{} = t{}.{}".format(1, join[0], i + 2, join[1])
                              for i, join in enumerate(join_atts)]))
        else:
            sql = """CREATE TABLE tmpview AS (SELECT {} FROM {});""".format(
                ",".join(["coalesce({col},'-1') AS {col}".format(col=col[0]) if "character" in col[1]
                          else "{col}".format(col=col[0]) for col in columns_types]),
                table_names[0])

        if self.debug:
            print("Executing: {}".format(sql))
        self.cur.execute(sql)

        if cube:
            sql = """CREATE TABLE tmpview_cube AS (SELECT {col}, count(*)::integer, 0.0 as perc FROM tmpview 
                GROUP BY GROUPING SETS(({col})));
                UPDATE tmpview_cube SET perc = count/(SELECT SUM(count) FROM tmpview_cube);""".format(
                col=",".join(columns))
            if self.debug:
                print("Executing: {}".format(sql))
            self.cur.execute(sql)

            sql = """ANALYZE tmpview; ANALYZE tmpview_cube;"""
        else:
            sql = """ANALYZE tmpview;"""
        if self.debug:
            print("Executing: {}".format(sql))
        self.cur.execute(sql)

        # get the count of tuples in the tmpview
        sql = """SELECT count(*) FROM tmpview;"""
        if self.debug:
            print("Executing: {}".format(sql))
        self.cur.execute(sql)
        max_card = self.cur.fetchall()[0]

        return columns_types, max_card

    def collect_meta(self, columns: List[Tuple[str, str]]) -> (Dict[str, Tuple[int, int, int]], Dict):
        """
        after execution of setup_view this function returns the min and max values for the meta-table and the encoders

        :param columns: a list of tuples containing the name and the datatype for the columns, each as string
        :return: first: dictionary with the attribute-name as key and a tuple containing min-value, max-value and
            step-size (all as int) as value
            second: a dictionary of the not integer encoders with key attribute-name and value the encoder
        """

        if not self.cur:
            raise ConnectionError("The database-connection may not have been initialized correctly. Make sure to call "
                                  "'open_database_connection' befrore this method.")

        min_max = {}
        encoders = {}

        for col in columns:
            sql = """SELECT {col}, count(*) from tmpview GROUP BY {col};""".format(col=col[0])

            if self.debug:
                print("Executing: {}".format(sql))
            self.cur.execute(sql)
            tmp = self.cur.fetchall()

            cats = [x[0] for x in tmp if x[0] is not None]

            if col[1] != "integer":
                le = LabelEncoder()
                cats = le.fit_transform(sorted(cats))

                encoders[col[0]] = le

            min_max[col[0]] = (min(cats), max(cats), 1)

        return min_max, encoders

    @staticmethod
    def save_meta(meta_dict: Dict, file_name: str = "meta_information"):
        """
        method for saving the meta-information to file

        :param meta_dict: the dictionary containing the meta-information to save
        :param file_name: the name (without file-type) for the save-file
        :return: void
        """

        with open(file_name + ".yaml", "w") as file:
            yaml.safe_dump(meta_dict, file)

    def get_meta(self, table_names: List[str], columns: List[str], join_atts: List[Tuple[str, str]] = None,
                 save: bool = True, save_file_name: str = None) -> Dict:
        """
        function for the whole process of collecting the meta-information for the given tables joined on the given
        attributes and projected on the given columns

        :param table_names: list of the name of tables to join
        :param columns: name of the columns to project on
        :param join_atts: attributes to join the tables on -> is optional, because there is no join if there is only one
            table and so there would be no join-attribute needed in that case
        :param save: boolean whether to save the meta-information to file
        :param save_file_name: name for the save-file for the meta_information -> not needed if save==False
        :return: dictionary containing the meta-information
        """

        self.open_database_connection()
        cols, max_card = self.setup_view(table_names, columns, join_atts, True)
        mm, encs = self.collect_meta(cols)
        self.close_database_connection()

        result_dict = {"tables": table_names,
                       "columns": cols,
                       "join_attributes": join_atts,
                       "min_max_step": mm,
                       "encodings": encs,
                       "max_card": max_card}

        if save:
            if self.debug:
                print("Saving: {} to {}".format(result_dict, (save_file_name + ".yaml") if save_file_name else "file"))
            if save_file_name:
                self.save_meta(result_dict, save_file_name)
            else:
                self.save_meta(result_dict)

        return result_dict


mc = MetaCollector()
# example which should work -> takes quite a while to be processed
mc.get_meta(["title", "cast_info"], ["kind_id", "person_id", "role_id"], [("id", "movie_id")])
