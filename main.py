from crawler import Crawler
from estimator import Estimator
from meta_collector import MetaCollector
from vectorizer import Vectorizer


def crawl(file_path: str, save_file_path: str):
    crawler = Crawler()
    crawler.run(file_path=file_path, save_file_path=save_file_path)


def collect_meta(file_path: str, config_file_path: str, save_file_path: str):
    mc = MetaCollector(config_file_path=config_file_path)
    mc.get_meta_from_file(file_path=file_path, save_file_path=save_file_path)


def vectorize(queries_with_cardinalities_csv_path : str, output_file_path : str, filetype : str):
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities(queries_with_cardinalities_csv_path)
    vectorizer.vectorize()
    vectorizer.save(output_file_path, filetype)


def estimate(data_file_path: str, config_file_path: str, save_model_file_path: str):
    estimator = Estimator(config_file_path=config_file_path)
    estimator.run(data_file_path=data_file_path, save_model_file_path=save_model_file_path)


if __name__ == "__main__":
    crawl("assets/job-light.sql", "assets/solution_dict")
    collect_meta(file_path="assets/solution_dict.yaml", config_file_path="meta_collector/config.yaml",
                 save_file_path="assets/meta_information")

    vectorize("assets/queries_with_cardinalities.csv", "assets/main_py_test_vectorizer", "csv")
    estimate("assets/queries_with_cardinalites_vectors.npy", "estimator/config.yaml", "assets/model")
