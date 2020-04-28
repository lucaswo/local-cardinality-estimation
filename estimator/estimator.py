from typing import Dict, Any

import numpy as np
import yaml
from keras import backend as K
from keras.layers import Dense, Input, Dropout
from keras.models import Model
from keras.optimizers import Adam


class Estimator:
    max_card_log: int = None

    config: dict = None
    data_x = None
    data_y = None

    model: Model = None

    def __init__(self, config: Dict[str, Any] = None, data_x=None, data_y=None, model: Model = None, debug: bool = True):

        if config is None:
            with open("config.yaml") as file:
                config = yaml.safe_load(file)

        conf_keys = ["width", "loss_function", "dropout", "learning_rate", "kernel_initializer", "activation_strategy"]

        for key in conf_keys:
            if config[key] is None or config[key] == "":
                raise ValueError(
                    "Value for {} is needed! You can provide it with the config dict or in config.yaml!".format(key))

        if config["layer"] is None or config["layer"] == "" or len(config["layer"]) < 1:
            raise ValueError("Value for layer is needed! You can provide it with the config dict or in config.yaml!")

        self.config = config

        self.data_x = data_x
        self.data_y = data_y

        self.model = model

        if debug:
            print("Initialized Estimator with {}".format(config))

    def get_model(self, len_input: int = 32) -> Model:

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
        if self.max_card_log is not None:
            return (y - 0) / (self.max_card_log - 0)
        else:
            return (y - min(y)) / (max(y) - min(y))

    def q_loss(self, y_true, y_pred):
        y_true = self.denormalize(y_true, 0, self.max_card_log)
        y_pred = self.denormalize(y_pred, 0, self.max_card_log)

        return K.maximum(y_true, y_pred) / K.minimum(y_true, y_pred)

    def q_loss_np(self, y_true, y_pred):
        y_true = self.denormalize_np(y_true, 0, self.max_card_log)
        y_pred = self.denormalize_np(y_pred, 0, self.max_card_log)

        return np.maximum(y_true, y_pred) / np.minimum(y_true, y_pred)

    def split_data(self):
        print()

    def train(self):
        print()

    def test(self):
        print()

    def evaluate(self):
        print()


est = Estimator()
est.get_model()
