# %% 
from sklearn import datasets
import pandas as pd 
import numpy as np 
import datetime
from pathlib import Path 
import shutil
import types

from logging import getLogger

logger = getLogger(__name__)


def __check_str_col(d, cn):
    x = d[cn]
    print(f'most frequently appeard value::\n{x.mode()}\n')
    print('value counts...')
    print(x.value_counts())

def __check_numeric_col(d, cn):
    x_min = d[cn].min()
    x_max = d[cn].max()
    print(f'value range::{x_min},{x_max}')
    x_mean = d[[cn]].mean().values[0]
    print(f'mean::{x_mean}')
    x_median = d[[cn]].median().values[0]
    print(f'median::{x_median}')

    q01 = d[[cn]].quantile(0.01)[0]
    q10 = d[[cn]].quantile(0.10)[0]
    q25 = d[[cn]].quantile(0.25)[0]
    q50 = d[[cn]].quantile(0.50)[0]
    q75 = d[[cn]].quantile(0.75)[0]
    q90 = d[[cn]].quantile(0.90)[0]
    q99 = d[[cn]].quantile(0.99)[0]
    print('quantiles::1%, 10%, 25%, 50%, 75%, 90%, 99%')
    print((q01, q10, q25, q50, q75, q90, q99))

# pandas-profileっぽい感じので、ほしい情報を自分でいろいろつくれるように自作
def check_col_stats(d, cn):
    print(f'target column name...{cn}')
    print('______________________________________________')
    x = np.squeeze(d[[cn]].values)
    x_notnan = np.squeeze(d.loc[~d[cn].isna(), cn].values)
    n_unique = len(d[cn].unique())
    print(f'unique values::{n_unique}')

    n_missing = d[[cn]].isna().values.squeeze().sum()
    print(f'missing value count::{n_missing}')

    if isinstance(x_notnan[0], (str)):
        __check_str_col(d, cn)
    elif isinstance(x_notnan[0], (bool, int, float, np.float, np.double, np.integer)):
        __check_numeric_col(d, cn)
    
    print('\n')

def zen2han_num(x):
    x = x.replace("０", "0")
    x = x.replace("１", "1")
    x = x.replace("２", "2")
    x = x.replace("３", "3")
    x = x.replace("４", "4")
    x = x.replace("５", "5")
    x = x.replace("６", "6")
    x = x.replace("７", "7")
    x = x.replace("８", "8")
    x = x.replace("９", "9")
    return x

def add_target_enc(d, target_colname, grouping_colnames, agg_function, prefix=''):
    if type(grouping_colnames) is not list:
        grouping_colnames = [grouping_colnames]
    if prefix != '':
        prefix = prefix + '_'

    new_colname = f"{prefix}{agg_function.__name__}__{''.join(grouping_colnames)}__{target_colname}"
    tmp_d = d.groupby(grouping_colnames)[target_colname].agg(__c1__ = agg_function)
    tmp_d = tmp_d.rename({'__c1__':new_colname}, axis='columns')
    d =  d.merge(tmp_d, on=grouping_colnames, how='left')
    return d

def archive_old_files(target_dir: Path, target_ext: str, n_max_files=3):
    if type(target_dir) == str:
        target_dir = Path(target_dir)
    archive_dir = target_dir / 'old'

    if not archive_dir.exists():
        archive_dir.mkdir()

    files = [x for x in target_dir.iterdir() if x.suffix == target_ext]
    files.sort()
    archive_files = files[0:(len(files)-n_max_files)]
    if len(archive_files) > n_max_files:
        for x in archive_files:
            shutil.move(x, archive_dir / x.name)


# original code:
# https://gist.github.com/ax3l/59d92c6e1edefcef85ac2540eb056da3
# 
# License:
#   I hereby state this snippet is below "threshold of originality" where applicable (public domain).
#
# Otherwise, since initially posted on Stackoverflow, use as:
#   CC-BY-SA 3.0 skyking, Glenn Maynard, Axel Huebl
#   http://stackoverflow.com/a/31047259/2719194
#   http://stackoverflow.com/a/4858123/2719194

def imports():
    for name, val in globals().items():
        # module imports
        if isinstance(val, types.ModuleType):
            yield name, val
        # functions / callables
        if hasattr(val, '__call__'):
            yield name, val

noglobal = lambda fn: types.FunctionType(fn.__code__, dict(imports()))


def print_func_name(func):
    def f(*args, **k):
        t0 = datetime.datetime.now()
        logger.info(func.__name__+'\t\t\tstart')
        result = func(*args, **k)
        logger.info(func.__name__+'\t\t\tend')
        logger.info('processing time::\t\t\t' + str(datetime.datetime.now() - t0))
        return result
    return f
