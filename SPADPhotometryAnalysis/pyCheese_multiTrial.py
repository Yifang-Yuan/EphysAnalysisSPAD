# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 20:22:58 2023
@author: Yifang

This code is to analyse pyPhotometry recorded data when a mouse is performing cheeseboard task for a multiple trials.
A sync pulse was send to pyPhotometry Digital 1 as CamSync
An LED pulse was recorded by the camera to sync the photometry signal with the animal's behaviour.

Analysing of behaviour was performed with COLD-a cheeseboard behaviour tracking pipeline developed by Daniel-Lewis Fallows
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import photometry_functions as fp
import os
# Folder with your files
#folder = 'C:/SPAD/pyPhotometry_v0.3.1/data/' # Modify it depending on where your file is located
#folder ='E:/Qingren/1002/Day2/'
#COLD_folder='E:/Qingren/'
folder ='C:/Users/yifan/Downloads/1665 TrainingD4/'
COLD_folder='C:/Users/yifan/Downloads/'
# Set your parameters
COLD_filename='1665.xlsx'
pyFs=130
CamFs=24
#half_timewindow=1
animalID='(Mouse 1665D4 GCcamp8)'
#%%
#cheeaseboard_session_data=fp.read_cheeseboard_from_COLD (COLD_folder, COLD_filename)
'''This function will read all photometry recording and COLD file for a session or multiple trials'''
df_py_cheese=fp.read_all_photometry_files(folder, '2023','Sync',CamFs,pyFs,COLD_folder,COLD_filename)
#%%
#Enter the value 
before_window=5
after_window=10
event_window_traces=fp.Plot_multiple_PETH_different_window(df_py_cheese,before_window,after_window,fs=pyFs,animalID=animalID)
'''save the pkl file for the PETH data with half window time specified'''
filename='1665D4PETH_'+str(before_window)+'seconds_day4.pkl'
event_window_traces.to_pickle(folder+filename)

#%%
'''plot traces all together'''
''' you need to put all the PETH files with the same half window in the same folder '''
folder_for_all='C:/Users/yifan/Downloads/1665 TrainingD4/'

PSTH_collection=fp.Read_Concat_pkl_files(folder_for_all, IndexNumFromFilename=-4)

filtered_columns = [col for col in PSTH_collection.columns if col.endswith('_1')]
Well1_PETH = PSTH_collection[filtered_columns]

filtered_columns = [col for col in PSTH_collection.columns if col.endswith('_2')]
Well2_PETH = PSTH_collection[filtered_columns]

#%%
'''plot'''
fig, ax = plt.subplots(figsize=(10, 4))
fp.Plot_mean_With_Std_PSTH(Well1_PETH, before_window, after_window, animalID, meancolor='green', stdcolor='lightgreen', ax=ax)

fig, ax = plt.subplots(figsize=(10, 4))
fp.Plot_mean_With_Std_PSTH(Well2_PETH, before_window, after_window, animalID, meancolor='red', stdcolor='lightcoral', ax=ax)

fig, ax = plt.subplots(figsize=(10, 4))
fp.Plot_mean_With_Std_PSTH(PSTH_collection, before_window, after_window, animalID, meancolor='blue', stdcolor='lightblue', ax=ax)
#%%
'''choose the trial index you want to plot, this is the trial num that you have photometry recordings.
You can check Well1PETH variable for the index'''
singleTrial_index=7
timediff=df_py_cheese['well2time'+str(singleTrial_index)][0]-df_py_cheese['well1time'+str(singleTrial_index)][0]

fig, ax = plt.subplots(figsize=(10, 4))
fp.Plot_single_trial_PSTH(Well1_PETH, singleTrial_index,timediff,before_window, after_window, animalID, meancolor='b', ax=ax)