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
from pm_helper import get_ids

select_province = 'Sachsen'
select_feature = 'gdp'
select_feature_name = 'GDP'

id_dict = get_ids() # usage: id = id_dict['country']['Croatia'] 

#sql query 
sql = "SELECT x.value AS " + select_feature + "_value, y.value AS energy_value, x.date, x.province_id, p.name AS province_name \
FROM data AS x, data AS y, province AS p \
WHERE x.date = y.date AND x.province_id = y.province_id AND x.province_id = p.id \
    AND x.province_id = " + str(id_dict['province'][select_province]) + " \
    AND x.feature_id = " + str(id_dict['feature'][select_feature]) + " \
    AND y.feature_id = " + str(id_dict['feature']['net_electricity_demand']) + " \
ORDER BY x.date;"

engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

df_data = pd.read_sql_query(sql, engine)

# change format year-12-31 to year-01-01
for i in range(len(df_data['date'])):
    new_date = datetime.date(df_data['date'][i].year,1,1)
    df_data['date'][i] = new_date

fig, ax1 = plt.subplots()
plt.title(select_feature_name+' and Energy Demand of '+select_province, fontsize = 14)
plt.grid()
color = 'tab:red'
ax1.set_xlabel('Year')
ax1.set_ylabel('Net Electricity Demand [GWh]', color=color)
ax1.plot(df_data['date'], df_data['energy_value'], color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel(select_feature_name, color=color)  # we already handled the x-label with ax1
ax2.plot(df_data['date'], df_data[select_feature+'_value'], color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()



# %%
