import importlib
import pandas as pd
import numpy as np
import logging
import os
import path
import click
import sys
import gc
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - CUHKSZ - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Engine():
    def __init__(self,cfg):
        self.config = cfg
        self.univ = list(map(lambda x:x.strip(),open(os.path.join(cfg['dir']['meta_dir'],'universe.txt')).readlines()))
        self.trading_dates = list(map(lambda x:x.strip(),open(os.path.join(cfg['dir']['meta_dir'],'trading_dates.txt')).readlines()))
        self.factor_model_obj_list = []

    def run(self):
        sys.path.append(self.config['dir']['factor_model_files_dir'])
        for factor_model in self.config['factors']:
            factor_model_class = importlib.__import__(factor_model['factor_model_file'])
            cfg = {
                'data_dir':self.config['dir']['data_dir'],
                'meta_dir':self.config['dir']['meta_dir'],
                'params':factor_model['params'],
                'factor_id':factor_model['factor_id']
            }
            factor_model_obj = factor_model_class.FactorModel(cfg)
            self.factor_model_obj_list.append(
                (factor_model['factor_id'], factor_model_obj, pd.DataFrame(columns=self.univ),pd.DataFrame(columns=self.univ),factor_model['operators'])
            )

        self.operator_obj = importlib.__import__('operators').Operator(factor_model_obj.dataloader)

        start_date = self.config['date']['start_date']
        end_date = self.config['date']['end_date']
        if start_date > end_date:
            raise ValueError("start_date 不能大于 end_date!")
        if start_date<self.trading_dates[0]:
            raise ValueError("start_date 超出数据范围！")
        if end_date<self.trading_dates[0]:
            raise ValueError("end_date 超出数据范围！")

        selected_trading_dates = [_ for _ in self.trading_dates if _ >= start_date and _ <= end_date]
        for date in selected_trading_dates:
            date_idx = self.trading_dates.index(date)
            self.run_oneday(date_idx)

        for factor_id,factor_model_obj,raw_factor_df,factor_df,operators in self.factor_model_obj_list:
            if not os.path.exists(self.config['dir']['result_save_path']):
                os.mkdir(self.config['dir']['result_save_path'])
            try:
                factor_df.to_csv(os.path.join(self.config['dir']['result_save_path'],f'{factor_id}.csv'))
                logger.info(
                    f"result of {factor_id} saved in {os.path.join(self.config['dir']['result_save_path'],f'{factor_id}.csv')}"
                )
            except:
                factor_df.to_csv(f'{factor_id}.csv')
                logger.info(
                    f"result_save_path error,results saved in current path."
                )

    def run_oneday(self,date_idx):

        for factor_id,factor_model_obj,raw_factor_df,factor_df,operators in self.factor_model_obj_list:
            logger.info(
                f"start running {factor_id} on {self.trading_dates[date_idx]}"
            )

            factor_series = factor_model_obj.daily_handler(date_idx)
            raw_factor_df.loc[self.trading_dates[date_idx],:] = factor_series
            factor_df.loc[self.trading_dates[date_idx],:] = factor_series

            flag = 0
            for operator in operators:
                op = operator['name']
                params = operator['params']
                operator_method = getattr(self.operator_obj, op)
                if not flag:
                    factor_df.loc[self.trading_dates[date_idx],:] = operator_method(raw_factor_df, params)
                    flag = 1
                else:
                    factor_df.loc[self.trading_dates[date_idx],:] = operator_method(factor_df, params)
            logger.info(
                "alpha stats: Min({:.2f}), Q1({:.2f}), Mean({:.2f}), Median({:.2f}), Q9({:.2f}),Max({:.2f}), Cnt({:.0f})".format(
                  factor_series.min(), factor_series.quantile(0.1), factor_series.mean(), factor_series.quantile(0.5),
                    factor_series.quantile(0.9), factor_series.max(), factor_series.count())
            )
@click.command()
@click.argument('configpath', required=True)
def run(configpath):

    configfile = configpath.split("\\")[-1]
    sys.path.append(configpath[:-len(configfile)-1])
    config = importlib.__import__(configfile.split(".")[0]).config
    engine = Engine(config)
    engine.run()

if __name__ == "__main__":
    run()
