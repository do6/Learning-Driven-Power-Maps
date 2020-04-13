#create sql to import data
#%%
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd


feature_name = 'gdp'


engine = create_engine("postgresql://dorowiemann@localhost:5432/power_maps")

df_province = pd.read_sql_table("province", engine, columns=['name','id'])
dict_province = df_province.set_index('name').to_dict('int') #syntax for retreiving data: dict_province['name']['id']

df_country = pd.read_sql_table("country", engine, columns=['name','id'])
dict_country = df_country.set_index('name').to_dict('int')

df_feature = pd.read_sql_table("feature", engine, columns=['name','id'])
dict_feature = df_feature.set_index('name').to_dict('int')

#%% 
filename = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/data/gdp_de_province.csv'
csv = open(filename, 'r', encoding="utf-8")
lines = csv.readlines() 
number_of_headerlines = 6

f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_gdp.sql", "w")

sql = "INSERT INTO data (feature_id, value, province_id, country_id, spatial_resolution, temporal_resolution, date)\nVALUES"
# province = []
counter = 0
for line in lines:
    counter += 1
    # skip header
    if counter <= number_of_headerlines:
        continue
    
    splitted = line.split(";")
    if counter == number_of_headerlines + 1:
        province = [splitted[i+1] for i in range(len(splitted)-2)]
    else:
        year = splitted[0]
        value_province = [splitted[i+1] for i in range(len(splitted)-2)]
        value_country = splitted[-1].rstrip()
        #feature_id, value, province_id, country_id, spatial_resolution, temporal_resolution, date
        for j in range(len(value_province)):
            sql += "\n("+ str(dict_feature['gdp']['id']) + \
                ", "+ value_province[j] +", " + str(dict_province[province[j]]['id']) + \
                    ", " + str(dict_country['Germany']['id']) + \
                        ", \'province\', \'year\', \'" + year + "-12-31\'),"
        
        # add last column which is total value for country
        sql +=  "\n("+ str(dict_feature['gdp']['id']) + \
            ", "+ value_country + ", NULL, " + \
                str(dict_country['Germany']['id']) + \
                    ", \'country\', \'year\', \'" + year + "-12-31\'),"

        


sql = sql[:-1]
sql+=";"
f.write(sql)

print('\ndone\n')
# %%
