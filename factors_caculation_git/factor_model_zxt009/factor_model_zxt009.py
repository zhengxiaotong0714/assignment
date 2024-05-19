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
        self.n1 = cfg['params'].get('n1', 20)
        self.n2 = cfg['params'].get('n2', 5)

        '''
        load data you need
        '''
        self.volume_df = self.dataloader.load_dailydata('volume')
        self.high_adj_df = self.dataloader.load_dailydata('high_adj')
        self.low_adj_df = self.dataloader.load_dailydata('low_adj')
        self.clse_adj_df = self.dataloader.load_dailydata('close_adj')
        '''
        if some calc steps are very easy,you can type them here
        '''
        self.volume_mean = self.volume_df.rolling(window=self.n1).mean()

        logger.info(f"{cfg['factor_id']} done with initialization")


    def daily_handler(self,date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_n2 = self.trading_dates[max(0, date_idx - self.n2 + 1)]

        mean_volume = self.volume_mean.loc[date_n2:date_now]
        low = self.low_adj_df.loc[date_n2:date_now]
        high = self.high_adj_df.loc[date_now]
        close = self.clse_adj_df.loc[date_now]
        low_now = self.low_adj_df.loc[date_now]

        corr = mean_volume.corrwith(low)
        factor_thisday = (corr + ((high + low_now) / 2)) - close
        factor_thisday = factor_thisday.replace([np.inf,-np.inf],np.nan)

        return factor_thisday











