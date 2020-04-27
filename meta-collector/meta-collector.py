from typing import List, Tuple, Dict

import psycopg2 as postgres
import yaml
from sklearn.preprocessing import LabelEncoder


class MetaCollector:
    db_name: str = None
    db_user: str = None
    db_password: str = None
    db_host: str = None
    db_port: str = None

    conn = None
    cur = None

    def __init__(self, config: dict = None):
        if config is None:
            with open("config.yaml") as file:
                config = yaml.safe_load(file)

        self.db_name = config["db_name"] if config["db_name"] is not None else None
        self.db_user = config["user"] if config["user"] is not None else None
        self.db_password = config["password"] if config["password"] is not None else None
        self.db_host = config["host"] if config["host"] is not None else None
        self.db_port = config["port"] if config["port"] is not None else None

        print()

    def open_database_connection(self):
        """ connect to the postgres database with the specified information """

        self.conn = postgres.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,
                                     host=self.db_host, port=self.db_port)
        self.conn.set_session(autocommit=True)
        self.cur = self.conn.cursor()

    def close_database_connection(self):
        """ close  the connection to the database """

        self.conn.close()

    def setup_view(self, table_names: List[str], columns: List[str], join_atts: List[Tuple[str, str]] = None,
                   cube: bool = False) -> (List[Tuple[str, str]], int):
        """ create the tables tmpview and if cube==True also tmpview_cube containing the metadata for the given tables,
            columns and attributes
        """

        # drops maybe already existing tables with metadata
        sql = """DROP TABLE IF EXISTS tmpview; DROP TABLE IF EXISTS tmpview_cube;"""
        self.cur.execute(sql)

        # get column-name and datatype for the requested columns of the corresponding tables
        sql = """SELECT column_name, data_type FROM information_schema.columns 
                     WHERE table_schema = 'public' AND table_name IN ('{}') 
                     AND column_name IN ('{}') ORDER BY 1;""".format("','".join(table_names), "','".join(columns))
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

        self.cur.execute(sql)

        if cube:
            sql = """CREATE TABLE tmpview_cube AS (SELECT {col}, count(*)::integer, 0.0 as perc FROM tmpview 
                GROUP BY GROUPING SETS(({col})));
                UPDATE tmpview_cube SET perc = count/(SELECT SUM(count) FROM tmpview_cube);""".format(
                col=",".join(columns))
            self.cur.execute(sql)

            sql = """ANALYZE tmpview; ANALYZE tmpview_cube;"""
        else:
            sql = """ANALYZE tmpview;"""
        self.cur.execute(sql)

        # get the count of tuples in the tmpview
        sql = """SELECT count(*) FROM tmpview;"""
        self.cur.execute(sql)
        N = self.cur.fetchall()[0]

        return columns_types, N

    def collect_meta(self, columns):
        min_max = {}
        encoders = {}

        for col in columns:
            sql = """SELECT {col}, count(*) from tmpview GROUP BY {col};""".format(col=col[0])

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
    def save_meta(meta_dict: Dict):
        with open("meta_information.yaml", "w") as file:
            yaml.safe_dump(meta_dict, file)

    def get_meta(self, table_names: List[str], columns: List[str], join_atts: List[Tuple[str, str]] = None,
                 save: bool = True):
        self.open_database_connection()
        cols, max_card = self.setup_view(table_names, columns, join_atts, True)
        mm, encs = self.collect_meta(cols)
        self.close_database_connection()

        result_dict = {"min_max_step": mm,
                       "encodings": encs,
                       "columns": cols,
                       "max_card": max_card}

        if save:
            self.save_meta(result_dict)

        return result_dict


# TODO documentation


mc = MetaCollector()
# example which should work -> takes quite a while to be processed
mc.get_meta(["title", "cast_info"], ["kind_id", "person_id", "role_id"], [("id", "movie_id")])
