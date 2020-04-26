import psycopg2 as postgres
import yaml
from sklearn.preprocessing import LabelEncoder


class MetaCollector:
    db_name = None
    db_database = None
    db_user = None
    db_password = None
    db_host = None
    db_port = None

    conn = None
    cur = None

    def __init__(self, config=None):
        if config is None:
            with open("config.yaml") as file:
                config = yaml.safe_load(file)

        self.db_name = config["db_name"] if config["db_name"] is not None else None
        self.db_database = config["database"] if config["database"] is not None else None
        self.db_user = config["user"] if config["user"] is not None else None
        self.db_password = config["password"] if config["password"] is not None else None
        self.db_host = config["host"] if config["host"] is not None else None
        self.db_port = config["port"] if config["port"] is not None else None

        print()

    def open_database_connection(self):
        self.conn = postgres.connect(dbname=self.db_name, database=self.db_database, user=self.db_user,
                                     password=self.db_password, host=self.db_host, port=self.db_port)
        self.conn.set_session(autocommit=True)
        self.cur = self.conn.cursor()

    def close_database_connection(self):
        self.conn.close()

    # TODO:
    def setup_view(self, table_names, columns, join_atts=None, cube=False):
        sql = "DROP TABLE IF EXISTS tmpview; DROP TABLE IF EXISTS tmpview_cube;"
        self.cur.execute(sql)

        sql = """SELECT column_name, data_type FROM information_schema.columns 
                     WHERE table_schema = 'public' AND table_name IN ('{}') 
                     AND column_name IN ('{}') ORDER BY 1;""".format("','".join(table_names), "','".join(columns))
        self.cur.execute(sql)
        columns_types = self.cur.fetchall()

        if len(table_names) > 1:
            sql = """CREATE TABLE tmpview AS (SELECT {} FROM {} WHERE {});""".format(
                ",".join(["coalesce({col},'-1') AS {col}".format(col=col[0]) if "character" in col[1]
                          else "{col}".format(col=col[0]) for col in columns_types]),
                ",".join(["{} t{}".format(tab, i + 1) for i, tab in enumerate(table_names)]),
                " AND ".join(["t{}.{} = t{}.{}".format(1, join[0], i + 2, join[1])
                              for i, join in enumerate(join_atts)]))
            # print(sql)
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
            # print(sql)
            self.cur.execute(sql)

        if cube:
            sql = """ANALYZE tmpview; ANALYZE tmpview_cube;"""
        else:
            sql = """ANALYZE tmpview;"""
        self.cur.execute(sql)

        sql = """SELECT count(*) FROM tmpview;"""
        self.cur.execute(sql)
        N = self.cur.fetchall()[0]

        return columns_types, N

    # TODO
    def collect_meta(self, columns):
        # columns with type
        min_max = {}
        encoders = {}

        # f = IntProgress(min=0, max=len(columns))
        # display(f)
        i = 0
        for col in columns:
            # continue
            # if "character" in col[1]:
            sql = """SELECT {col}, count(*) from tmpview GROUP BY {col};""".format(col=col[0])

            self.cur.execute(sql)
            tmp = self.cur.fetchall()

            cats = [x[0] for x in tmp if x[0] is not None]
            # counts = np.array([x[1] for x in tmp])

            if col[1] != "integer":
                le = LabelEncoder()
                cats = le.fit_transform(sorted(cats))

                encoders[col[0]] = le
            step = 1
            # else:
            #    sql = """SELECT min({col}), max({col}) from tmpview;""".format(col=col[0])
            #    cur.execute(sql)
            #    cats = cur.fetchall()[0]
            #    if col[1] == "integer":
            #        step = 1
            #    else:
            #        step = 1/1000

            min_max[col[0]] = (min(cats), max(cats), step)
            # norms = (cats - min(cats))/(max(cats) - min(cats))
            i += 1
            # f.value = i
            # f.description = str(round(i/len(columns)*100)) + "%"

        return min_max, encoders

    @staticmethod
    def save_meta(meta_dict):
        with open("meta_information.yaml", "w") as file:
            print(yaml.safe_dump(meta_dict, file))


#TODO documentation