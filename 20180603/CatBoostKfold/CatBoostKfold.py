# coding:utf-8

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
np.random.seed(7)


class CatBoostKfold(object):

    def __init__(self, *, input_path, output_path, output_file_name):
        self.__input_path = input_path
        self.__output_path = output_path
        self.__output_file_name = output_file_name

        self.__train, self.__test = [None for _ in range(2)]
        self.__sample_submission = None
        self.__train_feature, self.__train_label = [None for _ in range(2)]
        self.__test_feature = None
        self.__categorical_index = None
        self.__numeric_index = None

        self.__folds = None
        self.__oof_preds = None
        self.__sub_preds = None
        self.__cat = None

    def data_prepare(self):
        self.__train = pd.read_csv(os.path.join(self.__input_path, "train_feature_df.csv"))
        self.__test = pd.read_csv(os.path.join(self.__input_path, "test_feature_df.csv"))
        self.__sample_submission = pd.read_csv(os.path.join(self.__input_path, "sample_submission_one.csv"))

        self.__train_label = self.__train["TARGET"]
        self.__train_feature = self.__train.drop("TARGET", axis=1)
        self.__test_feature = self.__test[self.__train_feature.columns]

        self.__categorical_index = np.where(self.__train_feature.dtypes == "object")[0]
        self.__numeric_index = np.where(self.__train_feature.dtypes != "object")[0]

        self.__train_feature.iloc[:, self.__categorical_index] = (
            self.__train_feature.iloc[:, self.__categorical_index].fillna("missing")
        )
        self.__test_feature.iloc[:, self.__categorical_index] = (
            self.__test_feature.iloc[:, self.__categorical_index].fillna("missing")
        )
        self.__train_feature.iloc[:, self.__numeric_index] = (
            self.__train_feature.iloc[:, self.__numeric_index].apply(
                lambda x: x.fillna(-999.0) if x.median() > 0 else x.fillna(999.0)
            )
        )
        self.__test_feature.iloc[:, self.__numeric_index] = (
            self.__test_feature.iloc[:, self.__numeric_index].apply(
                lambda x: x.fillna(-999.0) if x.median() > 0 else x.fillna(999.0)
            )
        )

    def model_fit(self):
        self.__folds = StratifiedKFold(n_splits=5, shuffle=True)
        self.__oof_preds = np.zeros(shape=self.__train_feature.shape[0])
        self.__sub_preds = np.zeros(shape=self.__test_feature.shape[0])

        for n_fold, (trn_idx, val_idx) in enumerate(self.__folds.split(self.__train_feature, self.__train_label)):
            trn_x, trn_y = self.__train_feature.iloc[trn_idx], self.__train_label.iloc[trn_idx]
            val_x, val_y = self.__train_feature.iloc[val_idx], self.__train_label.iloc[val_idx]

            self.__cat = CatBoostClassifier(
                iterations=3500,
                od_type="Iter",
                eval_metric="AUC"
            )
            self.__cat.fit(
                trn_x,
                trn_y,
                cat_features=self.__categorical_index,
                eval_set=[(val_x, val_y)],
                use_best_model=True
            )
            pred_val = self.__cat.predict_proba(val_x)[:, 1]
            pred_test = self.__cat.predict_proba(self.__test_feature)[:, 1]

            self.__oof_preds[val_idx] = pred_val
            self.__sub_preds += pred_test / self.__folds.n_splits

    def model_predict(self):
        self.__sample_submission["TARGET"] = self.__sub_preds
        self.__sample_submission.to_csv(os.path.join(self.__output_path, self.__output_file_name), index=False)


if __name__ == "__main__":
    cbk = CatBoostKfold(
        input_path=sys.argv[1],
        output_path=sys.argv[2],
        output_file_name=sys.argv[3]
    )
    cbk.data_prepare()
    cbk.model_fit()
    cbk.model_predict()