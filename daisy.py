import numpy as np
import pandas as pd
import os
import math as mt
os.chdir("D:\Daisy")
data=[]
for i in range(7):
    data_sub = pd.read_csv("track_"+str(i+1)+".csv",header=None)
    data.append(data_sub)



# try tier combinations:
list=[]
tier = [0,2,3,4,6]
acceleration = [10,15,20,25,30]
breaking = [-10,-15,-20,-25,-30]
v_max = [10,20,30,40,50]
gas = [500,750,1000,1250,1500]
tire = [500,750,1000,1250,1500]
handling = [9,12,15,18,21]

total_info=[]
for a in range(5):
    for b in range(5):
        for c in range(5):
            for d in range(5):
                for e in range (5):
                    for f in range(5):
                        cost =tier[a]+tier[b]+tier[c]+tier[d]+tier[e]+tier[f]
                        if (cost<=18) & (cost >15): # capped at 16,17,18
                            result = [a,b,c,d,e,f]
                            list.append(result)
                            result = tuple(result)
                            total_info.append([result,acceleration[a],breaking[b],v_max[c],\
                            gas[d],tire[e],handling[f]])
v_limit_total=[]  

################  encapsulate into one training per car model
# Waited for innitalize a_0, randomize inputs, threshold function 
Testing_result = [] # ultimate result for all car models                           
for car_model in total_info:
    # simulation_run(car_model[0], car_model[1], car_model[2],car_model[3], car_model[4],\
    #                 car_model[5],car_model[6],data[0][0])
    v_limit = []
    track=data[0][0] # for track 0
    for i in range(len(track)-2):
        H = np.float64(track[i+1])
        if H>=0.0:
            v_limit.append(mt.sqrt(car_model[6]*H/1000000))
        else :
            v_limit.append(-1)
    v_limit_total.append(v_limit)
    
    i = 1
    a=np.zeros(1001)
    v=np.zeros(1001)
    g=np.zeros(1001)
    w=np.zeros(1001)
    t=np.zeros(1001)
    pit_stop=np.zeros(1001)
    while (i <=1000):
        no_gas = 0
        tire_break = 0
        if a[i]>0:
            v[i+1] = mt.sqrt(v[i]**2+2*a[i]*1)
            g[i+1] = g[i] - 0.1* (a[i]**2)
            if g[i+1]<0:
                no_gas = 1
                w[i+1] = w[i]
                t[i]=(v[i+1]-v[i])/a[i]
                
        elif a[i]<0:
            v_fa = v[i]**2 + 2*a[i]*d
            if v_fa>0: 
                v[i+1]=mt.sqrt(v[i]**2+2*a[i]*d)
            elif v_fa<0:
                a[i]=-(v[i]**2)/2/1    
            else:
                if tire_break | no_gas:
                    pit_stop[i+1] = 1
                    g[i+1] = car_model[4]
                    w[i+1] = car_model[5]
            w[i+1] = w[i] - 0.1*a[i]**2 # wait to be fixed
            
            if w[i+1]< threshold # wait to be implemented
                a[i] = -(v[i]**2)/2/1
                tire_break=1
                continue
            else:
                if !tire_break & !no_gas:
                    g[i+1] = g[i]
                t[i] = (v[i+1]-v[i])/a[i]  
                      
        else:  
            g[i+1] = g[i]
            w[i+1] = w[i]
            v[i+1] = v[i]
            t[i]=1/v[i]
        
        i++
    
    sum_t=0
    for d_t in t:
        sum_t += d_t
        
    print ("time for car model %s is %f").format(car_model[0], sum_t)   
                
                
                
                
                
                 

    