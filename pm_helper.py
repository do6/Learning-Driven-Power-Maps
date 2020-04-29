#pm helper functions
#%%
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd

def get_ids():
    engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

    df_province = pd.read_sql_table("province", engine, columns=['name','id'])
    dict_province = df_province.set_index('name').T.to_dict('int')

    df_city = pd.read_sql_table("city", engine, columns=['name','id'])
    dict_city = df_city.set_index('name').T.to_dict('int')

    df_country = pd.read_sql_table("country", engine, columns=['name','id'])
    dict_country = df_country.set_index('name').T.to_dict('int')

    df_feature = pd.read_sql_table("feature", engine, columns=['name','id'])
    dict_feature = df_feature.set_index('name').T.to_dict('int')

    id_dict = {'country':dict_country['id'], 'province':dict_province['id'], 'city':dict_city['id'], 'feature':dict_feature['id']}

    return id_dict

# %%
