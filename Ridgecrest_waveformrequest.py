#!/usr/bin/env python
# coding: utf-8

# # Ridgecrest Waveform request
# This will read Thugman's event catalog and dowaload waveforms for each event. ObsPy, numpy, scipy, matplotlib are required.

# ## Import ObsPy module

# In[1]:


from obspy import read
from obspy import UTCDateTime
from obspy import read, read_inventory
from obspy.clients.fdsn import Client

import obspy as ob
print("# obspy version = ",ob.__version__)


# ## Import SciPy, NumPy, matplotlib, pandas module

# In[2]:


import numpy as np
import scipy as sp
import matplotlib as mpl
import pandas as pd

print("# numpy version = ",np.__version__)
print("# scipy version = ",sp.__version__)
print("# matplotlib version = ",mpl.__version__)
print("# pandas version = ",pd.__version__)

import matplotlib.pyplot as plt

import os
import json
import time
import sys


# In[3]:


# should fail all time
def test_fail():
    print(test_value)


# ## function: request_waveform

# In[71]:


def request_waveform(eventid, request_server, distdeg_from_eq, catalog, 
                     pre_tw_sec, tw_sec, debugOPT, net_listOUT, sta_list, com_listOUT, 
                     max_retry, sleep_time_sec, failtestOPT):
    
    # name for output directory
    pwd_dir = os.getcwd() 
    # v1
    #outdir = pwd_dir +"/"+(str)(eventid) +"_dist"+(str)(distdeg_from_eq)+"deg"
    # v2
    outdir = pwd_dir +"/"+(str)(eventid)
    
    print("# outdir = ",outdir)

    # create output directory
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # get event info. based on eventif
    event_select = catalog [ (catalog ['evid'] == eventid) ]
    print("# event_select = ", event_select)

    index = event_select['evla'].index.to_numpy()
    if debugOPT:
        print("# index = ", index)

    latitude = event_select['evla'][index].to_numpy()
    longitude = event_select['evlo'][index].to_numpy()
    if debugOPT:
        print("# latitude = ", latitude," longitude = ", longitude)


    
    origin_time = event_select['origin_time'][index].to_numpy()
    #print("# origin_time = ",  origin_time)
    
    origin_time = UTCDateTime( origin_time[0]  )
    if debugOPT:
        print("# origin_time = ",  origin_time)

    starttime_tw = UTCDateTime(origin_time-pre_tw_sec)
    endtime_tw = UTCDateTime(origin_time+tw_sec)

    if debugOPT:
        print("# starttime_tw = ",starttime_tw," endtime_tw = ",endtime_tw)

           
    ### v2
    yearOUT = origin_time.year
    jdayOUT = origin_time.julday
    hourOUT = origin_time.hour
    minOUT = origin_time.minute
    secOUT = origin_time.second

    yearOUT2 = (str)(yearOUT)

    jdayOUT2 = (str)(jdayOUT)
    if jdayOUT < 100:
        jdayOUT2 = "0"+(str)(jdayOUT)


    if jdayOUT < 10:
        jdayOUT2 = "00"+(str)(jdayOUT)
        

    hourOUT2 = (str)(hourOUT)
    if hourOUT < 10:
        hourOUT2 = "0"+(str)(hourOUT)


    minOUT2 = (str)(minOUT)
    if minOUT < 10:
        minOUT2 = "0"+(str)(minOUT)


    secOUT2 = (str)(secOUT)
    if secOUT < 10:
        secOUT2 = "0"+(str)(secOUT)


    mseedid = yearOUT2+"."+jdayOUT2+"."+hourOUT2+""+minOUT2+""+secOUT2

    if debugOPT:
        print("# yearOUT2 = ",yearOUT2," jdayOUT2 = ",jdayOUT2," hourOUT2 = ",hourOUT2," minOUT2 = ",minOUT2," secOUT2 = ",secOUT2)
        print("# mseedid = "+mseedid)
    ### v2
        
    

    # first set
    # Without nodal first (network 3J)
    #net_listOUT = "*"
    #sta_list = "*"
    
    #if checkOPT:
    #    net_listOUT = "CI"
    #    sta_list = "WMF"

        
    print("# net_listOUT = ", net_listOUT)
    print("# sta_list = ", sta_list)
    
    #com_listOUT = "HHZ,HHZ,DP1,EP1"
    #HNZ HLZ 
    #B? 20 or 40sps 
    #M>=3 or 4 EQ -> only B stations 
    # v1 vertical only
    #com_listOUT = "H?Z,E?Z,D?Z,E?Z,C?Z"
    # v2 includ all components
    #com_listOUT = "H??,E??,D??,E??,C??"
    #com_listOUT = "H?Z,H?1,E?Z,E?1,D?Z,D?1,E?Z,E?1,C?Z,C?1"
    #com_listOUT = "HH?,HN?,DP?,EP?,EH?,CN?,CL?"
    
    #if checkOPT:
    #    com_listOUT = "HHZ"

    print("# com_listOUT = ", com_listOUT)

    if request_server == 1:
        server_nameOUT = "iris"
        clientOUT = Client("IRIS", timeout=600)
    
    elif request_server == 2:
        server_nameOUT = "scedc"
        clientOUT = Client("SCEDC", timeout=600)

    elif request_server == 3:
        server_nameOUT = "ncedc"
        clientOUT = Client("NCEDC", timeout=600)

    if debugOPT:
        print(clientOUT)
    

    # search area
    minradius = 0
    maxradius = distdeg_from_eq
    
    connectionOUT = 0 # 0 is failed. 1 is success
    
    for i_try in range(max_retry + 1):
        print("# i_try = ", i_try)
    
        try:
            
            if failtestOPT:
                test_fail()
            else:
                # inventory 
                print("# download response")
                invOUT = clientOUT.get_stations(network=net_listOUT, station=sta_list, channel=com_listOUT, 
                                                starttime=starttime_tw, endtime=endtime_tw,
                                                latitude=latitude, longitude=longitude,
                                                minradius=minradius, maxradius=maxradius,
                                                level="response")
                # channel info.
                print("# download stataion info.")
                channelOUT = clientOUT.get_stations(network=net_listOUT, station=sta_list, channel=com_listOUT, 
                                                starttime=starttime_tw, endtime=endtime_tw,
                                                latitude=latitude, longitude=longitude,
                                                minradius=minradius, maxradius=maxradius,
                                                level="channel")
                #print(invOUT)

        except Exception as e:
            print("# failed to connect to {} for {}... retry={}/{}".format(server_nameOUT, eventid, i_try, max_retry))
            print("# waiting "+str(sleep_time_sec)+" sec")
            time.sleep(sleep_time_sec)

        
        else:
            print("# success")
            connectionOUT = 1
            break

    # if all falied. need to check if this is okay
    else:
        print("# all failed to connect to {} for {}...".format(server_nameOUT, eventid))
        connectionOUT = 0
        pass
    


    print("# connectionOUT = ", connectionOUT)
    if connectionOUT:
    #    continue


        # save station list
        #inv_fiOUT = outdir + "/" + (str)(eventid)+".sta."+(str)(distdeg_from_eq)+"deg."+server_nameOUT+".txt"
        inv_fiOUT = outdir + "/" + (str)(eventid)+"."+server_nameOUT+".txt"

        if debugOPT:
            print("# inv_fiOUT = "+inv_fiOUT)
        invOUT.write(inv_fiOUT, format='STATIONTXT')  

        # save station xml
        #inv_fiOUT = outdir + "/" + (str)(eventid)+".sta."+(str)(distdeg_from_eq)+"deg."+server_nameOUT+".xml"
        inv_fiOUT = outdir + "/" + (str)(eventid)+"."+server_nameOUT+".xml"

        if debugOPT:
            print("# inv_fiOUT = "+inv_fiOUT)
        invOUT.write(inv_fiOUT, format='STATIONXML')  

        # save sac pz
        #inv_fiOUT = outdir + "/" + (str)(eventid)+".sta."+(str)(distdeg_from_eq)+"deg."+server_nameOUT+".sacpz"
        inv_fiOUT = outdir + "/" + (str)(eventid)+"."+server_nameOUT+".sacpz"

        if debugOPT:
            print("# inv_fiOUT = "+inv_fiOUT)
        invOUT.write(inv_fiOUT, format='SACPZ')  


        # get sncl list
        ch_listOUT = ""
        j2=0
        sncl_list = []
        for i in range(len(channelOUT)):        
            netOUT = channelOUT[i].code
            #print (inv_ncedc[i].code)
            for ii in range(len(channelOUT[i])):
                #print(ii)
                #print(inv[i][ii].code)    
                staOUT = channelOUT[i][ii].code
                for iii in range(len(channelOUT[i][ii])):
                    chaOUT = channelOUT[i][ii][iii].code 
                    locOUT = channelOUT[i][ii][iii].location_code
                    snclOUT = netOUT+"."+staOUT+"."+locOUT+"."+chaOUT
                    #print("# j2 = ",j2," snclOUT = ",snclOUT)
                    sncl_list.append(snclOUT)
                    j2+=1



        # get station list
        sta_listOUT = ""
        j=0
        for i in range(len(invOUT)):
            #print (inv_ncedc[i].code)
            for ii in range(len(invOUT[i])):
                #print(ii)
                #print(inv[i][ii].code)
                if j==0:
                        sta_listOUT = invOUT[i][ii].code
                else:
                        sta_listOUT = sta_listOUT+","+invOUT[i][ii].code
                j+=1



        print("# sta_listOUT = ",sta_listOUT)


        
        connectionOUT_wave = 0 # 0 is failed. 1 is success
    
        for i_try_wave in range(max_retry + 1):
            print("# i_try_wave = ", i_try_wave)
    
            try:
 
                # need to add try/except here...
                # get seismic waveforms nased on station & network lists
                stOUT = clientOUT.get_waveforms(network=net_listOUT, station=sta_listOUT, channel=com_listOUT, location="*",
                                        starttime=starttime_tw, endtime=endtime_tw)
                #CI.WMF..HHZ
                #stOUT = clientOUT.get_waveforms(network="CI", station="WMF", channel="BHZ", location="*",
                #                                starttime=starttime_tw, endtime=endtime_tw)    

            except Exception as e:
                print("# failed to wave connect to {} for {}... retry={}/{}".format(server_nameOUT, eventid, i_try_wave, max_retry))
                print("# waiting "+str(sleep_time_sec)+" sec")
                time.sleep(sleep_time_sec)

        
            else:
                print("# success")
                connectionOUT_wave = 1
                break                

        # if all falied need to check if this is okay
        #else
        else:
            print("# all failed to connect to {} for {}...".format(server_nameOUT, eventid))
            connectionOUT_wave = 0
            pass
    


        print("# connectionOUT_wave = ", connectionOUT_wave)
        if connectionOUT_wave:
        

            if debugOPT:
                print(stOUT)



            #for i in range(len(stOUT)):
            for tr in stOUT:
                if debugOPT:
                    print(tr)

                netOUT = tr.stats.network
                comOUT = tr.stats.channel
                staOUT = tr.stats.station
                locOUT = tr.stats.location

                if netOUT == "3J":
                    # nodal data will be excluded
                    continue

                stid = netOUT+"."+staOUT+"."+locOUT+"."+comOUT
                sncl_id = staOUT+"."+netOUT+"."+comOUT+"."+locOUT

                # v1
                #mseed_fiOUT = outdir+"/"+sncl_id+".ms"
                # v2
                mseed_fiOUT = outdir+"/"+sncl_id+"."+mseedid+"."+str(eventid)+".ms"

                if debugOPT:
                    print("# staOUT = ",staOUT," netOUT = ",netOUT," comOUT = ",comOUT," locOUT = ",locOUT)
                    print("# mseed_fiOUT = ", mseed_fiOUT)
                #print("# stid = "+stid)
                tr.write(mseed_fiOUT, format="MSEED") 

        else:
            print("# failed to get waveform  for {} with {}".format(eventid, server_nameOUT))
            # ubs obspy test data now. but need to reconsider later...
            stOUT = read() 
    else:
        print("# failed to get resp & station info. for {} with {}".format(eventid, server_nameOUT))
        # ubs obspy test data now. but need to reconsider later...
        stOUT = read()
    return stOUT
    
    


# In[ ]:





# In[72]:


inp_fi = "rc_request.json"
inp_fd = open(inp_fi, mode='r')
inp_para = json.load(inp_fd)
inp_fd.close()
print("# inp_para : ", type(inp_para))
print(inp_para)


# ## debugOPT

# In[73]:


# check output values 
#debugOPT = 1
#debugOPT = 0
debugOPT = inp_para['debugOPT']


# ## plotOPT

# In[74]:


# show waveforms from last data center

#plotOPT = 0
plotOPT = inp_para['plotOPT']


# In[75]:


#max_retry = 10
max_retry = inp_para['max_retry']
#sleep_time_sec = 10
sleep_time_sec = inp_para['sleep_time_sec']

#failtestOPT = 1 # do fail for all connections to get resp & station info.
failtestOPT = inp_para['failtestOPT']

print("# max_retry = ", max_retry, " sleep_time_sec = ", sleep_time_sec)
print("# failtestOPT = ", failtestOPT)


# ## Reading relocated catalog
# use Daniel Trugman's reolocated catalog.

# In[76]:


#cat Dataset\ S1.txt | awk '{print $1","$2","$3","$4","$5","$6","$7","$8}' | less >! Dataset_S1.csv
#catalog_fi = "/Users/taira/Downloads/bssa-2020009_supplement_datasets+s1+and+s2/Dataset_S1.csv"
#catalog_fi = "./Dataset_S1.csv"
catalog_fi = inp_para['catalog_fi']
print("# catalog_fi = ", catalog_fi)

#Dataset S1. Relocated earthquake catalog. Each row corresponds to an earthquake, and there are 7 columns in total: 
#1.	Event ID
#2.	Origin Time
#3.	Magnitude (SCEDC preferred)
#4.	Longitude
#5.	Latitude
#6.	Depth (km)
#7.	Relocated (0 = No, 1 = Yes) -> locid


catalog = pd.read_csv(catalog_fi, skiprows=None,
                       sep=",",names=["evid", "origin_time1","origin_time2", "scedc_mag", "evlo", "evla", "dep", "locid"],header=None)

catalog['origin_time'] = catalog['origin_time1']+"T"+catalog['origin_time2']
catalog['time'] = pd.to_datetime(catalog['origin_time'])
print(catalog.head())


# ## Selecting events
# minimum magnitude is 1.0. Duration is two week from July 4, 2019 at 00:00.00 UTC

# In[77]:


# minimum magnitude
#minmag = 1.0 
minmag = inp_para['minmag']
maxmag = inp_para['maxmag']
print("# minmag = ", minmag," maxmax = ", maxmag)

# two-week time window 
#start_time = "2019-07-04T00:00:00"
#end_time = "2019-07-18T00:00:00"
start_time = inp_para['start_time']
end_time = inp_para['end_time']


# half hour time window
# beta test 04.14.21
#start_time = "2019-07-07T00:00:00"
#end_time = "2019-07-14T01:30:00"

print("# start_time = ", start_time)
print("# end_time   = ", end_time)
# select events based on magnitude and origin time
catalog_select = catalog[ (catalog['time']  >=  start_time) & (catalog['time']  <=  end_time) 
                         & (catalog['scedc_mag']  >=  minmag) & (catalog['scedc_mag']  <=  maxmag)    ]

#print(catalog_select.head())
print(catalog_select)


# In[78]:


print(len(catalog_select))


# In[79]:


# 38443183 M6.40
# 38457511 M7.10
# 38548295 M4.90
# 38475431 M4.15
# 38541359 M3.94
# 38553919 M3.19
# 38553671 M2.50
# 38553575 M2.01
# 38553519 M1.63
# 38553495 M1.18
betaOPT = inp_para['betaOPT']
if betaOPT:
    catalog_select = catalog[ (catalog['evid']  == 38443183) | (catalog['evid']  == 38457511) |
                            (catalog['evid']  == 38548295) | (catalog['evid']  == 38475431) |
                            (catalog['evid']  == 38541359) | (catalog['evid']  == 38553919) |
                            (catalog['evid']  == 38553671) | (catalog['evid']  == 38553575) |
                            (catalog['evid']  == 38553519) | (catalog['evid']  == 38553495) 
                            ]
    print(catalog_select)


# In[ ]:





# In[80]:


#print(catalog_select)


# In[81]:


#len(catalog_select)


# In[ ]:





# ## Waveform request parameters

# In[82]:


# request server list
# 1 -> IRIS
# 2 -> SCEDC
# 3 -> NCEDC
#request_servers = [3, 1, 2] # NCEDC -> IRIS -> SCEDC
request_servers = inp_para['request_servers']

# SCEDC test
#request_servers = [2] # SCEDC
print(type(request_servers))
print("# request_servers = ", request_servers )


# distance from hypocenter in degrees
#distdeg_from_eq = 1.0 # -> ~110km
distdeg_from_eq = inp_para['distdeg_from_eq']
print("# distdeg_from_eq = ", distdeg_from_eq)

# time window from origin time to extract waveform
# from BE
#You might consider increasing the length to 2 minutes (10 before to 110 after), but I don’t feel strongly about it.
# from RA -> 90 seconds
# coda?  55min! 4.0<=M 300km

# time window from event origin time
#pre_tw_sec = 0 # 0 seconds before the origin time
#tw_sec = 90 # 90 sec after the origin time


# In[83]:


#len(catalog_select['evla'].index.to_numpy())
#catalog_select['evla']


# In[84]:


#testOPT = 1 # -> only one event
testOPT = inp_para['testOPT']

#no_waveOPT = 1 
no_waveOPT = inp_para['no_waveOPT']


print("# testOPT = ", testOPT)
print("# no_waveOPT = ", no_waveOPT)


# In[85]:


#net_listOUT = "*"
net_listOUT = inp_para['net_listOUT']
print("# net_listOUT = ", net_listOUT)


# In[86]:


sta_list = "*"
sta_list = inp_para['sta_list']
print("# sta_list = ", sta_list)


# In[87]:


#com_listOUT = "HH?,HN?,DP?,EP?,EH?,CN?,CL?"
com_listOUT = inp_para['com_listOUT']
print("# com_listOUT = ", com_listOUT)


# In[88]:


#start_i = 0
start_i = inp_para['start_i']
print("# start_i = ", start_i)

#step_i = 1
step_i = inp_para['step_i']
print("# step_i =", step_i)


# In[89]:


selectEQ_index = catalog_select['evla'].index.to_numpy()
print("# selectEQ_index = ", selectEQ_index)

#for i in range(len(selectEQ_index)):
#for i in range(0, len(selectEQ_index), 1):
for i in range(start_i, len(selectEQ_index), step_i):

    print("# i = ", i)
    i2 = selectEQ_index[i]
    eventid = catalog_select['evid'][i2]
    
    mag=catalog_select['scedc_mag'][i2]
    print("# eventid = ", eventid," mag = ", mag)
    
    # RC mainshock 
    #eventid = 38457511 # 

    # time window from event origin time
    pre_tw_sec = 15 # 15 seconds before the origin time
    tw_sec = 60 # 75 sec after the origin time

    if 2<=mag and mag<3:
        pre_tw_sec = 30
        tw_sec = 90
   
    if 3<=mag and mag<4:
        pre_tw_sec = 45
        tw_sec = 130
    
    if 4<=mag and mag<5:
        pre_tw_sec = 60
        tw_sec = 180

    if 5<=mag and mag<6:
        pre_tw_sec = 75
        tw_sec = 240        
        
    if 6<=mag:
        pre_tw_sec = 90
        tw_sec = 310
        
    print("# pre_tw_sec = ",pre_tw_sec," tw_sec = ",tw_sec)

    if no_waveOPT:
        continue
        
    for request_server in request_servers:
        print("# request_server = ", request_server)
        stOUT = request_waveform(eventid, request_server, distdeg_from_eq, catalog, 
                                 pre_tw_sec, tw_sec, debugOPT, 
                                 net_listOUT, sta_list, com_listOUT,
                                 max_retry, sleep_time_sec, failtestOPT)

    if (i == 0) and testOPT:
        break
        


# In[ ]:





# ## Showing waveforms from the last request server

# In[61]:


#print(stOUT)


# In[62]:


if plotOPT: 
    for tr in stOUT:
        _plot = tr.plot()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




