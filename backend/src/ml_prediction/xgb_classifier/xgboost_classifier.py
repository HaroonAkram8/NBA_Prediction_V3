import os
import yaml

from xgboost import XGBClassifier

from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import RandomizedSearchCV

import numpy as np

from src.ml_prediction.load_dataset import load_clustered_dataset
from src.globals import (
    TRAIN, VALIDATION, TEST, COLUMNS_TO_REMOVE
)


class XGBoost_Classifier:
    def __init__(self):
        self.train_set, self.val_set, self.test_set, self.gamelogs = None, None, None, None
        self.model = None
        self.hyperparameters = {}
        self.log_loss = None

    def load(self, train_val_test_split: list = [0.7, 0.15], paired: bool = True, num_rows_per_cluster: int = 10, columns_to_remove: list = []):
        self.train_set, self.val_set, self.test_set, self.gamelogs = load_clustered_dataset(train_val_test_split=train_val_test_split,
                                                                                            paired=paired,
                                                                                            columns_to_remove=columns_to_remove,
                                                                                            num_rows_per_cluster=num_rows_per_cluster)
        self.train_set = self.__flatten_dataset__(self.train_set)
        self.val_set = self.__flatten_dataset__(self.val_set)
        self.test_set = self.__flatten_dataset__(self.test_set)

    def _get_features_labels(self):
        X_train = [item[0] for item in self.train_set]
        y_train = [item[1] for item in self.train_set]
        return X_train, y_train

    def save_model(self):
        fitness = str(round(abs(self.log_loss), 3)).replace('.', '_')
        model_name = f'xgboost-model-{fitness}.json'
        file_path = os.path.realpath(__file__)
        dir_path = os.path.dirname(file_path)
        model_dir = os.path.join(dir_path, 'models')
        model_path = os.path.join(model_dir, model_name)
        self.model.save_model(model_path)

        hyperparameters_name = f'hypr-{fitness}.yaml'
        hypr_path = os.path.join(model_dir, hyperparameters_name)
        with open(hypr_path, 'w') as file:
            yaml.dump(self.hyperparameters, file)

    def search_hyperparameters(self, num_trials: int = 10):
#        hyperparameter_space = {
#                'n_estimators': np.arange(200, 3001, 50),
#                'learning_rate': [0.003, 0.01, 0.05, 0.1, 0.3],
#                'max_depth': np.arange(3, 7, 1),
#                'subsample': np.arange(0.4, 1, 0.03),
#                'colsample_bytree': np.arange(0.6, 1, 0.03),
#                'colsample_bylevel': np.arange(0.6, 1, 0.03),
#                'colsample_bynode': np.arange(0.6, 1, 0.03),
#                'gamma': [0, 0.1, 0.2, 0.3],
#                }
        hyperparameter_space = {
                'n_estimators': np.arange(200, 3001, 50),
                'learning_rate': [0.003, 0.01, 0.05, 0.1, 0.3],
                'max_depth': [5], #np.arange(3, 7, 1),
                'subsample': [0.7], #np.arange(0.4, 1, 0.03),
                'colsample_bytree': [0.8], #np.arange(0.6, 1, 0.03),
                'colsample_bylevel': [0.8], #np.arange(0.6, 1, 0.03),
                'colsample_bynode': [0.8], #np.arange(0.6, 1, 0.03),
                'gamma': [0.05], #[0, 0.1, 0.2, 0.3],
                }

        X_train, y_train = self._get_features_labels()

        xgb_model = XGBClassifier(objective='binary:logistic')
        random_search = RandomizedSearchCV(xgb_model, param_distributions=hyperparameter_space,
                                           n_iter=num_trials, scoring='neg_log_loss',
                                           n_jobs=-1, cv=5, verbose=3, refit=False)
        random_search.fit(X_train, y_train)

        print(f"Best parameters found: {random_search.best_params_}")
        print(f"Best log_loss found: {random_search.best_score_}")
        self.log_loss = random_search.best_score_

        self.hyperparameters = random_search.best_params_

    def train(self):
        X_train, y_train = self._get_features_labels()

        self.model = XGBClassifier(objective='binary:logistic', **self.hyperparameters)
        self.model.fit(X_train, y_train)

        return self.__predict__(dataset=self.train_set)

    def accuracy_results(self, data_type: int = TRAIN):
        if data_type == TRAIN:
            return self.__predict__(dataset=self.train_set)
        elif data_type == VALIDATION:
            return self.__predict__(dataset=self.val_set)
        elif data_type == TEST:
            return self.__predict__(dataset=self.test_set)

        return None, None, None, None

    def __predict__(self, dataset: list = []):
        X_test = [item[0] for item in dataset]
        y_test = [item[1] for item in dataset]

        y_pred = self.model.predict(X_test)

        return accuracy_score(y_test, y_pred), classification_report(y_test, y_pred), y_test, y_pred

    def __flatten_dataset__(self, dataset: list = []):
        flattened_set = []

        for entry in dataset:
            flattened_set.append((self.__flatten__(entry[0]), entry[1]))

        return flattened_set

    def __flatten__(self, l: list = []):
        return [item for sublist in l for item in sublist]


def main():
    xgb_classif_model = XGBoost_Classifier()

    xgb_classif_model.load(columns_to_remove=COLUMNS_TO_REMOVE, num_rows_per_cluster=10)

    xgb_classif_model.search_hyperparameters(10)
    train_acc, train_classif_rep, train_test, train_pred = xgb_classif_model.train()
    print('Train accuracy: ' + str(train_acc))
    print(train_classif_rep)

    val_acc, val_classif_rep, val_test, val_pred = xgb_classif_model.accuracy_results(data_type=VALIDATION)
    print('Validation accuracy: ' + str(val_acc))
    print(val_classif_rep)

    xgb_classif_model.save_model()


if __name__ == "__main__":
    main()
