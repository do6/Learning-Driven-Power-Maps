# Learning Driven Power Maps

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
import sklearn.model_selection as model_selection
from sklearn.metrics import mean_squared_error, r2_score

#from sqlalchemy import create_engine

#engine = create_engine('postgresql://dorowiemann@5432/power_maps')


# import test data
data = pd.read_csv('/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/data/test/population_vs_demand.csv', \
    delimiter=';')

x = np.array(data['population'])
x = x.reshape(-1, 1) # if one single feature
y = data['energy_demand']

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

# print('Mean squared error: %.2f' %mse)


### uncomment to make a single regression with all datapoints
reg = LinearRegression().fit(x, y)
y_pred = reg.predict(x)

#%% plots
### uncomment blocks below for plots

### uncomment only with single regression (not for cross validation)
plt.scatter(x,y)
plt.plot(x, y_pred)
plt.title('Population of Germany 1991 - 2018 vs. Energy Demand')
plt.ylabel('Energy Demand [GWh]')
plt.xlabel('Population')
plt.show()

### uncomment only with cross validation (not for single regression)
# plt.hist(mse_list,bins=10)
# plt.title('Mean Squared Error of Population vs. Energy Demand Regression')
# plt.xlabel('MSE')
# plt.ylabel('Non-normalized amount')
# plt.show()

# take squareroot from mse values
for i in range(len(mse_list)):
    mse_list[i] = np.sqrt(mse_list[i])

print('Mean Error: ', np.average(mse_list))


