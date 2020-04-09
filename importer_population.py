#%% import population

import os
import numpy as np

filename = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/data/population_de_province_yearly.csv'

csv = open(filename, 'r', encoding="utf-8")
lines = csv.readlines() 
number_of_headerlines = 5

if not os.path.exists('/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_population.sql'):
    f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_population.sql", "w")
else:
    f = open("/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/sql/import_population.sql", "a")

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


sql = "INSERT INTO data (feature_id, value, province_id, spatial_resolution, temporal_resolution, date)\nVALUES"


line_counter = 0
for line in lines:
    # skip header
    if line_counter < number_of_headerlines:
        line_counter += 1
        continue

    elif line_counter == number_of_headerlines:
        column_names = line.split(";") # column names are dates in this case
        year_list = [""]*(len(column_names)-1)
        a=0
        #### headers are years here. Adjust to usecase
        for header in column_names[1:]:
            date = header.split(".")    # headers are dates in german format
            year = date[2].replace('\n', '')    # year is 3rd element in header string
            #### this is necessary because the year comes in two digits. Remove if not needed
            if int(year) <21:
                year_list[a] = "20"+str(year)
            else:
                year_list[a] = "19"+str(year)
            a+=1

    else:
        a = 0      
        splitted = line.split(";")
        province = splitted[0]
        for value in splitted[1:]:
            # order: feature_id (=2 for population), value, province_id, spatial_resolution, temporal_resolution, date
            if value != '':
                sql += "\n(" + \
                "2" + "," + \
                value + "," + \
                str(dict_province[province]) + "," + \
                "\'province\',\'year\'," + \
                "\'" + year_list[a] + "-12-31\'" + "),"
            a += 1    

    line_counter += 1
    print(line_counter)

sql = sql[:-1]
sql+=";"
f.write(sql)

print('\ndone.\n')

