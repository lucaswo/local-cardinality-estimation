import numpy as np
import os

from query_parser import QueryParser, QueryFormat
from database_connector import DatabaseConnector, Database
from estimator import Estimator
from meta_collector import MetaCollector
from vectorizer import Vectorizer
from query_communicator import QueryCommunicator


def parse_query_file(file_path: str, save_file_path: str, inner_separator: str = None, outer_separator: str = None,
                     query_format: QueryFormat = None):
    query_parser = QueryParser()
    query_parser.run(file_path=file_path, save_file_path=save_file_path, inner_separator=inner_separator,
                     outer_separator=outer_separator, query_format=query_format)


def collect_meta(file_path: str, config_file_path: str, save_file_path: str):
    db_conn = DatabaseConnector(database=Database.POSTGRES)
    db_conn.connect(config_file_path=config_file_path)
    mc = MetaCollector(db_conn)
    mc.get_meta_from_file(file_path=file_path, save_file_path=save_file_path)
    db_conn.close_database_connection()


def vectorize(queries_with_cardinalities_csv_path: str, output_base_path: str, output_result_folder: str, output_base_filename : str, output_filetypes: str):
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities(queries_with_cardinalities_csv_path)
    vectorizer.vectorize()
    vectorizer.save(output_base_path, output_result_folder, output_base_filename, output_filetypes)


def estimate(data_path: str, config_file_path: str, save_model_file_path: str):

    files = [os.path.join(data_path, f) for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
    for file in files:
        loaded_data = []
        root, extension = os.path.splitext(file)
        query_set_id = int(os.path.basename(root).rsplit("_")[-1])
        if extension == ".csv":
            loaded_data = np.genfromtxt(file, delimiter=",")
        elif extension == ".npy":
            loaded_data = np.load(file)

        estimator = Estimator(config_file_path=config_file_path, data=loaded_data)
        estimator.run(save_model_file_path=save_model_file_path + "_{}".format(query_set_id))


def communicate(input_file_path: str, query_number: int, nullqueries: bool, save_file_path: str, config_file_path: str):
    db_conn = DatabaseConnector(database=Database.POSTGRES)
    db_conn.connect(config_file_path=config_file_path)
    communicator = QueryCommunicator(meta_file_path=input_file_path)
    communicator.produce_queries(query_number=query_number, nullqueries=nullqueries, save_file_path=save_file_path,
                                 database_connector=db_conn)
    db_conn.close_database_connection()


if __name__ == "__main__":
    parse_query_file(file_path="assets/job-light.sql", save_file_path="assets/solution_dict")
    collect_meta(file_path="assets/solution_dict.yaml", config_file_path="meta_collector/config_postgres.yaml",
                 save_file_path="assets/meta_information")
    communicate(input_file_path='assets/meta_information.yaml', query_number=10, nullqueries=False,
                save_file_path='assets/fin_queries_with_cardinalities.csv',
                config_file_path="meta_collector/config_postgres.yaml")
    vectorize("assets/fin_queries_with_cardinalities.csv", "assets", "vectorizer_results", "main_py_test_vectors", "csv")
    estimate("assets/vectorizer_results", "estimator/config.yaml", "assets/model")
