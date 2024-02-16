# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 16:11:42 2023

@author: Yifang
"""
import os
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pylab as plt
import pynapple as nap
import OpenEphysTools as OE
'''
This part is for finding the SPAD recording mask, camera recording masks, and to read animal tracking data (.csv).
The final output should be a pandas format EphysData with data recorded by open ephys, a SPAD_mask,and a synchronised behavior state data. 
'''
#%%
directory = "G:/SPAD/SPADData/20231030_GCAMP8mOEC/2023-10-30_14-53-00/" #Indeed noisy
dpath="G:/SPAD/SPADData/20231030_GCAMP8mOEC/20231030_SyncRecording2/"

Ephys_fs=30000
'''recordingNum is the index of recording from the OE recording'''
EphysData=OE.readEphysChannel (directory, recordingNum=1)
#%%
'''This is to check the SPAD mask range and to make sure SPAD sync is correctly recorded by the Open Ephys'''
fig, ax = plt.subplots(figsize=(15,5))
ax.plot(EphysData['SPADSync'])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
#%%
'''This is to find the SPAD mask based on the proxy time range of SPAD sync.
Change the start_lim and end_lim to generate the SPAD mask.
'''
SPAD_mask = OE.SPAD_sync_mask (EphysData['SPADSync'], start_lim=1000000, end_lim=4400000)
#%%
fig, ax = plt.subplots(figsize=(15,5))
ax.plot(SPAD_mask)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
#%%
OE.check_SPAD_mask_length(SPAD_mask)
#%% Save spad mask
EphysData['SPAD_mask'] = SPAD_mask
#%%
'''Check the Cam sync is correct and the threshold for deciding the Cam mask is 29000.
If not, add a number to EphysData['CamSync'] 
'''
#EphysData['CamSync']=EphysData['CamSync'].add(42000)
OE.plot_trace_in_seconds(EphysData['CamSync'],Ephys_fs)
#%%
OE.save_open_ephys_data (dpath,EphysData)

#%%
'This is the LFP data that need to be saved for the sync ananlysis'
LFP_data=EphysData['LFP_2']
timestamps=EphysData['timestamps'].copy()
timestamps=timestamps.to_numpy()
timestamps=timestamps-timestamps[0]

'To plot the LFP data using the pynapple method'
LFP=nap.Tsd(t = timestamps, d = LFP_data.to_numpy(), time_units = 's')
fig, ax = plt.subplots(figsize=(15,5))
ax.plot(LFP.as_units('s'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel("Time (s)")
ax.set_title("LFP_raw")

#%%
'''This is to set the short interval you want to look at '''
ex_ep = nap.IntervalSet(start = 44, end = 45, time_units = 's') 

fig, ax = plt.subplots(figsize=(15,5))
ax.plot(LFP.restrict(ex_ep).as_units('s'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel("Time (s)")
ax.set_xlabel("LFP_raw")
plt.show()
#%%
Low_thres=2
High_thres=10
ripple_band_filtered,nSS,nSS3,rip_ep,rip_tsd = OE.getRippleEvents (LFP,Ephys_fs,windowlen=1200,Low_thres=2,High_thres=10)
#%% detect theta wave
lfp_theta = OE.band_pass_filter(LFP,4,15,Ephys_fs)
lfp_theta=nap.Tsd(t = timestamps, d = lfp_theta, time_units = 's')

plt.figure(figsize=(15,5))
plt.plot(lfp_theta.restrict(ex_ep).as_units('s'))
plt.xlabel("Time (s)")
plt.title("theta band")
plt.show()
#%%
fig, ax = plt.subplots(4, 1, figsize=(15, 8))
OE.plotRippleSpectrogram (ax, LFP, ripple_band_filtered, rip_ep, rip_tsd, ex_ep, nSS, nSS3, Low_thres, y_lim=30, Fs=Ephys_fs)

#%%
import matplotlib.pylab as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
# from mpl_toolkits.axes_grid1 import make_axes_locatable
from waveletFunctions import wave_signif, wavelet

signal=LFP.to_numpy()
sst = OE.butter_filter(signal, btype='low', cutoff=500, fs=Ephys_fs, order=5)
#sst = OE.butter_filter(signal, btype='high', cutoff=30, fs=Recording1.fs, order=5)

sst = sst - np.mean(sst)
variance = np.std(sst, ddof=1) ** 2
print("variance = ", variance)
# ----------C-O-M-P-U-T-A-T-I-O-N------S-T-A-R-T-S------H-E-R-E---------------
if 0:
    variance = 1.0
    sst = sst / np.std(sst, ddof=1)
n = len(sst)
dt = 1/Ephys_fs
time = np.arange(len(sst)) * dt   # construct time array
#%%
pad = 1  # pad the time series with zeroes (recommended)
dj = 0.25  # this will do 4 sub-octaves per octave
s0 = 25 * dt  # this says start at a scale of 6 months
j1 = 7 / dj  # this says do 7 powers-of-two with dj sub-octaves each
lag1 = 0.1  # lag-1 autocorrelation for red noise background
print("lag1 = ", lag1)
mother = 'MORLET'

# Wavelet transform:
wave, period, scale, coi = wavelet(sst, dt, pad, dj, s0, j1, mother)
power = (np.abs(wave)) ** 2  # compute wavelet power spectrum
global_ws = (np.sum(power, axis=1) / n)  # time-average over all times
frequency=1/period
#%%
xlim = ([65,75])  # plotting range
fig, plt3 = plt.subplots(figsize=(15,5))

levels = [0, 4,20, 100, 200, 300]
# *** or use 'contour'
CS = plt.contourf(time, frequency, power, len(levels))

plt.xlabel('Time (seconds)')
plt.ylabel('Frequency (Hz)')
plt.title('Wavelet Power Spectrum')
plt.xlim(xlim[:])
plt3.set_yscale('log', base=2, subs=None)
#plt.ylim([np.min(frequency), np.max(frequency)])
plt.ylim([0, 300])
ax = plt.gca().yaxis
ax.set_major_formatter(ticker.ScalarFormatter())
plt3.ticklabel_format(axis='y', style='plain')
#plt3.invert_yaxis()
# set up the size and location of the colorbar
position=fig.add_axes([0.2,0.01,0.4,0.02])
plt.colorbar(CS, cax=position, orientation='horizontal', fraction=0.05, pad=0.5)

plt.subplots_adjust(right=0.7, top=0.9)

#%%