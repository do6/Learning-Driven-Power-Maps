# Learning Driven Power Maps -- multi dimensional model

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sklearn.model_selection as model_selection
from sklearn.metrics import mean_squared_error, r2_score
from sqlalchemy import create_engine

select_x = ['population_value','gdp_value']
select_x_name = 'Population, GDP'

engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

df_feature = pd.read_sql_table("feature", engine, columns=['name','id'])
dict_feature = df_feature.set_index('name').to_dict('int')

energy_id = dict_feature['net_electricity_demand']['id']
population_id = dict_feature['population']['id']
population_density_id = dict_feature['population_density']['id']
gdp_id = dict_feature['gdp']['id']
gdp_per_capita_id = dict_feature['gdp_per_capita']['id']
#%%

sql = "SELECT y.value AS energy_value, y.date, y.province_id, \
x1.value AS population_value, \
x2.value AS population_density_value, \
x3.value AS gdp_value, \
x4.value AS gdp_per_capita_value, \
p.name AS province_name \
FROM data AS y, province AS p, data AS x1, data AS x2, data AS x3, data AS x4 \
WHERE y.date = x1.date AND y.province_id = x1.province_id AND y.province_id = p.id \
AND y.date = x2.date AND y.province_id = x2.province_id \
AND y.date = x3.date AND y.province_id = x3.province_id \
AND y.date = x4.date AND y.province_id = x4.province_id \
AND y.feature_id = " + str(energy_id) + " \
AND x1.feature_id = " + str(population_id) + " \
AND x2.feature_id = " + str(population_density_id) + " \
AND x3.feature_id = " + str(gdp_id) + " \
AND x4.feature_id = " + str(gdp_per_capita_id) + ";"
    
df_data = pd.read_sql_query(sql, engine)

# %%
x = df_data[select_x]
y = df_data['energy_value']


mse_list = []

# k-fold cross-validation
# --> k iterations
# --> model_selection doku

k = 100
for i in range(k):
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, train_size=0.9,test_size=0.1)

    reg = LinearRegression().fit(x_train, y_train)
    #print(reg.score(x, y))
    #print(reg.coef_)
    #print(reg.intercept_)
    # print('y test: ', y_test)
    y_pred = reg.predict(x_test)
    mse = mean_squared_error(y_test, y_pred)

    mse_list.append(mse)


print('\nMean MSE: ', np.average(mse_list))

mean_error = [0]*len(mse_list)
# take squareroot from mse values
for i in range(len(mse_list)):
    mean_error[i] = np.sqrt(mse_list[i])

print('\nMean Error: ', np.average(mean_error))

plt.hist(mean_error,bins=10)
plt.title('Mean Error 2 dimensional Linear Regression\nFeatures: ' + select_x_name)
plt.xlabel('Mean Error [GWh]')
plt.ylabel('Amount out of '+str(k)+'-fold cross validation')
plt.show()

# test
# reg = LinearRegression().fit(x, y)
# #print(reg.score(x, y))
# print('\ncoeff: ', reg.coef_)
# #print(reg.intercept_)
# # print('y test: ', y_test)
# y_pred = reg.predict(x)
# mse = mean_squared_error(y, y_pred)
# print('\nmse: ', mse, '\n')

# %%
