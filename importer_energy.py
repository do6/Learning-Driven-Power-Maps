# import words to table
#%%
import os
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd

engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

df_province = pd.read_sql_table("province", engine, columns=['name','id'])
dict_province = df_province.set_index('name').to_dict('int') #syntax for retreiving data: dict_province['name']['id']

df_feature = pd.read_sql_table("feature", engine, columns=['name','id'])
dict_feature = df_feature.set_index('name').to_dict('int')

#%% 
filename = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/data/energy_de_province_yearly.csv'
csv = open(filename, 'r', encoding="utf-8")
lines = csv.readlines() 
number_of_headerlines = 5

if not os.path.exists('/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_energy.sql'):
    f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_energy.sql", "w")
else:
    print("sql file already exists. Appending")
    f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_energy.sql", "a")

#%%

sql = "INSERT INTO data (feature_id, value, province_id, spatial_resolution, temporal_resolution, date)\nVALUES"

counter = 0
for line in lines:
    # skip header
    if counter < number_of_headerlines:
        counter += 1
        continue
    
    counter += 1
    splitted = line.split(";")
    province = splitted[0]
    year = splitted[1]
    comment = splitted[2]
    total = splitted[3]
    black_coal = splitted[4]
    brown_coal = splitted[5]
    petroleum = splitted[6]
    gas = splitted[7]
    renewables = splitted[8]
    electric_energy = splitted[9]
    if electric_energy != "": #convert terajoule to GWh
        electric_energy = float(electric_energy)/3.6 
    district_heat = splitted[10]
    other = splitted[11]

    if electric_energy != "":
    # order: feature_id, value, country_id, province_id, spatial_resolution, temporal resolution, date
        sql += "\n(" + \
            str(dict_feature['net_electricity_demand']['id']) + "," + \
            str(electric_energy) + "," + \
            str(dict_province[province]['id']) + "," + \
            "\'province\',\'year\'," + \
            "\'" + str(year) + "-12-31\'" + "),"

sql = sql[:-1]
sql+=";"
f.write(sql)

print('\ndone.\n')
