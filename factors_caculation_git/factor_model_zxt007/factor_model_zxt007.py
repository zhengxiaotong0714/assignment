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
        self.n = cfg['params'].get('n', 6)

        '''
        load data you need
        '''
        self.amount_df = self.dataloader.load_dailydata('amount')

        logger.info(f"{cfg['factor_id']} done with initialization")


    def daily_handler(self,date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_n = self.trading_dates[max(0, date_idx - self.n + 1)]

        tmp_amount_df = self.amount_df.loc[date_n:date_now]

        factor_thisday = - tmp_amount_df.std()
        factor_thisday = factor_thisday.replace([np.inf,-np.inf],np.nan)

        return factor_thisday











