import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt

# Import csv files into dataframes
obc_weekday = pd.read_csv('obc-weekday.csv')
obc_weekend = pd.read_csv('obc-weekend.csv')
sc_weekday = pd.read_csv('stagecoach-weekday.csv')
sc_weekend = pd.read_csv('stagecoach-weekend.csv')
tt_weekday = pd.read_csv('thames-travel-weekday.csv')
tt_weekend = pd.read_csv('thames-travel-weekend.csv')
shared_weekday = pd.read_csv('shared-weekday.csv')          # These routes are shared by OBC and stagecoach
shared_weekend = pd.read_csv('shared-weekend.csv')

# OBG (Oxford Bus Group) is OBC + TT + 0.5*Shared
# SC (Stagecoach) is SC + 0.5*shared

sc_literature_distance = 16.2*1000000 # SC literature distance = 16.2 million km (2019)
obg_literature_fuel = 7000000/4.546 # OBG literature fuel usage = 7 million/4.546 gallons of Diesel, will have to convert this to distance using an mpg range = 7-9. 

obc_weekly_distance_total_miles = 5*obc_weekday['Daily Total Distance (miles)'].sum() + 2*obc_weekend['Daily Total Distance (miles)'].sum()
sc_weekly_distance_total_miles = 5*sc_weekday['Daily Total Distance (miles)'].sum() + 2*sc_weekend['Daily Total Distance (miles)'].sum()
tt_weekly_distance_total_miles = 5*tt_weekday['Daily Total Distance (miles)'].sum() + 2*tt_weekend['Daily Total Distance (miles)'].sum()
shared_weekly_distance_total_miles = 5*shared_weekday['Daily Total Distance (miles)'].sum() + 2*shared_weekend['Daily Total Distance (miles)'].sum()

# yearly distance in km for sc and obg
sc_yearly_distance = 1.609*52*(sc_weekly_distance_total_miles + 0.5*shared_weekly_distance_total_miles) 
obg_yearly_distance = 1.609*52*(obc_weekly_distance_total_miles + tt_weekly_distance_total_miles + 0.5*shared_weekly_distance_total_miles)

sc_covid_factor = sc_literature_distance/sc_yearly_distance

obg_literature_distance = obg_literature_fuel*7*1.609 # using a low mpg as worst case scenario, in km
obg_covid_factor = obg_literature_distance/obg_yearly_distance
print("Total Yearly Distance = ", round(obg_literature_distance+sc_literature_distance,1), "km")

# create lists of dataframes
weekday_dfs_list = [obc_weekday, sc_weekday, tt_weekday, shared_weekday]
weekend_dfs_list = [obc_weekend, sc_weekend, tt_weekend, shared_weekend]

# FUEL USAGE
# calculate fuel usage in gallons
for i in weekday_dfs_list:
    i['Daily Fuel Usage (gallons)'] = i.apply(lambda row: row["Daily Total Distance (miles)"]/row["MPG rating"], axis=1)

for j in weekend_dfs_list:
    j['Daily Fuel Usage (gallons)'] = j.apply(lambda row: row["Daily Total Distance (miles)"]/row["MPG rating"], axis=1)

# sum fuel usage for each company per week (weekday*5 + weekend*2) 
obc_weekly_fuel_usage = obc_weekday['Daily Fuel Usage (gallons)'].sum()*5 + obc_weekend['Daily Fuel Usage (gallons)'].sum()*2
sc_weekly_fuel_usage = sc_weekday['Daily Fuel Usage (gallons)'].sum()*5 + sc_weekend['Daily Fuel Usage (gallons)'].sum()*2
tt_weekly_fuel_usage = tt_weekday['Daily Fuel Usage (gallons)'].sum()*5 + tt_weekend['Daily Fuel Usage (gallons)'].sum()*2
shared_weekly_fuel_usage = shared_weekday['Daily Fuel Usage (gallons)'].sum()*5 + shared_weekend['Daily Fuel Usage (gallons)'].sum()*2

obg_actual_weekday_fuel_usage = obg_covid_factor*(obc_weekday['Daily Fuel Usage (gallons)'].sum()) + obg_covid_factor*(tt_weekday['Daily Fuel Usage (gallons)'].sum()) + 0.5*obg_covid_factor*(shared_weekday['Daily Fuel Usage (gallons)'].sum())
obg_actual_weekend_fuel_usage = obg_covid_factor*(obc_weekend['Daily Fuel Usage (gallons)'].sum()) + obg_covid_factor*(tt_weekend['Daily Fuel Usage (gallons)'].sum()) + 0.5*obg_covid_factor*(shared_weekend['Daily Fuel Usage (gallons)'].sum())
obg_actual_weekly_fuel_usage = 5*obg_actual_weekday_fuel_usage + 2*obg_actual_weekend_fuel_usage

sc_actual_weekday_fuel_usage = sc_covid_factor*(sc_weekday['Daily Fuel Usage (gallons)'].sum()) + sc_covid_factor*0.5*(shared_weekday['Daily Fuel Usage (gallons)'].sum())
sc_actual_weekend_fuel_usage = sc_covid_factor*(sc_weekend['Daily Fuel Usage (gallons)'].sum()) + sc_covid_factor*0.5*(shared_weekend['Daily Fuel Usage (gallons)'].sum())

total_weekday_fuel_usage = obg_actual_weekday_fuel_usage + sc_actual_weekday_fuel_usage
total_weekend_fuel_usage = obg_actual_weekend_fuel_usage + sc_actual_weekend_fuel_usage

total_yearly_fuel_usage = 52*(5*total_weekday_fuel_usage + 2*total_weekend_fuel_usage) # gallons
print("Total Yearly Fuel Usage = ", round(total_yearly_fuel_usage*4.546, 1), "L")
print("Total Yearly CO2 Emissions = ", round(total_yearly_fuel_usage*4.546*2.68, 1), "kg")


# energy equivalence and hydrogen requirement
# E = V*rho*eta where rho = energy density and eta = drivetrain efficiency

diesel_rho = 175 # MJ/gallon
diesel_eta = 0.41 # (Rosero, Fonseca, López, & Casanova, 2020)

h2_rho = 120 # MJ/kg
h2_eta = 0.6 # (Folkson, 2014)

diesel_to_hydrogen = (diesel_rho*diesel_eta)/(h2_rho*h2_eta)

total_weekday_hydrogen_requirement = total_weekday_fuel_usage*diesel_to_hydrogen
total_weekend_hydrogen_requirement = total_weekend_fuel_usage*diesel_to_hydrogen

total_yearly_hydrogen_requirement = 52*(5*total_weekday_hydrogen_requirement + 2*total_weekend_hydrogen_requirement)
print("Total Yearly Hydrogen Requirement = ", round(total_yearly_hydrogen_requirement, 1), "kg")
print("Hydrogen Weekday Requirement = ", round(total_weekday_hydrogen_requirement,1), "kg")
print("Hydrogen Weekend Requirement = ", round(total_weekend_hydrogen_requirement, 1), "kg")

hydrogen_distance_ratio = total_yearly_hydrogen_requirement/(obg_literature_distance+sc_literature_distance)
print("Ratio = ", round(hydrogen_distance_ratio*100,1), "kg per 100 km")

a = round(total_weekday_hydrogen_requirement,1)
b = round(total_weekend_hydrogen_requirement,1)
c = [a,a,a,a,a,b,b]
daily_hydrogen_need = [a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a,a,a,a,b,b,a,a]
print(len(daily_hydrogen_need))
with open('daily_hydrogen_output.csv', 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(daily_hydrogen_need)

obc_proportion = 29/44
tt_proportion = 15/44

company_data = {'Stagecoach':[0.001*52*diesel_to_hydrogen*(sc_actual_weekday_fuel_usage*5 + sc_actual_weekend_fuel_usage*2), 4.546*(sc_actual_weekday_fuel_usage*5 + sc_actual_weekend_fuel_usage*2), 0.001*2.68*4.546*(sc_actual_weekday_fuel_usage*5 + sc_actual_weekend_fuel_usage*2)], 'OBC': [0.001*52*diesel_to_hydrogen*(obg_actual_weekly_fuel_usage*obc_proportion), 4.546*(obg_actual_weekly_fuel_usage*obc_proportion), 0.001*2.68*4.546*(obg_actual_weekly_fuel_usage*obc_proportion)], 'Thames Travel':[0.001*52*diesel_to_hydrogen*(obg_actual_weekly_fuel_usage*tt_proportion), 4.546*(obg_actual_weekly_fuel_usage*tt_proportion), 0.001*2.68*4.546*(obg_actual_weekly_fuel_usage*tt_proportion)]}
company_dataframe = pd.DataFrame(data=company_data)


# PLOTTING

miles_to_km = 1.609

# ANNUAL HYDROGEN USAGE PER OPERATOR
distance_row = company_dataframe.iloc[0]
distance_row.plot.bar(rot=0)
plt.xlabel('Network Operator', fontsize=20)
plt.ylabel('Annual Hydrogen Usage (tonnes)', fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.show()

# ANNUAL EMISSIONS PER COMPANY
emissions_row = company_dataframe.iloc[2]
emissions_row.plot.bar(rot=0)
plt.xlabel('Network Operator', fontsize=20)
plt.ylabel('CO2 Emissions (tonnes)', fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.show()


obc_yearly_fuel_usage = obc_proportion*4.546*52*(5*obg_actual_weekday_fuel_usage + 2*obg_actual_weekend_fuel_usage)
tt_yearly_fuel_usage = tt_proportion*4.546*52*(5*obg_actual_weekday_fuel_usage + 2*obg_actual_weekend_fuel_usage)
sc_yearly_fuel_usage = 52*4.546*(5*sc_actual_weekday_fuel_usage + 2*sc_actual_weekend_fuel_usage)
print(round(obc_yearly_fuel_usage,1))
print(round(tt_yearly_fuel_usage,1))
print(round(sc_yearly_fuel_usage,1))
print(company_dataframe)

# OBC WEEKDAY DISTANCE
obc_weekday["Daily Total Distance (miles)"] = obc_weekday["Daily Total Distance (miles)"]*obg_covid_factor*obc_proportion*miles_to_km
obc_weekday.plot.bar(rot=0, x="Route Name", y="Daily Total Distance (miles)",legend=None)
plt.xlabel('Route Number', fontsize=20)
plt.ylabel('Daily Distance (km)', fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.show()

# OBC WEEKEND DISTANCE
obc_weekend["Daily Total Distance (miles)"] = obc_weekend["Daily Total Distance (miles)"]*obg_covid_factor*obc_proportion*miles_to_km
obc_weekend.plot.bar(rot=0,x="Route Name",y="Daily Total Distance (miles)",legend=None)
plt.xlabel('Route Number', fontsize=20)
plt.ylabel('Daily Distance (km)', fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.show()

# OBC WEEKDAY FUEL
obc_weekday["Daily Fuel Usage (gallons)"] = obc_weekday["Daily Fuel Usage (gallons)"]*4.546*obg_covid_factor*obc_proportion
obc_weekday.plot.bar(rot=0,x="Route Name",y="Daily Fuel Usage (gallons)",legend=None)
plt.xlabel('Route Number', fontsize=20)
plt.ylabel('Daily Fuel Consumption (L)', fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.show()

# OBC WEEKEND FUEL
obc_weekend["Daily Fuel Usage (gallons)"] = obc_weekend["Daily Fuel Usage (gallons)"]*4.546*obg_covid_factor*obc_proportion
obc_weekend.plot.bar(rot=0,x="Route Name",y="Daily Fuel Usage (gallons)",legend=None)
plt.xlabel('Route Number', fontsize=20)
plt.ylabel('Daily Fuel Consumption (L)', fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.show()





