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
        self.high = self.dataloader.load_dailydata('high_adj')
        self.low = self.dataloader.load_dailydata('low_adj')
        self.clse_yes = self.dataloader.load_dailydata('close_adj').shift()
        self.open = self.dataloader.load_dailydata('open_adj')
        self.volume = self.dataloader.load_dailydata('volume')
        self.turn_yes = self.dataloader.load_dailydata('S_DQ_TURN').shift()


        '''
        因子公式：
        factor =  (ts_rank((self.volume / self.adv20), 20) * ts_rank((-1 * delta(self.clse, 7)), 8)) 
        '''
        
        logger.info(f"{cfg['factor_id']} done with initialization")



    def daily_handler(self, date_idx) -> pd.Series:
        date_now = self.trading_dates[date_idx]
        date_n = self.trading_dates[date_idx - self.n]

        tmp_opn_df = self.open.loc[date_n:date_now]
        tmp_clse_yes_df = self.clse_yes.loc[date_n:date_now]
        tmp_turn_yes_df = self.turn_yes.loc[date_n:date_now]

        night_ret = tmp_opn_df/tmp_clse_yes_df - 1
        factor_thisday = night_ret.where(night_ret<0).corrwith(tmp_turn_yes_df)


        factor_thisday = factor_thisday.replace([np.inf, -np.inf], np.nan)

        return factor_thisday