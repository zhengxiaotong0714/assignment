import gc

import pandas as pd
import numpy as np
import sys
from sklearn.linear_model import LinearRegression


def mul_neut(factor_score, risks_df):

    all_df = risks_df

    all_df['raw'] = factor_score.replace([np.inf,-np.inf], np.nan)
    all_df = all_df.dropna()

    lr = LinearRegression()
    if (all_df.shape[0]) == 0:
        return pd.Series().reindex(factor_score.index)
    lr.fit(all_df.drop('raw', axis=1), all_df['raw'])
    factor_predict = lr.predict(all_df.drop('raw', axis=1))
    result =  (all_df['raw'] - factor_predict).reindex(factor_score.index)

    return result

class Operator():
    def __init__(self,dataloader):
        self.dataloader = dataloader
        self.loaded_data_dict = {}

    def op_rank(self,raw_factor_df,params={})->pd.Series:
        return raw_factor_df.iloc[-1].rank(pct=True)

    def op_tsrank(self,raw_factor_df:pd.DataFrame,params={})->pd.Series:
        n = params.get('n',20)
        return raw_factor_df.iloc[-n:].rank(pct=True).iloc[-1]

    def op_neut(self, raw_factor_df: pd.DataFrame, params={})->pd.Series:
        date = raw_factor_df.index[-1]

        risks = params.get('risks','')
        risks_name_list = risks.split(',')

        risks_df = pd.DataFrame()
        for risk_name in risks_name_list:
            if risk_name in self.loaded_data_dict.keys():
                risks_df[risk_name] = self.loaded_data_dict[risk_name].loc[date].replace([np.inf,-np.inf], np.nan)
            else:
                risk_df = self.dataloader.load_dailydata(risk_name)
                self.loaded_data_dict[risk_name] = risk_df
                risks_df[risk_name] = risk_df.loc[date].replace([np.inf,-np.inf], np.nan)

        result = mul_neut(raw_factor_df.loc[date],risks_df)
        return result

    def op_rankneut(self, raw_factor_df: pd.DataFrame, params={})->pd.Series:
        date = raw_factor_df.index[-1]

        risks = params.get('risks','')
        risks_name_list = risks.split(',')

        risks_df = pd.DataFrame()
        for risk_name in risks_name_list:
            if risk_name in self.loaded_data_dict.keys():
                risks_df[risk_name] = self.loaded_data_dict[risk_name].loc[date].replace([np.inf,-np.inf], np.nan).rank(pct=True)
            else:
                risk_df = self.dataloader.load_dailydata(risk_name)
                self.loaded_data_dict[risk_name] = risk_df
                risks_df[risk_name] = risk_df.loc[date].replace([np.inf,-np.inf], np.nan).rank(pct=True)

        result = mul_neut(raw_factor_df.loc[date],risks_df)
        return result

    def op_capsecneut(self, raw_factor_df: pd.DataFrame, params={})->pd.Series:
        date = raw_factor_df.index[-1]


        cap_series = pd.Series(dtype=np.float32)
        if 'S_VAL_MV' in self.loaded_data_dict.keys():
            cap_series= self.loaded_data_dict['S_VAL_MV'].loc[date].replace([np.inf,-np.inf], np.nan)
        else:
            cap_df = self.dataloader.load_dailydata('S_VAL_MV')
            self.loaded_data_dict['S_VAL_MV'] = cap_df
            cap_series = cap_df.loc[date].replace([np.inf,-np.inf], np.nan)

        sector_series = pd.Series(dtype=np.float32)
        if 'citics_1' in self.loaded_data_dict.keys():
            sector_series= self.loaded_data_dict['citics_1'].loc[date].replace([np.inf,-np.inf], np.nan)
        else:
            sector_df = self.dataloader.load_dailydata('citics_1')
            self.loaded_data_dict['citics_1'] = sector_df
            sector_series = sector_df.loc[date].replace([np.inf,-np.inf], np.nan)

        cap_series = np.log(cap_series)
        sector_dummies = pd.get_dummies(sector_series.replace(0, np.nan)).reindex(raw_factor_df.columns)
        risks_df = pd.DataFrame(cap_series)
        risks_df = pd.concat([risks_df, sector_dummies], axis=1)
        result = mul_neut(raw_factor_df.loc[date],risks_df)
        return result
