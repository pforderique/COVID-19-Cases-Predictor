##########################################
# COVID-19 Cases Predictor 
#
# Purpose: To show COVID-19 cases and predict using 
#           regression models
# @author Piero Orderique
#
# TODO:
#   1) research more about tkinter. 
#   2) Practice reading in data from google on jupyter
#   3) Start building basic startup GUI
#   4) Figure out how to display graphs
#   5) Implement the machine learning part into program
##########################################

import pandas as pd
import numpy as np
from tkinter import Tk, Label, PhotoImage
from tkinter.ttk import Combobox

#New York Times Data 
NYT_US = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
NYT_states = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
NYT_counties = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

print("\nApp Started.\n")

#theme colors
BURGANDY = '#630019'
DARK_BURGANDY = '#3d0110'
LIGHT_BEIGE = '#e6c88e'
DARK_GREY = '#454545'

main_df = None # holds USA or individual df of choice
state_df = None #holds ALL states
county_df = None #hold ALL counties

def startupScreen():
    #window
    startWindow = Tk()
    startWindow.title('COVID-19 Tracker')
    startWindow.geometry('600x370')
    startWindow.config(bg=DARK_BURGANDY)
    icon = PhotoImage(file ='images\COVID-19-virus-white.png')
    startWindow.iconphoto(False, icon)

    #window title
    titleLabel = Label(startWindow, text="COVID-19 Cases Predictor", font=("Times New Roman Bold", 25),bg=DARK_BURGANDY,fg='white')
    titleLabel.pack(pady=10)#grid(column=0, row=0, padx=13,pady=10)
    
    #logo
    main_image = PhotoImage(file ='images\COVID-19-virus.png')
    main_image_lbl = Label(image=main_image)
    main_image_lbl.image = main_image
    main_image_lbl.place(relx=0.04, rely=0.2)

    #Select Data
    lbl_combo = Label(startWindow, text="Select Data:", font=("Times New Roman Bold", 18),bg=DARK_BURGANDY,fg='white')
    lbl_combo.place(relx=0.55,rely=0.4)
    comboValues = ['Select Data','USA NATIONAL DATA','USA STATES DATA','USA COUNTIES DATA']
    combo = Combobox(startWindow,values=comboValues,state="readonly",width=35)
    combo.place(relx=0.55,rely=0.5)
    combo.current(0)
    def comboFunc(event):
        if combo.get() == comboValues[1]:
            startWindow.destroy()
            loadingScreen("National")
        elif combo.get() == comboValues[2]:
            startWindow.destroy()
            loadingScreen("State")
        elif combo.get() == comboValues[3]:
            startWindow.destroy()
            loadingScreen("County")
    combo.bind("<<ComboboxSelected>>", comboFunc)
    startWindow.mainloop()

def loadingScreen(graphType):
    #start loading page
    loadingWindow = Tk()
    loadingWindow.title('Data Collection Page')
    loadingWindow.geometry('385x50')
    loadingWindow.config(bg=DARK_BURGANDY)
    icon = PhotoImage(file ='images\COVID-19-virus-white.png')
    loadingWindow.iconphoto(False, icon)

    #title
    titleLabel = Label(loadingWindow, text="Loading Data...", font=("Times New Roman Bold", 14),bg=DARK_BURGANDY,fg='white')
    titleLabel.grid(column = 0, row=0, padx=12,pady=12)
    #shows FIRST, then tries to load in the data!
    titleLabel.wait_visibility()
    titleLabel.update_idletasks()
    #make df
    if graphType == "National":
        global main_df
        main_df = createDataFrame("National")
        loadingWindow.destroy()
        graphScreen(main_df, "National")
    elif graphType == "State":
        global state_df
        state_df = createDataFrame("State")
        loadingWindow.destroy()
        graphScreen(state_df, "State")
    elif graphType == "County":
        global county_df
        county_df = createDataFrame("County")
        loadingWindow.destroy()
        graphScreen(county_df, "County")

def graphScreen(df, graphType):
    pass

def createDataFrame(data):
    pass

if __name__ == "__main__":
    startupScreen()