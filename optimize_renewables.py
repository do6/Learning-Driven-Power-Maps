# optimize_renewables

# %% import libs
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys
sys.path.insert(1, '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/import')
from pm_helper import get_ids, get_data
from sqlalchemy import create_engine

# %% prepare
id_dict = get_ids() # usage: id_dict['country']['Croatia']
engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")
# %% get data for wind, insolation and energy demand per day
data_dict = {}

region_list = ['North','East','South','West']
for region in region_list:
    prov_id = str(id_dict['province'][region])
    sql = 'select p.name as region, e.date, w.value as wind_speed, i.value as insolation, e.value as energy_demand FROM province p, data w, data i, data e \
        where \
        w.feature_id = '+str(id_dict['feature']['avg_wind_speed'])+' and \
        i.feature_id = '+str(id_dict['feature']['insolation'])+' and \
        e.feature_id = '+str(id_dict['feature']['entsoe_energy_demand'])+' and \
        w.province_id = '+ prov_id +' and \
        i.province_id = '+ prov_id +' and \
        e.province_id = '+ prov_id +' and \
        p.id = e.province_id and \
        extract(year from w.date) = 2015 and \
        extract(year from i.date) = 2015 and \
        extract(year from e.date) = 2015 and \
        w.date = e.date and \
        i.date = e.date and \
        w.spatial_resolution = \'province\' and \
        i.spatial_resolution = \'province\' and \
        e.spatial_resolution = \'province\' and \
        w.temporal_resolution = \'day\' and\
        i.temporal_resolution = \'day\' and\
        e.temporal_resolution = \'day\';'

    data_dict[region] = pd.read_sql(sql, engine)

# %% get data of current power plants
plants_dict = {}
capa_total_dict = {}
region_list = ['North','East','South','West']
for region in region_list:
    prov_id = str(id_dict['province'][region])
    sql_plants = 'SELECT capacity, region, energy_carrier, plant_number, province_id \
        FROM plant \
        WHERE region = \''+region[0]+'\' AND plant_number = \'total\' \
        AND (energy_carrier = \'Solare Strahlungsenergie\' \
        OR energy_carrier LIKE \'Windenergie%%\');'
    plants_dict[region] = pd.read_sql(sql_plants, engine)
    
    sql_capa = 'SELECT SUM(capacity), energy_carrier, region \
        FROM plant \
        WHERE region = \''+region[0]+'\' AND plant_number = \'total\' \
        AND (energy_carrier = \'Solare Strahlungsenergie\' \
        OR energy_carrier LIKE \'Windenergie%%\') \
        GROUP BY energy_carrier, region;'
    capa_total_dict[region] = pd.read_sql(sql_capa, engine)
    
# %% display dict
# plants_dict['South']
capa_total_dict['South']
# north_wind = 

#%% get Kw0, Ks0
Kw0_dict = {}
Ks0_dict = {}
for region in region_list:
    if region == 'North':
        Kw0 = float(capa_total_dict[region].loc[capa_total_dict[region]['energy_carrier']== 'Windenergie (Offshore-Anlage)']['sum']) + float(capa_total_dict[region].loc[capa_total_dict[region]['energy_carrier']== 'Windenergie (Onshore-Anlage)']['sum'])
    else:
        Kw0 = float(capa_total_dict[region].loc[capa_total_dict[region]['energy_carrier']== 'Windenergie (Onshore-Anlage)']['sum'])
    Kw0_dict[region] = Kw0

    Ks0 = float(capa_total_dict[region].loc[capa_total_dict[region]['energy_carrier']== 'Solare Strahlungsenergie']['sum'])
    Ks0_dict[region] = Ks0

#%% calculate Renewable Energy
#### set region

region = 'North'

date_list = []
El_list = []
Ew_list = []
Es_list = []
for i in range(len(data_dict[region])):
    date = data_dict[region]['date'][i]
    date_list.append(date)
    El = data_dict[region]['energy_demand'][i] # energy_load
    El_list.append(El)
    # formula wind speed
    # P = K*(v(t)-vci)/(vwn-vci)    if vci <= v(t) <= vwr
    # P = K                         if vwr <= v(t) < vco
    # P = 0                         if v(t) >= vco
    # 
    # with [m/s]
    v_ci = 3.5
    v_wn = 14
    v_co = 25
    # calculate wind energy
    # convert plant capacity from MW to kW
    Kw0 = Kw0_dict[region] / 1000
    # for i in range(len(data_dict)):
    v_t = data_dict[region]['wind_speed'][i]
    if v_t < v_ci or v_t >= v_co:
        Pw = 0
    elif v_ci <= v_t and v_t < v_wn:
        Pw = Kw0*(v_t-v_ci)/(v_wn-v_ci)
    elif v_wn <= v_t and v_t < v_co:
        Pw = Kw0
    else:
        print('v(t)=',v_t)
    Ew = Pw*24        #energy in kWh
    # Ew = Ew/1000000   #energy in GWh
    Ew_list.append(Ew)
    # formula solar energy
    # P(t) = (G(t)/G0)*K*eta(t)
    # 
    # with G(t)*eta(t) = dr(t)/dt #r is radiation
    # and [kW/m2]
    G0 = 1
    # calculate solar energy
    # convert plant capacity from MW to kW
    Ks0 = Ks0_dict[region] / 1000
    r_t = data_dict[region]['insolation'][i]
    if r_t < 0:
        r_t = 0
    Es = Ks0*r_t/G0     #energy in kWh
    # Es = Es/1000000     #energy in GWh
    Es_list.append(Es)

#%%
def calc_energy(kw,ks,v_t,r_t):
    # wind
    v_ci = 3.5
    v_wn = 14
    v_co = 25
    if v_t < v_ci or v_t >= v_co:
        Pw = 0
    elif v_ci <= v_t and v_t < v_wn:
        Pw = kw*(v_t-v_ci)/(v_wn-v_ci)
    elif v_wn <= v_t and v_t < v_co:
        Pw = kw
    else:
        print('v(t)=',v_t)
        sys.exit()
    Ew = Pw*24        #energy in kWh
    # Ew = Ew/1000   #energy in GWh #####

    # solar
    G0 = 1
    # in one file r(t) was -999 for 1 day, remove that point
    if r_t < 0:
        r_t = 0
    Es = ks*r_t/G0     #energy in kWh
    # Es = Es/1000     #energy in GWh

    return Es, Ew

#%%
def get_grad(vw,rs,Es,Ew,El):
    #wind params
    v_ci = 3.5
    v_wn = 14
    v_co = 25
    #solar param
    G0 = 1 # kW/m2
    grad_ks = 0
    grad_kw = 0
    # if El-(Es+Ew) > 0:
    #     fac = 1
    # else:
    #     fac = 1
    if vw < v_ci or vw >= v_co:
        grad_kw = 0
    elif v_ci <= vw and vw < v_wn:
        grad_kw = (-24*(vw-v_ci)/(v_wn-v_ci))*2*(El-(Es+Ew))
    elif v_wn <= vw and vw < v_co:
        grad_kw = (-24*2)*(El-(Es+Ew))
    else:
        print('v(t)=',v_t)
        sys.exit()
    
    grad_ks = (-rs/G0)*2*(El-(Es+Ew))
        
    return grad_kw, grad_ks
    
#%% gradient descent
'''
### set params
region = 'North'
alpha = 0.01
iterations = 10
#Get initial capacity and convert MW to kW
Kw0 = Kw0_dict[region] * 1000
Ks0 = Ks0_dict[region] * 1000
#wind params in m/s
v_ci = 3.5
v_wn = 14
v_co = 25
#solar param in kW/m2
G0 = 1
cost_list = []
abs_error_list = []
ren_surplus_list = []
kw_list = []
ks_list = []
grad_kw_list = []
grad_ks_list = []
Ks = Ks0 # in kW
Kw = Kw0 # in kW
if len(Es_list) != len(Ew_list) or len(Es_list) != len(El_list):
    sys.exit('Solar and Wind lists do not have same length.')
for i in range(iterations):
    # calculate loss
    cost = 0
    abs_error = 0
    ren_surplus = 0
    error_sum = 0
    grad_kw_sum = 0
    grad_ks_sum = 0
    for j in range(len(data_dict[region])):
        vw = data_dict[region]['wind_speed'][j] # in m/s
        rs = data_dict[region]['insolation'][j] # in kW/m2
        El = data_dict[region]['energy_demand'][j]*1000000      # in kWh
        Es, Ew = calc_energy(Kw,Ks,vw,rs)   # in kWh
        error = (El-(Es+Ew))    # in kWh
        error_sum += error
        cost += error**2     # in (kWh)^2
        abs_error += abs(error)
        if error < 0:
            ren_surplus += error    # in -kWh
        grad_kw, grad_ks = get_grad(vw,rs,Es,Ew,El)

        # cost_list.append(cost)
        # abs_error_list.append(abs_error)
        # ren_surplus_list.append(ren_surplus)
        # grad_kw_list.append(grad_kw)
        # grad_ks_list.append(grad_ks)
        # kw_list.append(Kw)
        # ks_list.append(Ks)
        # #update ks, kw
        # Ks = Ks - alpha * grad_ks
        # Kw = Kw - alpha * grad_kw
        grad_kw_sum += grad_kw
        grad_ks_sum += grad_ks
    #save error and k
    cost_list.append(cost)
    abs_error_list.append(abs_error)
    ren_surplus_list.append(ren_surplus)
    grad_kw_list.append(grad_kw_sum)
    grad_ks_list.append(grad_ks_sum)
    kw_list.append(Kw)
    ks_list.append(Ks)
    # update ks, kw:
    Ks = Ks - alpha * grad_ks_sum
    Kw = Kw - alpha * grad_kw_sum
    if Ks <0:
        Ks = 0
    if Kw <0:
        Kw = 0

'''
#%% gd func
region = 'North'
def get_day_data(day, region = region):
    vw = data_dict[region]['wind_speed'][day] # in m/s
    rs = data_dict[region]['insolation'][day] # in kW/m2
    El = data_dict[region]['energy_demand'][day] # in GWh

    return vw, rs, El



def gd(Ks, Kw, iterations, alpha = 0.0000001, squared_error_list = [], region = region):
    kw_list = []
    ks_list = []
    squared_error_list = []
    error_list = []
    error_abs_list = []
    for i in range(iterations):
        alpha_new = alpha
        grad_kw_sum = 0
        grad_ks_sum = 0
        squared_error = 0
        error_sum = 0
        error_abs_sum = 0
        for day in range(len(data_dict[region])):
            vw, rs, El = get_day_data(day)
            Es, Ew = calc_energy(Kw, Ks, vw, rs)
            error = El - (Es + Ew)
            error_sum += error
            error_abs_sum += abs(error)
            squared_error += error**2
            grad_kw, grad_ks = get_grad(vw, rs, Es, Ew, El)
            grad_kw_sum += grad_kw
            grad_ks_sum += grad_ks

        kw_list.append(Kw)
        ks_list.append(Ks)
        squared_error_list.append(squared_error)
        error_list.append(error_sum)
        error_abs_list.append(error_abs_sum)
        Kw = Kw - alpha_new * grad_kw_sum   
        Ks = Ks - alpha_new * grad_ks_sum 
    return squared_error_list, kw_list, ks_list, error_list, error_abs_list

#%% run gd
region = 'East'
# Ks = 0
# Kw = 0
Ks = Ks0_dict[region] / 1000
Kw = Kw0_dict[region] / 1000
iterations = 10000
squared_error_list, kw_list, ks_list, error_list, error_abs_list = gd(Ks, Kw, iterations, region = region)

# convert capacity back to MW
# kw_list = np.array(kw_list)/1000 
# ks_list = np.array(ks_list)/1000

#%% plot gradient descent results
x_axis = np.linspace(1,iterations,iterations)
paramstr = 'Parameters: \nRegion: ' + region + '\nLearning Rate: ' + '0.0000001' + '\nIterations: '+str(iterations)
props = dict(boxstyle='round', facecolor='white', alpha=0.5)

fig = plt.figure()
ax1 = fig.add_subplot(3,1,1)
plt.title('Cost Function')
plt.ylabel('[GWh^2]')
ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
ax1.plot(x_axis, squared_error_list)

ax2 = fig.add_subplot(3,1,2)
plt.title('Solar Power Capacity')
plt.ylabel('Capacity [GW]')
ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
ax2.plot(x_axis, ks_list)

ax3 = fig.add_subplot(3,1,3)
plt.title('Wind Power Capacity')
plt.ylabel('Capacity [GW]')
plt.xlabel('Iterations')
ax3.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
ax3.plot(x_axis, kw_list)
fig.text(1.03, 0.5, paramstr, fontsize=12,    verticalalignment='center', horizontalalignment='left', bbox=props) #, transform=ax3.transAxes
plt.tight_layout()
plt.show()


#%%plot cost function
# x_axis = np.linspace(1,iterations,iterations)
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
# plt.title('Cost Function')
# plt.ylabel('[kWh^2]')
# ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
# ax1.plot(x_axis, squared_error_list)

# #%%plot kw_list
# x_axis = np.linspace(1,iterations,iterations)
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
# plt.title('Kw')
# plt.ylabel('[kw]')
# ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
# ax1.plot(x_axis, kw_list)

#%% plot gradient descent yearly update results
# x_axis = np.linspace(1,iterations,iterations)
# paramstr = 'Parameters: \nRegion: ' + region + '\nLearning Rate: ' + str(alpha) + '\nIterations: '+str(iterations)
# props = dict(boxstyle='round', facecolor='white', alpha=0.5)

# fig = plt.figure()
# ax1 = fig.add_subplot(3,1,1)
# plt.title('Cost Function')
# plt.ylabel('[kWh^2]')
# ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
# ax1.plot(x_axis, cost_list)

# ax2 = fig.add_subplot(3,1,2)
# plt.title('Solar Power Capacity')
# plt.ylabel('Capacity [kW]')
# ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
# ax2.plot(x_axis, ks_list)

# ax3 = fig.add_subplot(3,1,3)
# plt.title('Wind Power Capacity')
# plt.ylabel('Capacity [kW]')
# plt.xlabel('Iterations')
# ax3.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))
# ax3.plot(x_axis, kw_list)
# # plt.plot(x_axis, abs_error_list)
# # plt.plot(x_axis, ren_surplus_list)
# fig.text(1.03, 0.5, paramstr, fontsize=12,    verticalalignment='center', horizontalalignment='left', bbox=props) #, transform=ax3.transAxes
# plt.tight_layout()
# plt.show()
# # %% plot potential for given k_s, k_w
# # plt.subplot(2,1,1)
# # plt.plot(date_list, Es_list)
# # plt.suptitle('Renewable Energy Potential: '+region, y=1.05, fontsize=15, ha='center')
# # plt.title('Solarenergy')
# # plt.xlabel('Date')
# # plt.ylabel('Energy [GWh]')

# # plt.subplot(2,1,2)
# # plt.plot(date_list, Ew_list)
# # plt.title('Windenergy')
# # plt.xlabel('Date')
# # plt.ylabel('Energy [GWh]')

# # plt.tight_layout()
# # plt.show()

# %%
