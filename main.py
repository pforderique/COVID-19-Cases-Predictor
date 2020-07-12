##################################################################################
##                             COVID-19 Cases Predictor                         ##
##                                                                              ##
## Purpose: To show COVID-19 cases and predict casez using regression models    ##
##                                                                              ##
## @author Piero Orderique                                                      ##
##                                                                              ##
##################################################################################

import pandas as pd
import numpy as np
from tkinter import Tk, Label, PhotoImage, Button, BOTH, TOP, NORMAL, DISABLED
from tkinter.ttk import Combobox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
from sklearn import linear_model as lm

#New York Times Data 
NYT_US = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'
NYT_states = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
NYT_counties = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

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

    #regression 
    lbl_regr = Label(text="Run Regression Model:", font=("Times New Roman",20),bg=DARK_BURGANDY,fg='white')
    lbl_regr.place(relx=0.71,rely=0.22)
    def runRegression():
        btn_regression.config(state=DISABLED,bg='grey')
        global main_df
        global INITIAL_DATE
        global GRAPH_TITLE

        #creating the training and testing data sets 
        mask = np.random.rand(len(main_df)) < 0.8
        train = main_df[mask]
        test = main_df[~mask]

        #training and testing arrays
        xtrain = np.asanyarray(train[['days_since_'+INITIAL_DATE]])
        ytrain = np.asanyarray(train[['cases']])
        xtest = np.asanyarray(test[['days_since_'+INITIAL_DATE]])
        ytest = np.asanyarray(test[['cases']])
             
        #We specifiy the degree for our model
        DEGREE = 4 #getBestDegree(train_x, train_y, test_x, test_y) #--FAILED METHOD: Best degree is always the largest in range
        poly = PolynomialFeatures(degree=DEGREE)
        xtrain_poly = poly.fit_transform(xtrain) 

        #fit_transform makes our coeffecients look like they're from a mulitple linear regression, so we use a linear regression!
        clf = lm.LinearRegression()
        y_fit = clf.fit(xtrain_poly, ytrain)

        #create data
        extendedDomain = len(main_df)*1.2 #plot 1/5 more of available values
        XX = np.arange(0.0, extendedDomain, 0.1) 
        yy = clf.intercept_[0]
        for n in range(DEGREE+1):
            yy+= clf.coef_[0][n]*np.power(XX, n)

        #Evaluation
        xtest_poly = poly.fit_transform(xtest)
        ytest_predict = clf.predict(xtest_poly)
        eval_lbl  = Label(text="Regression Data: ",font=("Times New Roman",18),bg=DARK_BURGANDY,fg="white",padx=3,pady=3)
        eval_lbl1 = Label(text="Degree Chosen: %i" % DEGREE,font=("Times New Roman",15),bg=DARK_BURGANDY,fg="white",padx=3,pady=3)
        eval_lbl2 = Label(text="Mean absolute error: %.2f" % np.mean(np.absolute(ytest_predict - ytest)),font=("Times New Roman",15),bg=DARK_BURGANDY,fg="white",padx=3,pady=3)
        eval_lbl3 = Label(text="Residual sum of squares (MSE): %.2f" % np.mean((ytest_predict - ytest) ** 2),font=("Times New Roman",15),bg=DARK_BURGANDY,fg="white",padx=3,pady=3)
        eval_lbl4 = Label(text="R2-score: %.2f" % r2_score(ytest_predict , ytest),font=("Times New Roman",15),bg=DARK_BURGANDY,fg="white",padx=3,pady=3)
        eval_lbl.place(relx=0.7, rely=0.52)
        eval_lbl1.place(relx=0.7, rely=0.58)
        eval_lbl2.place(relx=0.7, rely=0.62)
        eval_lbl3.place(relx=0.7, rely=0.66)
        eval_lbl4.place(relx=0.7, rely=0.7)

        #plot regression model
        figure = Figure(figsize=(8,5.8), dpi=90)
        figure.patch.set_facecolor(LIGHT_BEIGE)
        ax = figure.add_subplot(111)
        ax.plot(XX, yy, '-r' )
        ax.scatter(main_df['days_since_'+INITIAL_DATE], main_df['cases'], color='blue')
        ax.set_title(GRAPH_TITLE)
        ax.set_xlabel('Days since '+INITIAL_DATE)
        if graphType == "National": 
            ax.set_ylabel('Cases per '+str(POP_NORM_NAT))
        elif graphType == "State":
            ax.set_ylabel('Cases per '+str(POP_NORM_STATE))
        elif graphType == "County":
            ax.set_ylabel('Cases per '+str(POP_NORM_COUNTY))
        #embedding
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
    btn_regression = Button(graphWindow, text="Run",command=runRegression, bg=LIGHT_BEIGE,fg=DARK_GREY,font=("Times New Roman", 18))
    btn_regression.place(relx=0.8,rely=0.3)
    
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
            btn_regression.config(state=NORMAL,bg=LIGHT_BEIGE,fg=DARK_GREY) #re-enables regression button
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
    elif graphType == "County":
        #choosing state
        lbl2 = Label(text="Choose Display:", font=("Times New Roman",12),bg=LIGHT_BEIGE,fg=DARK_GREY)
        lbl2.place(relx=0.05,rely=0.16)
        comboVals_county_state = ['Select a State']+sorted(df.state.unique().tolist())
        combo_county1 = Combobox(graphWindow,values=comboVals_county_state,state="readonly",width=32)
        combo_county1.place(relx=0.15,rely=0.165)
        combo_county1.current(0)
        def comboFunc_county_state(event):
            myState = combo_county1.get()
            if myState != "Select a State":
                global main_df
                main_df = None
                main_df = df[df.state == myState]
                comboVals_county_county = ['Select a County']+sorted(main_df.county.unique().tolist())
                combo_county2 = Combobox(graphWindow,values=comboVals_county_county,state="readonly",width=32)
                combo_county2.place(relx=0.35,rely=0.165)
                combo_county2.current(0)
                def comboFunc_county_county(event):
                    btn_regression.config(state=NORMAL,bg=LIGHT_BEIGE,fg=DARK_GREY) #re-enables regression button
                    myCounty = combo_county2.get()
                    if myCounty != "Select a County":
                        global ax
                        global INITIAL_DATE
                        global GRAPH_TITLE
                        global main_df
                        ax = None
                        main_df = None
                        main_df = df[df.state == myState]
                        main_df = main_df[main_df.county == myCounty] 
                        INITIAL_DATE = main_df['date'].iloc[0] # not all states started recording on same date
                        main_df['days_since_'+INITIAL_DATE] = list(range(0, len(main_df)))
                        lbl_main.config(text=myCounty+', '+myState+' Data') #change label text
                        print(main_df)
                        #creating initial plot
                        figure = Figure(figsize=(8,5.8), dpi=90)
                        figure.patch.set_facecolor(LIGHT_BEIGE)
                        ax = figure.add_subplot(111)
                        ax.scatter(main_df['days_since_'+INITIAL_DATE],main_df['cases'],color='blue')
                        GRAPH_TITLE = myCounty+" COVID-19 Cases"
                        ax.set_title(GRAPH_TITLE)
                        ax.set_xlabel('Days since '+INITIAL_DATE)
                        ax.set_ylabel('Cases per '+str(POP_NORM_COUNTY))
                        #embedding
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
                combo_county2.bind("<<ComboboxSelected>>", comboFunc_county_county)
        combo_county1.bind("<<ComboboxSelected>>", comboFunc_county_state)

    #backbutton to return to home screen       
    def returnHome():
        graphWindow.destroy()
        startupScreen()
    btn_back = Button(graphWindow, text="Return Home",command=returnHome, bg=LIGHT_BEIGE,fg=DARK_GREY,font=("Times New Roman", 18))
    btn_back.place(relx=0.86,rely=0.84)

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

print("\nApp Started.\n")
startupScreen()