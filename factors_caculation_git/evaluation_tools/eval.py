import os
import numpy as np
import pandas as pd
import click
#pd.set_option('max_columns', None)
pd.set_option('display.expand_frame_repr', False)
NUM_DAYS = 242

@click.command()
@click.argument('filepath', required=True)
@click.option('-t', '--dtype', default='yearly',type=str, help='dtype. e.g. yearly or monthly', show_default=True)
def run(filepath, dtype='yearly'):
    assert os.path.exists(filepath), f"{filepath} does not exist"
    df = pd.read_csv(filepath,index_col=0)
    df['dateStr'] = df['index'].str.replace('-','')
    df['month'] = df['dateStr'].apply(lambda x:int(x[:6]))
    df['year'] = df['dateStr'].apply(lambda x:int(x[:4]))
    df['trials'] = 1


    df = df.groupby('dateStr').mean(numeric_only=True)
    df = df.dropna(subset=['pnl'])
    for col in ['year', 'month']:
        df[col] = df[col].apply(lambda x:str(int(x)))

    if dtype == 'yearly':
        group_cols = 'year'
    else:
        raise AssertionError(f"dtype:{dtype} does not support! choose from yearly and monthly")

    def get_mdd_start_date(x):
        x_cumsum = x.cumsum()
        end_idx = (x_cumsum.cummax() - x_cumsum).idxmax()
        return x_cumsum.cummax().loc[:end_idx].pipe(lambda x:x[x.diff()!=0]).index[-1]

    stats = df.groupby(group_cols).agg(
            ret = ('pnl', lambda x:round(x.mean() * NUM_DAYS,4)),
            longRet=('pnl_long', lambda x: round(x.mean() * NUM_DAYS, 4)),
            longPos = ('long_pos', lambda x:round(x.mean(),0)),
            shortPos = ('short_pos', lambda x:round(x.mean(),0)),
            longNum = ('long_num', lambda x:int(x.mean())),
            shortNum = ('short_num', lambda x:int(x.mean())),
            tvr = ('tvr', lambda x:round(x.mean(), 3)),
            sharpe = ('pnl', lambda x:round(x.mean()/x.std() * np.sqrt(NUM_DAYS), 2)),
            drawdown = ('pnl', lambda x:round((x.cumsum().cummax() - x.cumsum()).max(), 4)),
            dd_start = ('pnl', get_mdd_start_date),
            dd_end = ('pnl', lambda x:(x.cumsum().cummax() - x.cumsum()).idxmax()),
            win_rate = ('pnl', lambda x:round((x > 0).sum() / x.shape[0], 3)),
            days = ('pnl', lambda x:x.shape[0])
        )
    stats['bp_mrgn'] = stats.ret / stats.tvr / NUM_DAYS  * 1e4
    print(stats.head(50))
    summary = df.groupby('trials').agg(
            ret = ('pnl', lambda x:round(x.mean() * NUM_DAYS,4)),
            longRet=('pnl_long', lambda x: round(x.mean() * NUM_DAYS, 4)),
            longPos = ('long_pos', lambda x:round(x.mean(),0)),
            shortPos = ('short_pos', lambda x:round(x.mean(),0)),
            longNum = ('long_num', lambda x:int(x.mean())),
            shortNum = ('short_num', lambda x:int(x.mean())),
            tvr = ('tvr', lambda x:round(x.mean(), 3)),
            sharpe = ('pnl', lambda x:round(x.mean()/x.std() * np.sqrt(NUM_DAYS), 2)),
            drawdown = ('pnl', lambda x:round((x.cumsum().cummax() - x.cumsum()).max(), 4)),
            dd_start = ('pnl', get_mdd_start_date),
            dd_end = ('pnl', lambda x:(x.cumsum().cummax() - x.cumsum()).idxmax()),
            win_rate = ('pnl', lambda x:round((x > 0).sum() / x.shape[0], 3)),
            days = ('pnl', lambda x:x.shape[0])
        )
    print(summary.reset_index(drop=True))

if __name__ == "__main__":
    run()