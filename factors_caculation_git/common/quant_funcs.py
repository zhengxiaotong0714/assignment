import numpy as np
import pandas as pd
from numpy import abs
from numpy import log
from numpy import sign
from scipy.stats import rankdata

# region Auxiliary functions
def ts_sum(df, window=10):
    """
    用于滚动求和
    参数: df: a pandas DataFrame.
        window: the rolling window.滚动窗口大小
    返回值: a pandas DataFrame with the time-series min over the past 'window' days.
         会返回一个dataframe，同时所求值会落在每个window天数的最后一天
    """
    
    return df.rolling(window).sum()

def sma(df, window=10):
    """
    Wrapper function to estimate SMA.
    用于估计简单滑动平均simple moving average
    :param df: a pandas DataFrame.
    :param window: the rolling window.
    :return: a pandas DataFrame with the time-series min over the past 'window' days.
    会返回一个dataframe，同时所求的过去window天数的平均值会落在每个window的最后一天
    """
    return df.rolling(window).mean()

def stddev(df, window=10):
    """
    Wrapper function to estimate rolling standard deviation.
    计算滚动标准差
    :param df: a pandas DataFrame.
    :param window: the rolling window.
    :return: a pandas DataFrame with the time-series min over the past 'window' days.
    """
    return df.rolling(window).std()

def correlation(x, y, window=10):
    """
    Wrapper function to estimate rolling correlations.
    计算滚动相关性
    :param df: a pandas DataFrame.
    输入的x和y都是df格式
    :param window: the rolling window.
    :return: a pandas DataFrame with the time-series min over the past 'window' days.
    计算了两个矩阵之间各个对应列的滚动的在过去window天的相关性？
    """
    return x.rolling(window).corr(y)

def covariance(x, y, window=10):
    """
    Wrapper function to estimate rolling covariance.
    估计滚动协方差
    :param df: a pandas DataFrame.
    x,y皆为df形式
    :param window: the rolling window.
    :return: a pandas DataFrame with the time-series min over the past 'window' days.
    计算了两个矩阵之间各个对应列滚动的在过去window天的协方差
    """
    return x.rolling(window).cov(y)

def rolling_rank(na):
    """
    Auxiliary function to be used in pd.rolling_apply
    是一个辅助函数,辅助后续ts_rank函数的构建
    :param na: numpy array.
    输入参数是numpy包的array向量形式
    :return: The rank of the last value in the array.
    返回了赋予该向量排序的序数后，最后一个数的序数
    需要添加method='min'吗？
    """

    return na.rank(pct=True).iloc[-1]

def ts_rank(df, window=10):
    """
    Wrapper function to estimate rolling rank.
    返回滚动排序的矩阵
    :param df: a pandas DataFrame.
    :param window: the rolling window.
    :return: a pandas DataFrame with the time-series rank over the past window days.
    不断的滚动，并求出各个股票当天某项A值在过去window天内的A值进行排序得到的序数
    """

    new_df = pd.DataFrame().reindex_like(df)
    for i in range(window,df.shape[0]):
        date_now = df.index[i]
        date_n = df.index[i-window]
        new_df.loc[date_now] = rolling_rank(df.loc[date_n:date_now])
    return new_df

def rolling_prod(na):
    """
    Auxiliary function to be used in pd.rolling_apply
    辅助函数
    :param na: numpy array.
    输入了array
    :return: The product of the values in the array.
    返回了数组中所有值的乘积
    """
    return np.prod(na)

def product(df, window=10):
    """
    Wrapper function to estimate rolling product.
    计算滚动乘积
    :param df: a pandas DataFrame.
    :param window: the rolling window.
    :return: a pandas DataFrame with the time-series product over the past 'window' days.
    返回了矩阵，计算了股票当天到过去window天的某项A值的乘积
    """
    return df.rolling(window).apply(rolling_prod)

def ts_min(df, window=10):
    """
    估计滚动最小值
    参数: df: pandas DataFrame.
    参数: window: 滚动窗口值，默认10
    输出: 过去 'window' 天的时间序列最小值的 pandas DataFrame

    """
    return df.rolling(window).min()

def ts_max(df, window=10):
    """
    估计滚动最大值
    参数: df: pandas DataFrame.
    参数: window: 滚动窗口值，默认10
    输出: 过去 'window' 天的时间序列最大值的 pandas DataFrame

    """
    return df.rolling(window).max()

def delta(df, period=1):
    """
    估计差值
    参数: df: pandas DataFrame.
    参数: period: 比较的日期间隔， period 天前，默认1
    输出: pandas DataFrame 中今天的值减去'period'天之前的值
    """
    return df.diff(period)

def delay(df, period=1):
    """
    估计滞后
    参数: df: pandas DataFrame.
    参数: period: 滞后的时间
    输出: 按照时间序列滞后的 pandas DataFrame
    """
    return df.shift(period)

def rank(df):
    """
    横截面等级。
    参数: df: a pandas DataFrame.
    输出: 按照【列】百分比排列的 pandas DataFrame
    """
    return df.rank(pct=True,axis = 1)

def scale(df, k=1):
    """
    缩放时间序列
    参数: df: a pandas DataFrame.
    参数: k: 缩放比例
    输出: 将 pandas DataFrame 重新缩放，使 DataFrame 中绝对值的总和等于 k
    """
    return df.mul(k).div(np.abs(df).sum())

def ts_argmax(df, window=10):
    """
    估计 ts_max(df, window) 发生的日期
    参数: df: a pandas DataFrame.
    参数: window: 滚动窗口值，默认10
    输出: 估计 window 时间窗口内的最大值所对应的窗口内的位置
    """
    new_df = pd.DataFrame().reindex_like(df)
    for i in range(window,df.shape[0]):
        date_now = df.index[i]
        date_n = df.index[i-window]
        new_df.loc[date_now] = df.loc[date_n:date_now].reset_index(drop=True).idxmax()+1
    return new_df

def ts_argmin(df, window=10):
    """
    估计 ts_mix(df, window) 发生的日期
    参数: df: a pandas DataFrame.
    参数: window: 滚动窗口值，默认10
    输出: 估计 window 时间窗口内的最小值所对应的窗口内的位置
    """
    new_df = pd.DataFrame().reindex_like(df)
    for i in range(window,df.shape[0]):
        date_now = df.index[i]
        date_n = df.index[i-window]
        new_df.loc[date_now] = df.loc[date_n:date_now].reset_index(drop=True).idxmin()+1
    return new_df

def decay_linear(df, period=10):
    """
    实现线性加权移动平均linear weighted moving average
    参数: df: a pandas DataFrame.
    参数: period: 线性加权移动平均的周期，权重的数量
    输出: 线性加权移动平均 pandas DataFrame ，对时间序列数据进行平滑处理
    """
    # 清洗数据
    if df.isnull().values.any():
        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)
        df.fillna(value=0, inplace=True)
    na_lwma = np.zeros_like(df)
    na_lwma[:period, :] = df.iloc[:period, :]
    na_series = df.to_numpy()

    divisor = period * (period + 1) / 2
    y = (np.arange(period) + 1) * 1.0 / divisor
    # 用实际收盘价估算实际lwma
    # 确保回测引擎不受过度拟合影响
    for row in range(period - 1, df.shape[0]):
        x = na_series[row - period + 1: row + 1, :]
        na_lwma[row, :] = (np.dot(x.T, y))
    return pd.DataFrame(na_lwma, index=df.index, columns=df.columns)
    # endregion

def indneut(factor_df,sector_df):
    new_factor_df = factor_df.copy()
    sector_ls = sector_df.stack().unique()
    for sector in sector_ls:
        if sector == 0:
            continue
        new_factor_df[sector_df == sector] = new_factor_df[sector_df == sector].sub(
            new_factor_df[sector_df == sector].mean(axis=1), axis=0)
    return new_factor_df