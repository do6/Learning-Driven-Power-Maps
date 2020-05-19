# importer entsoe datasets
#%%
import os
from sqlalchemy import create_engine, MetaData, Table
import pandas as pd
from pm_helper import get_ids
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


#%%
# id_dict = get_ids() # usage: id_dict['country']['Croatia']
# save_as_path = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/entsoe/'
# filename = '/Users/dorowiemann/Documents/_Uni/_SJTU_PowerMaps/Learning-Driven-Power-Maps/data/entsoe_belgium/Total Load - Day Ahead _ Actual_201701010000-201801010000.csv'

#%%
def import_entsoe_datasets(filename, save_as_path, id_dict):
    csv = open(filename, 'r', encoding="utf-8")
    lines = csv.readlines() 
    # number_of_headerlines = 0
    time0 = datetime.strptime(lines[1].split(',')[0].split('-')[0], '"%d.%m.%Y %H:%M ')
    time1 = datetime.strptime(lines[1].split(',')[0].split('-')[1], ' %d.%m.%Y %H:%M"')
    time_diff = (time1-time0).seconds/60/60 #=time difference in hours (i.e. 0.25)

    sql = "INSERT INTO data (feature_id, value, country_id, spatial_resolution, temporal_resolution, date)\nVALUES"
    country = ''
    date = []
    energy_daily = []
    power_daily_maximum = 0
    power_daily_minimum = 0
    power_daily_max_list = []
    power_daily_min_list = []
    counter = 0
    global_error_counter = 0
    local_error_counter = 0
    missing_data_flag = False
    max_local_error_counter = 0
    interpolation_counter = 0
    error_log = ''
    for line in lines:
        counter+=1
        if counter == 1:
            splitted = line.split(' ')
            for word in splitted:
                if word in id_dict['country']:
                    country = word
                    break
                else:
                    continue
            if country == '':
                print('\nerror: no country detected. Check csv file.')
                break
            else:
                print('\ncountry: '+country)
        
        else:
            splitted = line.split(',')
            #extract date
            date_line_dot = splitted[0].split(' ')[0].replace('"','')
            date_line = date_line_dot.split('.')[2] + '-' + date_line_dot.split('.')[1] + '-' + date_line_dot.split('.')[0]
            #extract actual value
            try:
                #power_line is the value that is used to caluclate energy and gets written to database
                power_line = float(splitted[-1].replace('"','').replace('\n',''))
                #extract the peak power for every day, later gets appended to array
                if power_line > power_daily_maximum: power_daily_maximum = power_line
                if power_line < power_daily_minimum or power_daily_minimum == 0: power_daily_minimum = power_line
                #if the last data point/s were missing, take the average.
                if missing_data_flag == True:
                    interpolation_counter += local_error_counter
                    interpolate_data = (power_line + last_valid_value)/2
                    power_line = local_error_counter * interpolate_data
                    if max_local_error_counter < local_error_counter:
                        max_local_error_counter = local_error_counter
                    last_valid_value = power_line / local_error_counter
                    local_error_counter = 0
                #else: everything normal
                else:
                    last_valid_value = power_line
                missing_data_flag = False
            except ValueError:
                #every year in March, Europe begins daylight saving time. Clocks are forwarded 1 hour. No values for this hour.
                error_log += 'Value Error. Date: ' + date_line + ' Value: ' + splitted[-1]
                global_error_counter += 1
                power_line = 0
                #if the value is N/A, we have no value where a value was expected.
                if "N/A" in splitted[-1]:
                    missing_data_flag = True
                    local_error_counter += 1

            except:
                error_log += 'Something else went wrong. Date: ' + date_line + ' Value: ' + splitted[-1]
                global_error_counter += 1
                local_error_counter += 1
                power_line = 0
                missing_data_flag = True
            # we have average power every time_diff (1/4h, 1/2h or 1h) in MW. Calculate energy in GWh.
            energy_line = power_line*time_diff/1000
            if counter == 2:
                date = [date_line]
                energy_daily = [energy_line]
            elif date_line == date[-1]:
                energy_daily[-1] += energy_line
            else:
                #append daily energy value
                date.append(date_line)
                energy_daily.append(energy_line)

    #get monthly resolution
    for i in range(len(energy_daily)):
        month = date[i].split('-')[1]
        if i==0:
            energy_monthly = [energy_daily[0]]
            date_monthly = [date[0]]
        elif month == last_month:
            energy_monthly[-1] += energy_daily[i]
        elif month != last_month and i > 0:
            energy_monthly.append(energy_daily[i])
            date_monthly.append(date[i])
        last_month = month

    error_log += '\ntotal yearly energy demand (daily data): ' + str(sum(energy_daily))
    error_log += '\ntotal yearly energy demand (monthly data): ' + str(sum(energy_monthly))

        
    try:
        # print('Creating sql. Country name: ', country, ', country id: ', id_dict['country'][country])
        for i in range(len(energy_daily)):
            #create sql
            #feature_id, value, country_id, spatial_resolution, temporal_resolution, date
            sql += '\n(' + str(id_dict['feature']['entsoe_energy_demand']) + ', '\
            + str(energy_daily[i]) + ', '\
            + str(id_dict['country'][country]) + ', '\
            + '\'country\'' + ', '\
            + '\'day\'' + ', '\
            + '\'' + date[i] +'\'),'
        sql += '\n----END DAILY VALUES, START MONTHLY VALUES----'
        for i in range(len(energy_monthly)):
            sql += '\n(' + str(id_dict['feature']['entsoe_energy_demand']) + ', '\
            + str(energy_monthly[i]) + ', '\
            + str(id_dict['country'][country]) + ', '\
            + '\'country\'' + ', '\
            + '\'month\'' + ', '\
            + '\'' + date_monthly[i] +'\'),'
        sql += '\n----END MONTHLY VALUES, START DAILY PEAKS----'
        for i in range(len(power_daily_maximum)):
            sql += '\n(' + str(id_dict['feature']['entsoe_power_peak']) + ', '\
            + str(power_daily_maximum[i]) + ', '\
            + str(id_dict['country'][country]) + ', '\
            + '\'country\'' + ', '\
            + '\'day\'' + ', '\
            + '\'' + date_power_daily_max_list[i] +'\'),'
    except:
        print('country not valid')
        error_log = 'country not valid, please check file. ' + country
        with open(save_as_path + country + '_' + date_monthly[0].split('-')[0] + '_entsoe_errorlog.txt', 'w') as log_file:
            print(error_log, file=log_file)
        return

    sql = sql[:-1]
    sql+=";"

    error_log = 'country: ' + country + \
    '\nyear: ' + date[0].split('-')[0] + \
    '\ntotal number of errors: ' + str(global_error_counter) + \
    '\nmax local errors: ' + str(max_local_error_counter) + \
    '\ntotal number of interpolated values: ' + str(interpolation_counter) + \
    '\nErrors: \n' + error_log

    year = date_monthly[0].split('-')[0]
    with open(save_as_path + country + '_' + year + '_entsoe.sql', 'w') as sql_file:
        print(sql, file=sql_file)

    with open(save_as_path + country + '_' + year + '_entsoe_errorlog.txt', 'w') as log_file:
        print(error_log, file=log_file)

    #warn if 1h or more has been interpolated, or a lot of errors occurred
    if max_local_error_counter > 3:
        print('File with hole. Please double check ', country, ', ', year)
    if global_error_counter > 4:
        print('\ntotal number of errors: ', global_error_counter)
    print(counter)
    print('\ndone!\n')


    # %% plot!
    jan = 0
    feb = jan + 31
    mar = feb + 28 #### 28 or 29
    apr = mar + 31
    may = apr + 30
    jun = may + 31
    jul = jun + 30
    aug = jul + 31
    sep = aug + 31
    octo = sep + 30
    nov = octo + 31
    dev = nov + 30

    # convert the elements of date list to datetime objects for plotting
    plot_date_daily = [datetime.strptime(i, "%Y-%m-%d").date() for i in date]
    # plot_date_daily = plot_date_daily #[octo:octo+31]
    plot_energy_daily = energy_daily #[octo:octo+31]

    plt.figure(1)
    plt.plot_date(plot_date_daily,plot_energy_daily,'-')
    # plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.SU))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=90)
    plt.grid()
    plt.title('Daily Demand of Electric Energy in ' + country)
    plt.xlabel('Date')
    plt.ylabel('Electric Energy Demand [GWh]')
    plt.tight_layout()
    plt.savefig(save_as_path+country+'_'+year+'_plot_daily_demand.pdf')
    plt.clf()

    # plot monthly resolution data
    plt.figure(2)
    plot_date_monthly = [datetime.strptime(i, "%Y-%m-%d").date() for i in date_monthly]
    plot_date_monthly = plot_date_monthly #[octo:octo+31]
    plot_energy_monthly = energy_monthly #[octo:octo+31]
    plt.plot_date(plot_date_monthly,plot_energy_monthly,'-')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=90)
    plt.grid()
    plt.title('Monthly Demand of Electric Energy in ' + country)
    plt.xlabel('Date')
    plt.ylabel('Electric Energy Demand [GWh]')
    plt.tight_layout()
    plt.savefig(save_as_path+country+'_'+year+'_plot_monthly_demand.pdf')
    plt.clf()
