###       /bin/bash runTestCases_docker.sh
import numpy as np
import matplotlib.pyplot as plt 
from netCDF4 import Dataset,netcdftime,num2date
from datetime import datetime
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
from sklearn.metrics import mean_squared_error
import itertools
import csv
from allNcFiles import av_ncfiles
#%% defining functions
def mySubtract(myList,num):
    return list(np.subtract(myList,num))
def myMultiply(myList,num):
    return list(np.multiply(myList,num))
def sum2lists (list1,list2):
    return list(np.add(list1,list2))

def readAllNcfilesAsDataset(allNcfiles):
    allNcfilesDataset = []
    for ncfiles in allNcfiles:
        allNcfilesDataset.append(Dataset(ncfiles))
    return allNcfilesDataset
#hruname = hru_names_df[0]
def readVariablefromNcfilesDatasetasDF(NcfilesDataset,variable,hruname):
    variableNameList = []
    for datasets in NcfilesDataset:
        variableNameList.append(pd.DataFrame(datasets[variable][:][:]))
    variableNameDF = pd.concat (variableNameList, axis=1)
    variableNameDF.columns = hruname
    counter = pd.DataFrame(np.arange(0,np.size(variableNameDF[hruname[0]])),columns=['counter'])
    counter.set_index(variableNameDF.index,inplace=True)
    variableNameDF = pd.concat([counter, variableNameDF], axis=1)
    return variableNameDF

def readSomePartofVariableDatafromNcfilesDatasetasDF(NcfilesDataset,variable,hruname,paretoNameDF):
    variableNameList = []
    for datasets in NcfilesDataset:
        variableNameList.append(pd.DataFrame(datasets[variable][:]))
    variableDF = pd.concat (variableNameList, axis=1)
    variableDF.columns = hruname
    desiredDataframe = []
    for paretos in paretoNameDF:
        desiredDataframe.append(variableDF[paretos])
    return desiredDataframe

def date(allNcfilesDataset,formatDate):
    Time = allNcfilesDataset[0].variables['time'][:] 
    #TimeSa = np.concatenate((TimeSa2006, TimeSa2007), axis=0)
    t_unit = allNcfilesDataset[0].variables['time'].units 
    
    try :
        t_cal = allNcfilesDataset[0].variables['time'].calendar
    
    except AttributeError : # Attribute doesn't exist error
        t_cal = u"gregorian" # or standard
    #tvalueSa = num2date(TimeSa, units=t_unitSa, calendar=t_cal)
    tvalue = num2date(Time, units=t_unit, calendar=t_cal)
    Date = [i.strftime(formatDate) for i in tvalue] # "%Y-%m-%d %H:%M"
    return Date

def readSpecificDatafromAllHRUs(variablename,hruname,day):
    dayData = []
    for names in hruname:
        dayData.append(variablename[names][day])
    return dayData

def sumBeforeSpecificDatafromAllHRUs(variablename,hruname,day):
    sumData = []
    for names in hruname:
        sumData.append(sum(variablename[names][0:day]))
    return sumData   

def snowLayerAttributeforSpecificDate(layerattributefile,hruname,sumlayer,snowlayer): #like snowlayertemp, volFracosIce, ....
    snowlayerattribute = []
    for names in hruname:
        snowlayerattribute.append(list(layerattributefile[names][sumlayer[names][0]:sumlayer[names][0]+snowlayer[names][0]]))
    return snowlayerattribute

def depthOfLayers(heightfile):
    finalHeight = []
    for lsts in heightfile:
        sumSofar=0
        lstscopy= lsts[:]
        lstscopy.reverse()
        height_ls = []
        for values in lstscopy:
            height=2*(abs(values)-sumSofar)
            height_ls.append(height)
            sumSofar+=height
        #print ("original:", height_ls) 
        height_ls.reverse()
        #print ("after reverse:", height_ls)
        finalHeight.append(height_ls)
    return finalHeight



def SWEandSWEDateforSpecificDate(hruname,hour,swe_df,dosd):
    SWE = []
    SWEdate = []
    for names in hruname:
        if swe_df[names][hour]>0:
            SWE.append(swe_df[names][hour])
            SWEdate.append(hour)
        else: 
            SWE.append(float(swe_df[names][dosd[names]-1]))
            SWEdate.append(float(dosd[names]-1))
    return SWE,SWEdate

def meltingRateBetween2days(swe1,swe2,sweDate1,sweDate2):
    mdeltaday = []; mdeltaSWE = []; meltingrate = []; #cm/day
    for counterhd in range (np.size(swe1)):
        mdeltaday.append(float(sweDate2[counterhd]-sweDate1[counterhd]))
        mdeltaSWE.append(float(swe1[counterhd]-swe2[counterhd]))
        if mdeltaday[counterhd]==0:
            meltingrate.append(float(0))
        else: meltingrate.append(float(0.1*24*mdeltaSWE[counterhd]/mdeltaday[counterhd]))
    return meltingrate
    
#%% SWE observation data 
date_swe = ['2006-11-01 11:10','2006-11-30 12:30','2007-01-01 11:10','2007-01-30 10:35','2007-03-05 14:30','2007-03-12 14:00', 
            '2007-03-19 12:30','2007-03-26 12:30','2007-04-02 12:30','2007-04-18 08:35','2007-04-23 10:30','2007-05-02 08:40', 
            '2007-05-09 08:50','2007-05-16 09:00','2007-05-23 08:30','2007-05-30 09:00','2007-06-06 08:15', 
            
            '2007-12-03 10:45','2008-01-01 11:30','2008-01-31 12:00','2008-03-03 14:30','2008-03-24 09:10','2008-04-01 09:55', 
            '2008-04-14 14:45','2008-04-22 12:30','2008-04-28 12:30','2008-05-06 09:15','2008-05-12 12:45','2008-05-19 10:40',
            '2008-05-26 08:45','2008-06-02 12:45','2008-06-08 08:45'] 
            
swe_mm = [58,  169, 267, 315, 499, 523, 503, 549, 611, 678, 654, 660, 711, 550, 443, 309, 84, 
          141, 300, 501, 737, 781, 837, 977, 950, 873, 894, 872, 851, 739, 538, 381]  

#obs_swe_date = pd.DataFrame (np.column_stack([date_swe,swe_mm]), columns=['date_swe','swe_mm'])
obs_swe = pd.DataFrame (swe_mm, columns=['swe_mm'])
obs_swe.set_index(pd.DatetimeIndex(date_swe),inplace=True)

max_swe_obs = max(obs_swe['swe_mm'])
max_swe_date_obs = obs_swe[obs_swe ['swe_mm']== max_swe_obs].index.tolist()  

swe_obs2006 = pd.DataFrame (obs_swe['swe_mm']['2006-11-01':'2007-06-06'], columns=['swe_mm'])
swe_obs2007 = pd.DataFrame (obs_swe['swe_mm']['2007-12-03':'2008-06-08'], columns=['swe_mm'])
date_swe2006 = ['2006-11-01 11:10','2006-11-30 12:30','2007-01-01 11:10','2007-01-30 10:35','2007-03-05 14:30', 
                '2007-03-12 14:00','2007-03-19 12:30','2007-03-26 12:30','2007-04-02 12:30','2007-04-18 08:35', 
                '2007-04-23 10:30','2007-05-02 08:40','2007-05-09 08:50','2007-05-16 09:00','2007-05-23 08:30',
                '2007-05-30 09:00','2007-06-06 08:15']
swe_obs2006.set_index(pd.DatetimeIndex(date_swe2006),inplace=True)  
#%% Snow depth observation data
with open("snowDepth_2006_2008.csv") as safd1:
    reader1 = csv.reader(safd1)
    raw_snowdepth1 = [r for r in reader1]
sa_snowdepth_column1 = []
for csv_counter1 in range (len (raw_snowdepth1)):
    for csv_counter2 in range (2):
        sa_snowdepth_column1.append(raw_snowdepth1[csv_counter1][csv_counter2])
sa_snowdepth=np.reshape(sa_snowdepth_column1,(len (raw_snowdepth1),2))
sa_sd_obs=[np.array(val) for val in sa_snowdepth[1:len(raw_snowdepth1)-1,1:]]
#sa_sd_obs = [float(value) for value in sa_snowdepth1]
sa_sd_obs_date = pd.DatetimeIndex(sa_snowdepth[1:len(raw_snowdepth1)-1,0])

snowdepth_obs_df = pd.DataFrame(sa_sd_obs, columns = ['observed_snowdepth']) 
snowdepth_obs_df.set_index(sa_sd_obs_date,inplace=True)

#%% defining hrus_name
p1 = [0.1] #LAIMIN
p2 = [1] #LAIMAX
p3 = [0.1] #winterSAI
p4 = [0.9] #summerLAI
p5 = [0.5] #rootingDepth
p6 = [0.5] #heightCanopyTop
p7 = [0.01] #heightCanopyBottom
p8 = [0.89] #throughfallScaleSnow
p9 = [55] #newSnowDenMin 
p10 = [500000, 1000000, 1300000] ##albedoDecayRate |       1.0d+6 |       0.1d+6 |       5.0d+6 
p11 = [0.8, 0.9, 0.94] #albedoMaxVisible |       0.9500 |       0.7000 |       0.9500
p12 = [0.6, 0.68, 0.74] #albedoMinVisible |       0.7500 |       0.5000 |       0.7500
p13 = [0.55, 0.65, 0.7] #albedoMaxNearIR |       0.6500 |       0.5000 |       0.7500
p14 = [0.2, 0.3, 0.4] #albedoMinNearIR  |       0.3000 |       0.1500 |       0.4500
p15 = [0.002] #[0.001, 0.002] #z0Snow
p16 = [6]# 1, 3, 6] #albedoRefresh |       1.0000 |       1.0000 |      10.0000
p17 = [4] #2, 3, 4] #mw_exp exponent for meltwater flow
p18 = [0.6] #0.2, 0.4 , 0.6] #fixedThermalCond_snow

def hru_ix_ID(p10, p11, p12, p13, p14):
    ix10 = np.arange(1,len(p10)+1)
    ix11 = np.arange(1,len(p11)+1)
    ix12 = np.arange(1,len(p12)+1)
    ix13 = np.arange(1,len(p13)+1)
    ix14 = np.arange(1,len(p14)+1)

    c = list(itertools.product(ix10,ix11,ix12,ix13,ix14))
    ix_numlist=[]
    for tup in c:
        ix_numlist.append(''.join(map(str, tup)))
    new_list = [float(i) for i in ix_numlist]

    return(new_list)  

hruidx = hru_ix_ID(p10, p11, p12, p13, p14)

hruidxID = []
for index in hruidx:
    hruidxID.append(int(index))
    
hru_num = np.size(hruidxID)
years = ['2006','2007']
out_names = [#"lj1110","lj1120","lj1130","lj1210","lj1220","lj1230","lj1310","lj1320","lj1330","lj2110","lj2120","lj2130","lj2210","lj2220","lj2230","lj2310","lj2320","lj2330",

             #"mj1110","mj1120","mj1130","mj1210","mj1220","mj1230","mj1310","mj1320","mj1330","mj2110","mj2120","mj2130","mj2210","mj2220","mj2230","mj2310","mj2320","mj2330",

             #"s2110",
             #"sj1110", "sj1120","sj1130","sj1210","sj1220","sj1230","sj1310","sj1320","sj1330","sj2120","sj2130","sj2210","sj2220","sj2230","sj2310","sj2320","sj2330",

             #"lc1111","lc1112","lc1113","lc1121","lc1122","lc1123","lc1131","lc1132","lc1133","lc1211","lc1212","lc1213","lc1221","lc1222","lc1223","lc1231","lc1232","lc1233",
             #"lc1311","lc1312","lc1313","lc1321","lc1322","lc1323","lc1331","lc1332","lc1333","lc2111","lc2112","lc2113","lc2121","lc2122","lc2123","lc2131","lc2132","lc2133",
             #"lc2211","lc2212","lc2213","lc2221","lc2222","lc2223","lc2231","lc2232","lc2233","lc2311","lc2312","lc2313","lc2321","lc2322","lc2323","lc2331","lc2332","lc2333",

             "mc1111","mc1112","mc1113","mc1121","mc1122","mc1123","mc1131","mc1132","mc1133","mc1211","mc1212","mc1213","mc1221","mc1222","mc1223","mc1231","mc1232","mc1233",
#             "mc1311","mc1312","mc1313","mc1321","mc1322","mc1323","mc1331","mc1332","mc1333","mc2111","mc2112","mc2113","mc2121","mc2122","mc2123","mc2131","mc2132","mc2133",
#             "mc2211","mc2212","mc2213","mc2221","mc2222","mc2223","mc2231","mc2232","mc2233","mc2322","mc2323","mc2331",
#
#             "sc1111","sc1112","sc1113","sc1121","sc1122","sc1123","sc1131","sc1132","sc1133","sc1211","sc1212","sc1213","sc1221","sc1222","sc1223","sc1231","sc1232","sc1233",
#             "sc1311","sc1312","sc1313","sc1321","sc1322","sc1323","sc1331","sc1332","sc1333","sc2111","sc2112","sc2113","sc2121","sc2122","sc2123","sc2131","sc2132","sc2133",
#             "sc2211","sc2212","sc2213","sc2221","sc2222","sc2223","sc2231","sc2232","sc2233","sc2311","sc2312","sc2313","sc2321","sc2322","sc2323","sc2331","sc2332","sc2333"
             ]

paramModel = (np.size(out_names))*(hru_num)
hru_names =[]
for i in out_names:
    hru_names.append(['{}{}'.format(j, i) for j in hruidxID])
hru_names1 = np.reshape(hru_names,(paramModel,1))
hru_names_df = pd.DataFrame (hru_names1)

#%%  reading output files
av_all = readAllNcfilesAsDataset(av_ncfiles)
DateSa = date(av_all,"%Y-%m-%d %H:%M")

av_sd_df = readVariablefromNcfilesDatasetasDF(av_all,'scalarSnowDepth',hru_names_df[0])
av_sd_df.set_index(pd.DatetimeIndex(DateSa),inplace=True)
av_swe_df =  readVariablefromNcfilesDatasetasDF(av_all,'scalarSWE',hru_names_df[0])
av_swe_df.set_index(pd.DatetimeIndex(DateSa),inplace=True)

#%% ploting annual swe curves
#DateSa2 = date(av_all,"%Y-%m-%d")
#sax = np.arange(0,np.size(DateSa2))
#sa_xticks = DateSa2
#safig, saax = plt.subplots(1,1, figsize=(20,15))
#plt.xticks(sax, sa_xticks[::1000], rotation=25, fontsize=20)
#saax.xaxis.set_major_locator(ticker.AutoLocator())
#plt.yticks(fontsize=20)
#for hru in hru_names_df[0]:
#    plt.plot(av_swe_df[hru])#, sbx, swe_obs2006, 'k--', linewidth=0.5)#, label='wwe', color='maroon') param_nam_list[q] color_list[q]
#
#plt.plot(swe_obs2006, 'ok', markersize=10)
#
#plt.title('rainbow_SWE', position=(0.04, 0.88), ha='left', fontsize=40)
#plt.xlabel('Time 2006-2007', fontsize=30)
#plt.ylabel('SWE(mm)', fontsize=30)
##plt.show()
#plt.savefig('SA2/swetotal.png')
#%% day of snow disappearance (based on snowdepth)-final output
av_sd_df5000 = av_sd_df[:][5000:8737]

zerosnowdate = []
for val in hru_names_df[0]:
    zerosnowdate.append(np.where(av_sd_df5000[val]==0))
zerosnowdate_omg = [item[0] for item in zerosnowdate] #change tuple to array
for i,item in enumerate(zerosnowdate_omg):
    if len(item) == 0:
        zerosnowdate_omg[i] = 3737
for i,item in enumerate(zerosnowdate_omg):
    zerosnowdate_omg[i] = zerosnowdate_omg[i]+5000
        
first_zerosnowdate =[]
for i,item in enumerate(zerosnowdate_omg):
    if np.size(item)>1:
        #print np.size(item)
        first_zerosnowdate.append(item[0])
    if np.size(item)==1:
        first_zerosnowdate.append(item)
    
#first_zerosnowdate_df = pd.DataFrame(np.reshape(first_zerosnowdate, ((np.size(hru_names1)),0)).T, columns=out_names)
dosd_df = pd.DataFrame(np.array(first_zerosnowdate)).T
dosd_df.columns = hru_names_df[0]
#first_zerosnowdate_df_obs = pd.DataFrame(np.array([[5985],[6200]]).T,columns=out_names)
dosd_obs = pd.DataFrame(np.array([5985]),columns=['2006'])

dosd_residual=[]
for hru in dosd_df.columns:
    dosd_residual.append((dosd_df[hru][0]-dosd_obs['2006'])/24)

dosd_residual_df = pd.DataFrame(np.reshape(np.array(dosd_residual),(np.size(out_names),hru_num)).T, columns=out_names)

#%%**************************************************************************************************
# *********************** finding max corespondance swe for '2007-05-09 08:50'***********************
#'2007-04-18' 4776: 4800, '2007-04-23' 4896:4920, '2007-05-02' 5112:5136
#Group1: '2007-03-12 14:00' (3902),'2007-03-19 12:30 (4068)','2007-03-26 12:30 (4236)','2007-04-02 12:30'(4404),
#Group2: '2007-04-18 08:35' (4784),'2007-04-23 10:30 (4907)','2007-05-02 08:40'(5121), 

maxSWE = readSpecificDatafromAllHRUs(av_swe_df,hru_names_df[0],5289)
maxSWE_obs = [711]  

av_swe_df2 = av_swe_df.copy(); av_swe_df2.set_index(av_swe_df['counter'],inplace=True)
realMaxSWE = av_swe_df2.max()
realMaxSWE_date = av_swe_df2.idxmax()
#%%**************************************************************************************************
# ********************** calculating snowmelt rate based on SWE *************************************
sweM1,SWE1date = SWEandSWEDateforSpecificDate(hru_names_df[0],5289,av_swe_df,dosd_df)
sweM2,SWE2date = SWEandSWEDateforSpecificDate(hru_names_df[0],5457,av_swe_df,dosd_df)
sweM3,SWE3date = SWEandSWEDateforSpecificDate(hru_names_df[0],5793,av_swe_df,dosd_df)
sweM4,SWE4date = SWEandSWEDateforSpecificDate(hru_names_df[0],5960,av_swe_df,dosd_df)
#%%
meltingrate1 = meltingRateBetween2days(sweM1,sweM2,SWE1date,SWE2date)
meltingrate2 = meltingRateBetween2days(sweM2,sweM3,SWE2date,SWE3date)
meltingrate3 = meltingRateBetween2days(sweM3,sweM4,SWE3date,SWE4date)

meltingrateAvg_mod = []
for countermr in range (np.size(meltingrate1)):
    meltingrateAvg_mod.append((meltingrate1[countermr]+meltingrate2[countermr]+meltingrate3[countermr])/3)
#%%
sweMR = [711, 550, 309, 84]
mrDate = ['2007-05-09 08:50 5289','2007-05-16 09:00 5457','2007-05-30 09:00 5793','2007-06-06 08:15 5960']  
meltingrate1_obs = np.array([0.1*24*(711-550.)/(5457.-5289)])
meltingrate2_obs = np.array([0.1*24*(550.-309)/(5793.-5457)])
meltingrate3_obs = np.array([0.1*24*(309-84.)/(5960-5793.)])
meltingrateAvg_obs = (meltingrate1_obs+meltingrate2_obs+meltingrate3_obs)/3.
#'2007-05-09 08:50':5289, to '2007-06-06 08:15': 5960, 
#swe_mm = [711, 84]
meltingRate_obs = [0.1*24*(711-84.)/(5960-5289.)] #cm/day
#
#%% defining criteria
#coldcontentcrit = [abs(values) for values in mySubtract(coldcontent0305,cc0305)]
meltingRateCrit = [abs(values) for values in mySubtract(meltingrateAvg_mod,meltingrateAvg_obs)]
maxSWEcrit = [abs(values) for values in mySubtract(maxSWE,maxSWE_obs)]

#fig = plt.figure(figsize=(20,15))
#xs = meltingRateCrit
#ys = maxSWEcrit
#plt.scatter(xs, ys)
#plt.title('criteria for best combos')
#plt.xlabel('delta_maxSWE (mm)',fontsize=20)
#plt.ylabel('delta_meltingRate (cm/day)',fontsize=20)
#plt.savefig('SA2/'+'maxswe_meltinRateAvg')

#coldcontentcrit_df = pd.DataFrame(coldcontentcrit, columns=['coldContent'])
meltingRateCrit_df = pd.DataFrame(meltingRateCrit, columns=['meltingRate'])
maxSWECrit_df = pd.DataFrame(maxSWEcrit, columns=['maxSWE'])
criteria_df = pd.concat([meltingRateCrit_df, maxSWECrit_df], axis=1) #coldcontentcrit_df, 
criteria_df.set_index(hru_names_df[0],inplace=True)
Apareto_model_param = pd.DataFrame(criteria_df.index[((criteria_df['maxSWE']) <= 70) & ((criteria_df['meltingRate'])<=0.2)].tolist()) # & ((criteria_df['coldContent'])<=7)

#%% **************************************************************************************************
## ************************** calculating cold content ************************************************
##observed cold content in each day

heatCapacityIce1 = -2102. #J kg-1 K-1
swe0305 = [0.83,0.94,0.65,0.91,0.68,0.61,0.37]; T0305 = [-0.45,-1.45,-2.45,-3.4,-5.35,-8,-4.7] #14:30 #3734
swe0312 = [0.81,0.91,0.85,0.76,0.69,0.61,0.38,0.22]; T0312 = [-0.8,-1.8,-2.4,-3.2,-3.8,-4.3,-4.6,-1] #14:00 #3902
swe0319 = [0.83,0.84,0.95,0.75,0.69,0.36,0.27,0.34]; T0319 = [-0.4,-1,-1.4,-1.5,-1.5,-1.5,-0.7,0] # 12:30 #4068
swe0326 = [0.93,0.87,0.75,0.81,0.70,0.80,0.63]; T0326 = [-0.06,-0.2,-0.2,-0.2,-0.3,-0.7,-0.3] #12;30 #4236

cc0305 = [sum(np.multiply((heatCapacityIce1/1000000.),np.multiply(swe0305,T0305)))]
cc0312 = [sum(np.multiply((heatCapacityIce1/1000000.),np.multiply(swe0312,T0312)))]
cc0319 = [sum(np.multiply((heatCapacityIce1/1000000.),np.multiply(swe0319,T0319)))]
cc0326 = [sum(np.multiply((heatCapacityIce1/1000000),np.multiply(swe0326,T0326)))]

coldContenAvg_obs = np.mean([cc0305,cc0312,cc0319])
#%% calculating modeled cold content in each day
nvolfracIce = pd.concat(readSomePartofVariableDatafromNcfilesDatasetasDF(av_all,'mLayerVolFracIce',hru_names_df[0],Apareto_model_param[0]), axis=1)
nvolfracliq = pd.concat(readSomePartofVariableDatafromNcfilesDatasetasDF(av_all,'mLayerVolFracLiq',hru_names_df[0],Apareto_model_param[0]), axis=1)
nheight = pd.concat(readSomePartofVariableDatafromNcfilesDatasetasDF(av_all,'mLayerHeight',hru_names_df[0],Apareto_model_param[0]), axis=1)
nlayerTemp =  pd.concat(readSomePartofVariableDatafromNcfilesDatasetasDF(av_all,'mLayerTemp',hru_names_df[0],Apareto_model_param[0]), axis=1)
nsnow =  pd.concat(readSomePartofVariableDatafromNcfilesDatasetasDF(av_all,'nSnow',hru_names_df[0],Apareto_model_param[0]), axis=1)
nlayer = pd.concat(readSomePartofVariableDatafromNcfilesDatasetasDF(av_all,'nLayers',hru_names_df[0],Apareto_model_param[0]), axis=1)

#%% number of snowlayer
nsnow0305 = pd.DataFrame(readSpecificDatafromAllHRUs(nsnow,Apareto_model_param[0],3734)).T; nsnow0305.columns = Apareto_model_param[0]
nsnow0312 = pd.DataFrame(readSpecificDatafromAllHRUs(nsnow,Apareto_model_param[0],3902)).T; nsnow0312.columns = Apareto_model_param[0]
nsnow0319 = pd.DataFrame(readSpecificDatafromAllHRUs(nsnow,Apareto_model_param[0],4068)).T; nsnow0319.columns = Apareto_model_param[0]
nsnow0319 = pd.DataFrame(readSpecificDatafromAllHRUs(nsnow,Apareto_model_param[0],4236)).T; nsnow0319.columns = Apareto_model_param[0]

# sum of all layers befor target layer
sumlayer0305 = pd.DataFrame(sumBeforeSpecificDatafromAllHRUs(nlayer,Apareto_model_param[0],3734)).T; sumlayer0305.columns = Apareto_model_param[0]
sumlayer0312 = pd.DataFrame(sumBeforeSpecificDatafromAllHRUs(nlayer,Apareto_model_param[0],3902)).T; sumlayer0312.columns = Apareto_model_param[0]
sumlayer0319 = pd.DataFrame(sumBeforeSpecificDatafromAllHRUs(nlayer,Apareto_model_param[0],4068)).T; sumlayer0319.columns = Apareto_model_param[0]
#%%snow layer temperature
snowlayertemp0305 = snowLayerAttributeforSpecificDate(nlayerTemp,Apareto_model_param[0],sumlayer0305,nsnow0305)
snowlayertemp0312 = snowLayerAttributeforSpecificDate(nlayerTemp,Apareto_model_param[0],sumlayer0312,nsnow0312)
snowlayertemp0319 = snowLayerAttributeforSpecificDate(nlayerTemp,Apareto_model_param[0],sumlayer0319,nsnow0319)

#%% volumetric fraction of ice in snow layers
volfracIce0305 = snowLayerAttributeforSpecificDate(nvolfracIce,Apareto_model_param[0],sumlayer0305,nsnow0305)
volfracIce0312 = snowLayerAttributeforSpecificDate(nvolfracIce,Apareto_model_param[0],sumlayer0312,nsnow0312)
volfracIce0319 = snowLayerAttributeforSpecificDate(nvolfracIce,Apareto_model_param[0],sumlayer0319,nsnow0319)

#%% volumetric fraction of liquid in snow layers
volfracLiq0305 = snowLayerAttributeforSpecificDate(nvolfracliq,Apareto_model_param[0],sumlayer0305,nsnow0305)
volfracLiq0312 = snowLayerAttributeforSpecificDate(nvolfracliq,Apareto_model_param[0],sumlayer0312,nsnow0312)
volfracLiq0319 = snowLayerAttributeforSpecificDate(nvolfracliq,Apareto_model_param[0],sumlayer0319,nsnow0319)
#%% height of each snow layer
height0305 = snowLayerAttributeforSpecificDate(nheight,Apareto_model_param[0],sumlayer0305,nsnow0305)
height0312 = snowLayerAttributeforSpecificDate(nheight,Apareto_model_param[0],sumlayer0312,nsnow0312)
height0319 = snowLayerAttributeforSpecificDate(nheight,Apareto_model_param[0],sumlayer0319,nsnow0319)

height0305layer = depthOfLayers(height0305)
height0312layer = depthOfLayers(height0312)
height0319layer = depthOfLayers(height0319)

#%% cold content in each day
def coldContentFunc(hruname,volfracLiq,volfracIce,snowlayertemp,layerHeight):
    densityofWater = 997. #kg/m³
    densityofIce = 917. #kg/m3
    heatCapacityIce2 = -2102./1000000. #Mj kg-1 m3-1
    coldcontent = []
    for nlst in range (np.size(hruname)):
        swe = np.array(sum2lists(myMultiply(volfracLiq[nlst],densityofWater/1000.),myMultiply(volfracIce[nlst],densityofIce/1000.))) #[swe] = m
        temp = np.array(mySubtract(snowlayertemp[nlst],273.2))
        HCItHS = np.array(myMultiply(heatCapacityIce2,layerHeight[nlst]))
        cct = sum(list(swe*temp*HCItHS))
        coldcontent.append(cct)
    return coldcontent

coldcontent0305 = coldContentFunc(Apareto_model_param[0],volfracLiq0305,volfracIce0305,snowlayertemp0305,height0305layer)
coldcontent0312 = coldContentFunc(Apareto_model_param[0],volfracLiq0312,volfracIce0312,snowlayertemp0312,height0312layer)
coldcontent0319 = coldContentFunc(Apareto_model_param[0],volfracLiq0319,volfracIce0319,snowlayertemp0319,height0319layer)
coldContentAvg_mod = np.mean([coldcontent0305,coldcontent0312,coldcontent0319],axis=0)


#xs = coldcontent0305
#ys = coldcontent0509
#plt.scatter(xs, ys)
#plt.xlabel('cold content 305 (Mj/m2)',fontsize=20)
#plt.ylabel('cold content 509 (Mj/m2)',fontsize=20)
#plt.savefig('SA2/'+'ccvscc')
#
##3d Plot
##fig = plt.figure(figsize=(20,15))
##ax = fig.add_subplot(111, projection='3d')
##
##xs = coldcontentcrit
##ys = meltingRateCrit
##zs = maxSWEcrit
##ax.scatter(xs, ys, zs)
##
##ax.set_xlabel('cold content (Mj/m2)',fontsize=20)
##ax.set_ylabel('melting rate (cm/day)',fontsize=20)
##ax.set_zlabel('maxSWE (mm)',fontsize=20)
##plt.savefig('SA2/'+'sc2')
##plt.show()

#%%
##for varname in av_all[0].variables.keys():
##    var = av_all[0].variables[varname]
##    print (varname, var.dtype, var.dimensions, var.shape)
#%% day of snow disappreance plot
##plt.xticks(x, hru[::3], rotation=25)
##for namefile in out_names:
##    x = list(np.arange(1,244))
##    fig = plt.figure(figsize=(20,15))
##    plt.bar(x,zerosnowdate_residual_df[namefile])
##    plt.title(namefile, fontsize=42)
##    plt.xlabel('hrus',fontsize=30)
##    plt.ylabel('residual dosd (day)', fontsize=30)
##    #vax.yaxis.set_label_coords(0.5, -0.1) 
##    plt.savefig('SA2/'+namefile)

#%%        
















    
    
    
    
    