from vectorizer import Vectorizer

def vectorize(queries_with_cardinalities_csv_path : str, output_folder_path : str, filename : str):
    vectorizer = Vectorizer(4)
    vectorizer.add_queries_with_cardinalities(queries_with_cardinalities_csv_path)
    vectorizer.vectorize()
    vectorizer.save(output_folder_path, filename)

vectorize("assets/queries_with_cardinalities.csv", "assets/", "main_py_test")