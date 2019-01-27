import numpy as np
import pandas as pd
import os
import math as mt


#Globals:
data=[]
total_info=[]
tier = [0,2,3,4,6]
acceleration = [10,15,20,25,30]
breaking = [-10,-15,-20,-25,-30]
v_max = [10,20,30,40,50]
gas = [500,750,1000,1250,1500]
tire = [500,750,1000,1250,1500]
handling = [9,12,15,18,21]

def init():
    os.chdir("D:\Daisy")
    for i in range(7):
        data_sub = pd.read_csv("track_"+str(i+1)+".csv",header=None)
        data.append(data_sub)
    for a in range(5):
        for b in range(5):
            for c in range(5):
                for d in range(5):
                    for e in range (5):
                        for f in range(5):
                            cost =tier[a]+tier[b]+tier[c]+tier[d]+tier[e]+tier[f]
                            if (cost<=18) & (cost >15): # capped at 16,17,18
                                result = [a,b,c,d,e,f]
                                result = tuple(result)
                                total_info.append([result,acceleration[a],breaking[b],v_max[c],\
                                gas[d],tire[e],handling[f]])