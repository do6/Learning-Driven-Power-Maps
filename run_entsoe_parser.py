# importer entsoe datasets
#%%
import os
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
from pm_helper import get_ids
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from import_entsoe_datasets import import_entsoe_datasets

#%%
id_dict = get_ids() # usage: id_dict['country']['Croatia']
save_as_path = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/entsoe/'

countries_list = ['austria','belgium','bulgaria','croatia','cyprus','denmark',\
    'estonia','finland','france','germany','greece','hungary','ireland','italy',\
    'latvia','lithuania','luxembourg','netherlands','norway','poland','portugal',\
    'romania','slovakia','slovenia','spain','sweden','switzerland']
filenames_list = ['Total Load - Day Ahead _ Actual_201501010000-201601010000.csv',\
    'Total Load - Day Ahead _ Actual_201601010000-201701010000.csv',\
    'Total Load - Day Ahead _ Actual_201701010000-201801010000.csv',\
    'Total Load - Day Ahead _ Actual_201801010000-201901010000.csv',\
    'Total Load - Day Ahead _ Actual_201901010000-202001010000.csv']

for i in range(len(countries_list)):
    path = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/data/entsoe_'\
        + countries_list[i] + '/'
    for name in filenames_list:
        filename = path + name
        if os.path.exists(filename):
            import_entsoe_datasets(filename, save_as_path, id_dict)