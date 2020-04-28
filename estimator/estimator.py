import numpy as np
from keras import backend as K
from keras.layers import Dense, Input, Dropout
from keras.models import Model
from keras.optimizers import Adam


class Estimator:
    max_card_log: int = None

    model: Model = None

    def __init__(self):
        print("Placeholder")

    @staticmethod
    def get_model(width: int = 64, depth: int = 2, loss: str = "mean_squared_error", len_input: int = 32,
                  dropout: float = 0.2, learning_rate: float = 0.0001, kernel_initializer: str = "normal"):

        one_input = Input(shape=(len_input,), name='one_input')
        x = Dense(width, activation="relu", kernel_initializer=kernel_initializer)(one_input)

        for i in range(1, depth):
            width = max(8, int(width / 2))
            x = Dense(width, activation="relu", kernel_initializer=kernel_initializer)(x)
            x = Dropout(dropout)(x)

        x = Dense(1, kernel_initializer=kernel_initializer, name="main_output", activation="linear")(x)

        model = Model(inputs=one_input, outputs=x)
        model.compile(loss=loss, optimizer=Adam(lr=learning_rate))

        return model

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
