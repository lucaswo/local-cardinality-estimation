import argparse
import os.path
from enum import Enum
from typing import List, Tuple, Dict

import yaml
from sklearn.preprocessing import LabelEncoder

from database_connector import Database, DatabaseConnector


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
    Class for MetaCollector.
    """

    db_conn = None

    debug: bool = None

    def __init__(self, database_connector: DatabaseConnector, debug: bool = True):
        """
        Initializer for the MetaCollector

        :param database_connector: The connector to the used database.
        :param debug: boolean whether to print additional information while processing
        """

        self.db_conn = database_connector

        self.debug = debug

    def get_columns_data(self, table_names: List[str or Tuple[str, str]], columns: List[str]) -> \
            List[Tuple[str, str, str, Tuple[int, int, int], Dict[str, LabelEncoder], str]]:
        """
        Get column-name and datatype for the requested columns of the corresponding tables.

        :param table_names: List of names of tables, as strings or tuples containing table-name in first and alias in
            second place, to join.
        :param columns: Columns to project on.
        :return:
        """

        if isinstance(table_names[0], list) or isinstance(table_names[0], tuple):
            columns_string = "','".join(column.split(".")[-1] for column in columns)
        else:
            columns_string = "','".join(columns)

        columns_types = []
        already_seen = []

        for table_name in table_names:
            if isinstance(table_name, list) or isinstance(table_name, tuple):
                sql = """SELECT column_name, data_type FROM information_schema.columns
                                             WHERE table_name = '{}'
                                             AND column_name IN ('{}') ORDER BY 1;""".format(table_name[0],
                                                                                             columns_string)
            else:
                sql = """SELECT column_name, data_type FROM information_schema.columns
                                             WHERE table_name IN ('{}')
                                             AND column_name IN ('{}') ORDER BY 1;""".format(table_name, columns_string)
            self.db_conn.execute(sql)

            # get all remaining rows from the result set
            column_type = self.db_conn.fetchall()

            for index, column in enumerate(column_type):
                if column[1] == "int" or column[1] == "bigint": column = (column[0], "integer")
                if isinstance(table_name, list) or isinstance(table_name, tuple):
                    min_max_step, encoders = self.collect_min_max_step(table_name[0], (column[0], column[1]))
                    columns_types.append((column[0], table_name[1], column[1], min_max_step, encoders,
                                          "" if column[0] not in already_seen else "_".join(
                                              [table_name[1], column[0]])))
                else:
                    min_max_step, encoders = self.collect_min_max_step(table_name, (column[0], column[1]))
                    columns_types.append((column[0], table_name, column[1], min_max_step, encoders,
                                          "" if column[0] not in already_seen else "_".join([table_name, column[0]])))

                if column[0] not in already_seen:
                    already_seen.append(column[0])

        return columns_types

    def get_columns_data_sqlite(self, table_names: List[str or Tuple[str, str]], columns: List[str]) -> \
            List[Tuple[str, str, str, Tuple[int, int, int], Dict[str, LabelEncoder], str]]:

        columns_types = []
        already_seen = []

        for table_name in table_names:
            if isinstance(table_name, list) or isinstance(table_name, tuple):
                tablename = table_name[0]
            else:
                tablename = table_name

            sql = """ PRAGMA table_info("{}") """.format(tablename)

            self.db_conn.execute(sql)

            # get all remaining rows from the result set
            column_type = self.db_conn.fetchall()

            for index, column in enumerate(column_type):
                column = (column[1], column[2].lower())
                if table_name[1] + "." + column[0] in columns or column[0] in columns:
                    min_max_step, encoders = self.collect_min_max_step(tablename, (column[0], column[1]))
                    if isinstance(table_name, list) or isinstance(table_name, tuple):
                        columns_types.append((column[0], table_name[1], column[1], min_max_step, encoders,
                                              "" if column[0] not in already_seen else "_".join(
                                                  [table_name[1], column[0]])))
                    else:
                        columns_types.append((column[0], table_name, column[1], min_max_step, encoders,
                                              "" if column[0] not in already_seen else "_".join(
                                                  [table_name, column[0]])))

        return columns_types

    def collect_min_max_step(self, tablename: str, column: Tuple[str, str]) -> (Tuple[int, int, int], Dict):
        """
        After collecting the datatype information for the columns this function returns the min and max values for the
        meta-table and the encoders.

        :param tablename: String containing the name of the table where to find the column
        :param column: a tuple containing the name and the datatype for the column, each as string
        :return: first: dictionary with the attribute-name as key and a tuple containing min-value, max-value and
            step-size (all as int) as value
            second: a dictionary of the not integer encoders with key attribute-name and value the encoder
        """

        encoders = {}

        if column[1].lower() == "integer" or column[1].lower() == "int":
            sql = """SELECT MIN({col}) AS min, MAX({col}) AS max FROM {tab}""".format(col=column[0], tab=tablename)

            self.db_conn.execute(sql)
            tmp = self.db_conn.fetchone()

            return (tmp[0], tmp[1], 1), encoders
        else:
            sql = """SELECT {col}, count(*) from {tab} GROUP BY {col};""".format(col=column[0], tab=tablename)

            self.db_conn.execute(sql)
            tmp = self.db_conn.fetchall()

            cats = [x[0] for x in tmp if x[0] is not None]

            le = LabelEncoder()
            cats = le.fit_transform(sorted(cats))

            for index in cats:
                encoders[str(le.classes_[index])] = index.item()

            return (min(cats).item(), max(cats).item(), 1), encoders

    def get_max_card(self, table_names: List[str or Tuple[str, str]], join_atts: List[str or Tuple[str, str]]) -> int:

        if len(table_names) > 1:
            if isinstance(table_names[0], list) or isinstance(table_names[0], tuple):
                tables_string = ",".join(["{} {}".format(tab[0], tab[1]) for tab in table_names])
                attributes_string = " AND ".join(["{}".format(join) for join in join_atts])
            else:
                tables_string = ",".join(["{} t{}".format(tab, i + 1) for i, tab in enumerate(table_names)])
                attributes_string = " AND ".join(["t{}.{} = t{}.{}".format(1, join[0], i + 2, join[1]) for i, join in
                                                  enumerate(join_atts)])

            sql = """SELECT COUNT(*) FROM {} WHERE {}""".format(tables_string, attributes_string)
        else:
            sql = """SELECT COUNT(*) FROM {}""".format(table_names[0])

        self.db_conn.execute(sql)

        return self.db_conn.fetchone()[0]

    def setup_view(self, table_names: List[str or Tuple[str, str]], columns_types: List[Tuple],
                   join_atts: List[str or Tuple[str, str]] = None, cube: bool = False,
                   mode: CreationMode = CreationMode.NONE) -> (List[Tuple[str, str]], int):
        """
        Create the tables tmpview and if cube==True also tmpview_cube containing the metadata for the given tables
        joined on the attributes and projected on the columns.

        :param table_names: List of names of tables, as strings or tuples containing table-name in first and alias in
            second place, to join.
        :param columns_types: columns to project on
        :param join_atts: List of attributes, as strings or tuples containing the two attributes to join with '=', to
            join the tables on. -> is optional, because there is no join if there is only one table and so there would
            be no join-attribute needed in that case
        :param cube: boolean whether to create the *_cube table, too
        :param mode: see CreationMode-Enum
        :return: first: a list of tuples containing the name and the datatype for the columns, each as string
            second: the maximal cardinality as integer
        """

        if mode == CreationMode.TEMPORARY:
            new_table_name = "tmpview"
        elif mode == CreationMode.PERMANENT:
            new_table_name = "tmpview_{}".format(
                "_".join((table[0] if not isinstance(table, str) else table) for table in table_names))
        else:
            raise ValueError("Invalid mode selected!")

        if mode == CreationMode.TEMPORARY:
            # drops maybe already existing tables with metadata
            sql = """DROP TABLE IF EXISTS {tab};""".format(tab=new_table_name)
            self.db_conn.execute(sql)
            sql = """DROP TABLE IF EXISTS {tab}_cube;""".format(tab=new_table_name)
            self.db_conn.execute(sql)

        columns_string = ",".join(["coalesce({col},'-1') AS {col}".format(col=col[0]) if "character" in col[2]
                                   else "{col}".format(col=col[0]) for col in columns_types])
        if len(table_names) > 1:
            attributes_string = " AND ".join(["{}".format(join) for join in join_atts])
            if isinstance(table_names[0], list) or isinstance(table_names[0], tuple):
                tables_string = ",".join(["{} {}".format(tab[0], tab[1]) for tab in table_names])
            else:
                tables_string = ",".join(["{}".format(tab) for tab in table_names])

            sql = """CREATE TABLE IF NOT EXISTS {} AS SELECT {} FROM {} WHERE {};""".format(new_table_name,
                                                                                            columns_string,
                                                                                            tables_string,
                                                                                            attributes_string)
        else:
            sql = """CREATE TABLE IF NOT EXISTS {} AS SELECT {} FROM {};""".format(new_table_name, columns_string,
                                                                                   table_names[0])

        if mode == CreationMode.TEMPORARY or mode == CreationMode.PERMANENT:
            self.db_conn.execute(sql)
            sql = """SELECT count(*) FROM {};""".format(new_table_name)

        self.db_conn.execute(sql)

        # get the count of tuples in the tmpview
        max_card = self.db_conn.fetchone()[0]

        if cube:
            self.setup_cube_view(new_table_name=new_table_name, columns=columns_types)

        return max_card

    def setup_cube_view(self, new_table_name: str, columns):
        sql = """CREATE TABLE {tab}_cube AS (SELECT {col}, count(*)::integer, 0.0 as perc FROM {tab}
                        GROUP BY GROUPING SETS(({col})));
                        UPDATE tmpview_cube SET perc = count/(SELECT SUM(count) FROM tmpview_cube);""".format(
            tab=new_table_name, col=",".join(column[0].split(".")[-1] for column in columns))

        self.db_conn.execute(sql)

    @staticmethod
    def eliminate_duplicates(columns: List[str]) -> List[str]:
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
                 join_atts: List[str or Tuple[str, str]] = None, mode: CreationMode = CreationMode.NONE,
                 save: bool = True, save_file_name: str = None, batchmode: bool = False, cube: bool = False) -> Dict:
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

        if self.db_conn.database == Database.POSTGRES or self.db_conn.database == Database.MARIADB:
            columns_data = self.get_columns_data(table_names=table_names, columns=columns)
        elif self.db_conn.database == Database.SQLITE:
            columns_data = self.get_columns_data_sqlite(table_names=table_names, columns=columns)
        else:
            raise ValueError("Invlid Database Connection!")

        print(columns_data)

        if mode == CreationMode.NONE:
            max_card = self.get_max_card(table_names=table_names, join_atts=join_atts)
        elif mode == CreationMode.TEMPORARY or mode == CreationMode.PERMANENT:
            max_card = self.setup_view(table_names, columns_data, join_atts, cube=cube, mode=mode)
        else:
            raise ValueError("Invalid CreationMode selected!")

        result_dict = {"table_names": table_names,
                       "columns": columns_data,
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
        :param save_file_path: Optional path for the save-file.
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

        for index in batch:
            if index != 14: continue
            solution_dict = {index: self.get_meta(table_names=batch[index]["table_names"],
                                                  columns=batch[index]["selection_attributes"],
                                                  join_atts=batch[index]["join_attributes"],
                                                  save=False, batchmode=True, mode=mode)}

            if save:
                if save_file_path:
                    self.save_meta(solution_dict, save_file_path, mode="a+")
                else:
                    self.save_meta(solution_dict, mode="a+")

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


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-s", "--save", action="store_true", help="Whether to save the results.", default=True)
#     parser.add_argument("-o", "--override", action="store_true", help="Whether to override already existing results.",
#                         default=True)
#     parser.add_argument("-m", "--mode", type=int, help="The creation mode. 0-> None; 1-> Temporary; 2-> Permanent",
#                         default=0)
#     parser.add_argument("--file_path", type=str, help="The path for the file containing the join information.")
#     parser.add_argument("--save_file_path", type=str, help="The path for the file where the results should be saved.")
#
#     args = parser.parse_args()
#
#     db_conn = DatabaseConnector()
#     db_conn.connect(database=Database.MARIADB, config_file_path="config_mariadb.yaml")
#     mc = MetaCollector(db_conn)
#     mc.get_meta_from_file(file_path=args.file_path, save=args.save, save_file_path=args.save_file_path, mode=args.mode,
#                           override=args.override)
#     db_conn.close_database_connection()

# TODO: correct docu, optional: find a way to make the commandline version work

# db_conn = DatabaseConnector(database=Database.SQLITE)
# db_conn.connect(sqlite_file_path="E:/imdb.db")
db_conn = DatabaseConnector(database=Database.MARIADB)
db_conn.connect(config_file_path="config_mariadb.yaml")
# db_conn = DatabaseConnector(database=Database.POSTGRES)
# db_conn.connect(config_file_path="config_postgres.yaml")
mc = MetaCollector(db_conn)
# mc.get_meta(["movie_companies", "movie_info_idx", "title"], ["production_year", "info_type_id", "company_type_id"],
#             ["title.id=movie_companies.movie_id", "title.id=movie_info_idx.movie_id"], mode=CreationMode.TEMPORARY)
mc.get_meta_from_file(file_path="../assets/solution_dict.yaml")
# mc.get_meta(["title"], ["imdb_index"])
db_conn.close_database_connection()
