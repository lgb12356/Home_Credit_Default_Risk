# coding:utf-8

import os
import numpy as np
import pandas as pd


class PrepareCreditCard(object):

    def __init__(self, *, input_path):
        self.__input_path = input_path

        # data prepare
        self.__credit_card = None

        # data transform
        self.__start_time = pd.Timestamp("2018-07-20")

    def data_prepare(self):
        self.__credit_card = pd.read_csv(os.path.join(self.__input_path, "credit_card_balance.csv"))

    def data_transform(self):
        # self.__credit_card = self.__credit_card.replace(365243.0, np.nan)
        self.__credit_card["MONTHS_BALANCE"] = pd.to_timedelta(self.__credit_card["MONTHS_BALANCE"], "M")
        self.__credit_card["MONTHS_BALANCE"] += self.__start_time

        self.__credit_card = pd.get_dummies(
            data=self.__credit_card,
            prefix="FLAG_CREDIT_CARD",
            dummy_na=True,
            columns=self.__credit_card.select_dtypes(include="object").columns.tolist()
        )

    def data_generate(self):
        self.__credit_card["NEW_AMT_BALANCE_DIVIDE_AMT_CREDIT_LIMIT_ACTUAL"] = (
            # 余额可能大于额度
            self.__credit_card["AMT_BALANCE"] /
            self.__credit_card["AMT_CREDIT_LIMIT_ACTUAL"].replace(0, np.nan)
        )

        self.__credit_card["NEW_AMT_DRAWINGS_ATM_CURRENT_DIVIDE_CNT_DRAWINGS_ATM_CURRENT"] = (
            # ATM 平均每次取款金额
            self.__credit_card["AMT_DRAWINGS_ATM_CURRENT"] /
            self.__credit_card["CNT_DRAWINGS_ATM_CURRENT"].replace(0, np.nan)
        )

        self.__credit_card["NEW_AMT_DRAWINGS_CURRENT_DIVIDE_CNT_DRAWINGS_CURRENT"] = (
            # 平均每次取款金额
            self.__credit_card["AMT_DRAWINGS_CURRENT"] /
            self.__credit_card["CNT_DRAWINGS_CURRENT"].replace(0, np.nan)
        )

        self.__credit_card["NEW_AMT_DRAWINGS_OTHER_CURRENT_DIVIDE_CNT_DRAWINGS_OTHER_CURRENT"] = (
            # 平均每次取款其他金额
            self.__credit_card["AMT_DRAWINGS_OTHER_CURRENT"] /
            self.__credit_card["CNT_DRAWINGS_OTHER_CURRENT"].replace(0, np.nan)
        )

        self.__credit_card["NEW_AMT_DRAWINGS_POS_CURRENT_DIVIDE_CNT_DRAWINGS_POS_CURRENT"] = (
            # 平均每次取款其他金额
            self.__credit_card["AMT_DRAWINGS_POS_CURRENT"] /
            self.__credit_card["CNT_DRAWINGS_POS_CURRENT"].replace(0, np.nan)
        )

        self.__credit_card["NEW_SUM_AMT_DRAWINGS"] = (
            self.__credit_card["AMT_DRAWINGS_ATM_CURRENT"] + self.__credit_card["AMT_DRAWINGS_CURRENT"] +
            self.__credit_card["AMT_DRAWINGS_OTHER_CURRENT"] + self.__credit_card["AMT_DRAWINGS_POS_CURRENT"]
        )

        self.__credit_card["NEW_SUM_CNT_DRAWINGS"] = (
            self.__credit_card["CNT_DRAWINGS_ATM_CURRENT"] + self.__credit_card["CNT_DRAWINGS_CURRENT"] +
            self.__credit_card["CNT_DRAWINGS_OTHER_CURRENT"] + self.__credit_card["CNT_DRAWINGS_POS_CURRENT"]
        )

    def data_return(self):
        # print(self.__credit_card.head())

        return self.__credit_card

if __name__ == "__main__":
    pcc = PrepareCreditCard(
        input_path="C:\\Users\\puhui\\Desktop"
    )
    pcc.data_prepare()
    pcc.data_transform()
    pcc.data_generate()
    pcc.data_return()
