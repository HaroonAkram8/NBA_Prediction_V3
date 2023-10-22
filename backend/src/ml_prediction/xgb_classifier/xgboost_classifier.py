from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

from src.ml_prediction.load_dataset import load_clustered_dataset
from src.globals import (
    TRAIN, VALIDATION, TEST, COLUMNS_TO_REMOVE
)


class XGBoost_Classifier:
    def __init__(self):
        self.train_set, self.val_set, self.test_set, self.gamelogs = None, None, None, None
        self.model = XGBClassifier()

    def load(self, train_val_test_split: list = [0.7, 0.15], paired: bool = True, num_rows_per_cluster: int = 10, columns_to_remove: list = []):
        self.train_set, self.val_set, self.test_set, self.gamelogs = load_clustered_dataset(train_val_test_split=train_val_test_split,
                                                                                            paired=paired,
                                                                                            columns_to_remove=columns_to_remove,
                                                                                            num_rows_per_cluster=num_rows_per_cluster)
        self.train_set = self.__flatten_dataset__(self.train_set)
        self.val_set = self.__flatten_dataset__(self.val_set)
        self.test_set = self.__flatten_dataset__(self.test_set)

    def train(self):
        X_train = [item[0] for item in self.train_set]
        y_train = [item[1] for item in self.train_set]

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

    xgb_classif_model.load(columns_to_remove=COLUMNS_TO_REMOVE)

    train_acc, train_classif_rep, train_test, train_pred = xgb_classif_model.train()
    print('Train accuracy: ' + str(train_acc))
    print(train_classif_rep)

    val_acc, val_classif_rep, val_test, val_pred = xgb_classif_model.accuracy_results(data_type=VALIDATION)
    print('Validation accuracy: ' + str(val_acc))
    print(val_classif_rep)


if __name__ == "__main__":
    main()
