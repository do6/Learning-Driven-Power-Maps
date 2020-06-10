# %% cnn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import sklearn.model_selection as model_selection
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.tree import DecisionTreeRegressor
from sqlalchemy import create_engine
import sys
sys.path.insert(1, '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/import')
from pm_helper import get_ids, get_data
from sklearn.neighbors import NearestNeighbors
from sklearn.utils import shuffle
from sklearn.manifold import MDS
# cnn libs
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import tensorflow_docs as tfdocs
import tensorflow_docs.plots
import tensorflow_docs.modeling

#%% connect to db and get data
select_x = ['population','revenue_construction','revenue_manufacturing', 'tourism_guest_nights', 'area_non_agriculture'] #
engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

id_dict = get_ids() # usage: id_dict['country']['Croatia']
data_df = get_data(select_x, id_dict) # returns a dataframe with features as in select_x (list) and features per capita. Energy per person in kWh
# %% define model input
model_input = []
#extract month
# data_df['month'] = 0
# for i in range(len(data_df)):
#     data_df['month'][i] = data_df['date'][i].month
for i in range(len(select_x)):
    if select_x[i] != 'population':    
        model_input.append(select_x[i]+'_per_person')
# model_input.append('month')
# %%
# sns.pairplot(data_df[["energy_per_person","revenue_construction_per_person", "revenue_manufacturing_per_person", "tourism_guest_nights_per_person", "area_non_agriculture_per_person"]])
# %% split data into model and training data
# X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=0.9,test_size=0.1)
data_train = data_df.sample(frac=0.9, random_state = 0)
data_test = data_df.drop(data_train.index)
y_train = data_train.pop('energy_per_person')
y_test = data_test.pop('energy_per_person')
X_train = data_train[model_input]
X_test = data_test[model_input]
# norm training data
X_train_stats = X_train.describe()
for name in X_train.columns:
    X_train[name] = (X_train[name] - X_train_stats[name]['mean'])/X_train_stats[name]['std']
    X_test[name] = (X_test[name] - X_train_stats[name]['mean'])/X_train_stats[name]['std']

# %% build the model
nn_title = '2 Hidden Layer, 64 Units'
def build_model():
  model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=[len(X_train.keys())]),
    layers.Dense(64, activation='relu'),
    layers.Dense(1)
  ])

  optimizer = tf.keras.optimizers.RMSprop(0.001)

  model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])
  return model

#%%
model = build_model()
# %% train
EPOCHS = 960
history = model.fit(
  X_train, y_train,
  epochs=EPOCHS, validation_split = 0.2, verbose=0,
  callbacks=[tfdocs.modeling.EpochDots()])

#%%
hist = pd.DataFrame(history.history)
hist['epoch'] = history.epoch
hist.tail()
# %% plot
plotter = tfdocs.plots.HistoryPlotter(smoothing_std=2)
fig1 = plt.figure()
plotter.plot({'Basic': history}, metric = "mae")
plt.ylabel('MAE [kWh]')
plt.title('Mean Absolute Error -- Keras Regression Neural Network')
plt.show()

fig2 = plt.figure()
plotter.plot({'Basic': history}, metric = "mse")
plt.ylabel('MAE [kWh^2]')
plt.title('Mean Squared Error -- Keras Regression Neural Network')
plt.show()
# %% get results
print('model_input:', model_input)
print(nn_title)
loss, mae, mse = model.evaluate(X_test, y_test, verbose=2)
# %% predict
pred = model.predict(X_test).flatten()

a = plt.axes(aspect='equal')
plt.scatter(y_test, pred)
plt.xlabel('True Values [kWh]')
plt.ylabel('Predictions [kWh]')
plt.title(nn_title)
lims = [200, 840]
plt.xlim(lims)
plt.ylim(lims)
_ = plt.plot(lims, lims)

#%% k-fold cross validation
k = 100
mse_list = []
mae_list = []
for i in range(k):
    print('\ni =',i,'\n')
    # split data
    data_train = data_df.sample(frac=0.9)
    data_test = data_df.drop(data_train.index)
    y_train = data_train.pop('energy_per_person')
    y_test = data_test.pop('energy_per_person')
    X_train = data_train[model_input]
    X_test = data_test[model_input]
    # norm training data
    X_train_stats = X_train.describe()
    for name in X_train.columns:
        X_train[name] = (X_train[name] - X_train_stats[name]['mean'])/X_train_stats[name]['std']
        X_test[name] = (X_test[name] - X_train_stats[name]['mean'])/X_train_stats[name]['std']

    model = build_model()
    EPOCHS = 960
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS, validation_split = 0.2, verbose=0)
    
    loss, mae, mse = model.evaluate(X_test, y_test, verbose=2)
    mse_list.append(mse)
    mae_list.append(mae)

#%% plot histograms of  rmse
rmse_list = np.sqrt(mse_list)
mu = rmse_list.mean()
median = np.median(rmse_list)
sigma = rmse_list.std()
textstr = '\n'.join((
    r'$\mu=%.2f$' % (mu, ),
    r'$\mathrm{median}=%.2f$' % (median, ),
    r'$\sigma=%.2f$' % (sigma, )))
featurestr = 'Features: \n' + str(model_input).replace('[','').replace(']','').replace('\'','').replace(' ','\n')
props = dict(boxstyle='round', facecolor='white', alpha=0.5)

plot_title = 'RMSE of ' +str(k)+'-fold cross validation\nKeras Regression Neural Network'
fig3, ax3 = plt.subplots()
ax3.hist(rmse_list,bins=20)
plt.title(plot_title)
plt.xlabel('RMSE [kWh]')
plt.ylabel('Total Amount')
ax3.text(0.975, 0.95, textstr, transform=ax3.transAxes, fontsize=14,
        verticalalignment='top',horizontalalignment='right', bbox=props)
fig3.text(1.03, 0, featurestr, transform=ax3.transAxes, fontsize=11,
        verticalalignment='bottom', horizontalalignment='left', bbox=props)
plt.tight_layout()
plt.show()

#%% plot mae histogram
mae_list = np.array(mae_list)
mu = mae_list.mean()
median = np.median(mae_list)
sigma = mae_list.std()
textstr = '\n'.join((
    r'$\mu=%.2f$' % (mu, ),
    r'$\mathrm{median}=%.2f$' % (median, ),
    r'$\sigma=%.2f$' % (sigma, )))
featurestr = 'Features: \n' + str(model_input).replace('[','').replace(']','').replace('\'','').replace(' ','\n')
props = dict(boxstyle='round', facecolor='white', alpha=0.5)

plot_title = 'MAE of ' +str(k)+'-fold cross validation\nKeras Regression Neural Network'
fig3, ax3 = plt.subplots()
ax3.hist(mae_list,bins=20)
plt.title(plot_title)
plt.xlabel('MAE [kWh]')
plt.ylabel('Total Amount')
ax3.text(0.975, 0.95, textstr, transform=ax3.transAxes, fontsize=14,
        verticalalignment='top',horizontalalignment='right', bbox=props)
fig3.text(1.03, 0, featurestr, transform=ax3.transAxes, fontsize=11,
        verticalalignment='bottom', horizontalalignment='left', bbox=props)
plt.tight_layout()
plt.show()



# %%
