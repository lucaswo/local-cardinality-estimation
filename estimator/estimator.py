from typing import Dict, Any

import numpy as np
import yaml
from keras import backend as K
from keras.layers import Dense, Input, Dropout
from keras.models import Model
from keras.optimizers import Adam


class Estimator:
    max_card: float = None
    input_length: int = None

    config: Dict = None
    data: Dict[str, np.ndarray] = {"x": None, "y": None, "postgres_estimate": None}
    training_data: Dict[str, np.ndarray] = {"x": None, "y": None, "postgres_estimate": None}
    test_data: Dict[str, np.ndarray] = {"x": None, "y": None, "postgres_estimate": None}

    model: Model = None

    def __init__(self, config: Dict[str, Any] = None, data: Dict[str, np.ndarray] = None, model: Model = None,
                 debug: bool = True):

        if config is None:
            with open("config.yaml") as file:
                config = yaml.safe_load(file)

        conf_keys = ["loss_function", "dropout", "learning_rate", "kernel_initializer", "activation_strategy"]

        for key in conf_keys:
            if config[key] is None or config[key] == "":
                raise ValueError(
                    "Value for {} is needed! You can provide it with the config dict or in config.yaml!".format(key))

        if config["layer"] is None or config["layer"] == "" or len(config["layer"]) < 1:
            raise ValueError("Value for layer is needed! You can provide it with the config dict or in config.yaml!")

        self.config = config
        self.data = data
        self.model = model

        if debug:
            print("Initialized Estimator with {}".format(config))

    def get_model(self, len_input: int) -> Model:
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

    @staticmethod
    def denormalize(y, y_min, y_max):
        return K.exp(y * (y_max - y_min) + y_min)

    @staticmethod
    def denormalize_np(y, y_min, y_max):
        return np.exp(y * (y_max - y_min) + y_min)

    def normalize(self, y):
        y = np.log(y)
        # if self.max_card is not None:
        #     return (y - 0) / (self.max_card - 0)
        # else:
        return (y - min(y)) / (max(y) - min(y))

    def q_loss(self, y_true, y_pred):
        y_true = self.denormalize(y_true, 0, self.max_card)
        y_pred = self.denormalize(y_pred, 0, self.max_card)

        return K.maximum(y_true, y_pred) / K.minimum(y_true, y_pred)

    def q_loss_np(self, y_true, y_pred):
        y_true = self.denormalize_np(y_true, 0, self.max_card)
        y_pred = self.denormalize_np(y_pred, 0, self.max_card)

        return np.maximum(y_true, y_pred) / np.minimum(y_true, y_pred)

    def load_data_file(self, file_path: str):
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

        self.set_data(data)

    def set_data(self, data: Dict[str, np.ndarray]):
        self.data = data

        self.max_card = np.log(np.max(self.data["y"]))

        self.input_length = len(self.data["x"][0])

        self.data["y"] = self.normalize(self.data["y"])

    def split_data(self, split: float = 0.9):
        if "x" not in self.data or self.data["x"] is None:
            raise KeyError("You're trying to split data you haven't even loaded! Be sure to load data before attempting"
                           " to split it!")

        sample = np.random.choice(range(len(self.data["x"])), size=int(len(self.data["x"]) * split), replace=False)
        not_sample = list(set(range(len(self.data["x"]))) - set(sample))

        self.training_data["x"] = self.data["x"][sample]
        self.training_data["y"] = self.data["y"][sample]
        if "postgres_estimate" in self.data and self.data["postgres_estimate"]:
            self.training_data["postgres_estimate"] = self.data["postgres_estimate"][sample]

        self.test_data["x"] = self.data["x"][not_sample]
        self.test_data["y"] = self.data["y"][not_sample]
        if "postgres_estimate" in self.data and self.data["postgres_estimate"]:
            self.test_data["postgres_estimate"] = self.data["postgres_estimate"][not_sample]

    def train(self, epochs: int = 100, verbose: int = 0, shuffle: bool = True, batch_size: int = 32,
              validation_split: float = 0.1):
        if "x" not in self.training_data or self.training_data["x"] is None or "y" not in self.training_data or \
                self.training_data["y"] is None:
            raise KeyError("You're trying to train the network without loading data! Be sure to load data before "
                           "attempting to train the neural network!")
        if not self.model:
            raise ValueError("You haven't built a model to train yet.")

        return self.model.fit(self.training_data["x"], self.training_data["y"], epochs=epochs, verbose=verbose,
                              shuffle=shuffle, batch_size=batch_size, validation_split=validation_split)

    def test(self):
        if "x" not in self.test_data or self.test_data["x"] is None or "y" not in self.test_data or \
                self.test_data["y"] is None:
            raise KeyError("You're trying to test the network without loading data! Be sure to load data before "
                           "attempting to test the neural network!")
        if not self.model:
            raise ValueError("You haven't built a model to test yet.")

        return self.model.predict(self.test_data["x"])

    def predict(self, data: np.ndarray):
        if not self.model:
            raise ValueError("You haven't built a model to predict with, yet.")

        return self.model.predict(data)

    def run(self, data_file_path: str, epochs: int = 100, verbose: int = 1, shuffle: bool = True, batch_size: int = 32,
            validation_split: float = 0.1, save_history: bool = True):
        self.load_data_file(data_file_path)
        self.split_data()
        self.get_model(self.input_length)
        history = self.train(epochs=epochs, verbose=verbose, shuffle=shuffle, batch_size=batch_size,
                             validation_split=validation_split)
        predictions = self.test()

        if save_history:
            self.save_history(history.history)

        q_error_means = [np.mean(self.q_loss_np(self.test_data["y"], predictions[:, 0]))]

        return q_error_means


# TODO: add documentation, add safety-features, add save-methods

est = Estimator()
est.run("vectors_census.csv", epochs=1)
