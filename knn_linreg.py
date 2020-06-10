#%% import libraries
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
#%% connect to db and get data
select_x = ['population','revenue_construction','revenue_manufacturing', 'tourism_guest_nights', 'area_agriculture']
engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

id_dict = get_ids() # usage: id_dict['country']['Croatia']
data_df = get_data(select_x, id_dict) # returns a dataframe with features as in select_x (list) and features per capita. Energy per person in kWh
# %% define model input
model_input = []
for i in range(len(select_x)):
    if select_x[i] != 'population':    
        model_input.append(select_x[i]+'_per_person')

### overwrite if only a subset of select_x is needed
# model_input = ['tourism_guest_nights_per_person']

X = np.array(data_df[model_input])
# x_normed_list = []
# for feature in model_input:
#     x = np.array(data_df[feature])
#     x_normed = x - np.average(x)
#     x_normed_list.append(x_normed)

# X = np.array([x_normed_list[0], x_normed_list[1], x_normed_list[2], x_normed_list[3]]).T
y = np.array(data_df['energy_per_person'])

# %% k nearest neighbors and linear regression
# test train split
# x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, train_size=0.9,test_size=0.1)
# k cross validation
# mse_list = []

# nbrs = NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(X)
# distances, indices = nbrs.kneighbors(X)
#%% train
# distances: N x 5
# indicies: N x 5
# X[indices[2][3]] <- Der drittnächste Nachbar der zweiten Zeile in X

k = 51
#for i in range(k):
mse_list = []
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=0.9,test_size=0.1)
nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(X)
distances, indices = nbrs.kneighbors(X)
for i in range(len(X)):
    reg = LinearRegression().fit(X[indices[i][1:]], y[indices[i][1:]])
    # X[indices[i][1:]] n_neighbors X 5
    # indices[600] = [a,b,c,d,e]
    # indices[600][0] = a
    # X[a] = [q,w,e,r,t]
    pred = float(reg.predict(X[indices[i][0]].reshape(1,-1)))
    # mse = mean_squared_error(y[indices[i][0]], pred)
    mse = (y[indices[i][0]]-pred)**2
    mse_list.append(mse)
    # if i == 100:
    #     fig, ax = plt.subplots()
    #     ax.plot(X[indices[i][1:]],y[indices[i][1:]],'x',label='K Nearest Neighbors')
    #     ax.plot(X[indices[i][0]],pred,'o',label='Predicted Value for Sample')
    #     ax.plot(X[indices[i][0]],y[indices[i][0]],'x',label='Real Value of Sample')
    #     ax.legend(loc='best')
    #     plt.xlabel('Guest Nights per Capita')
    #     plt.ylabel('Energy Demand per Capita')
    #     plt.title('KNN Regression for one randomly selected datapoint')



# %% get results and plot
rmse_list = np.sqrt(mse_list)
# mean_energy_demand = np.array(y).mean()
# rmse_list_relative = 100*rmse_list/mean_energy_demand
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
    plot_title = 'RMSE one-dimensional KNN Regression for k = ' +str(k)
else:
    plot_title = 'RMSE multi dimensional KNN Regression for k = ' +str(k)

fig, ax = plt.subplots()
ax.hist(rmse_list,bins=20)
plt.title(plot_title)
plt.xlabel('RMSE [kWh]')
plt.ylabel('Total Amount')
ax.text(0.975, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top',horizontalalignment='right', bbox=props)
fig.text(1.03, 0, featurestr, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', horizontalalignment='left', bbox=props)
plt.tight_layout()

# %%

#   perform multivariate linear regression
#   compute error and add to mse list

# %% Multidimensional Scaling
from sklearn.manifold import MDS
embedding = MDS(n_components=2)
mds_result = embedding.fit_transform(X)
fig, ax = plt.subplots()
plt.title('MDS')
ax.scatter(mds_result[:,0],mds_result[:,1], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))

# %%
from sklearn import decomposition
pca = decomposition.PCA(n_components=2)
pca.fit(X)
pca_result = pca.transform(X)
fig, ax = plt.subplots()
plt.title('PCA')
ax.scatter(pca_result[:,0],pca_result[:,1])

# error measurement


# %%
