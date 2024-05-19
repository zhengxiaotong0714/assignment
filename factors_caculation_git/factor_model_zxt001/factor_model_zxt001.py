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
        self.n = cfg['params'].get('n',20)
        self.k = cfg['params'].get('k',0.2)

        '''
        load data you need
        '''
        self.high_adj_df = self.dataloader.load_dailydata('high_adj')
        self.low_adj_df = self.dataloader.load_dailydata('low_adj')
        self.clse_adj_df = self.dataloader.load_dailydata('close_adj')
        '''
        if some calc steps are very easy,you can type them here
        '''
        self.amp_df = self.high_adj_df/self.low_adj_df - 1

        logger.info(f"{cfg['factor_id']} done with initialization")


    def daily_handler(self,date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_n = self.trading_dates[date_idx-self.n]

        tmp_amp_df = self.amp_df.loc[date_n:date_now]
        tmp_clse_df = self.clse_adj_df.loc[date_n:date_now]

        factor_thisday = - tmp_amp_df.corrwith(tmp_clse_df)
        factor_thisday = factor_thisday.replace([np.inf,-np.inf],np.nan)

        return factor_thisday











