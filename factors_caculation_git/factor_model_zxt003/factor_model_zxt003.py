import sys
sys.path.append("D:\Python\Jupyter\AlgoTrade\assignment_zxt\code\framework\common")
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
        self.n = cfg['params'].get('n', 4)
        self.m = cfg['params'].get('m', 20)
        '''
        load data you need
        '''
        self.high_adj_df = self.dataloader.load_dailydata('high_adj')
        self.open_adj_df = self.dataloader.load_dailydata('open_adj')
        '''
        if some calc steps are very easy,you can type them here
        '''
        self.weighted_price = self.open_adj_df * 0.85 + self.high_adj_df * 0.15
        self.price_delta = self.weighted_price.diff(self.n)
        self.sign_delta = np.sign(self.price_delta)

        logger.info(f"{cfg['factor_id']} done with initialization")


    def daily_handler(self,date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_n = self.trading_dates[date_idx-self.m]

        sign_delta = self.sign_delta.loc[date_n:date_now]
        rank_delta = sign_delta.rank()

        factor_thisday = - rank_delta.iloc[-1]
        factor_thisday = factor_thisday.replace([np.inf,-np.inf],np.nan)

        return factor_thisday
