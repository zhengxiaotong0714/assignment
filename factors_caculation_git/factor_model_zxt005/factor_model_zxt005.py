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
        self.n = cfg['params'].get('n', 1)

        '''
        load data you need
        '''
        self.open_adj_df = self.dataloader.load_dailydata('open_adj')
        self.close_adj_df = self.dataloader.load_dailydata('close_adj')

        logger.info(f"{cfg['factor_id']} done with initialization")


    def daily_handler(self,date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_n = self.trading_dates[date_idx-self.n]

        # Get the open price of the current day and close price of n days ago
        open_now = self.open_adj_df.loc[date_now]
        close_n_days_ago = self.close_adj_df.loc[date_n]

        # Calculate the factor
        factor_thisday = open_now / close_n_days_ago - 1
        factor_thisday = factor_thisday.replace([np.inf,-np.inf],np.nan)

        return factor_thisday










