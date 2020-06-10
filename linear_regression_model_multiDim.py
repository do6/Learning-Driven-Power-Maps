# Learning Driven Power Maps -- multi dimensional model

#%% import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sklearn.model_selection as model_selection
from sklearn.metrics import mean_squared_error, r2_score
from sqlalchemy import create_engine
import sys
sys.path.insert(1, '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/import')
from pm_helper import get_ids, get_data

#%% connect to database
select_x = ['population','revenue_construction','revenue_manufacturing', 'tourism_guest_nights', 'area_agriculture']
engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

id_dict = get_ids() # usage: id_dict['country']['Croatia']
data_df = get_data(select_x, id_dict) # returns a dataframe with features as in select_x (list) and features per capita. Energy per person in kWh

# %% define model input
model_input = []
for i in range(len(select_x)):
    if select_x[i] != 'population':    
        model_input.append(select_x[i]+'_per_person')

# model_input = ['revenue_construction_per_person']

x = data_df[model_input]
y = data_df['energy_per_person']
#%% train model
mse_list = []
# k-fold cross-validation
# --> k iterations
# --> model_selection doku
if len(x.columns) == 1:
    x = np.array(x).reshape(-1, 1) # if one single feature

k = 500
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

rmse_list = np.sqrt(mse_list)


#%% plot!
# mean_energy_demand = np.array(y).mean()
# rmse_list = np.array(rmse_list)
# mean_relative_error = 100*rmse_list/mean_energy_demand
mu = rmse_list.mean()
median = np.median(rmse_list)
sigma = rmse_list.std()
textstr = '\n'.join((
    r'$\mu=%.2f$' % (mu, ),
    r'$\mathrm{median}=%.2f$' % (median, ),
    r'$\sigma=%.2f$' % (sigma, )))
featurestr = 'Features: \n' + str(model_input).replace('[','').replace(']','').replace('\'','').replace(' ','\n')
props = dict(boxstyle='round', facecolor='white', alpha=0.5)

if len(model_input) == 1:
    plot_title = 'RMSE one-dimensional Linear Regression'
else:
    plot_title = 'RMSE multi dimensional Linear Regression'

fig, ax = plt.subplots()
ax.hist(rmse_list,bins=20)
plt.title(plot_title)
plt.xlabel('RMSE [kWh]')
plt.ylabel('Total Amount')
ax.text(0.03, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
fig.text(1.03, 0, featurestr, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', horizontalalignment='left', bbox=props)
plt.tight_layout()

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
