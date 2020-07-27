import os.path
from enum import Enum
from typing import List, Tuple, Dict

import psycopg2 as postgres
import yaml
from sklearn.preprocessing import LabelEncoder


class CreationMode(Enum):
    """
    Enum for the different possibilities to use the MetaCollector.

    0 -> don't create table, 1 -> create temporary table, 2 -> create permanent table
    """

    NONE = 0
    TEMPORARY = 1
    PERMANENT = 2


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

    def __init__(self, config: dict = None, config_file_path: str = "config.yaml", debug: bool = True):
        """
        Initializer for the MetaCollector

        Configuration options are optionally passed via a config dict.
        It must contain at least the dbname, the username and the password.
        Additionally the host and the port can be given if there not default (host: localhost, port: 5432).

        :param config: if given: it has to be a dictionary with at least db_name, user and password and optionally host
            and port (default to host: localhost, port: 5432 if not given)
            if not given: the config file 'config.yaml' is used for these settings
        :param config_file_path: path for the config-file -> only necessary if no config is given
        :param debug: boolean whether to print additional information while processing
        """

        if config is None:
            with open(config_file_path) as file:
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

    def setup_view(self, table_names: List[str or Tuple[str, str]], columns: List[str],
                   join_atts: List[str or Tuple[str, str]] = None, cube: bool = False,
                   mode: CreationMode = CreationMode.NONE) -> (
            List[Tuple[str, str]], int):
        """
        Create the tables tmpview and if cube==True also tmpview_cube containing the metadata for the given tables
        joined on the attributes and projected on the columns.

        :param table_names: List of names of tables, as strings or tuples containing table-name in first and alias in
            second place, to join.
        :param columns: columns to project on
        :param join_atts: List of attributes, as strings or tuples containing the two attributes to join with '=', to
            join the tables on. -> is optional, because there is no join if there is only one table and so there would
            be no join-attribute needed in that case
        :param cube: boolean whether to create the *_cube table, too
        :param mode: see CreationMode-Enum
        :return: first: a list of tuples containing the name and the datatype for the columns, each as string
            second: the maximal cardinality as integer
        """

        if not self.cur:
            raise ConnectionError("The database-connection may not have been initialized correctly. Make sure to call "
                                  "'open_database_connection' before this method.")

        if mode == CreationMode.TEMPORARY:
            # drops maybe already existing tables with metadata
            sql = """DROP TABLE IF EXISTS tmpview; DROP TABLE IF EXISTS tmpview_cube;"""
            self.execute_sql(sql)

        # get column-name and datatype for the requested columns of the corresponding tables
        if isinstance(table_names[0], list) or isinstance(table_names[0], tuple):
            columns_string = "','".join(column.split(".")[-1] for column in columns)
        else:
            columns_string = "','".join(columns)

        columns_types = []

        for table_name in table_names:
            if isinstance(table_name, list) or isinstance(table_name, tuple):
                sql = """SELECT column_name, data_type FROM information_schema.columns 
                                     WHERE table_schema = 'public' AND table_name = '{}'
                                     AND column_name IN ('{}') ORDER BY 1;""".format(table_name[0], columns_string)
            else:
                sql = """SELECT column_name, data_type FROM information_schema.columns 
                                     WHERE table_schema = 'public' AND table_name IN ('{}') 
                                     AND column_name IN ('{}') ORDER BY 1;""".format(table_name, columns_string)
            self.execute_sql(sql)

            # get all remaining rows from the result set
            column_type = self.cur.fetchall()
            for column in column_type:
                if isinstance(table_name, list) or isinstance(table_name, tuple):
                    min_max_step, encoders = self.collect_meta(table_name[0], (column[0], column[1]))
                    columns_types.append((column[0], table_name[1], column[1], min_max_step, encoders))
                else:
                    min_max_step, encoders = self.collect_meta(table_name, (column[0], column[1]))
                    columns_types.append((column[0], table_name, column[1], min_max_step, encoders))

        # create table with the tuples for the given tables (join-result if
        # more than one table) with projection on the given columns
        if len(table_names) > 1:
            if isinstance(table_names[0], list) or isinstance(table_names[0], tuple):
                tables_string = ",".join(["{} {}".format(tab[0], tab[1]) for tab in table_names])
                columns = self.eliminate_duplicates(columns)
                columns_string = ",".join(["coalesce({col},'-1') AS {col}".format(col=col[0]) if "character" in col[2]
                                           else "{}".format(col) for col in columns])
                attributes_string = " AND ".join(["{}".format(join) for join in join_atts])
            else:
                tables_string = ",".join(["{} t{}".format(tab, i + 1) for i, tab in enumerate(table_names)])
                columns_string = ",".join(["coalesce({col},'-1') AS {col}".format(col=col[0]) if "character" in col[2]
                                           else "{col}".format(col=col[0]) for col in columns_types])
                attributes_string = " AND ".join(["t{}.{} = t{}.{}".format(1, join[0], i + 2, join[1]) for i, join in
                                                  enumerate(join_atts)])

            if mode == CreationMode.NONE:
                sql = """ SELECT COUNT(*) FROM {} WHERE {} """.format(tables_string, attributes_string)
            elif mode == CreationMode.TEMPORARY:
                new_table_name = "tmpview"
                sql = """CREATE TABLE {} AS (SELECT {} FROM {} WHERE {});""".format(new_table_name, columns_string,
                                                                                    tables_string, attributes_string)
            elif mode == CreationMode.PERMANENT:
                new_table_name = "tmpview_{}".format("_".join(table[0] for table in table_names))
                sql = """CREATE TABLE IF NOT EXISTS {} AS (SELECT {} FROM {} WHERE {});""".format(new_table_name,
                                                                                                  columns_string,
                                                                                                  tables_string,
                                                                                                  attributes_string)
            else:
                raise ValueError("Invalid mode selected. There are only 0, 1 or 2 as modes available!")
        else:
            columns_string = ",".join(["coalesce({col},'-1') AS {col}".format(col=col[0]) if "character" in col[2]
                                       else "{col}".format(col=col[0]) for col in columns_types])

            if mode == CreationMode.NONE:
                sql = """ SELECT COUNT(*) FROM {} """.format(table_names[0])
            elif mode == CreationMode.TEMPORARY:
                new_table_name = "tmpview"
                sql = """CREATE TABLE {} AS (SELECT {} FROM {});""".format(new_table_name, columns_string,
                                                                           table_names[0])
            elif mode == CreationMode.PERMANENT:
                new_table_name = "tmpview_{}".format(table_names[0])
                sql = """CREATE TABLE IF NOT EXISTS {} AS (SELECT {} FROM {});""".format(new_table_name, columns_string,
                                                                                         table_names[0])
            else:
                raise ValueError("Invalid mode selected. There are only 0, 1 or 2 as modes available!")

        if mode == CreationMode.TEMPORARY or mode == CreationMode.PERMANENT:
            # self.execute_sql(sql)
            # sql = """ANALYZE {};""".format(new_table_name)
            self.execute_sql(sql)
            sql = """SELECT count(*) FROM {};""".format(new_table_name)

        self.execute_sql(sql)

        # get the count of tuples in the tmpview
        max_card = self.cur.fetchall()[0]

        if cube:
            sql = """CREATE TABLE tmpview_cube AS (SELECT {col}, count(*)::integer, 0.0 as perc FROM tmpview
                GROUP BY GROUPING SETS(({col})));
                UPDATE tmpview_cube SET perc = count/(SELECT SUM(count) FROM tmpview_cube);""".format(
                col=",".join(column.split(".")[-1] for column in columns))
            if self.debug:
                print("Executing: {}".format(sql))
            self.cur.execute(sql)

            sql = """ANALYZE tmpview_cube;"""

            if self.debug:
                print("Executing: {}".format(sql))
            self.cur.execute(sql)

        return columns_types, max_card

    def collect_meta(self, tablename: str, column: Tuple[str, str]) -> (Tuple[int, int, int], Dict):
        """
        after execution of setup_view this function returns the min and max values for the meta-table and the encoders

        :param tablename: String containing the name of the table where to find the column
        :param column: a tuple containing the name and the datatype for the column, each as string
        :return: first: dictionary with the attribute-name as key and a tuple containing min-value, max-value and
            step-size (all as int) as value
            second: a dictionary of the not integer encoders with key attribute-name and value the encoder
        """

        if not self.cur:
            raise ConnectionError("The database-connection may not have been initialized correctly. Make sure to call "
                                  "'open_database_connection' before this method.")

        encoders = {}

        if column[1] != "integer":
            sql = """SELECT {col}, count(*) from {tab} GROUP BY {col};""".format(col=column[0], tab=tablename)

            self.execute_sql(sql)
            tmp = self.cur.fetchall()

            cats = [x[0] for x in tmp if x[0] is not None]

            le = LabelEncoder()
            cats = le.fit_transform(sorted(cats))

            encoders[column[0]] = le

            return (min(cats), max(cats), 1), encoders
        else:
            sql = """SELECT MIN({col}) AS min, MAX({col}) AS max FROM {tab}""".format(col=column[0], tab=tablename)

            self.execute_sql(sql)
            tmp = self.cur.fetchall()

            return (tmp[0][0], tmp[0][1], 1), encoders

    def eliminate_duplicates(self, columns: List[str]) -> List[str]:
        """
        This method is responsible for solving the problem of column-names existing at least double. Therefore it adds
        an alias which is build from the table-alias _ column-name.

        :param columns: List of strings of the column-names
        :return: List of strings of the column-names, without duplicates.
        """

        already_seen = []
        for index, column in enumerate(columns):
            column_split = column.split(".")
            if column_split[-1] not in already_seen:
                already_seen.append(column_split[-1])
            else:
                columns[index] = "{} {}".format(column, "_".join(column_split))

        return columns

    def get_meta(self, table_names: List[str or Tuple[str, str]], columns: List[str],
                 join_atts: List[str or Tuple[str, str]] = None, save: bool = True, save_file_name: str = None,
                 batchmode: bool = False, mode: CreationMode = CreationMode.NONE) -> Dict:
        """
        Method for the whole process of collecting the meta-information for the given tables joined on the given
        attributes and projected on the given columns.

        :param table_names: List of names of tables, as strings or tuples containing table-name in first and alias in
            second place, to join.
        :param columns: List of names of columns, as strings, to project on.
        :param join_atts: List of attributes, as strings or tuples containing the two attributes to join with '=', to
            join the tables on. -> is optional, because there is no join if there is only one table and so there would
            be no join-attribute needed in that case
        :param save: boolean whether to save the meta-information to file
        :param save_file_name: name for the save-file for the meta_information -> not needed if save==False
        :param batchmode: whether the meta data is collected in batches or not -> connection to db held open if batch
            mode
        :param mode: see CreationMode-Enum
        :return: dictionary containing the meta-information
        """

        if not batchmode:
            self.open_database_connection()

        cols, max_card = self.setup_view(table_names, columns, join_atts, cube=False, mode=mode)

        already_seen = []
        for index, col in enumerate(cols):
            if col[0] not in already_seen:
                already_seen.append(col[0])
            else:
                cols[index] = (col[0], col[1], col[2], col[3], col[4], "_".join([col[1], col[0]]))

        if not batchmode:
            self.close_database_connection()

        result_dict = {"table_names": table_names,
                       "columns": cols,
                       "join_attributes": join_atts,
                       "max_card": max_card}

        if not batchmode:
            result_dict = {0: result_dict}

        if save:
            if save_file_name:
                self.save_meta(result_dict, save_file_name)
            else:
                self.save_meta(result_dict)

        return result_dict

    def get_meta_from_file(self, file_path: str, save: bool = True, save_file_path: str = None,
                           mode: CreationMode = CreationMode.NONE, override: bool = True) -> Dict[int, any]:
        """
        Method for collecting meta data for the information given in a file from Crawler or at least a file formatted
        like this.

        :param file_path: Path to the file. Format has to be the same like the output of Crawler
        :param save: Whether to save the information to file or not. -> It is recommended to do so.
        :param save_file_path: Optional path for the file.
        :param mode: see CreationMode-Enum
        :param override: Whether to override an already existing meta_information file.
        :return: The solution dict.
        """

        if override:
            if save_file_path:
                if os.path.isfile(save_file_path + ".yaml"):
                    os.remove(save_file_path + ".yaml")
            else:
                if os.path.isfile("meta_information.yaml"):
                    os.remove("meta_information.yaml")

        solution_dict = {}

        with open(file_path) as file:
            batch = yaml.safe_load(file)

        self.open_database_connection()

        for index in batch:
            solution_dict = {index: self.get_meta(table_names=batch[index]["table_names"],
                                                  columns=batch[index]["selection_attributes"],
                                                  join_atts=batch[index]["join_attributes"],
                                                  save=False, batchmode=True, mode=mode)}

            if save:
                if save_file_path:
                    self.save_meta(solution_dict, save_file_path, mode="a+")
                else:
                    self.save_meta(solution_dict, mode="a+")

        self.close_database_connection()

        return solution_dict

    def save_meta(self, meta_dict: Dict, file_name: str = "meta_information", mode: str = "w"):
        """
        Method for saving the meta-information to file.

        :param meta_dict: the dictionary containing the meta-information to save
        :param file_name: the name (without file-type) for the save-file
        :param mode: The mode to open the file. Some common possibilities are 'w', 'w+', 'r', 'a', 'a+'
        """

        if self.debug:
            print("Saving: {} to {}".format(meta_dict, (file_name + ".yaml") if file_name else "file"))

        with open(file_name + ".yaml", mode) as file:
            yaml.safe_dump(meta_dict, file)

    def execute_sql(self, sql_string: str):
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
