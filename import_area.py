# import area csv file

import os
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd

engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

df_province = pd.read_sql_table("province", engine, columns=['name','id'])
dict_province = df_province.set_index('name').to_dict('int') #syntax for retreiving data: dict_province['name']['id']

df_country = pd.read_sql_table("country", engine, columns=['name','id'])
dict_country = df_country.set_index('name').to_dict('int')

df_feature = pd.read_sql_table("feature", engine, columns=['name','id'])
dict_feature = df_feature.set_index('name').to_dict('int')

filename = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/data/area_de_province.csv'

csv = open(filename, 'r', encoding="utf-8")
lines = csv.readlines() 
number_of_headerlines = 6

# if not os.path.exists('/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_area.sql'):
f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_area.sql", "w")


sql = "INSERT INTO data (feature_id, value, province_id, country_id, spatial_resolution, date)\nVALUES"

counter = 0
for line in lines:
    # skip header
    if counter < number_of_headerlines:
        counter += 1
        continue

    counter += 1
    splitted = line.split(";")
    province = splitted[0]
    value = splitted[1].rstrip()
    
    sql += "(" + str(dict_feature['area']['id']) +", "+ value + ", "+ \
        str(dict_province[province]['id']) +", "+ str(dict_country['Germany']['id']) + ", "+ \
        "\'country\', \'2016-12-31\'),\n"


sql = sql[:-2]
sql+=";"

f.write(sql)

print("\ndone.\n")