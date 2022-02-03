import json
import time
import tkinter.ttk
import zipfile
from tkinter import *
import csv
from tkinter import messagebox
from time import sleep
import google.auth.exceptions
import gspread.exceptions
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

App_version = "2.0.5"
App_code = "RDA1XC"

try:
    df0 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/average_daily_active_vehicles_on_the_street.csv")
#   gets the value of average number of scooter deployed
    df0 = df0.fillna(float(0))
    shape_df0 = df0.shape #  shape of df3 ( instance : tuple)
    df0_rows = int(shape_df0[0])
    #df_check = 1/int(df0_rows)
except FileNotFoundError:
    messagebox.showerror(message="the daily numbers for masterplan is not exsist in the downloads folder")
    sys.exit()
#except ZeroDivisionError:
    #messagebox.showerror(message="The CSV file does not contain any Cities")
    #sys.exit()


df1 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/average_daily_vehicles_with_1+_trips.csv")
#gets the value of scooters with rides in respect of the corresponding city
df1 = df1.fillna(float(0))
shape_df1 = df1.shape

df2 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/rides.csv")
df2 = df2.fillna(float(0))
shape_df2 = df2.shape


df3 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/gmv_from_passes.csv")
# changes NaN values to €0.0
df3 = df3.fillna("€0.0")
shape_df3 = df3.shape #  shape of df3 ( instance : tuple)
df3_rows = int(shape_df3[0])


    #retives  GMV without passes
df4 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/gmv_(without_passes).csv")
df4 = df4.fillna("0")
shape_df4 = df4.shape

#average order duration df5
df5 = pd.read_csv("~/Downloads/dashboard-daily_numbers_for_masterplan/average_order_duration,_minutes.csv")
df5 = df5.fillna("0")


today = date.today()

locker = "19StayHungryStayFoolish84"

def save_user_data():
    """
    Creates an an encrypted zip file of the user data, if a user has 20-30 or even more cities, it might become time
    consuming to add the cities to the list again.
    The encrypted zip file contains all the previously saved data of the user.
    User can choose where to save the file and the save option is available from the menu bar.
    :returns: The encrypted zip file
    """
    save_path = filedialog.askdirectory()
    if save_path != "":
        save_path = save_path+ "/user_data.zip"
        pyminizip.compress_multiple([os.path.join(os.getcwd(),
                                                  'downloads_path_container.yaml'),
                                     os.path.join(os.getcwd(), 'credentials_path_container.yaml'),
                                     os.path.join(os.getcwd(), 'E-Bikes_Master_Plan_links.csv'),
                                                  os.path.join(os.getcwd(),'Master_Plan_links.csv')],
                                    [u'/', u'/', u'/', u'/'], save_path, locker, 0)
        messagebox.showinfo(message="User data saved")
    else:
        messagebox.showinfo(message=" User data not saved")




def import_user_data():
    """
    Loads the user data from the encrypted zip file.
    User can load the data from the menu bar.
    :returns: Replaces the program's default files by the the previously saved files.
    """
    import_path = filedialog.askopenfilename(filetypes=[('Zip File', '*.zip')])
    if import_path != "":
        with zipfile.ZipFile(import_path, 'r') as user_data_zip:
            user_data_zip.extractall(pwd=locker.encode())
        messagebox.showinfo(message="User Data successfully loaded")
        os.remove(import_path)
    else:
        messagebox.showinfo(message=" User data not loaded")



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
    Retruns the values from the dataframes that mathces with the conditions.
    :param df: dataframe generated by panda from the csv files.
    :param city: A city from the added cities list.
    :returns: the coressponding value from the datafram that mathces with the city
    """

    select_csv = csv_selector()
    MP_links_df = pd.read_csv(select_csv)
    all_cities_list = MP_links_df['CityName'].values.tolist()
    """∆- ed the Dynamic Timeframe to the first row since, it is not standardized by looker (For ex: Slovakia)"""
    #df_first_col = df[:, 1].values.tolist()
    df_first_col = df.iloc[:, 1].tolist()
    #df_first_col = df['Dynamic Timeframe'].values.tolist()
    active_cities_list = [i for i in all_cities_list if i in df_first_col]
    cities_indexes = [df_first_col.index(x) for x in active_cities_list]
    cities_dictionary = dict(zip(active_cities_list, cities_indexes))
    df_row = cities_dictionary.get(city, -1)
    if df_row < 0:
        values = 0
    else:
        values = df.iat[df_row, 2]
    return values



# column B to C ∆ ed to match with new MP style and criteria names
def MP_row_value(MP_Sheet):
    MP_column_A_data = MP_Sheet.values_batch_get('Daily!C:C').get('valueRanges')
    MP_column_A_list = MP_column_A_data[0]
    MP_column_A_list = MP_column_A_list.get('values')
    crit =['Active supply (on street)'], ['Rides'], ['Ridden vehicles'], ['Revenue'], ['Ride Duration (minutes)']
    row_list = [i for i in crit if i in MP_column_A_list]
    row_indexes = [MP_column_A_list.index(x) for x in row_list]
    row_indexes = [x+1 for x in row_indexes]
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
        messagebox.showerror("Dates are not found in 2:2 row")
    return column_index


def open_downloads_folder_path():
    downloads_folder_path = filedialog.askdirectory()
    if downloads_folder_path != "":
        search_value = re.search('dashboard-daily_numbers_for_masterplan', downloads_folder_path)
        try:
            if search_value[0] =='dashboard-daily_numbers_for_masterplan':
                print(downloads_folder_path)
                messagebox_result = messagebox.askquestion(title="Submit", message="This folder will be removed after update. Are you sure?")
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

    #except FileNotFoundError:
        #messagebox.showerror(message="folder 'daily_numbers_for_masterplan' 's missing \n"
                                     #"To add: Click Target folder")
        #downloads_folder_path = ""
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
            yaml.dump(cred_filepath,cred_path_container,indent=2)
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


def update():
    switch = scooter_ebike.get()
    select_csv = csv_selector()
    cities_passed = 0
    MP_links_df = pd.read_csv(select_csv)
    number_of_cities_linked = MP_links_df.shape[0]
    all_cities_list = MP_links_df['CityName'].values.tolist()
    print(all_cities_list)
    if all_cities_list == []:
        messagebox.showerror(message="Nothing to update, City list is empty")
    else:
        try:
            if read_downloads_folder_path() != "" and read_cread_filepath != 0 and all_cities_list != []:
                service_account_key = read_cread_filepath()
                gc = gs.service_account(service_account_key)
                t2 = threading.Thread(target=p_bar)
                start_timer = time.process_time()
                while cities_passed < number_of_cities_linked:
                    # print(MP_links_df.iloc[0, 0])
                    CITY_NAME = MP_links_df['CityName'].values[cities_passed]
                    CITY_NAME = CITY_NAME
                    CITY_URL = MP_links_df['cityURL'].values[cities_passed]
                    scooters_deployed = retrieve_values(df0, CITY_NAME)
                    scooters_with_rides = retrieve_values(df1, CITY_NAME)
                    city_rides = retrieve_values(df2, CITY_NAME)
                    city_GMV_passes = retrieve_values(df3, CITY_NAME)
                    city_GMV_passes = zeroeuro(city_GMV_passes)
                    city_GMV_without_passes = retrieve_values(df4, CITY_NAME)
                    city_GMV_without_passes = zerocomma(city_GMV_without_passes)
                    city_GMV = replacesign(city_GMV_without_passes) + replaceEuro(city_GMV_passes)
                    ride_duration = retrieve_values(df5, CITY_NAME)
                    print(CITY_URL)
                    MP_sheet = gc.open_by_url(CITY_URL)
                    column_value = MP_column_value(MP_sheet)
                    row_value = MP_row_value(MP_sheet)
                    MP_WS = MP_sheet.worksheet('Daily')
                    MP_WS.update_cell(row_value[0], column_value, scooters_deployed)
                    if cities_passed < 1:
                        t2.start()
                    MP_WS.update_cell(row_value[1], column_value, city_rides)
                    MP_WS.update_cell(row_value[2], column_value, scooters_with_rides)
                    MP_WS.update_cell(row_value[3], column_value, city_GMV)
                    MP_WS.update_cell(row_value[4], column_value, ride_duration)
                    """
                    Row value[x] is always the th elemnt in list "crit"
                    """
                    sleep(5)
                    cities_passed += 1
                downloads_folder_path = read_downloads_folder_path()
                shutil.rmtree(downloads_folder_path)
                end_timer = time.process_time()
                time_spent_on_update = end_timer - start_timer
                dropdown_value = timeback.get()
                now_time = datetime.datetime.now()
                now_date =now_time.strftime('%Y-%m-%d')
                now_time = now_time.strftime('%H:%M:%S')
                with open(service_account_key, 'r') as service_account_json:
                    service_account_data = json.load(service_account_json)
                    client_email = service_account_data['client_email']
                try:
                    lytics_sheet = gc.open_by_key('1rOh6imkp-nLbnER4n-U7wQnEUhaaVmBZpilceUq56Zk')
                    Lytics_WS = lytics_sheet.worksheet('Data input')
                    cities_with_data = df0_rows-1
                    Lytics_WS.insert_row([client_email, number_of_cities_linked, cities_passed, cities_with_data,
                                          dropdown_value, time_spent_on_update, now_date,
                                          now_time, switch, App_version], 2)
                except gspread.exceptions.APIError:
                    messagebox.showerror(message="Credentials are not valid for analytics")
                messagebox.showinfo(message="Update successfull")
                sleep(0.7)
                root.quit()
                sys.exit()
            else:
                print("err found")

        except gspread.exceptions.NoValidUrlKeyFound:
            messagebox.showerror(message="URL error  \n "
                                     "You need to Clear city list, and Add valid URLs")
        except gspread.exceptions.APIError:
            messagebox.showerror(message="Permission denied,\n " 
                                         "your credentials does not have the right accesses. Contact the administrator")
#Added a new line here to exit when the user does not have the right permission
# TODO: (NEEDS TO BE TESTED)
            sys.exit()
        except FileNotFoundError as file_err:
            file_err = "File is missing or has been moved ", file_err
            messagebox.showerror(message=file_err,)
        except KeyError as keyerr:
            keyerr = "Key error  \n " "You need to Clear city list", keyerr
            messagebox.showerror(message=keyerr )
        except ValueError:
            messagebox.showerror(message="keys.JSON is missing, Please load credentials or contact the administrator")
        except google.auth.exceptions.RefreshError:
            messagebox.showerror(message="Your credentials are not valid")



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









Settings_ = True

root = Tk()
root.geometry("725x198+2+0")
root.title("Project_M")

# Menubar
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=1)
filemenu.add_command(label="Import User Data", command=import_user_data)
filemenu.add_command(label="Export User Data", command=save_user_data)
filemenu.add_separator()
menubar.add_cascade(label="File", menu=filemenu)

root.config(bg='#BAE2CD', menu=menubar)



#logo_file = 'Logo_.png'

#define variables
city_name = StringVar()
city_MP_link = StringVar()
cred_key = StringVar()
timeback = StringVar()
scooter_ebike = StringVar()
timeback.set("t-1")
dropdown_options = ["t-1", "t-2", "t-3", "t-4"]
boxvar = BooleanVar()
scooter_ebike.set("Scooters")
scooter_ebike_dropdown_options = ["Scooters", "E-bikes"]

def BELOW_ ():

    global Settings_
    if Settings_== False:
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


def callback(url):
    webbrowser.open_new_tab(url)

def about_dialog():
    root.tk.call('tk::mac::standardAboutPanel')

def tick():
    Txt = Label(text = "Master Plan Updater", font=("helvetica", 25, "bold",), bg=("#BAE2CD"))
    dev = Label(text ="@Adam Torkos",font=("helvetica",12), bg=("#BAE2CD"), cursor="hand2")
    dev.bind("<Button-1>", lambda e: callback("mailto:adam.torkos@bolt.eu?cc=adam.torkos@me.com&subject=Master%20Plan%20Updater"))
    Txt.grid(row=1, column=1)
    dev.grid(row=1, column=3)
    Button_1.grid(row=2, column=2, sticky=E, padx=10)
    Button_2.grid(row=2, column=3, sticky=E, padx=10)
    Button_3.grid(row=3, column=1, padx=10, pady=10)
    lbl_city = Label(text="Enter city Name",font=("helvetica", 12, "italic",), bg=("#BAE2CD"))
    lbl_city.grid(row=8, column=2)
    entry_city.grid(row=8, column=3)
    lbl_link = Label(text="Enter MP's link here",font=("helvetica", 12, "italic",), bg=("#BAE2CD"))
    lbl_link.grid(row=9, column=2)
    entry_link.grid(row=9, column=3)
    Button_Store.grid(row=10, column=3, padx=10)
    progress_bar.grid(row=2, column=1, pady=10, padx=10)
    Button_downloads_folder.grid(row=5, column=1, padx=10, pady=10)
    open_credentials.grid(row=4, column=1, padx=10, pady=10)
    browse_button.grid(row=3, column=3, padx=20, pady=0)
    dropdown.grid(row=3, column=2, padx=0, pady=10)
    scooter_ebike_dropdown.grid(row=4, column=2, padx=0, pady=10)

root.createcommand('tkAboutDialog', about_dialog)
Button_2 = Button(root, bg='#111111', fg='#111111', text=str(' ' * 2 + 'Edit Master Plan List' + ' ' * 2), command=BELOW_)
Button_1 = Button(root, fg='#111111', text=str(' ' * 2 + 'Update Master Plans' + ' ' * 2), command=run)
Button_3 = Button(root, fg='#111111', text=str(' ' * 2 + 'Clear city List' + ' ' * 2), command=csvGenerate_)
Button_Store = Button(root, fg='#111111', text=str(' ' * 2 + 'Store Data' + ' ' * 2), command=store_data)
entry_city = Entry(root, fg='#111111', textvariable=city_name)
entry_link = Entry(root, fg='#111111', textvariable=city_MP_link)
progress_bar = tkinter.ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')
Button_downloads_folder = Button(root , fg='#111111', text=str(' ' * 2 + 'Target folder' + ' ' * 2),command=open_downloads_folder_path)
open_credentials = Button(root, fg='#111111', text=str(' ' * 2 + 'Load credentials' + ' ' * 2), command=open_cred_filepath)
row_button = Button(root, fg='#111111', text=str(' ' * 2 + 'row test' + ' ' * 2), command=MP_row_value)
browse_button = Button(root, fg='#111111', text=str(' ' * 2 + 'Browse city list' + ' ' * 2), command=second_window)
dropdown = OptionMenu(root, timeback, *dropdown_options)
scooter_ebike_dropdown = OptionMenu(root, scooter_ebike, *scooter_ebike_dropdown_options)

tick()
root.mainloop()
