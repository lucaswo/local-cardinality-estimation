from typing import Dict, Any, Union

import numpy as np
import yaml
from keras.callbacks import History
from keras.layers import Dense, Input, Dropout
from keras.models import Model, load_model
from keras.optimizers import Adam


class Estimator:
    """
    Class containing the neural network for cardinality estimation. The specifications of the neural network can be
    changed in 'config.yaml'.
    """

    input_length: int = None

    config: Dict = None
    data: Dict[str, np.ndarray] = {"x": None, "y": None, "postgres_estimate": None}
    training_data: Dict[str, np.ndarray] = {"x": None, "y": None, "postgres_estimate": None}
    test_data: Dict[str, np.ndarray] = {"x": None, "y": None, "postgres_estimate": None}

    model: Model = None

    def __init__(self, config: Dict[str, Any] = None, data: Dict[str, np.ndarray] = None, model: Model = None,
                 model_path: str = None, debug: bool = True):
        """
        Initializer for the Estimator.

        Configuration options for the neural network are optionally passed via a config dict.
        It must contain at least the fields "loss_function", "dropout", "learning_rate", "kernel_initializer",
        "activation_strategy" and "layer".

        :param config: Only used if neither a model or a model_path is passed.
            if given: It must contain at least the fields "loss_function", "dropout", "learning_rate",
            "kernel_initializer", "activation_strategy" and "layer".
            if not given: the config file 'config.yaml' is used for these settings.
        :param data: Optional parameter for giving the data for training and testing. If given it has to be a Dict with
            at least "x" and "y" and optionally "postgres_estimate" as keys. The values have to be numpy.ndarray. For
            key "x" it should be the vectorized queries, for key "y" the true cardinalities in the same order and for
            optional key "postgres_estimate" the estimates of the postgres optimizer for the query.
        :param model: Option to pass a Model which can be used.
        :param model_path: Option to pass a path to a saved model in an .h5 file.
        :param debug: Boolean whether to print additional information while processing.
        """

        if model:
            self.model = model
        elif model_path:
            self.load_model(model_path)
        else:
            if config is None:
                with open("config.yaml") as file:
                    config = yaml.safe_load(file)

            conf_keys = ["loss_function", "dropout", "learning_rate", "kernel_initializer", "activation_strategy"]

            for key in conf_keys:
                if config[key] is None or config[key] == "":
                    raise ValueError(
                        "Value for {} is needed! You can provide it with the config dict or in config.yaml!".format(
                            key))

            if config["layer"] is None or config["layer"] == "" or len(config["layer"]) < 1:
                raise ValueError(
                    "Value for layer is needed! You can provide it with the config dict or in config.yaml!")

            self.config = config
            if debug:
                print("Initialized Estimator with {}".format(config))

        self.data = data

    def get_model(self, len_input: int, override: bool = False) -> Model:
        """
        Function for creating the model of the neural network with the information from self.config

        :param len_input: The size of the input vector.
        :param override: Whether an existing model should be overridden.
        :return: The model for the neural network with the given properties.
        """

        if self.model and not override:
            print("You already have a model defined. Please use override=True as parameter when you want to create a "
                  "new one.")
            return self.model

        if not len_input:
            raise ValueError("You should load the data before creating a model, because the model needs to know the "
                             "size of the input-vector!")

        one_input = Input(shape=(len_input,), name='one_input')

        for index, width in enumerate(self.config["layer"]):
            if width is None or width < 0:
                raise ValueError("A value provided for the layer is not set or negative! You can correct it in the "
                                 "config dict or in config.yaml!")

            x = Dense(width, activation="relu", kernel_initializer=self.config["kernel_initializer"])(
                one_input if index == 0 else x)
            x = Dropout(rate=self.config["dropout"])(x)

        x = Dense(1, kernel_initializer=self.config["kernel_initializer"], name="main_output", activation="linear")(x)

        self.model = Model(inputs=one_input, outputs=x)
        self.model.compile(loss=self.config["loss_function"], optimizer=Adam(lr=self.config["learning_rate"]))

        return self.model

    def load_model(self, model_path: str):
        """
        Method for loading an already existing model wich was saved to file.

        :param model_path: Path to the file containing the model to load
        """

        self.model = load_model(model_path)

    def q_loss_np(self, y_true, y_pred) -> np.ndarray:
        return np.maximum(y_true, y_pred) / np.minimum(y_true, y_pred)

    def load_data_file(self, file_path: str, override: bool = False) -> Dict[str, np.ndarray]:
        """
        Method for loading the data from file.

        :param file_path: Path for the file where the data is stored. Has to be a .csv or .npy file.
        :param override: Boolean whether to override already existing data.
        :return: The data which is set for the Estimator.
        """

        if self.data and not override and "x" in self.data and self.data["x"] is not None and "y" in self.data and \
                self.data["y"] is not None:
            print("You already have loaded data. Please use override=True as parameter when you want to override this"
                  " data.")
            return self.data

        data: Dict[str, np.ndarray] = {}
        if file_path.split(".")[-1] == "csv":
            loaded_data = np.genfromtxt(file_path, delimiter=",")
        elif file_path.split(".")[-1] == "npy":
            loaded_data = np.load(file_path)
        else:
            raise FileNotFoundError("No file found with path {}! Be sure to use a correct relative or an absolute path."
                                    .format(file_path))

        if loaded_data.shape[1] % 4 == 1:
            data["x"] = np.delete(loaded_data, -1, 1)
        elif loaded_data.shape[1] % 4 == 2:
            data["postgres_estimate"] = loaded_data[:, -2]
            data["x"] = np.delete(loaded_data, np.s_[-2:], 1)
        elif loaded_data.shape[1] % 4 == 3:
            data["postgres_estimate"] = loaded_data[:, -2]
            data["x"] = np.delete(loaded_data, np.s_[-3:], 1)

        data["y"] = loaded_data[:, -1]

        self.set_data(data, override)

        return self.data

    def set_data(self, data: Dict[str, np.ndarray], override: bool = False):
        """
        Method for setting data and dependent values like max_card and input_length. This includes a normalization of
        the true cardinalities

        :param data: Dictionary which must at least contain keys "x" and "y" and as values np.ndarray for each.
        :param override: Boolean whether to override already existing data.
        """

        if self.data and not override and "x" in self.data and self.data["x"] is not None and "y" in self.data and \
                self.data["y"] is not None:
            print("You already have loaded data. Please use override=True as parameter when you want to override this"
                  " data.")
            return self.data

        if data is None or "x" not in data or data["x"] is None or "y" not in data or data["y"] is None:
            raise KeyError("The given parameter data doesn't contain the data as expected.")

        self.data = data

        self.input_length = len(self.data["x"][0])

        self.data["y"] = self.data["y"]

    def split_data(self, split: float = 0.9):
        """
        Function to split the data into training- and test-set by a parameterized split value.

        :param split: Percentage of the data going into training set. (split=0.9 means 90% of data is training set)
        """

        if self.data is None or "x" not in self.data or self.data["x"] is None or "y" not in self.data or \
                self.data["y"] is None:
            raise KeyError("You're trying to split data you haven't even loaded! Be sure to load data before attempting"
                           " to split it!")

        sample = np.random.choice(range(len(self.data["x"])), size=int(len(self.data["x"]) * split), replace=False)
        not_sample = list(set(range(len(self.data["x"]))) - set(sample))

        self.training_data["x"] = self.data["x"][sample]
        self.training_data["y"] = self.data["y"][sample]
        if "postgres_estimate" in self.data and self.data["postgres_estimate"] is not None:
            self.training_data["postgres_estimate"] = self.data["postgres_estimate"][sample]

        self.test_data["x"] = self.data["x"][not_sample]
        self.test_data["y"] = self.data["y"][not_sample]
        if "postgres_estimate" in self.data and self.data["postgres_estimate"] is not None:
            self.test_data["postgres_estimate"] = self.data["postgres_estimate"][not_sample]

    def train(self, epochs: int = 100, verbose: int = 1, shuffle: bool = True, batch_size: int = 32,
              validation_split: float = 0.1) -> Union[History, History]:
        """
        Method for training the before created Model.

        :param epochs: Number of epochs for training.
        :param verbose: How much information to print while training. 0 = silent, 1 = progress bar, 2 = one line per
            epoch.
        :param shuffle: Whether to shuffle the training data -> not necessary if split was done by numpy.random.choice()
        :param batch_size: Size for the batches -> Smaller batches may be able to train the neural network better
            (possibly) but enlarge training time, while bigger batches may lead to a less well trained network while
            training faster.
        :param validation_split: How much of the data should be taken as validation set -> these are taken from the
            training data, not the test data, and are reselected for every epoch.
        :return: Training history as dict.
        """

        if "x" not in self.training_data or self.training_data["x"] is None or "y" not in self.training_data or \
                self.training_data["y"] is None:
            raise KeyError("You're trying to train the network without loading data! Be sure to load data before "
                           "attempting to train the neural network!")
        if not self.model:
            raise ValueError("You haven't built a model to train yet.")

        return self.model.fit(self.training_data["x"], self.training_data["y"], epochs=epochs, verbose=verbose,
                              shuffle=shuffle, batch_size=batch_size, validation_split=validation_split)

    def test(self) -> np.ndarray:
        """
        Let the trained neural network predict the test data.

        :return: numpy-array containing the normalized predictions of the neural network for the test data
        """

        if "x" not in self.test_data or self.test_data["x"] is None or "y" not in self.test_data or \
                self.test_data["y"] is None:
            raise KeyError("You're trying to test the network without loading data! Be sure to load data before "
                           "attempting to test the neural network!")
        if not self.model:
            raise ValueError("You haven't built a model to test yet.")

        return self.model.predict(self.test_data["x"]).flatten()

    def predict(self, data: np.ndarray) -> np.ndarray:
        """
        Let the trained neural network predict the given data.

        :param data: numpy-array containing at least one vectorized query which should be predicted
        :return: numpy-array containing the normalized predictions of the neural network for the given data
        """

        if not self.model:
            raise ValueError("You haven't built a model to predict with, yet.")

        return self.model.predict(data).flatten()

    def run(self, data_file_path: str = None, epochs: int = 100, verbose: int = 1, shuffle: bool = True,
            batch_size: int = 32, validation_split: float = 0.1, override_model: bool = False) -> np.ndarray:
        """
        Method for a full run of the Estimator, with training and testing.

        :param data_file_path: Optional path to saved data file. Only necessary if no data has been set before.
        :param epochs: Number of epochs for training.
        :param verbose: How much information to print while training. 0 = silent, 1 = progress bar, 2 = one line per
            epoch.
        :param shuffle: Whether to shuffle the training data -> not necessary if split was done by numpy.random.choice()
        :param batch_size: Size for the batches -> Smaller batches may be able to train the neural network better
            (possibly) but enlarge training time, while bigger batches may lead to a less well trained network while
            training faster.
        :param validation_split: How much of the data should be taken as validation set -> these are taken from the
            training data, not the test data, and are reselected for every epoch.
        :param override_model: Whether to override a probably already existing model.
        :return: A numpy.ndarray containing the calculated q-error.
        """

        if data_file_path:
            self.load_data_file(data_file_path)
        self.split_data()
        self.get_model(self.input_length)
        history = self.train(epochs=epochs, verbose=verbose, shuffle=shuffle, batch_size=batch_size,
                             validation_split=validation_split)
        predictions = self.test()

        q_error_means = np.mean(self.q_loss_np(self.test_data["y"], predictions))

        return q_error_means

    def save_model(self, filename: str = "model"):
        """
        Method for saving the Model to file.

        :param filename: Name of the file where the model should be stored. (Without file ending. ".h5" is added to the
            filename)
        """

        if self.model:
            self.model.save("{}.h5".format(filename))
        else:
            raise ValueError("No model for saving defined!")
