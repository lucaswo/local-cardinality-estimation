import numpy as np

from query_parser import QueryParser, QueryFormat
from database_connector import DatabaseConnector, Database
from estimator import Estimator
from meta_collector import MetaCollector
from vectorizer import Vectorizer


def parse_query_file(file_path: str, save_file_path: str, inner_separator: str = None, outer_separator: str = None,
                     query_format: QueryFormat = None):
    query_parser = QueryParser()
    query_parser.run(file_path=file_path, save_file_path=save_file_path, inner_separator=inner_separator,
                     outer_separator=outer_separator, query_format=query_format)


def collect_meta(file_path: str, config_file_path: str, save_file_path: str):
    db_conn = DatabaseConnector(database=Database.MARIADB)
    db_conn.connect(config_file_path=config_file_path)
    mc = MetaCollector(db_conn)
    mc.get_meta_from_file(file_path=file_path, save_file_path=save_file_path)
    db_conn.close_database_connection()


def vectorize(queries_with_cardinalities_csv_path: str, output_file_path: str, filetype: str):
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities(queries_with_cardinalities_csv_path)
    vectorizer.vectorize()
    vectorizer.save(output_file_path, filetype)


def estimate(data_file_path: str, config_file_path: str, save_model_file_path: str):
    loaded_data = []
    if data_file_path.split(".")[-1] == "csv":
        loaded_data = np.genfromtxt(data_file_path, delimiter=",")
    elif data_file_path.split(".")[-1] == "npy":
        loaded_data = np.load(data_file_path)

    query_set_ids = set([x.astype(int) for x in loaded_data[:, 0]])

    for query_set_id in query_set_ids:
        data = loaded_data[np.where(loaded_data[:, 0].astype(int) == query_set_id)]
        data = data[:, 1:]

        estimator = Estimator(config_file_path=config_file_path, data=data)
        estimator.run(save_model_file_path=save_model_file_path + "_{}".format(query_set_id))


if __name__ == "__main__":
    # crawl("assets/job-light.sql", "assets/solution_dict")
    collect_meta(file_path="assets/solution_dict.yaml", config_file_path="meta_collector/config_mariadb.yaml",
                 save_file_path="assets/meta_information")

    # vectorize("assets/queries_with_cardinalities.csv", "assets/main_py_test_vectorizer", "csv")
    # estimate("assets/queries_with_cardinalites_vectors.npy", "estimator/config.yaml", "assets/model")
