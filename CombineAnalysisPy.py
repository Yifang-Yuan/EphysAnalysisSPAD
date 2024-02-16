# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 22:30:19 2023
This is the main file to perform a comparison analysis between LFP and optical signal.
This code will create a Class for the recording session you want to analyse.
@author: Yifang
"""
import os
import numpy as np
import pandas as pd
#from open_ephys.analysis import Session
from SyncOECPySessionClass import SyncOEpyPhotometrySession
import OpenEphysTools as OE
#%%
dpath="E:/YYFstudy/20240214_Day3/SyncRecording10/"
#dpath="G:/SPAD/SPADData/20230722_SPADOE/SyncRecording0/"
Recording1=SyncOEpyPhotometrySession(dpath,IsTracking=False,read_aligned_data_from_file=False) 
'''You can try LFP1,2,3,4 and plot theta to find the best channel'''
LFP_channel='LFP_1'
#%%
'''To remove noises from the LFP data and cut Matrix to only preserve clean parts'''
# # Recording1.remove_noise(start_time=58,end_time=62)
# Recording1.remove_noise(start_time=22,end_time=25)
# Recording1.remove_noise(start_time=62,end_time=65)
# data=Recording1.reset_index_data()
#%%
'''separate the theta and non-theta parts.
theta_thres: the theta band power should be bigger than 80% to be defined as theta period.
nonthetha_thres: the theta band power should be smaller than 50% to be defined as theta period.'''
theta_part,non_theta_part=Recording1.separate_theta (LFP_channel,theta_thres=80,nonthetha_thres=50)
#%%
'''To plot the feature of a part of the signal'''
start_time=30
end_time=40
Recording1.plot_segment_feature (LFP_channel,start_time,end_time,SPAD_cutoff=50,lfp_cutoff=500)
'To plot the feature of theta-part of the signal'
#Recording1.plot_theta_feature (LFP_channel,start_time,end_time,LFP=True)
'To plot the feature of non-theta-part of the signal'
# Recording1.plot_ripple_feature (LFP_channel,start_time,end_time)
#%% This is to calculate and plot the trace around theta trough
silced_recording=theta_part
silced_recording['theta_angle']=OE.calculate_theta_phase_angle(silced_recording[LFP_channel], theta_low=5, theta_high=9)
OE.plot_trace_in_seconds(silced_recording['theta_angle'],Fs=10000)
trough_index = OE.calculate_theta_trough_index(silced_recording)
OE.plot_theta_cycle (silced_recording, LFP_channel,trough_index,half_window=0.1,fs=10000,plotmode='two')
#%% To plot feature of multiple smaller segments
timewindow=5 #the duration of the segment, in seconds
viewNum=10 #the number of segments
for i in range(viewNum):
    Recording1.plot_theta_feature (LFP_channel,start_time=timewindow*i,end_time=timewindow*(i+1))
#%%
'''Here for the spectrum, I used a 0.5Hz high pass filter to process both signals'''
timewindow=10 #the duration of the segment, in seconds
viewNum=2 #the number of segments
for i in range(viewNum):
    Recording1.plot_segment_feature (LFP_channel=LFP_channel,start_time=timewindow*i,end_time=timewindow*(i+1),SPAD_cutoff=50,lfp_cutoff=500)
#%%
'''sliced_recording:choose a segment or a part of your recording, this can be defined with start and end time,
or just by theta_part, non_theta_part'''
#silced_recording=Recording1.slicing_pd_data (Recording1.Ephys_tracking_spad_aligned,start_time=0, end_time=3)
silced_recording=theta_part
'''Calculate the cross correlation between two power spectrun over time at a specific frequency'''
sst_spad,frequency_spad,power_spad,global_ws_spad=OE.Calculate_wavelet(silced_recording['zscore_raw'],lowpassCutoff=500,Fs=10000)
sst_lfp,frequency_lfp,power_lfp,global_ws_lfp=OE.Calculate_wavelet(silced_recording[LFP_channel],lowpassCutoff=500,Fs=10000)
# Calculate the correlation coefficient
# lags,Corr_mean,Corr_std=Recording1.get_mean_corr_two_traces (power_spad[18],power_lfp[18],corr_window=1)
# lags,Corr_mean,Corr_std=Recording1.get_mean_corr_two_traces (power_spad[19],power_lfp[19],corr_window=1)
lags,Corr_mean,Corr_std=Recording1.get_mean_corr_two_traces (power_spad[20],power_lfp[20],corr_window=1)
#%%
'''Calculate the cross correlation between LFP and optical signal for a specific segment'''
#silced_recording=Recording1.slicing_pd_data (Recording1.Ephys_tracking_spad_aligned,start_time=0, end_time=90)
#silced_recording=theta_part
lags,Corr_mean,Corr_std=Recording1.get_mean_corr_two_traces (silced_recording['zscore_raw'],silced_recording[LFP_channel],corr_window=0.5)
#%%
'''Calculate the cross correlation between LFP and optical signal for a specific segment, with low-pass filter'''
spad_lowpass= OE.smooth_signal(silced_recording['zscore_raw'],Fs=10000,cutoff=50)
lfp_lowpass = OE.butter_filter(silced_recording[LFP_channel], btype='low', cutoff=50, fs=Recording1.fs, order=5)
spad_low = pd.Series(spad_lowpass, index=silced_recording['zscore_raw'].index)
lfp_low = pd.Series(lfp_lowpass, index=silced_recording[LFP_channel].index)
lags,Corr_mean,Corr_std=Recording1.get_mean_corr_two_traces (spad_low,lfp_low,corr_window=2)
#%% Detect ripple event
'''RIPPLE DETECTION
For a rigid threshold to get larger amplitude ripple events: Low_thres=3, for more ripple events, Low_thres=1'''
ripple_band_filtered,nSS,nSS3,rip_ep,rip_tsd,cross_corr_values=Recording1.pynappleAnalysis (lfp_channel=LFP_channel,ep_start=0,ep_end=80,
                                                                          Low_thres=2,High_thres=10,plot_ripple_ep=True)
#This is to plot the average calcium transient around a ripple peak
transient_trace=Recording1.Ephys_tracking_spad_aligned['zscore_raw']
#transient_trace= OE.smooth_signal(transient_trace,Fs=10000,cutoff=100)
mean_z_score,std_z_score=OE.Transient_during_LFP_event (rip_tsd,transient_trace,half_window=0.2,fs=10000)
#time_duration=transient_trace.index[-1].total_seconds()
#%% Detect theta event
'''THETA PEAK DETECTION
For a rigid threshold to get larger amplitude theta events: Low_thres=1, for more ripple events, Low_thres=0.5'''
theta_band_filtered,nSS,nSS3,rip_ep,rip_tsd,cross_corr_values=Recording1.pynappleThetaAnalysis (lfp_channel=LFP_channel,ep_start=0,ep_end=10,
                                                                         Low_thres=0.5,High_thres=10,plot_ripple_ep=True)
#This is to plot the average calcium transient around a ripple peak
transient_trace=Recording1.Ephys_tracking_spad_aligned['zscore_raw']
#transient_trace= OE.smooth_signal(transient_trace,Fs=10000,cutoff=100)
mean_z_score,std_z_score=OE.Transient_during_LFP_event (rip_tsd,transient_trace,half_window=0.5,fs=10000)
#time_duration=transient_trace.index[-1].total_seconds()
#%%
'''This can convert the speed to moving state'''
# moving_state = silced_recording['speed_abs'].apply(lambda x: 1 if x > 5 else 0)
# fig, ax = plt.subplots(figsize=(15,5))
# ax=OE.plot_moving_state_heatmap(ax, moving_state,cbar=True,annot=False)
# Recording1.plot_two_traces (spad_low,lfp_low,moving_state)