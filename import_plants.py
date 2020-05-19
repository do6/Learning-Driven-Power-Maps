#%% Import
import os
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
from pm_helper import get_ids
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from import_entsoe_datasets import import_entsoe_datasets
#%% prepare
id_dict = get_ids() # usage: id_dict['country']['Croatia'] gets province, feature, country
filename = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/data/Kraftwerksliste_trimmed.csv'
sql_file = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_plants.sql'
#open sql file
f = open(sql_file, 'w')
#open csv file
csv = open(filename, 'r', encoding='latin-1') #, encoding="utf-8"
lines = csv.readlines()
#%% execute

number_of_headerlines = 1
counter = 0
#prepare sql string
sql = "INSERT INTO plant (plant_number, province_id, zip, energy_carrier, capacity)\nVALUES"
#parse csv file
for line in lines:
    counter += 1
    # skip header
    if counter <= number_of_headerlines:
        continue

    splitted = line.split(';')
    # print(splitted)
    # print('\nlength: ', len(splitted))
    plant_number = splitted[0]
    zip_code = splitted[1]
    #if zip code has only 4 digits, add a leading 0
    if len(zip_code) == 4:
        zip_code = '0' + zip_code
    if zip_code == '':
        zip_code = '0'
    province = splitted[3]
    status = splitted[4]
    energy_carrier = splitted[5]
    capacity = splitted[6]
    capacity = capacity.replace('.','')
    capacity = capacity.replace(',','.')
    capacity = capacity.replace('\n','')
    # skip plants that are shut down
    if status != ('in Betrieb' or 'Gesetzlich an Stilllegung gehindert' or 'Sicherheitsbereitschaft'):
        continue
    # skip plant if it has 0 capacity
    try:
        float(capacity)
    except ValueError:
        continue
    # skip plant without BN number
    if plant_number == '':
        continue
    # rename AWZ to Offshore
    if province == 'AWZ':
        province = 'Offshore'
    # check if province exists
    if province in id_dict['province']:
        province_id = id_dict['province'][province]
    # skip, if province is not in province list
    else:
        continue
    
    if 'A' in zip_code:
        continue
    if len(zip_code) > 5:
        print(zip_code)
    # add to sql string
    # (plant_number, province_id, zip, type, energy_carrier, capacity, voltage_level)
    sql += '\n(' + \
        '\''+ plant_number +'\', ' + \
        str(province_id) + ', ' + \
        '\''+ zip_code +'\', ' + \
        '\''+ energy_carrier +'\', ' + \
        capacity + '),'

sql = sql[:-1]
sql += ';'
f.write(sql)

print('\ndone.\n')
#%%
