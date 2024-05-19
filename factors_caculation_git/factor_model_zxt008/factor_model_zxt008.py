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
        self.n = cfg['params'].get('nday',20)

        self.type = cfg['params'].get('type',0)

        self.k = cfg['params'].get('k',0.2)


        '''
        load data you need
        '''
        self.high_adj_df = self.dataloader.load_dailydata('high_adj')
        self.low_adj_df = self.dataloader.load_dailydata('low_adj')
        self.clse_adj_df = self.dataloader.load_dailydata('close_adj')
        self.volume_df = self.dataloader.load_dailydata('volume')


        '''
        if some calc steps are very easy,you can type them here
        '''
        def rank(df):
            """
            横截面等级。
            参数: df: a pandas DataFrame.
            输出: 按照【列】百分比排列的 pandas DataFrame
            """
            return df.rank(pct=True,axis = 1)
        self.amp_df = rank(rank(self.high_adj_df).rolling(window=5).cov(rank(self.volume_df)))

        logger.info(f"{cfg['factor_id']} done with initialization")



    def daily_handler(self, date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        factor_thisday = -self.amp_df.loc[date_now]
        factor_thisday = factor_thisday.replace([np.inf, -np.inf], np.nan)

        return factor_thisday