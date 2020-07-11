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
from tkinter import Tk

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