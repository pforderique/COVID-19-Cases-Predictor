##########################################
# COVID-19 Cases Predictor 
#
# Purpose: To show COVID-19 cases and predict using 
#           regression models
# @author Piero Orderique
#
# TODO:
#   1) Add combo functionality for state and local level.
#   2) Figure out how to display graphs AND add a WORKING navigation bar... first 2 attempts failed
#   3) Implement the machine learning part into program
##########################################

import pandas as pd
import numpy as np
from tkinter import Tk, Label, PhotoImage
from tkinter.ttk import Combobox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

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
canvas = None
toolbar = None
ax = None 
POP_NORM_NAT = 100000 #population normal for cases
POP_NORM_STATE = 10000
POP_NORM_COUNTY = 1000
INITIAL_DATE = ''
GRAPH_TITLE = ''

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
    graphWindow = Tk()
    graphWindow.title('COVID-19 Tracker')
    graphWindow.geometry('1220x700')
    graphWindow.config(bg=DARK_BURGANDY)
    icon = PhotoImage(file ='images\COVID-19-virus.png')
    graphWindow.iconphoto(False, icon)

    #labels
    lbl_main = Label(text=graphType+" Data", font=("Times New Roman",42),bg=DARK_BURGANDY,fg='white',padx=0)
    lbl_main.place(relx=0.05,rely=0.03)
    #show no chart initially
    noChart = PhotoImage(file ='images/NoChartImage.png')
    noChartLbl = Label(image=noChart)
    noChartLbl.image = noChart #DOING THIS keeps a reference to the tkinter object - now the picture shows!
    noChartLbl.place(relx=0.05, rely=0.2)
    
    #chart display logic
    global GRAPH_TITLE
    global INITIAL_DATE
    if graphType == "National":
        INITIAL_DATE = "2020-Jan-21"
        df['days_since_'+INITIAL_DATE] = df.index
        #creating initial plot
        figure = Figure(figsize=(8,5.8), dpi=90)
        figure.patch.set_facecolor(LIGHT_BEIGE)
        ax = figure.add_subplot(111)
        ax.scatter(df['days_since_'+INITIAL_DATE],df['cases'],color='blue')
        GRAPH_TITLE = "USA COVID-19 Cases"
        ax.set_title(GRAPH_TITLE)
        ax.set_xlabel('Days since January 21st')
        ax.set_ylabel('Cases per '+str(POP_NORM_NAT))
        #embedding
        canvas = FigureCanvasTkAgg(figure, graphWindow)
        canvas.draw()
        canvas.get_tk_widget().place(relx=0.05,rely=0.2)  
    elif graphType == "State":
        #choosing state
        lbl2 = Label(text="Choose Display:", font=("Times New Roman",12),bg=LIGHT_BEIGE,fg=DARK_GREY)
        lbl2.place(relx=0.05,rely=0.16)
        comboValues_state = ['Select a State']+sorted(df.state.unique().tolist())
        combo_state = Combobox(graphWindow,values=comboValues_state,state="readonly",width=32)
        combo_state.place(relx=0.15,rely=0.165)
        combo_state.current(0)
        def comboFunc_state(event):
            myState = combo_state.get()
            if myState != "Select a State":
                global main_df
                global ax
                global INITIAL_DATE
                global GRAPH_TITLE
                ax = None
                main_df = None
                main_df = df[df.state == myState]
                INITIAL_DATE = main_df['date'].iloc[0] # not all states started recording on same date
                main_df['days_since_'+INITIAL_DATE] = list(range(0, len(main_df)))
                lbl_main.config(text=myState+' Data') #change label text
                #creating initial plot
                figure = Figure(figsize=(8,5.8), dpi=90)
                figure.patch.set_facecolor(LIGHT_BEIGE)
                ax = figure.add_subplot(111)
                ax.scatter(main_df['days_since_'+INITIAL_DATE],main_df['cases'],color='blue')
                GRAPH_TITLE = myState+" COVID-19 Cases"
                ax.set_title(GRAPH_TITLE)
                ax.set_xlabel('Days since '+INITIAL_DATE)
                ax.set_ylabel('Cases per '+str(POP_NORM_STATE))
                #embedding
                global canvas
                canvas = None
                canvas = FigureCanvasTkAgg(figure, graphWindow)
                canvas.draw()
                canvas.get_tk_widget().place(relx=0.05,rely=0.2)
                #toolbar
                global toolbar
                try:
                    toolbar.destroy()
                except:
                    pass
                toolbar = NavigationToolbar2Tk(canvas, graphWindow)
                toolbar.update()
        combo_state.bind("<<ComboboxSelected>>", comboFunc_state)

def createDataFrame(data):
    if data == "National":
        df = pd.read_csv(NYT_US, error_bad_lines=False)
        df['time_since_Jan21'] = df.index
        #scale down cases
        df['cases'] /= POP_NORM_NAT #cases = new cases
        return df
    elif data == "State":
        df = pd.read_csv(NYT_states, error_bad_lines=False)
        #scale down cases 
        df['cases'] /= POP_NORM_STATE #cases = new cases
        return df
    elif data == "County":
        df = pd.read_csv(NYT_counties, error_bad_lines=False)
        #scale down cases 
        df['cases'] /= POP_NORM_COUNTY #cases = new cases
        return df
    return None

if __name__ == "__main__":
    startupScreen()