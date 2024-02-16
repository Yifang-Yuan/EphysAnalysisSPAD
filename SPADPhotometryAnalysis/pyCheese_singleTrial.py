# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 16:13:41 2022
@author: Yifang

This code is to analyse pyPhotometry recorded data when a mouse is performing cheeseboard task for a single trial.
A sync pulse was send to pyPhotometry Digital 1 as CamSync
An LED pulse was recorded by the camera to sync the photometry signal with the animal's behaviour.

Analysing of behaviour was performed with COLD-a cheeseboard behaviour tracking pipeline developed by Daniel-Lewis Fallows
"""
import numpy as np
import matplotlib.pyplot as plt
import photometry_functions as fp
import scipy

# Folder with your files
#folder = 'C:/SPAD/pyPhotometry_v0.3.1/data/' # Modify it depending on where your file is located
folder ='E:/Qingren/1002/Day2/'
COLD_folder='E:/Qingren/'
# File name
file_name = '1002-2023-08-12-180348_9.csv'
sync_filename='1002_Sync_9.csv'
COLD_filename='Training Data_adjusted.xlsx'

'''Sampling rate of pyPhotometry is 130'''
sampling_rate=130 
CamFs=24
#%%
'''Analysing a single recording from pyPhotometry'''
raw_signal,raw_reference,Cam_Sync=fp.read_photometry_data (folder, file_name, readCamSync='True',plot=False)
#raw_signal,raw_reference=read_photometry_data (folder, file_name, readCamSync='False')
CamSync_LED=fp.read_Bonsai_Sync (folder, sync_filename,plot=False)
fp.plot_sync (raw_signal,raw_reference,Cam_Sync,CamSync_LED,pyFs=sampling_rate,CamFs=CamFs)
zdFF = fp.get_zdFF(raw_reference,raw_signal,smooth_win=5,remove=0,lambd=5e4,porder=1,itermax=50)
fig = plt.figure(figsize=(16, 5))
ax1 = fig.add_subplot(111)
ax1 = fp.plotSingleTrace (ax1, zdFF, SamplingRate=sampling_rate,color='black',Label='zscore_signal')
#%%
zscore_sync,Sync_index_inCam,Sync_Start_time=fp.sync_photometry_Cam(zdFF,Cam_Sync,CamSync_LED,CamFs=CamFs)
reference_sync=fp.Cut_photometry_data (raw_reference, Cam_Sync)
signal_sync=fp.Cut_photometry_data (raw_signal, Cam_Sync)
#%%
'''
From here, you'll need COLD output to get the PETH plot
'''
cheeaseboard_session_data=fp.read_cheeseboard_from_COLD (COLD_folder, COLD_filename)
'''for this trial'''
entertime, well1time,well2time=fp.adjust_time_to_photometry(cheeaseboard_session_data,9,Sync_Start_time)
half_timewindow=2
fig = plt.figure(figsize=(16, 5))
ax = fig.add_subplot(111)
fp.PETH_plot_zscore(ax, zscore_sync,centre_time=well2time, half_timewindow=half_timewindow, fs=sampling_rate,color='black')
ax.axvline(x=2, color='red', linestyle='--', label='Event Time')

fig = plt.figure(figsize=(16, 5))
ax1 = fig.add_subplot(211)
fp.PETH_plot_zscore(ax1, signal_sync,centre_time=well2time, half_timewindow=half_timewindow, fs=sampling_rate,color='blue')
ax1.axvline(x=2, color='red', linestyle='--', label='Event Time')
ax2 = fig.add_subplot(212)
fp.PETH_plot_zscore(ax2, reference_sync,centre_time=well2time, half_timewindow=half_timewindow, fs=sampling_rate,color='purple')
ax2.axvline(x=2, color='red', linestyle='--', label='Event Time')
