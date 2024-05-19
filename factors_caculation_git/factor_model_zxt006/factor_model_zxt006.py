import sys
sys.path.append("/home/quant/work/code/share/common/")
import pandas as pd
import numpy as np
import logging

from model_base import FactorModelBase

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FactorModel(FactorModelBase):
    def __init__(self,cfg):
        super().__init__(cfg)

        '''
        get params you set in config_factor_xxx.py
        '''
        self.n = cfg['params'].get('n', 9)
        self.m = cfg['params'].get('m', 30)
        '''
        load data you need
        '''
        self.open_adj_df = self.dataloader.load_dailydata('open_adj')
        self.close_adj_df = self.dataloader.load_dailydata('close_adj')
        self.high_adj_df = self.dataloader.load_dailydata('high_adj')
        self.low_adj_df = self.dataloader.load_dailydata('low_adj')
        '''
        if some calc steps are very easy,you can type them here
        '''
        self.close_open = self.close_adj_df - self.open_adj_df
        self.close_open_abs = self.close_open.abs()
        self.low_min = self.low_adj_df.rolling(window=self.n, min_periods=1).min()
        self.high_max = self.high_adj_df.rolling(window=self.n, min_periods=1).max()
        self.factor = (self.close_adj_df - self.low_min) / (self.high_max - self.low_min) * 100

        logger.info(f"{cfg['factor_id']} done with initialization")

    def daily_handler(self,date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_past = self.trading_dates[max(0, date_idx - self.m):date_idx]

        factor = self.factor.loc[date_past]

        def sma(data, n, m):
            result = data.copy()
            for i in range(1, len(data)):
                result.iloc[i] = ((data.iloc[i] * m) + (result.iloc[i - 1] * (n - m))) / n
            return result
        factor_thisday = sma(factor, 3, 1)
        factor_thisday = - factor_thisday.iloc[-1]
        factor_thisday = factor_thisday.replace([np.inf,-np.inf],np.nan)

        return factor_thisday
