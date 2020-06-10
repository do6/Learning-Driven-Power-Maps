# pca

#%%
import sys
sys.path.append('/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/import')
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.pyplot as plt
import datetime
from sklearn.linear_model import LinearRegression
import sklearn.model_selection as model_selection
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.decomposition import PCA
from sqlalchemy import create_engine
from pm_helper import get_ids, get_data


select_x = ['population','area_agriculture','revenue_manufacturing','revenue_construction','tourism_guest_nights']

# %% connect and get data
engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")
id_dict = get_ids()
data_df = get_data(select_x, id_dict)

# %% get total area of provinces
sql = 'select value, province_id from data where feature_id = ' +str(id_dict['feature']['area'])+ ' and spatial_resolution = \'province\';'
total_area_df = pd.read_sql_query(sql, engine)
total_area_dict = total_area_df.set_index('province_id').T.to_dict('index')
total_area_dict = total_area_dict['value']

#%% get non-agricultural area
data_df['non-agricultural_area'] = 0
for i in range(len(data_df)):
    prov = data_df['province_id'][i]
    data_df['non-agricultural_area'][i] = total_area_dict[prov] - data_df['area_agriculture_value'][i]

data_df['non-agricultural_area_per_person'] = data_df['non-agricultural_area']/data_df['population_value']
# %% prepare pca
y = np.array(data_df['energy_per_person'])
x1 = np.array(data_df['non-agricultural_area_per_person'])
x2 = np.array(data_df['revenue_manufacturing_per_person'])
x3 = np.array(data_df['revenue_construction_per_person'])
x4 = np.array(data_df['tourism_guest_nights_per_person'])

x1 = x1 - np.average(x1)
x2 = x2 - np.average(x2)
x3 = x3 - np.average(x3)
x4 = x4 - np.average(x4)

x = np.array([x1, x2, x3, x4]).T

# %% plot
# fig1, ax1  = plt.subplots()
# ax1.scatter(x1, y, c='g')
# ax1.scatter(x4, y, c='b')

# fig2, ax2 = plt.subplots()
# ax2.scatter(x2, y, c='r')
# ax2.scatter(x3, y, c='y')

#%% pca
pca = PCA(n_components=4, whiten=True)
pca.fit(x)
X = pca.transform(x)
print(pca.explained_variance_)
# print(pca.singular_values_)

#%%plot!
fig2 = plt.figure()
ax1 = plt.subplot(4,4,1)
ax1.scatter(X[:, 0], X[:, 0], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax1.set_ylabel('X0')
ax2 = plt.subplot(4,4,2)
ax2.scatter(X[:, 1], X[:, 0], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax3 = plt.subplot(4,4,3)
ax3.scatter(X[:, 2], X[:, 0], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax4 = plt.subplot(4,4,4)
ax4.scatter(X[:, 3], X[:, 0], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))


ax5 = plt.subplot(4,4,5)
ax5.scatter(X[:, 0], X[:, 1], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax5.set_ylabel('X1')
ax6 = plt.subplot(4,4,6)
ax6.scatter(X[:, 1], X[:, 1], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax7 = plt.subplot(4,4,7)
ax7.scatter(X[:, 2], X[:, 1], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax8 = plt.subplot(4,4,8)
ax8.scatter(X[:, 3], X[:, 1], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))


ax9 = plt.subplot(4,4,9)
ax9.scatter(X[:, 0], X[:, 2], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax9.set_ylabel('X2')
ax10 = plt.subplot(4,4,10)
ax10.scatter(X[:, 1], X[:, 2], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax11 = plt.subplot(4,4,11)
ax11.scatter(X[:, 2], X[:, 2], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax12 = plt.subplot(4,4,12)
ax12.scatter(X[:, 3], X[:, 2], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))


ax13 = plt.subplot(4,4,13)
ax13.scatter(X[:, 0], X[:, 3], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax13.set_ylabel('X3')
ax13.set_xlabel('X0')
ax14 = plt.subplot(4,4,14)
ax14.scatter(X[:, 1], X[:, 3], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax14.set_xlabel('X1')
ax15 = plt.subplot(4,4,15)
ax15.scatter(X[:, 2], X[:, 3], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax15.set_xlabel('X2')
ax16 = plt.subplot(4,4,16)
ax16.scatter(X[:, 3], X[:, 3], c=y, edgecolor='none', alpha=0.5,
            cmap=plt.cm.get_cmap('Oranges', 10))
ax16.set_xlabel('X3')

plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])
plt.show()


# %%
