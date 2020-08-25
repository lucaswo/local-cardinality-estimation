import argparse
import os

import numpy as np

from query_parser import QueryParser, QueryFormat
from database_connector import DatabaseConnector, Database
from estimator import Estimator
from meta_collector import MetaCollector
from vectorizer import Vectorizer
from query_communicator import QueryCommunicator


def parse_query_file(file_path: str, save_file_path: str, inner_separator: str = None, outer_separator: str = None,
                     query_format: QueryFormat = None):
    print("The input file %s will be parsed." % file_path)
    query_parser = QueryParser()
    query_parser.run(file_path=file_path, save_file_path=save_file_path, inner_separator=inner_separator,
                     outer_separator=outer_separator, query_format=query_format)
    print("The result of the QueryParser is saved to %s." % (save_file_path + ".yaml"))


def collect_meta(file_path: str, config_file_path: str, save_file_path: str):
    print("Starting to collect meta information with %s as input." % file_path)
    db_conn = DatabaseConnector(database=Database.POSTGRES)
    db_conn.connect(config_file_path=config_file_path)
    mc = MetaCollector(db_conn)
    mc.get_meta_from_file(file_path=file_path, save_file_path=save_file_path)
    db_conn.close_database_connection()
    print("Saving meta information to %s." % (save_file_path + ".yaml"))


def vectorize(queries_with_cardinalities_csv_path: str, output_base_path: str, output_result_folder: str,
              output_base_filename: str, output_filetypes: str):
    print("Vectorizing the given queries from %s." % queries_with_cardinalities_csv_path)
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities(queries_with_cardinalities_csv_path)
    vectorizer.vectorize()
    vectorizer.save(output_base_path, output_result_folder, output_base_filename, output_filetypes)
    print("Saving the output to %s." % (output_base_filename + "." + output_filetypes))


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

        print()
        print("Training neural network on data from %s." % file)
        estimator = Estimator(config_file_path=config_file_path, data=loaded_data)
        estimator.run(save_model_file_path=save_model_file_path + "_{}".format(query_set_id))
        print("The trained model is saved to %s." % (save_model_file_path + ("_%i" % query_set_id) + ".h5"))


def communicate(input_file_path: str, query_number: int, nullqueries: bool, save_file_path: str, config_file_path: str):
    print("Starting query generation and evaluation from %s." % input_file_path)
    db_conn = DatabaseConnector(database=Database.POSTGRES)
    db_conn.connect(config_file_path=config_file_path)
    communicator = QueryCommunicator(meta_file_path=input_file_path)
    communicator.produce_queries(query_number=query_number, nullqueries=nullqueries, save_file_path=save_file_path,
                                 database_connector=db_conn)
    db_conn.close_database_connection()
    print("Saving the output to %s." % save_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input_file", type=str, default="assets/job-light.sql",
                        help="The input file which contains the sql queries for the QueryParser.")
    parser.add_argument("-q", "--query_number", type=int, help="The number of queries you want for the result.",
                        default=10000)
    parser.add_argument("-n", "--nullqueries", action="store_true", default=False,
                        help="Whether to produce queries with the true cardinality 0. When disabling this option the "
                             "creation process takes a longer time.")
    parser.add_argument("-d", "--working_directory", type=str, default="assets/",
                        help="The directory where to save the intermediate result files for the modules.")

    args = parser.parse_args()

    wd = args.working_directory

    if not os.path.isdir(wd):
        try:
            os.makedirs(wd)
        except OSError:
            print("Creation of the directory %s failed" % wd)
        else:
            print("Successfully created the directory %s " % wd)
    else:
        print("Results are saved into existing directory '%s'" % wd)

    print()
    parse_query_file(file_path=args.input_file, save_file_path=os.path.join(wd, "solution_dict"))
    print()
    collect_meta(file_path=os.path.join(wd, "solution_dict.yaml"),
                 config_file_path="meta_collector/config_postgres.yaml",
                 save_file_path=os.path.join(wd, "meta_information"))
    print()
    communicate(input_file_path=os.path.join(wd, "meta_information.yaml"), query_number=args.query_number,
                nullqueries=args.nullqueries, save_file_path=os.path.join(wd, "fin_queries_with_cardinalities.csv"),
                config_file_path="meta_collector/config_postgres.yaml")
    print()
    vectorize(os.path.join(wd, "fin_queries_with_cardinalities.csv"), wd, "vectorizer_results", "main_py_test_vectors",
              "csv")
    print()
    estimate(os.path.join(wd, "vectorizer_results"), os.path.join("estimator", "config.yaml"),
             os.path.join(wd, "model"))
