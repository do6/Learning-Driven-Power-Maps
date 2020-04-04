# import words to table
#%%
import os

filename = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/LearningDrivenPowerMaps/data/energy_de_province_yearly.csv'
save_as = 'energy_de_province_yearly.sql'
#%% 
csv = open(filename, 'r', encoding="utf-8")
lines = csv.readlines() 
number_of_headerlines = 5

if not os.path.exists('/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/LearningDrivenPowerMaps/sql/import_energy.sql'):
    f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/LearningDrivenPowerMaps/sql/import_energy.sql", "w")
else:
    f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/LearningDrivenPowerMaps/sql/import_energy.sql", "a")
#%%
dict_province = {
    'Baden-Wuerttemberg': 1,
    'Bayern': 2,
    'Berlin': 3,
    'Brandenburg': 4,
    'Bremen': 5,
    'Hamburg': 6,
    'Hessen': 7,
    'Mecklenburg-Vorpommern': 8,
    'Niedersachsen': 9,
    'Nordrhein-Westfalen': 10,
    'Rheinland-Pfalz': 11,
    'Saarland': 12,
    'Sachsen': 13,
    'Sachsen-Anhalt': 14,
    'Schleswig-Holstein': 15,
    'Thueringen': 16
}

dict_country = {
    'China': 1,
    'Germany': 2
}

dict_feature = {
    'net_electricity_demand': 1
}
#%%

sql = "INSERT INTO data (feature_id, value, country_id, province_id, spatial_resolution, temporal_resolution, date)\nVALUES"

counter = 0
for line in lines:
    # skip header
    if counter < number_of_headerlines:
        counter += 1
        continue
    
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
    district_heat = splitted[10]
    other = splitted[11]

    if electric_energy != "":
    # order: feature_id, value, country_id, province_id, spatial_resolution, temporal resolution, date
        sql += "\n(" + \
            str(dict_feature['net_electricity_demand']) + "," + \
            electric_energy + "," + \
            str(dict_country['Germany']) + "," + \
            str(dict_province[province]) + "," + \
            "\'province\',\'year\'," + \
            "\'" + str(year) + "-12-31\'" + "),"

sql = sql[:-1]
sql+=";"
f.write(sql)

print('\ndone.\n')
