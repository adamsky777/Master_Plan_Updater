import json
import time
import tkinter.ttk
import urllib.error
import zipfile
from tkinter import *
import csv
from tkinter import messagebox
from time import sleep
import google.auth.exceptions
import gspread.exceptions
import numpy as np
import pandas as pd
import gspread as gs
import shutil
from datetime import date
from tkinter import filedialog
import threading
import re
import yaml
import webbrowser
from datetime import timedelta
import datetime
import sys
import pyminizip
import os
import semver
import send2trash
import copy
import ssl
#from tkhtmlview import HTMLLabel
from tkinterweb import HtmlLabel

from tkinterhtml import HtmlFrame
#from signal import signal, SIGPIPE, SIG_DFL
#Ignore SIG_PIPE and don't throw exceptions on it... (http://docs.python.org/library/signal.html)
#signal(SIGPIPE, SIG_DFL)
#_______________________________________________LEGACY CODE_____________________________________________________________

App_version = "2.1.8"
App_code = "H5TM230621"

# LOAD Default message
ssl._create_default_https_context = ssl._create_unverified_context
try:
    default_message = pd.read_html("https://docs.google.com/spreadsheets/d/e/2PACX-1vSkU65RepNSeh2li9jHweV9G-0E4NXYsokzoTAwZ3VbeS2x2abtGgxQkP7Nx6hD-qQffhcb-SDi4nPB/pubhtml?gid=0&single=true", skiprows=1)
    default_message = default_message[0]
    del default_message[default_message.columns[0]]
    default_message = (default_message.columns.tolist())[0]
except urllib.error.URLError as URL_err:
    messagebox.showerror(message=str(URL_err) + " You might not connected to the internet.")
    sys.exit()



empty_df = {
    'Unnamed: 0': [],
    'Dynamic Timeframe': [],
    '3PL': []
}
empty_df_3PL = {
    'Unnamed: 0':[],
    'Dynamic Timeframe':[],
    '3PL': []
               }

empty_df_Total = {
    'Unnamed: 0': [],
    'Dynamic Timeframe': [],
    'Total': []
}

#empty_df_3PL = pd.DataFrame(empty_df_3PL)
#print(empty_df_3PL)
missing_log = []

# Print text green
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))

def find_folders(path_to_dir, suffix=""):
    """
    lists all files in a specified Directory
    :param path_to_dir: Path to the directory
    :param suffix: criteria that the file ends with (in this case folder does not ends with anything)
    :return: returns all the folders in a list
    """
    download_directory = os.path.expanduser(path_to_dir)
    filenames = os.listdir(download_directory)
    return [filename for filename in filenames if filename.endswith(suffix)]


directory = '~/Downloads/'
all_folders_list = find_folders(directory)

folder_list = []
for x in all_folders_list:
    if "dashboard-daily_numbers_for_masterplan" in x:
        folder_list.append(x)

if len(folder_list) > 1:
    messagebox.showerror(message="Duplicates found. Remove all the folders from your downloads folder named: "
                                 "'dashboard-daily_numbers_for_masterplan'")
    duplicates_question = messagebox.askquestion(message="Do you want to remove the duplicates?")
    if duplicates_question == "yes":
        for i in folder_list:
            send2trash.send2trash(os.path.expanduser("~")+"/Downloads/"+i)
            print(i)

        sys.exit()
    else:
        sys.exit()



elif len(folder_list) == 0:
    messagebox.showerror(message="Folder: 'dashboard-daily_numbers_for_masterplan' is missing from your downloads folder")
    sys.exit()

# Todo: Handle when cities paused, but revenue coming from passes. -> Looker generates csv with 3 columns instead of 2.

else:
    try:
        # Avg daily active vehicles on the street df0
        df0 = pd.read_csv(
            "~/Downloads/dashboard-daily_numbers_for_masterplan/average_daily_active_vehicles_on_the_street.csv")
        #   gets the value of average number of scooter deployed
        df0 = df0.fillna(float(0))
        shape_df0 = df0.shape  # shape of df3 ( instance : tuple)
        df0_rows = int(shape_df0[0])
        df0_columns = int(shape_df0[1])
        # Drops a message to the user only when incorrect schedule loaded in. Ignores when values missing.
        prGreen(df0_columns)
        if df0_columns > 3 and df0_rows > 0:
            messagebox.showerror(message="Your Looker schedule is incorrect. Too many days in the data. "
                                         "Set it to: 'is in the last 1 complete day'.")
            sys.exit()

        # df_check = 1/int(df0_rows)
    except FileNotFoundError:
        messagebox.showerror(message="the daily numbers for masterplan is not exsist in the downloads folder")
        sys.exit()
    # except ZeroDivisionError:
    # messagebox.showerror(message="The CSV file does not contain any Cities")
    # sys.exit()

    try:
        # Avg daily vehicles with 1+ trip df1
        df1 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/average_daily_vehicles_with_1+_trips.csv")
        # gets the value of scooters with rides in respect of the corresponding city
        df1 = df1.fillna(float(0))
        shape_df1 = df1.shape
    except FileNotFoundError:
        df1 = pd.DataFrame(empty_df)
        missing_log.append("average_daily_vehicles_with_1+_trips.csv")

    try:
        # Rides df2
        df2 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/rides.csv")
        df2 = df2.fillna(float(0))
        shape_df2 = df2.shape
    except FileNotFoundError:
        df2 = pd.DataFrame(empty_df)
        missing_log.append("rides.csv")
    try:
        # GMV from PASSES df3
        df3 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/gmv_from_passes.csv")
        # changes NaN values to €0.0
        df3 = df3.fillna("€0.0")
        shape_df3 = df3.shape  # shape of df3 ( instance : tuple)
        df3_rows = int(shape_df3[0])
    except FileNotFoundError:
        df3 = pd.DataFrame(empty_df)
        missing_log.append("gmv_from_passes.csv")

    try:
        # GMV without passes df4
        df4 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/gmv_(without_passes).csv")
        df4 = df4.fillna("0")
        shape_df4 = df4.shape
    except FileNotFoundError:
        df4 = pd.DataFrame(empty_df)
        missing_log.append("gmv_(without_passes).csv")

    try:
        # average order duration df5
        df5 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/average_order_duration,_minutes.csv")
        df5 = df5.fillna("0")
    except FileNotFoundError:
        df5 = pd.DataFrame(empty_df)
        missing_log.append("average_order_duration_minutes.csv")

    try:
        # battery swaps 3PL df6
        df6 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/battery_swaps_by_3pl.csv", skiprows=[1],
                          thousands=',')
        df6 = df6.fillna("0")
        if df6.shape[0] == 0:
            df6 = pd.DataFrame(empty_df_3PL)
        else:
            df6 = df6.rename(columns={df6.columns[2]: '3PL'})
    except FileNotFoundError:
        df6 = pd.DataFrame(empty_df_3PL)
        missing_log.append("battery_swaps_by_3pl.csv")

    try:
        # collected 3PL df7
        df7 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/collected_by_3pl.csv", skiprows=[1])
        df7 = df7.fillna("0")
        if df7.shape[0] == 0:
            df7 = pd.DataFrame(empty_df_3PL)
        else:
            df7 = df7.rename(columns={df7.columns[2]: '3PL'})
    except FileNotFoundError:
        df7 = pd.DataFrame(empty_df_3PL)
        missing_log.append("collected_by_3pl.csv")

    try:
        # deployed 3PL df8
        df8 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/deployed_by_3pl.csv", skiprows=[1])
        df8 = df8.fillna("0")
        if df8.shape[0] == 0:
            df8 = pd.DataFrame(empty_df_3PL)
        else:
            df8 = df8.rename(columns={df8.columns[2]: '3PL'})
    except FileNotFoundError:
        df8 = pd.DataFrame(empty_df_3PL)
        missing_log.append("deployed_by_3pl.csv")

    try:

        # Waiting for parts
        """Note that csv of WP has different style, so inserting a row to the left achieves the same look 
            -> we can use the same iteration """
        df9 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/vehicles_waiting_for_parts.csv")
        df9.insert(loc=0, column="Num", value=0)
        df9 = df9.fillna("0")
    except FileNotFoundError:
        df9 = pd.DataFrame(empty_df)
        missing_log.append("vehicles_waiting_for_parts.csv")

    try:
        # sum collected df10
        df10 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/collected.csv", skiprows=[1])
        df10 = df10.fillna("0")
        if df10.shape[0] == 0:
            df10 = pd.DataFrame(empty_df_Total)
        else:
            df10 = df10.rename(columns={df10.columns[2]: 'Total'})
    except FileNotFoundError:
        df10 = pd.DataFrame(empty_df_Total)
        missing_log.append("collected.csv")

    try:
        # sum deployed df11
        df11 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/deployed.csv", skiprows=[1])
        df11 = df11.fillna("0")
        if df11.shape[0] == 0:
            df11 = pd.DataFrame(empty_df_Total)
        else:
            df11 = df11.rename(columns={df11.columns[2]: 'Total'})
    except FileNotFoundError:
        df11 = pd.DataFrame(empty_df_Total)
        missing_log.append("deployed.csv")
    try:
        # sum battery_swaps df12
        df12 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/battery_swaps.csv", skiprows=[1],
                           thousands=',')
        df12 = df12.fillna("0")
        if df12.shape[0] == 0:
            df12 = pd.DataFrame(empty_df_Total)
        else:
            df12 = df12.rename(columns={df12.columns[2]: 'Total'})
    except FileNotFoundError:
        df12 = pd.DataFrame(empty_df_Total)
        missing_log.append("battery_swaps.csv")

    # vehciles waiting for service.
    try:
        df14 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/vehicles_waiting_for_service.csv", thousands=',')
        df14 = df14.fillna(0)
    except FileNotFoundError:
        df14 = pd.DataFrame(empty_df)
        missing_log.append("vehicles_waiting_for_service.csv")

# ______________________________________Import Actually waiting for parts_______________________________________________
    # FROM: Waiting for Parts VS Inventory - Dump : Data_Dump
    try:
        df15 = pd.read_html(
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGJbzJGxdGv96zStGyv9Ce48XG_Bq8VRE5ki3OsfRWDlCpjVlVWwhCtEcSf__IbXIMAslfwkLTB1jm/pubhtml?gid=0&single=true",
            skiprows=1)
        df15 = df15[0]
        del df15[df15.columns[0]]
        df15 = df15.drop(['city', 'all_waiting_for_parts'], axis=1)
        city = df15.pop('ASCII_City')
        df15.insert(2, 'ASCII_City', city)

    except urllib.error.URLError as URL_err:
        messagebox.showerror(message=str(URL_err) + "You might not be connected to the internet.")
        sys.exit()

    try: # Read vehicle inflow
        df16 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/inbound_for_maintenance.csv",
                           thousands=',')
        df16 = df16.fillna(0)

    except FileNotFoundError:
        df16 = pd.DataFrame(empty_df)
        missing_log.append("inbound_for_maintenance.csv")

    try: #Read vehicle outflow
        df17 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/outbound_from_maintenance.csv",
                           thousands=',')
        df17 = df17.fillna(0)

    except FileNotFoundError:
        df17 = pd.DataFrame(empty_df)
        missing_log.append("outbound_from_maintenance.csv")



# TODO: Reference table
# Import reference table.
to_pop = ['LOC_ID',	'Closure', 'Country']
ref_table = pd.read_html("https://docs.google.com/spreadsheets/d/e/2PACX-1vSiC77seEnxY1agmLMEvbD8WENw7itCkDL_prQx2wlQz2OKNUk3A9S6KOObQMThEDsHDyakECGrIo7N/pubhtml?gid=0&single=true",skiprows=1, encoding='utf-8')
ref_table = ref_table[0]
del ref_table[ref_table.columns[0]]

ref_table = ref_table[ref_table['Closure'] != 'CLOSED']
ref_table.drop(columns=to_pop, inplace=True)
ref_table.rename(columns={"Main_City": "city"}, inplace=True)

SC_cols = [i for i in ref_table.columns if "SC" in i ]
city_map = pd.melt(ref_table, id_vars=['city'], value_vars=SC_cols, value_name="Satellite_City")
city_map.drop_duplicates(inplace=True)
#city_map.dropna(inplace=True)
del city_map['variable']
city_map = city_map[['Satellite_City','city']]
city_map0 = city_map.values.tolist()
city_map = [i for s in city_map0 for i in s]
city_map = pd.DataFrame(city_map, columns=['City'])
city_map.dropna(inplace=True), city_map.drop_duplicates(inplace=True)
all_city_ref = city_map['City'].to_list # reverting back to as a list -> buut, type() will be method.
all_city_ref = list(all_city_ref())  # converting method to list by list(some_method()) function.

sat_cit_list = ref_table.melt(value_vars=SC_cols)['value'].dropna().drop_duplicates().tolist() # satellite city list

# __________________________________________ In-house FOA calculations ________________________________________________

print(df7.columns)

collected_merge_df = pd.merge(df10, df7,
                   on='Dynamic Timeframe',
                   how='outer')

#prGreen(collected_merge_df.columns)
collected_merge_df['Total'] = collected_merge_df['Total'].fillna(0).astype(int)
collected_merge_df["3PL"] = collected_merge_df["3PL"].fillna(0).astype(int)
collected_merge_df["FOA"] = collected_merge_df['Total'] - collected_merge_df["3PL"]
collected_merge_df["FOA"] = collected_merge_df["FOA"].fillna(0)

# Use deepcopy function provided in the default package 'copy'
df10 = copy.deepcopy(collected_merge_df[["Dynamic Timeframe", "FOA"]])
df10['FOA'] = df10['FOA'].mask(df10['FOA'] < 0, 0) # mask negative values.
df10.loc[-1] = ['City Country Region', 'Count Operations']
df10 = df10.sort_index().reset_index(drop=True)
df10.insert(0, 'Unnamed: 0', np.nan)


deployed_merge_df = pd.merge(df11, df8,
                   on='Dynamic Timeframe',
                   how='outer')

deployed_merge_df['Total'] = deployed_merge_df['Total'].fillna(0).astype(int)
deployed_merge_df["3PL"] = deployed_merge_df["3PL"].fillna(0).astype(int)
deployed_merge_df["FOA"] = deployed_merge_df['Total'] - deployed_merge_df["3PL"]
deployed_merge_df["FOA"] = deployed_merge_df["FOA"].fillna(0)

df11 = copy.deepcopy(deployed_merge_df[["Dynamic Timeframe", "FOA"]])
df11['FOA'] = df11['FOA'].mask(df11['FOA'] < 0, 0) # mask negative values.
df11.loc[-1] = ['City Country Region', 'Count Operations']
df11 = df11.sort_index().reset_index(drop=True)
df11.insert(0, 'Unnamed: 0', np.nan)



swaps_merge_df = pd.merge(df12, df6,
                   on='Dynamic Timeframe',
                   how='outer')

swaps_merge_df['Total'] = swaps_merge_df['Total'].fillna(0).astype(int)
swaps_merge_df["3PL"] = swaps_merge_df["3PL"].fillna(0).astype(int)
swaps_merge_df["FOA"] = swaps_merge_df['Total'] - swaps_merge_df["3PL"]
swaps_merge_df["FOA"] = swaps_merge_df["FOA"].fillna(0).astype(int)



df12 = copy.deepcopy(swaps_merge_df[["Dynamic Timeframe", "FOA"]])
df12['FOA'] = df12['FOA'].mask(df12['FOA'] < 0, 0) # mask negative values.
df12.loc[-1] = ['City Country Region', 'Count Operations']
df12 = df12.sort_index().reset_index(drop=True)
df12.insert(0, 'Unnamed: 0', np.nan)



print(df12.columns, df6.columns)

for i in [df12, df11, df10, df6, df7, df8]:
    print(i.shape)

def revert_df_layout(df):
    old_entry = ['777', 'City Country Region', 'Count Operations']
    df.loc[((len(df) - 1.5) - len(df))] = old_entry
    df = df.sort_index().reset_index(drop=True)
    return df

for i in [df12, df11, df10, df6, df7, df8]:
    revert_df_layout(i)


# __________________________________________ END In-house FOA calculations _____________________________________________

missing_log = [i +", " for i in missing_log]
missing_log ="".join(str(i) for i in missing_log)

today = date.today()
print(missing_log)
locker = "19StayHungryStayFoolish84"


with open("coll_dep_swap_container.yaml", mode='r') as coll_dep_swap_container:
    cb_var_yaml = yaml.load(coll_dep_swap_container, Loader=yaml.FullLoader)

with open("coll_dep_swap_container.json", mode='r')as coll_dep_swap_container:
    cb_var_json = json.load(coll_dep_swap_container)
    cb_var_3PL = cb_var_json["3PL"]
    cb_var_in_house = cb_var_json["In-house"]
    cb_var_Backlog = cb_var_json['Backlog']


def save_user_data():
    """
    Creates an encrypted zip file of the user data, if a user has 20-30 or even more cities, it might become time
    consuming to add the cities to the list again.
    The encrypted zip file contains all the previously saved data of the user.
    User can choose where to save the file and the save option is available from the menu bar.
    :returns: The encrypted zip file
    """
    save_path = filedialog.askdirectory()
    if save_path != "":
        save_path = save_path + "/user_data.zip"
        pyminizip.compress_multiple([os.path.join(os.getcwd(),
                                                  'downloads_path_container.yaml'),
                                     os.path.join(os.getcwd(), 'credentials_path_container.yaml'),
                                     os.path.join(os.getcwd(), 'E-Bikes_Master_Plan_links.csv'),
                                     os.path.join(os.getcwd(), 'Master_Plan_links.csv'),
                                    os.path.join(os.getcwd(), 'user_ID.yaml')],
                                    [u'/', u'/', u'/', u'/', u'/'], save_path, locker, 0)
        messagebox.showinfo(message="User data saved")
    else:
        messagebox.showinfo(message=" User data not saved")


def import_user_data():
    """
    Loads the user data from the encrypted zip file.
    User can load the data from the menu bar.
    :returns: Replaces the program's default files by the previously saved files.
    """
    import_path = filedialog.askopenfilename(filetypes=[('Zip File', '*.zip')])
    if import_path != "":
        with zipfile.ZipFile(import_path, 'r') as user_data_zip:
            user_data_zip.extractall(pwd=locker.encode(), path="Temp/")
            temp_folder_items = os.listdir("Temp")
            prGreen(check_user())
            if check_user() == "OK":
                user_data_zip.extractall(pwd=locker.encode())
                messagebox.showinfo(message="User Data successfully loaded")
                for i in temp_folder_items:
                    send2trash.send2trash(os.path.join("Temp", i))

            elif check_user() == "not valid":
                prGreen(temp_folder_items)
                for i in temp_folder_items:
                    send2trash.send2trash(os.path.join("Temp", i))
                messagebox.showerror(message="User Data is NOT interchangeable. Use city list instead.")

        send2trash.send2trash(import_path)
    else:
        messagebox.showinfo(message=" User data not loaded")


def save_city_data():
    """
    Creates an encrypted zip file containing the city list both for scooters and ebikes.
    The encrypted zip file only contains the data of the city lists, excluding the user data.
    Hence, users can circulate the zip file if they have 20-40 cities. So new members don't need to add the cities again.
    :return: The encrypted zip file.
    """
    save_path = filedialog.askdirectory()
    if save_path != "":
        save_path = save_path + "/city_data.zip"
        pyminizip.compress_multiple([
                                     os.path.join(os.getcwd(), 'E-Bikes_Master_Plan_links.csv'),
                                     os.path.join(os.getcwd(), 'Master_Plan_links.csv')],
                                    [u'/', u'/'], save_path, locker, 0)
        messagebox.showinfo(message="City data saved")
    else:
        messagebox.showinfo(message="City data not saved")


def import_city_data():
    """
    Loads the City data from the encrypted zip file.
    User can load the data from the menu bar.
    :returns: Replaces the program's default files by the the previously saved files.
    """
    import_path = filedialog.askopenfilename(filetypes=[('Zip File', '*.zip')])
    if import_path != "":
        with zipfile.ZipFile(import_path, 'r') as city_data_zip:
            city_data_zip.extractall(pwd=locker.encode())
        messagebox.showinfo(message="City Data successfully loaded")
        os.remove(import_path)
    else:
        messagebox.showinfo(message=" City data not loaded")

def in_out_flow():
    """
    Store inflow and outflow settings (not implemented feature)
    :return:
    """
    ioflow_txt = open(os.path.join(os.getcwd() + "/Temp/in_out_flow.txt"),"w")
    ioflow_txt.write("On\n")
    ioflow_txt.close()

def get_date(day):
    """
    Get the index of the dropdown menu section.
    :param day: the index of the dropdown menu (default: t-1 = 0)
    :returns: the date on the time horizon (t-1...t-4)
    """

    if day == 0:
        timehorizon = today.strftime('%-d-%b')
    else:
        timehorizon = today - timedelta(days=day)
        timehorizon = timehorizon.strftime('%-d-%b')
    return timehorizon


def replacesign(a):
    """
    Replaces removes comma, to normalize values and converts to float
    :param a: the string from any df that we want to transform
    :returns: :param a: as float
    """

    a = a.replace(",", "")
    a = float(a)
    return a


def replaceEuro(b):
    """
    Removes euro sign to work normalize the string and converts to float.
    :param b: the string from any df that we want to transform
    :returns: :param b: as float
    """

    b = b.replace("€", "")
    b = b.replace(",", "")
    b = float(b)
    return b


def zeroeuro(city_GMV_passes):
    """
    Adds euro sign and converts it to a string if no revenue from passes.
    :param city_GMV_passes:  The city's revenue from  passes.
    :return: :param city_GMV_passes:
    """

    if city_GMV_passes == 0:
        city_GMV_passes = "€0"
    else:
        "do nothing"
    return city_GMV_passes


def zerocomma(city_GMV_without_passes):
    """
    Adds a comma and convert it to string if there is no revenue.
    :param city_GMV_without_passes: City's revenue, passes excluded
    :return:
    """

    if city_GMV_without_passes == 0:
        city_GMV_without_passes = "0,0"
    else:
        "do nothing"
    return city_GMV_without_passes


def retrieve_values(df, city):
    """
    Returns the values from the dataframes that mathces with the conditions.
    :param df: dataframe generated by panda from the csv files.
    :param city: A city from the added cities list.
    :returns: the corresponding value from the dataframe that matches with the city
    """

    select_csv = csv_selector()
    MP_links_df = pd.read_csv(select_csv)
    all_cities_list = MP_links_df['CityName'].values.tolist()
    """∆- ed the Dynamic Timeframe to the first row since, it is not standardized by looker (For ex: Slovakia)"""
    # df_first_col = df[:, 1].values.tolist()
    df_first_col = df.iloc[:, 1].tolist()
    prGreen(df_first_col)
     # df_first_col = df['Dynamic Timeframe'].values.tolist()
    active_cities_list = [i for i in all_cities_list if i in df_first_col]
    cities_indexes = [df_first_col.index(x) for x in active_cities_list]
    cities_dictionary = dict(zip(active_cities_list, cities_indexes))
    df_row = cities_dictionary.get(city, -1)
    if df_row < 0:
        values = 0
    else:
        values = df.iat[df_row, 2]
    return values



def get_awfp(df15):
    dropdown_value = timeback.get()
    dropdown_index = dropdown_options.index(dropdown_value)
    today = get_date(dropdown_index)
    date_backlog = date.today() - timedelta(days=(abs(int((dropdown_index + 1) * (-1)))))
    print("dropdown ind:",dropdown_index)
    # convert the date column to a datetime object and set it as the index
    #df15['Date'] = pd.to_datetime(df15['Date'])
    #df15 = df15.set_index('Date')
    # filter the dataframe by a specific date
    df15_filtered = df15[df15['Date'] == str(date_backlog)]
    #df15_filtered = df15.loc[str(yday)]
    df15_filtered = df15_filtered.iloc[:,-2:] # return the last two columns only from the df
    df15_filtered.insert(0,"index",'') # to match with retrieve values let's insert an empty col. to the left.
    return df15_filtered


# column B to C ∆ ed to match with new MP style and criteria names
def MP_row_value(MP_Sheet):
    MP_column_A_data = MP_Sheet.values_batch_get('Daily!C:C').get('valueRanges')
    MP_column_A_list = MP_column_A_data[0]
    MP_column_A_list = MP_column_A_list.get('values')
    crit = ['Active supply (on street)'], ['Rides'], ['Ridden vehicles'], ['Revenue (inc. VAT)'], ['Ride Duration (minutes)'], [
        '3PL # collected tasks fulfilled'], ['3PL # deployed tasks fulfilled'], ['3PL # swapped tasks fulfilled'], \
           ["Waiting for parts"], ['FOA # collected tasks fulfilled'], ['FOA # deployed tasks fulfilled'], \
           ['FOA # swapped tasks fulfilled'], ['Backlog'], ['Inflow damaged vehicles for maintenance'], [
        'Outflow (fixed) vehicles, after maintenance']
    if 'Backlog daily change' in MP_column_A_list:
        MP_column_A_list.replace('Backlog daily change', 'Daily Change Backlog')
        """
        NB:
        Before we iterate over the list, replaces Backlog Daily ∆ with Daily Change Backlog.
        The reason: We want to return the index below, related to "Backlog" instead having the posibility to falsely 
        returning "Backlog daily Change".
        """

    row_list = [i for i in crit if i in MP_column_A_list]
    row_indexes = [MP_column_A_list.index(x) for x in row_list]
    row_indexes = [x + 1 for x in row_indexes]
    return row_indexes


def MP_column_value(MP_Sheet):
    MP_row2_data = MP_Sheet.values_batch_get('Daily!2:2').get('valueRanges')
    MP_row2_list = MP_row2_data[0].get('values')[0]
    dropdown_value = timeback.get()
    dropdown_index = dropdown_options.index(dropdown_value)
    today = get_date(dropdown_index)
    if today in MP_row2_list:
        column_index = (MP_row2_list.index(today))
    else:
        print("Item not found in Dataset")
        column_index = "nan"
        messagebox.showerror(message="Dates are not found in 2:2 row / incorrect date formatting")
    return column_index


def open_downloads_folder_path():
    downloads_folder_path = filedialog.askdirectory()
    if downloads_folder_path != "":
        search_value = re.search('dashboard-daily_numbers_for_masterplan', downloads_folder_path)
        try:
            if search_value[0] == 'dashboard-daily_numbers_for_masterplan':
                print(downloads_folder_path)
                messagebox_result = messagebox.askquestion(title="Submit",
                                                           message="This folder will be removed after update. Are you sure?")
                if messagebox_result == "yes":
                    with open("downloads_path_container.yaml", mode='w') as downloads_folder_path_container:
                        yaml.dump(downloads_folder_path, downloads_folder_path_container, indent=2)
                        messagebox.showinfo(message="target folder added")

                else:
                    messagebox.showinfo(message="target folder NOT added")
            else:
                messagebox.showerror("You selected a wrong folder")
        except TypeError:
            messagebox.showerror(message="Folder does not match \n"
                                         "must be called 'dashboard-daily_numbers_for_masterplan'")
    else:
        messagebox.showinfo(message="target folder NOT added")


def read_downloads_folder_path():
    """
    Reads the download folder path from the yaml file that user has been added, and returns the path.
    :returns: the downloads folder path
    """

    try:
        with open("downloads_path_container.yaml", mode='r') as downloads_folder_path_container:
            downloads_folder_path = yaml.load(downloads_folder_path_container, Loader=yaml.FullLoader)
            print(downloads_folder_path)
            return downloads_folder_path

    # except FileNotFoundError:
    # messagebox.showerror(message="folder 'daily_numbers_for_masterplan' 's missing \n"
    # "To add: Click Target folder")
    # downloads_folder_path = ""
    # return downloads_folder_path
    except yaml.YAMLError:
        messagebox.showerror(message="folder 'daily_numbers_for_masterplan' 's missing \n"
                                     "To add: Click Target folder")
        downloads_folder_path = ""
        return downloads_folder_path


def open_cred_filepath():
    cred_filepath = filedialog.askopenfilename(filetypes=[("JSON file", "*.json")])
    print(cred_filepath)
    if cred_filepath != "":
        with open("credentials_path_container.yaml", mode='w') as cred_path_container:
            yaml.dump(cred_filepath, cred_path_container, indent=2)
            messagebox.showinfo(message="credentials loaded")
    else:
        messagebox.showinfo(message="credentials NOT loaded")


def read_cread_filepath():
    try:
        with open("credentials_path_container.yaml", mode='r') as cred_path_container:
            cred_path = yaml.load(cred_path_container, Loader=yaml.FullLoader)
            return cred_path
    except FileNotFoundError:
        messagebox.showerror(message="keys.JSON is missing, Please load credentials or contact the administrator")
        cred_path = 0
        return cred_path
    except yaml.YAMLError:
        messagebox.showerror(message="keys.JSON is missing, Please load credentials or contact the administrator")
        cred_path = 0
        return cred_path


def p_bar():
    progress_bar.start(10)


def run():
    t1 = threading.Thread(target=update)
    t1.start()


def mulitplier_selection():
    switch = scooter_ebike.get()
    if switch == "Scooters":
        multiplier = 1
    else:
        multiplier = 0
    return multiplier


def empty_csv():
    if len(missing_log) != 0:
        missing_csv_message = "CSV file(s) missing from Daily numbers for masterplan " + missing_log \
                              + " Proceed anyway?"
        proceed_csv = messagebox.askquestion(message=missing_csv_message)
        if proceed_csv != "yes":
            root.quit()
            sys.exit()


def update():
    label_indicator.config(text="", bg="#BAE2CD")
    label_indicator.config(text="Please Wait", bg="#BAE2CD")

    sc = pd.read_csv("Master_Plan_links.csv") # read Scooter Cities added
    eb = pd.read_csv("E-Bikes_Master_Plan_links.csv") # read Ebike cities added
    del sc['cityURL'], eb['cityURL'] # drop the URLs
    merged_list = (pd.merge(sc, eb, how='outer')).iloc[:, 0].tolist() # merge SC and EB cities names and add them to a list.
    not_in_revamped_dict = [c for c in merged_list if c not in all_city_ref]  # filter cities that are in the merged list but don't apear in Revamped dictionary
    nird_message = str("The following cities are not in the Revamped dictionary, Please contact COPS. " + str(not_in_revamped_dict))
    # Display message if there are cities missing from the revamped dictionary
    if not_in_revamped_dict != []:
        messagebox.showerror(message=nird_message)
        not_in_revamped_dict.clear() # clear the cities so once user removes the "bad" city it won't be in the list
        label_indicator.config(text="", bg="#BAE2CD") # clear main message label.
        label_indicator.config(text=default_message, bg="#BAE2CD") # Back to default message state.
        return # back to the main.
    i_sites = [c for c in merged_list if c not in sat_cit_list]
    inventory_balance_awfp = get_awfp(df15)   # get inventory balance actual waiting for parts
    inventory_balance_cities = inventory_balance_awfp['ASCII_City'].to_list()
    i_sites_missing = [i for i in i_sites if i not in inventory_balance_cities]
    missing_sites_message = str("The following sites are not in the Actual WFP Daily Data Dump. Please contact COPS. " + str(i_sites_missing))
    if len(i_sites_missing) > 0:
        messagebox.showerror(message=missing_sites_message)
        i_sites_missing.clear()  # clear the cities so once user removes the "bad" city it won't be in the list
        label_indicator.config(text="", bg="#BAE2CD")  # clear main message label.
        label_indicator.config(text=default_message, bg="#BAE2CD")  # Back to default message state.
        return
    local_inv_sites = [i for i in i_sites if i in inventory_balance_cities]
    AWFP = inventory_balance_awfp[inventory_balance_awfp['ASCII_City'].isin(local_inv_sites)] # Actual waiting for parts for the Local inventory site

    ### Map waiting for service
    city_mapping = dict(city_map0) # create dict. of the default revamped dictionary.
    city_mapping = {k: v for k, v in city_mapping.items() if pd.notna(k)} # key value pairs if the key is notNa assign k,v to the dictionary.

    df14.reset_index(drop=True, inplace=True)
    df14['city_mapped'] = pd.Series(df14.iloc[:, 1].values).map(city_mapping).fillna('0')  # create city mapped column

    for i in range(len(df14)):
        if df14.at[i, 'city_mapped'] != '0':
            df14.iat[i, 1] = df14.at[i, 'city_mapped']
    del df14['city_mapped'], df14[df14.columns[0]]

    df14_filtered = df14[(df14.iloc[:, 0] != 'City') & (df14.iloc[:, 0] != 'city')]
    df14_filtered.insert(1, "Backlog", copy.deepcopy(df14_filtered.iloc[:, 1].str.replace(',', '')))
    df14_filtered.drop(df14_filtered.columns[2], axis=1, inplace=True)
    df14_filtered['Backlog'] = df14_filtered['Backlog'].astype(float)
    df14_filtered = df14_filtered.groupby(df14_filtered.columns[0]).sum() # Total backlog per inventory site.
    df14_filtered = df14_filtered.reset_index()
    df14_filtered.insert(0, "Unnamed", value=0)


#_________________________________________________VEHICLE INFLOW________________________________________________________
# Disabled, atm no need to aggregate inflow and outflow per inventory site
    """
    df16['city_mapped'] = pd.Series(df16.iloc[:, 1].values).map(city_mapping).fillna('0')

    for i in range(len(df16)):
        if df16.at[i, 'city_mapped'] != '0':
            df16.iat[i, 1] = df16.at[i, 'city_mapped']
    del df16['city_mapped'], df16[df16.columns[0]]

    for i in range(len(df16)):
        try:
            df16.iat[i, 1] = float(df16.iat[i, 1])
        except ValueError:
            df16.iat[i, 1] = np.nan  # Set the element at row i, column 1 to NaN
    df16.dropna(inplace=True)
    df16_inflow = df16.groupby(df16.columns[0]).sum().reset_index()
    df16_inflow.insert(0, "Unnamed", value=0)
    """

#_____________________________________________END INFLOW_______________________________________________________________

#_____________________________________________VEHICLE OUTFLOW____________________________________________________________
# Disabled, atm no need to aggregate inflow and outflow per inventory site
    """
    df17['city_mapped'] = pd.Series(df17.iloc[:, 1].values).map(city_mapping).fillna('0')  # create city mapped column
    for i in range(len(df17)):
        if df17.at[i, 'city_mapped'] != '0':
            df17.iat[i, 1] = df17.at[i, 'city_mapped']
    del df17['city_mapped'], df17[df17.columns[0]]

    for i in range(len(df17)):
        try:
            df17.iat[i, 1] = float(df17.iat[i, 1])
        except ValueError:
            df17.iat[i, 1] = np.nan  # Set the element at row i, column 1 to NaN

    df17.dropna(inplace=True)
    df17_outflow = df17.groupby(df16.columns[0]).sum().reset_index()
    df17_outflow.insert(0, "Unnamed", value=0)
    """

    # _____________________________________________END VEHICLE OUTFLOW__________________________________________________

    print(check_version_approve())
    if check_version_approve() < 1:
        messagebox.showinfo(message="DErrNO5 e8641d72759eecd7d9461c8443ed2fcd, contact the developer M.")
        root.quit()
        sys.exit()
    empty_csv()
    multiplier = mulitplier_selection()
    print(multiplier, "multiplier ")
    coll_dep_swap_inhouse = cb_in_house_var.get()
    coll_dep_3PL = cb_3PL_var.get()
    cb_bl = cb_Backlog_var.get()
    switch = scooter_ebike.get()
    print(switch)
    select_csv = csv_selector()
    print(select_csv)
    cities_passed = 0
    MP_links_df = pd.read_csv(select_csv)
    number_of_cities_linked = MP_links_df.shape[0]
    all_cities_list = MP_links_df['CityName'].values.tolist()
    print(all_cities_list)
    label_indicator.config(text="", bg="#BAE2CD")
    label_indicator.config(text="Connection OK", bg="#BAE2CD")
    sleep(0.5)
    if all_cities_list == []:
        messagebox.showerror(message="Nothing to update, City list is empty")
    else:
        try:
            if read_downloads_folder_path() != "" and read_cread_filepath != 0 and all_cities_list != []:
                service_account_key = read_cread_filepath()
                gc = gs.service_account(service_account_key)
                t2 = threading.Thread(target=p_bar)
                start_timer = time.process_time()
                label_indicator.config(text="", bg="#BAE2CD")
                while cities_passed < number_of_cities_linked:
                    # print(MP_links_df.iloc[0, 0])
                    CITY_NAME = MP_links_df['CityName'].values[cities_passed]
                    CITY_NAME = CITY_NAME
                    CITY_URL = MP_links_df['cityURL'].values[cities_passed]
                    scooters_deployed = retrieve_values(df0, CITY_NAME)
                    scooters_with_rides = retrieve_values(df1, CITY_NAME)
                    city_rides = retrieve_values(df2, CITY_NAME)
                    city_GMV_passes = retrieve_values(df3, CITY_NAME)
                    print(city_GMV_passes)
                    city_GMV_passes = zeroeuro(city_GMV_passes)
                    city_GMV_without_passes = retrieve_values(df4, CITY_NAME)
                    city_GMV_without_passes = zerocomma(city_GMV_without_passes)
                    city_GMV = replacesign(city_GMV_without_passes) + (multiplier * replaceEuro(city_GMV_passes))
                    ride_duration = retrieve_values(df5, CITY_NAME)
                    swapped_tasks_3PL = retrieve_values(df6, CITY_NAME)
                    collected_tasks_3PL = retrieve_values(df7, CITY_NAME)
                    deployed_tasks_3PL = retrieve_values(df8, CITY_NAME)
                    waiting_for_parts = (retrieve_values(AWFP, CITY_NAME)) * multiplier
                    waiting_for_service = (retrieve_values(df14_filtered, CITY_NAME)) * multiplier
                    collected_tasks_FOA = retrieve_values(df10, CITY_NAME)
                    deployed_tasks_FOA = retrieve_values(df11, CITY_NAME)
                    swapped_tasks_FOA = retrieve_values(df12, CITY_NAME)
                    vehicle_inflow = retrieve_values(df16, CITY_NAME)
                    vehicle_outflow = retrieve_values(df17, CITY_NAME)
                    if multiplier == 0:
                        waiting_for_parts = 0
                        waiting_for_service = 0
                    else:
                        waiting_for_parts = waiting_for_parts
                        waiting_for_service = waiting_for_service
                    print(CITY_NAME, CITY_URL)
                    print(vehicle_inflow)
                    prGreen(waiting_for_service)
                    label_indicator.config(text= "", bg="#BAE2CD")
                    label_indicator.config(text= "In progress: " + CITY_NAME , bg="#BAE2CD")
                    MP_sheet = gc.open_by_url(CITY_URL)
                    column_value = MP_column_value(MP_sheet)
                    row_value = MP_row_value(MP_sheet)
                    MP_WS = MP_sheet.worksheet('Daily')
                    try:
                        MP_WS.update_cell(row_value[0], column_value, scooters_deployed)
                        if cities_passed < 1:
                            t2.start()
                        MP_WS.update_cell(row_value[1], column_value, city_rides)
                        MP_WS.update_cell(row_value[2], column_value, scooters_with_rides)
                        MP_WS.update_cell(row_value[3], column_value, city_GMV)
                        MP_WS.update_cell(row_value[4], column_value, ride_duration)
                        if cb_bl == 1:
                            MP_WS.update_cell(row_value[8], column_value, waiting_for_parts)
                            MP_WS.update_cell(row_value[12], column_value, waiting_for_service)  # Waiting for service = Total Backlog
                            MP_WS.update_cell(row_value[13], column_value, vehicle_inflow)
                            MP_WS.update_cell(row_value[14], column_value, vehicle_outflow)
                        if coll_dep_swap_inhouse == 1 and coll_dep_3PL == 1:
                            MP_WS.update_cell(row_value[5], column_value, collected_tasks_3PL)
                            MP_WS.update_cell(row_value[6], column_value, deployed_tasks_3PL)
                            MP_WS.update_cell(row_value[7], column_value, swapped_tasks_3PL)
                            MP_WS.update_cell(row_value[9], column_value, collected_tasks_FOA)
                            MP_WS.update_cell(row_value[10], column_value, deployed_tasks_FOA)
                            MP_WS.update_cell(row_value[11], column_value, swapped_tasks_FOA)

                        elif coll_dep_swap_inhouse == 0 and coll_dep_3PL == 1:
                            MP_WS.update_cell(row_value[5], column_value, collected_tasks_3PL)
                            MP_WS.update_cell(row_value[6], column_value, deployed_tasks_3PL)
                            MP_WS.update_cell(row_value[7], column_value, swapped_tasks_3PL)

                        elif coll_dep_swap_inhouse == 1 and coll_dep_3PL == 0:
                            MP_WS.update_cell(row_value[9], column_value, collected_tasks_FOA)
                            MP_WS.update_cell(row_value[10], column_value, deployed_tasks_FOA)
                            MP_WS.update_cell(row_value[11], column_value, swapped_tasks_FOA)

                        else:
                            "do nothing"

                        """
                        Row value[x] is always the th element in list "crit"
                        """
                        sleep(5)
                        cities_passed += 1
                    except IndexError as i_err:
                        index_error_message= "One or more metrics are missing from the Masterplan Column C, Ask the developer for instructions. "+ str(i_err)
                        messagebox.showerror(message=index_error_message)
                        root.quit()
                        sys.exit()
                downloads_folder_path = read_downloads_folder_path()
                shutil.rmtree(downloads_folder_path)
                end_timer = time.process_time()
                time_spent_on_update = end_timer - start_timer
                dropdown_value = timeback.get()
                now_time = datetime.datetime.now()
                now_date = now_time.strftime('%Y-%m-%d')
                now_time = now_time.strftime('%H:%M:%S')
                UID = re.sub("[/].*[/]", "", os.path.expanduser('~'))
                cb_var_json['In-house'] = coll_dep_swap_inhouse
                cb_var_json['3PL'] = coll_dep_3PL
                cb_var_json['Backlog'] = cb_bl #checkbox backlog
                with open("coll_dep_swap_container.json", mode='w') as coll_dep_swap_container:
                    json.dump(cb_var_json, coll_dep_swap_container)

                if  cb_var_json['In-house'] == 1 and cb_var_json['3PL'] == 1:
                    cb_log = 1
                elif cb_var_json['In-house'] == 0 and cb_var_json['3PL'] == 0:
                    cb_log = 0
                elif cb_var_json['In-house'] == 0 and cb_var_json['3PL'] == 1:
                    cb_log = "3PL"
                elif cb_var_json['In-house'] == 1 and cb_var_json['3PL'] == 0:
                    cb_log = "In-house"
                else:
                    cb_log = ""

                if UID != "":
                    try:
                        with open("user_ID.yaml", mode='w') as user_id_file:
                            yaml.dump(UID, user_id_file, indent=2)
                    except yaml.parser.ParserError as yml_err:
                        messagebox.showerror(text=yml_err)

                with open(service_account_key, 'r') as service_account_json:
                    service_account_data = json.load(service_account_json)
                    client_email = service_account_data['client_email']
                try:
                    lytics_sheet = gc.open_by_key('1rOh6imkp-nLbnER4n-U7wQnEUhaaVmBZpilceUq56Zk')
                    Lytics_WS = lytics_sheet.worksheet('Data input')
                    cities_with_data = df0_rows - 1
                    Lytics_WS.insert_row([client_email, number_of_cities_linked, cities_passed, cities_with_data,
                                          dropdown_value, time_spent_on_update, now_date,
                                          now_time, switch, App_version, missing_log, UID, cb_log, cb_bl],  2)
                except gspread.exceptions.APIError:
                    messagebox.showerror(message="Credentials are not valid for analytics")
                label_indicator.config(text="", bg="#BAE2CD")
                label_indicator.config(text="Done!", bg="#BAE2CD")
                messagebox.showinfo(message="Update successfull")
                sleep(0.7)
                root.quit()
                sys.exit()
            else:
                print("err found")

        except gspread.exceptions.NoValidUrlKeyFound as nw_url_key:
            messagebox.showerror(message="URL error  \n "
                                         "You need to Clear city list, and Add valid URLs")
            print(nw_url_key)
        except gspread.exceptions.APIError as API_err:
            messagebox.showerror(message="Permission denied,\n "
                                         "your credentials does not have the right accesses. Contact the administrator")
            print(API_err)
            # Added a new line here to exit when the user does not have the right permission
            # TODO: (NEEDS TO BE TESTED)
            sys.exit()
        except FileNotFoundError as file_err:
            file_err = "File is missing or has been moved ", file_err
            messagebox.showerror(message=file_err, )
        except KeyError as keyerr:
            keyerr = "Key error  \n " "You need to Clear city list", keyerr
            messagebox.showerror(message=keyerr)
        except ValueError as Val_err:
            Val_err = "Value error", Val_err
            messagebox.showerror(message= Val_err)
        except google.auth.exceptions.RefreshError:
            messagebox.showerror(message="Your credentials are not valid")


def check_version_approve():
    try:
        with open("credentials_path_container.yaml", mode='r') as cred_path_container:
            cred_path = yaml.load(cred_path_container, Loader=yaml.FullLoader)
            if cred_path != "":
                service_account_key = read_cread_filepath()
                gc = gs.service_account(service_account_key)
                lytics_sheet = gc.open_by_key('1rOh6imkp-nLbnER4n-U7wQnEUhaaVmBZpilceUq56Zk')
                WS_Update = lytics_sheet.worksheet('UPDATE')
                Approved_v = ((WS_Update.get_values("B2")[0])[0])

                return semver.compare(App_version, Approved_v)

            else:
                "Do nothing"

    except ValueError as vr:
        print(vr)
    except gspread.exceptions.APIError as api_err:
        print(api_err)
    except yaml.parser.ParserError as yml_err:
        print(yml_err)
        label_indicator.config(text="Connection Failed.", bg="#BAE2CD")
        messagebox.showerror(message="To Proceed please load credentials")
    except gspread.exceptions.NoValidUrlKeyFound as NoValidUrlKeyFound:
        messagebox.showerror(message=NoValidUrlKeyFound)



def check_update():
    """
    Checks whether the user has the key, and reads the latest available App version from google sheets.
    :returns: Compares the App version with the latest available version and returns the semver value.
    """
    try:
        with open("credentials_path_container.yaml", mode='r') as cred_path_container:
            cred_path = yaml.load(cred_path_container, Loader=yaml.FullLoader)
            if cred_path != "":
                service_account_key = read_cread_filepath()
                gc = gs.service_account(service_account_key)
                lytics_sheet = gc.open_by_key('1rOh6imkp-nLbnER4n-U7wQnEUhaaVmBZpilceUq56Zk')
                WS_Update = lytics_sheet.worksheet('UPDATE')
                latest_available_version = ((WS_Update.get_values("A2")[0])[0])

                return semver.compare(App_version, latest_available_version)

            else:
                "do nothing"
    except ValueError as vr:
        print(vr)
    except gspread.exceptions.APIError as api_err:
        print(api_err)
    except yaml.parser.ParserError as yml_err:
        print(yml_err)
    except gspread.exceptions.NoValidUrlKeyFound as NoValidUrlKeyFound:
        messagebox.showerror(message=NoValidUrlKeyFound)

def check_user():
    try:
        with open("Temp/user_ID.yaml", mode='r') as user_ID_yml:
            user_ID = yaml.load(user_ID_yml, Loader=yaml.FullLoader)
            if user_ID == "" or user_ID == (re.sub("[/].*[/]", "", os.path.expanduser('~'))):
                return "OK"
            else:
                return "not valid"
    except yaml.parser.ParserError as yml_err:
        messagebox.showerror(message="no prevously saved UID" + str(yml_err))

    except FileNotFoundError as old_user_data_missing_err:
        messagebox.showerror(message="User ID can't be verified" + str(old_user_data_missing_err))
        if old_user_data_missing_err == old_user_data_missing_err:
            return "OK"


def csv_selector():
    """
    Select between scooters and E-bikes csv file.
    :returns: the CSV file that user selected via dropdown menu.
    """

    switch = scooter_ebike.get()
    if switch == "Scooters":
        select_csv = 'Master_Plan_links.csv'
    else:
        select_csv = 'E-Bikes_Master_Plan_links.csv'
    return select_csv


def store_data():
    # TODO: check whether whitespace in city name affects the csv file
    #  if so, explicitly throw error when there is space between city names.
    #  Looker has dashes between city names, the same format has to be used.
    #  Also, look for gid in the URL of masterplan.
    #  Give suggestion in a window from the csv files how the cities should be named.
    acity_name = city_name.get()
    print(acity_name)
    acity_link = city_MP_link.get()
    if acity_link == "" or acity_name == "":
        print("Error")
        messagebox.showerror(title="Value Error", message="you forgot to enter all values")
        city_MP_link.set("")
        city_name.set("")
    else:
        messagebox_results = messagebox.askquestion(title="Submit", message="Are you ready to submit?")
        if messagebox_results == "yes":
            print(acity_link, acity_name)
            city_url = "'" + acity_link + "'"
            City_Name_URL_Dict = {'CityName': [acity_name],
                                  'cityURL': [city_url]}
            df_city_URL = pd.DataFrame(City_Name_URL_Dict)
            select_csv = csv_selector()
            df_city_URL.to_csv(select_csv, mode='a', header=False, index=False)
            df_city_name_test = pd.read_csv(select_csv)
            column_values_list = df_city_name_test['CityName'].tolist()
            criteria = acity_name in column_values_list
            print(criteria)
            if criteria == True:
                messagebox.showinfo(message="Values Added")
                city_MP_link.set("")
                city_name.set("")
            else:
                messagebox.showerror(message="Value error  \n "
                                             "You need to Clear city list first")
        else:
            city_MP_link.set("")
            city_name.set("")


def second_window():
    """
    Second window to show the added Master Plans, (by returning the name of the city from the CSV file in a list)
    :returns: a listbox with added cities.
    """

    sec_win = Tk()
    sec_win.geometry('480x198+18+18')
    sec_win.config(bg='#BAE2CD')
    select_csv = csv_selector()
    if select_csv == "E-Bikes_Master_Plan_links.csv":
        sec_win.title("Data Frame Viewer E-Bikes - List of Added Cities")
        select_ID = 0
    else:
        select_ID = 1
        sec_win.title("Data Frame Viewer Scooters - List of Added Cities")
    added_cities = pd.read_csv(select_csv)
    cities_list = added_cities.values.tolist()
    list_of_entries = []
    for x in list(range(0, len(cities_list))):
        list_of_entries.append(cities_list[x][0])
    listbox = Listbox(sec_win)
    for x, y in enumerate(list_of_entries):
        listbox.insert(x, y)
    listbox.grid(row=0, column=0)

    def remove_city():
        try:
            print(select_ID)

            if select_ID == 1:
                csv_df = pd.read_csv("Master_Plan_links.csv")
            else:
                csv_df = pd.read_csv("E-Bikes_Master_Plan_links.csv")

            index = listbox.curselection()[0]
            csv_df = csv_df.drop(index=index)
            print(csv_df)
            if select_ID == 1:
                csv_df.to_csv(r'Master_Plan_links.csv', index=False)
                sec_win.destroy()
                second_window()
            else:
                csv_df.to_csv(r'E-Bikes_Master_Plan_links.csv', index=False)
                sec_win.destroy()
                second_window()
        except IndexError:
            messagebox.showerror(message="City List is empty, nothing to remove")

    remove_button = Button(sec_win, text="Remove City", command=remove_city)
    remove_button.grid(row=1, column=0)


def callback(url):
    webbrowser.open_new_tab(url)


def sop_doc():
    callback("https://sites.google.com/bolt.eu/norwayintranet/management/master-plan-updater")


def about_dev():
    callback("https://no.linkedin.com/in/adam-torkos-4055a4a8")


def third_window():
    history_html = 'file:///' + os.getcwd() + '/' + 'history.html'
    callback(history_html)
    # Does not work with tkinkter somehow
    """
    with open('history.html') as app_history:
        contents = app_history.read()
    third_win = Tk()

    third_win.config(bg='#BAE2CD')
    third_win.title("About Me")

    html_label = HtmlLabel(third_win, text=contents)
    HtmlLabel.set_zoom(html_label, 1.5)
    html_label.pack(fill='both', expand=True)
"""

Settings_ = True

root = Tk()
root.geometry("725x198+2+0")
root.title("Project_M")

# Menubar
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=1)
helpmenu = Menu(menubar, tearoff=1)
filemenu.add_command(label="Import User Data", command=import_user_data)
filemenu.add_command(label="Export User Data", command=save_user_data)
filemenu.add_separator()
filemenu.add_command(label="Import City List", command=import_city_data)
filemenu.add_command(label="Export City List", command=save_city_data)
filemenu.add_separator()
#filemenu.add_command(label="Inflow/Outflow Agg. / Inv Site, Dev. Only", command=in_out_flow)

menubar.add_cascade(label="File", menu=filemenu)


helpmenu.add_command(label="About the Developer ", command=about_dev)
helpmenu.add_command(label="SOP Documentation ", command=sop_doc)
helpmenu.add_command(label="Update History", command=third_window)
menubar.add_cascade(label="Help", menu=helpmenu)

helpmenu.add_separator()






root.config(bg='#BAE2CD', menu=menubar)

# logo_file = 'Logo_.png'

# define variables
city_name = StringVar()
city_MP_link = StringVar()
cred_key = StringVar()
timeback = StringVar()
scooter_ebike = StringVar()
timeback.set("t-1")
dropdown_options = ["t-1", "t-2", "t-3", "t-4", "t-5", "t-6", "t-7"]
boxvar = BooleanVar()
scooter_ebike.set("Scooters")
scooter_ebike_dropdown_options = ["Scooters", "E-bikes"]



def BELOW_():
    global Settings_
    if Settings_ == False:
        root.geometry("725x198+2+0")
        Settings_ = True
    else:
        root.geometry("725x278+2+0")
        Settings_ = False


def csvGenerate_():
    switch = scooter_ebike.get()
    if switch == "Scooters":

        with open('Master_Plan_links.csv', 'w', newline="") as links_csvfile:
            writer = csv.writer(links_csvfile)
            writer.writerow(["CityName", "cityURL"])
            messagebox.showinfo(message="Scooter City list cleared")

    elif switch == "E-bikes":
        with open('E-Bikes_Master_Plan_links.csv', 'w', newline="") as links_csvfile:
            writer = csv.writer(links_csvfile)
            writer.writerow(["CityName", "cityURL"])
            messagebox.showinfo(message="E-bikes City list cleared")





def about_dialog():
    root.tk.call('tk::mac::standardAboutPanel')


def tick():
    Txt = Label(text="MasterPlan Updater", font=("helvetica", 25, "bold",), bg=("#BAE2CD"))
    dev = Label(text="@Adam Torkos", font=("helvetica", 12), bg=("#BAE2CD"), cursor="hand2")
    dev.bind("<Button-1>",
             lambda e: callback("mailto:adam.torkos@bolt.eu?cc=adam.torkos@me.com&subject=Master%20Plan%20Updater"))
    Txt.grid(row=1, column=1)
    dev.grid(row=1, column=3)
    Button_1.grid(row=2, column=2, sticky=E, padx=10)
    Button_2.grid(row=2, column=3, sticky=E, padx=10)
    Button_3.grid(row=3, column=1, padx=10, pady=10)
    lbl_city = Label(text="Enter city Name", font=("helvetica", 12, "italic",), bg=("#BAE2CD"))
    lbl_city.grid(row=8, column=2)
    entry_city.grid(row=8, column=3)
    lbl_link = Label(text="Enter MP's link here", font=("helvetica", 12, "italic",), bg=("#BAE2CD"))
    lbl_link.grid(row=9, column=2)
    entry_link.grid(row=9, column=3)
    Button_Store.grid(row=10, column=3, padx=10)
    progress_bar.grid(row=2, column=1, pady=10, padx=10)
    Button_downloads_folder.grid(row=5, column=1, padx=10, pady=10)
    open_credentials.grid(row=4, column=1, padx=10, pady=10)
    browse_button.grid(row=3, column=3, padx=20, pady=0)
    dropdown.grid(row=3, column=2, padx=0, pady=10)
    scooter_ebike_dropdown.grid(row=4, column=2, padx=0, pady=10)
    cb_inhouse.grid(column=3, row=4)
    cb_3PL.grid(column=3, row=5)
    cb_Backlog.grid(row=5, column=2, padx=0, pady=10)
    label_indicator.config(text=default_message, bg="#BAE2CD")
    label_indicator.grid(column=2, row=1)

    try:
        if check_update() < 0:
            messagebox.showinfo(message="Update available \n"
                                        "Export your user data before update!")
            callback("https://drive.google.com/drive/folders/1UBO98m8vKMXLdJaL4Zw4nw0GjOMfEvMo?usp=sharing")
    except TypeError as TypeErr:
        print(TypeErr)


root.createcommand('tkAboutDialog', about_dialog)
Button_2 = Button(root, bg='#111111', fg='#111111', text=str(' ' * 2 + 'Edit Master Plan List' + ' ' * 2),
                  command=BELOW_)
Button_1 = Button(root, fg='#111111', text=str(' ' * 2 + 'Update Master Plans' + ' ' * 2), command=run)
Button_3 = Button(root, fg='#111111', text=str(' ' * 2 + 'Clear city List' + ' ' * 2), command=csvGenerate_)
Button_Store = Button(root, fg='#111111', text=str(' ' * 2 + 'Store Data' + ' ' * 2), command=store_data)
entry_city = Entry(root, fg='#111111', textvariable=city_name)
entry_link = Entry(root, fg='#111111', textvariable=city_MP_link)
progress_bar = tkinter.ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')
Button_downloads_folder = Button(root, fg='#111111', text=str(' ' * 2 + 'Target folder' + ' ' * 2),
                                 command=open_downloads_folder_path)
open_credentials = Button(root, fg='#111111', text=str(' ' * 2 + 'Load credentials' + ' ' * 2),
                          command=open_cred_filepath)
row_button = Button(root, fg='#111111', text=str(' ' * 2 + 'row test' + ' ' * 2), command=MP_row_value)
browse_button = Button(root, fg='#111111', text=str(' ' * 2 + 'View city list' + ' ' * 2), command=second_window)
dropdown = OptionMenu(root, timeback, *dropdown_options)
scooter_ebike_dropdown = OptionMenu(root, scooter_ebike, *scooter_ebike_dropdown_options)
cb_var = IntVar()
cb_in_house_var = IntVar()
cb_3PL_var = IntVar()
cb_Backlog_var = IntVar()


cb_var.set(0 if cb_var_yaml == 0 else 1)
cb_3PL_var.set(0 if cb_var_3PL == 0 else 1)
cb_in_house_var.set(0 if cb_var_in_house == 0 else 1)
cb_Backlog_var.set(0 if cb_var_Backlog == 0 else 1)

def cb_change(read_value, write_value):
    if read_value ==0:
        write_value.set(0)
    else:
        write_value.set(1)


cb_inhouse = Checkbutton(root, text="Coll.Dep.Swap In-house", variable=cb_in_house_var, onvalue=1, offvalue=0)
cb_3PL = Checkbutton(root, text="Coll.Dep.Swap 3PL", variable=cb_3PL_var, onvalue=1, offvalue=0)
cb_Backlog = Checkbutton(root, text="Backlog Inflow Outflow", variable=cb_Backlog_var, onvalue=1, offvalue=0)
label_indicator = tkinter.Label(root)
label_indicator.grid(row=1, column=2)

tick()
root.mainloop()
