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
        self.N = cfg['params'].get('N', 12)
        self.M = cfg['params'].get('M', 6)

        '''
        load data you need
        '''
        self.close_adj_df = self.dataloader.load_dailydata('close_adj')

        '''
        if some calc steps are very easy,you can type them here
        '''
        self.ROC_df = (self.close_adj_df - self.close_adj_df.shift(self.N)) / self.close_adj_df.shift(self.N)

        logger.info(f"{cfg['factor_id']} done with initialization")


    def daily_handler(self,date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_M = self.trading_dates[max(0, date_idx-self.M+1)]

        ROC_M_days = self.ROC_df.loc[date_M:date_now]
        ROCMA = ROC_M_days.mean()
        ROC_now = self.ROC_df.loc[date_now]
        factor_thisday = -(ROC_now - ROCMA)
        factor_thisday = factor_thisday.replace([np.inf,-np.inf],np.nan)

        return factor_thisday