from vectorizer import Vectorizer

def vectorize(queries_with_cardinalities_csv_path : str, output_file_path : str, filetype : str):
    vectorizer = Vectorizer()
    vectorizer.add_queries_with_cardinalities(queries_with_cardinalities_csv_path)
    vectorizer.vectorize()
    vectorizer.save(output_file_path, filetype)

vectorize("assets/queries_with_cardinalities.csv", "assets/main_py_test_vectorizer", "csv")