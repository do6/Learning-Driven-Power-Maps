# Learning Driven Power Maps

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sklearn.model_selection as model_selection
from sklearn.metrics import mean_squared_error, r2_score
from sqlalchemy import create_engine

engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

df_feature = pd.read_sql_table("feature", engine, columns=['name','id'])
dict_feature = df_feature.set_index('name').to_dict('int')

population_id = dict_feature['population']['id']
energy_id = dict_feature['net_electricity_demand']['id']

sql = "SELECT x.value AS population_value, y.value AS energy_value, x.date, x.province_id, p.name AS province_name \
FROM data AS x, data AS y, province AS p \
WHERE x.date = y.date AND x.province_id = y.province_id AND x.province_id = p.id \
    AND x.feature_id = " + str(population_id) + " \
    AND y.feature_id = " + str(energy_id) + ";"

df_data = pd.read_sql_query(sql, engine)


#%% #### fertig bis hier

# import test data
# data = pd.read_csv('/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/data/test/population_vs_demand.csv', \
#     delimiter=';')


x = np.array(df_data['population_value'])
x = x.reshape(-1, 1) # if one single feature
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

print('Mean squared error: %.2f' %mse)


#%% plots
### uncomment blocks below for plots

mean_error = [0]*len(mse_list)
# take squareroot from mse values
for i in range(len(mse_list)):
    mean_error[i] = np.sqrt(mse_list[i])

print('Mean Error: ', np.average(mse_list))

### uncomment for cross validation histogram of mean error
plt.hist(mean_error,bins=10)
plt.title('Mean Error of Population vs. Energy Demand Regression in German States')
plt.xlabel('Mean Error [GWh]')
plt.ylabel('Amount out of 100-fold cross validation')
plt.show()

### uncomment for single regression (not for cross validation)
reg = LinearRegression().fit(x, y)
y_pred = reg.predict(x)

plt.scatter(x,y)
plt.plot(x, y_pred)
plt.title('Population of German States 1991 - 2018 vs. Energy Demand')
plt.ylabel('Net Electricity Demand [GWh]')
plt.xlabel('Population')
plt.show()






