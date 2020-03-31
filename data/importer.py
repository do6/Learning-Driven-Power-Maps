# import words to table

csv = open('population_vs_demand.csv', 'r', encoding="utf-8")
lines = csv.readlines() 
f = open("import.sql", "a")

featureIds = {"energy_demand": 1,
    "population": 2}

sql = "INSERT INTO data (value, date, featureId) VALUES "
counter = 0
number_of_headerlines = 1
for line in lines:
    # skip header
    if counter < number_of_headerlines:
        counter += 1
        continue
    
    splitted = line.split(";")
    year = splitted[0]
    letztverbraucher = splitted[1]
    sondervertragskunden = splitted[2]
    tarifkunden = splitted[3]
    energy_demand = splitted[4]
    population = splitted[5]

    sql += "(" + str(population) + "," + '31.12.' + str(year) + "," + str(featureIds['population']) + "), \n"
    sql += "(" + str(energy_demand) + "," + '31.12.' + str(year) + "," + str(featureIds['energy_demand']) + "), \n"

f.write(sql)
