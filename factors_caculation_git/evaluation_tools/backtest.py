import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import logging
import click
import sys
import importlib

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - MFE23 - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def backtest_single(factor_df,rtn_df,weights="rank",factor_id='',mode='simple'):
    factor_df = factor_df.copy()
    rtn_df = rtn_df.reindex(factor_df.index) #下一日收益率

    if weights == "rank":
        pos_df = factor_df.rank(axis=1,pct=True) - 0.5 #将因子值转换成横截面的序
        pos_df[pos_df>0] = pos_df[pos_df>0].div(pos_df[pos_df>0].sum(axis=1),axis=0) #归一化，多头仓位之和为1
        pos_df[pos_df<0] = -pos_df[pos_df<0].div(pos_df[pos_df<0].sum(axis=1),axis=0)#空头仓位之和为-1
    else:
        pos_df = factor_df.copy()
        pos_df[pos_df > 0] = pos_df[pos_df > 0].div(pos_df[pos_df > 0].sum(axis=1), axis=0)  # 归一化，多头仓位之和为1
        pos_df[pos_df < 0] = -pos_df[pos_df < 0].div(pos_df[pos_df < 0].sum(axis=1), axis=0)
    pos_df = pos_df.shift()

    if mode == "simple":
        pnl_long = (pos_df[pos_df>0]*rtn_df).sum(axis=1)  - rtn_df.mean(axis=1)#多头超额收益
        pnl_short = (pos_df[pos_df<0]*rtn_df).sum(axis=1) + rtn_df.mean(axis=1)#空头超额收益
        #上面在计算收益率的时候，将pos_df进行了shift。因为我们在计算的因子值的时候，对应日期是数据发生的日期，但我们得到该数据的时间是在数据发生之后。如20160104的收盘价，要在收盘后才能得到用于计算因子。所以我们最早在下一个交易日，即20160105才能进行交易，进而获取股票在20160105-20160106这未来一天的收益。

        tvr = pos_df.fillna(0).diff().abs().sum(axis=1)/(pos_df.fillna(0).abs().sum(axis=1).replace(0,np.nan))
        long_num = pos_df[pos_df>0].where(~pd.isnull(rtn_df)).count(axis=1)
        short_num = pos_df[pos_df<0].where(~pd.isnull(rtn_df)).count(axis=1)

        pnl_long = pnl_long.mask(long_num==0,np.nan)
        pnl_short = pnl_short.mask(short_num==0,np.nan)


        long_pos = pos_df[pos_df>0].sum(axis=1)
        short_pos = pos_df[pos_df<0].sum(axis=1)

        pnl = (pnl_long + pnl_short)/2#多空对冲的超额收益

        result_df = pd.DataFrame({
            'pnl':pnl,
            'pnl_long':pnl_long,
            'tvr':tvr,
            'long_num':long_num,
            'short_num':short_num,
            'long_pos':long_pos,
            'short_pos':short_pos,
        })

        plt.figure(figsize=(16, 8))
        p1 = plt.subplot(111)
        pnl.cumsum().plot(label=f'{factor_id} ls')
        pnl_long.cumsum().plot(label=f'{factor_id} long',ax = p1)
        plt.title(f'long Ann ret:{round(pnl_long.mean()*242,3)}  ls Ann ret:{round(pnl.mean()*242,3)}')

    if mode == "complex":
        pass

    return  pos_df,result_df.reset_index(),plt


def barra_analysis(pos_df,barra_ort_df,barra_ret_df,barra_alpha_df):

    position_series = pos_df.stack()
    position_series = position_series.where(position_series > 0)
    barra_exposure = barra_ort_df.reindex(position_series.index).apply(lambda x: x * position_series)
    barra_exposure_sum_df = barra_exposure.groupby(barra_exposure.index.get_level_values(0)).sum()
    position_barra_ret = barra_exposure_sum_df * barra_ret_df.reindex(pos_df.index)
    position_alpha = (pos_df.where(pos_df > 0) * barra_alpha_df.reindex(pos_df.index)).sum(axis=1)

    ret_sources_df = position_barra_ret
    ret_sources_df['Alpha'] = position_alpha

    plt.figure(figsize=(16, 8))

    p = plt.subplot(111)
    ret_sources_df.cumsum().plot(ax=p)
    p.grid()
    p.set_title(f"ret sources cumsum plot", fontdict={'fontsize': 14})
    return plt



@click.command()
@click.argument('configpath', required=True)
def run(configpath):

    configfile = configpath.split("\\")[-1]
    sys.path.append(configpath[:-len(configfile)-1])
    config = importlib.__import__(configfile.split(".")[0]).config

    rtn_df = pd.read_pickle(config['ret'])

    # barra_ort_df = pd.read_pickle(os.path.join(config['barra_dir'], 'barra_ort_df.pkl'))
    # barra_ret_df = pd.read_pickle(os.path.join(config['barra_dir'], 'barra_ret_df.pkl'))
    # barra_alpha_df = pd.read_pickle(os.path.join(config['barra_dir'], 'barra_alpha_df.pkl'))

    start_date = config['date']['start_date']
    end_date = config['date']['end_date']

    rtn_df = rtn_df.loc[start_date:end_date]

    for factor_info in config['factors']:
        logger.info(
            f"start backtesting {factor_info['factor_id']}"
        )
        factor_df = pd.read_csv(factor_info['factor_values_file'],index_col=0)
        factor_df.index = pd.to_datetime(factor_df.index.astype(str))
        factor_df = factor_df.loc[start_date:end_date]
        pos_df,result_df,fig = backtest_single(factor_df,rtn_df,factor_info['weights'],factor_info['factor_id'],factor_info['mode'])
        result_df.to_csv(os.path.join(factor_info['result_save_path'],f"{factor_info['factor_id']}.csv"))
        fig.savefig(os.path.join(factor_info['result_save_path'],f"{factor_info['factor_id']}.png"))
        logger.info(
            f"backtest result of {factor_info['factor_id']} saved:{factor_info['result_save_path']}"
        )

        if factor_info.get("barra",False):
            fig = barra_analysis(pos_df.loc['20171101':],barra_ort_df,barra_ret_df,barra_alpha_df)
            fig.savefig(os.path.join(factor_info['result_save_path'], f"{factor_info['factor_id']}_barra.png"))
            logger.info(
            f"barra result of {factor_info['factor_id']} saved:{factor_info['result_save_path']}"
            )

if __name__ == "__main__":
    run()