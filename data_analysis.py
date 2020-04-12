#%%
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.pyplot as plt
import datetime
from sklearn.linear_model import LinearRegression
import sklearn.model_selection as model_selection
from sklearn.metrics import mean_squared_error, r2_score
from sqlalchemy import create_engine

engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

#get IDs for feature and province from database
df_feature = pd.read_sql_table("feature", engine, columns=['name','id'])
dict_feature = df_feature.set_index('name').to_dict('int')
population_id = dict_feature['population']['id']
energy_id = dict_feature['net_electricity_demand']['id']

df_province = pd.read_sql_table("province", engine, columns=['name','id'])
dict_province = df_province.set_index('name').to_dict('int') #syntax for retreiving data: dict_province['name']['id']
nrw_id = dict_province['Nordrhein-Westfalen']['id']
bayern_id = dict_province['Bayern']['id']

#sql query 
sql = "SELECT x.value AS population_value, y.value AS energy_value, x.date, x.province_id, p.name AS province_name \
FROM data AS x, data AS y, province AS p \
WHERE x.date = y.date AND x.province_id = y.province_id AND x.province_id = p.id \
    AND x.province_id = " + str(bayern_id) + " \
    AND x.feature_id = " + str(population_id) + " \
    AND y.feature_id = " + str(energy_id) + ";"

df_data = pd.read_sql_query(sql, engine)

for i in range(len(df_data['date'])):
    new_date = datetime.date(df_data['date'][i].year,1,1)
    df_data['date'][i] = new_date
    # date = date.replace('-12-31','')

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Year')
ax1.set_ylabel('Net Electricity Demand [GWh]', color=color)
ax1.plot(df_data['date'], df_data['energy_value'], color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('Population', color=color)  # we already handled the x-label with ax1
ax2.plot(df_data['date'], df_data['population_value'], color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()



# %%
