import numpy as np
import pandas as pd
import os
import math as mt


# Globals:

# all track radius points
data=[]

# all cars info
total_info=[]
tier = [0,2,3,4,6]
acceleration = [10,15,20,25,30]
breaking = [-10,-15,-20,-25,-30]
v_max = [10,20,30,40,50]
gas = [500,750,1000,1250,1500]
tire = [500,750,1000,1250,1500]
handling = [9,12,15,18,21]



def init():
    # load all the tracks    
    os.chdir("D:\Daisy")
    for i in range(8): 
        data_sub = pd.read_csv("track_"+str(i+1)+".csv",header=None)
        data.append(data_sub)
        
    # test all possible combinations of tiers and find qualified models     
    for a in range(5):
        for b in range(5):
            for c in range(5):
                for d in range(5):
                    for e in range (5):
                        for f in range(5):
                            total_cost =tier[a]+tier[b]+tier[c]+tier[d]+tier[e]+tier[f]
                            if (total_cost <= 18) & (total_cost > 17):  # total cost capped at 16,17,18
                                cost = tuple([a,b,c,d,e,f])
                                total_info.append([cost, acceleration[a], breaking[b], v_max[c], \
                                gas[d], tire[e], handling[f]])  # append qualified car models into total_info

def one_car_run(track, car_model, input_per, acc_indicator):  ##### track1 <=> data[0][0]
    
    # calculation of velocity limits
    v_limit = [0]  # v_limit[i]: velocity limit between control points i and i+1
    H = car_model[6]  # handling of the selected car model
    j = 1
    while j<len(track):  # index ranges from 1 to 1000
        r = np.float64(track[j])  # radius of the track at point i 
        if r >= 0.0:
            v_limit.append(mt.sqrt(H*r/1000000))
        else:
            v_limit.append(car_model[3])
        j += 1
    v_limit.append(1000000)  # 1001-th end control point
    
    # variable initialization
    i = 1  # total of 1001 control points
    a=np.zeros(1001)  # a[i]: acceleration from i to i+1
    t=np.zeros(1001)  # t[i]: time differential from i to i+1
    v=np.zeros(1002)  # v[i]: velocity at i
    g=np.zeros(1002)  # g[i]: gas remaining at i
    w=np.zeros(1002)  # w[i]: tire remaining at i
    pit_stop=np.zeros(1001)  # pit_stop[i]: pitstop at control point i -> 1 = yes, 0 = no
    
    no_gas = 0  # no_gas: 1 = not enough gas for acceleration after control point i+1
    tire_break = 0  # tire_break: 1 = tire cannot support braking after control point i+1
    fail = 0  # fail: 1 = non-qualified set of accelerations
    
    v[1] = 0
    g[1] = car_model[4]
    w[1] = car_model[5]
    
    dec_max = 0
    dec_min = -999
    
    while (i <= 1000):
        
        # print("{} --------------------------------------------".format(i))
        
        # calculate the acceleration based on randomly generated percentage input_per
        if acc_indicator[i] == 0:
            v_m = min(car_model[3], v_limit[i], v_limit[i+1])
            if v_m < v[i]:
                acc_indicator[i] = 2
                continue
            elif v_m == v[i]:
                acc_indicator[i] = 1
                continue
            else:
                acc_max = min((v_m**2-v[i]**2)/2/1, car_model[1])
                a[i] = acc_max * input_per[i]*0.8    # customized!!!!!!!!!!!!!!!!!!!!
                
        elif acc_indicator[i] == 1:
            if i == 1:
                acc_indicator[i] = 0
                continue
            else:
                a[i] = 0
            
        else:
            if i == 1:
                acc_indicator[i] = 0
                continue
            if v[i] <= v_limit[i+1]:
                dec_max = 0
            else:
                dec_max = (v_limit[i+1]**2-v[i]**2)/2/1
            
            dec_min = car_model[2]
            dec_len = dec_max - dec_min
            
            if dec_min > dec_max:
                fail = 1
                
                # print("not possible")
                break
            else:
                a[i] = dec_min + dec_len * input_per[i]
        
               
        # print("acc[i], v[i], dec_max, dec_min {}, {}, {}, {} ".format(a[i], v[i], dec_max, dec_min))   
        
        
        # from control point i to i+1
        
        if (v[i] == 0) & (not (acc_indicator[i] == 0)):
            acc_indicator[i] = 0
            continue
        
        if a[i] > 0:  # acceleration
            v[i+1] = mt.sqrt(v[i]**2 + 2*a[i]*1)
            if g[i] == 0:  # zero gas to start with -> change to a non-positive acceleration
                no_gas = 1
                acc_indicator[i] = 1 + round(np.random.random())
                continue
            else:
                g[i+1] = g[i] - 0.1 * (a[i]**2)
                if g[i+1] < 0:  # not enough gas for acceleration -> reach next control point with zero remaining gas
                    no_gas = 1
                    # print("no gas at {}".format(i+1))
                    g[i+1] = 0
                w[i+1] = w[i]
                t[i] = (v[i+1]-v[i])/a[i]
                
                
        elif a[i] < 0:  # deceleration
            if (a[i] < car_model[2]) | (a[i] > (v_limit[i+1]**2-v[i]**2)/2/1):
                fail = 1
                # print("point 2 >>>>>>>>>>>>>>>>>>>>")
                break
                
            rad = v[i]**2 + 2*a[i]*1  # radicand of the square root
            if rad > 0:
                v[i+1] = mt.sqrt(rad)
            elif rad < 0:  # car never reaches the next point -> adjust the acceleration to reach with zero velocity
                a[i] = -(v[i]**2)/2/1    
                v[i+1] = 0
            else:  # car comes to a stop at the next control point
                v[i+1] = 0
           
            w[i+1] = w[i] - 0.1*a[i]**2
            if (w[i] < ((0.1*(a[i]**2))*1.5)) & (not tire_break):  
            # threshold is set to be 1.5 of the tire wearing -> replace tire at i+1
                a[i] = -(v[i]**2)/2/1
                tire_break = 1
                # print("tire break at {}".format(i+1))
                continue
                
            if tire_break | no_gas:
                pit_stop[i+1] = 1
                g[i+1] = car_model[4]
                w[i+1] = car_model[5]
                no_gas = 0
                tire_break = 0
                t[i] = (v[i+1]-v[i])/a[i] + 30
                # print("pit stop at {}".format(i+1))
            else:
                g[i+1] = g[i]
                t[i] = (v[i+1]-v[i])/a[i]  
                         
        
        else:  # zero acceleration
            if v[i] > v_limit[i+1]:
                acc_indicator[i] = 2
                continue
            else:
                g[i+1] = g[i]
                w[i+1] = w[i]
                v[i+1] = v[i]
                t[i] = 1/v[i]
        # print("left gas and tire {} {}".format(g[i],w[i]))
        i += 1
    
   
   # sum over all time differentials to get the overall time
    if not fail:
        sum_t=0
        for d_t in t:
            sum_t += d_t
        # print ("time for car model {} is {} _____________".format(car_model[0], sum_t))
        return a, pit_stop, sum_t
    else:
        # print ("failed at control point %d"%(i))
        # print("no_gas, tire_break, {} {}".format(no_gas, tire_break))
        return 0, 0, 0
    
    
    
    
def one_car_training(tracks, car_model, acc_input_all, acc_indicator_all):
    one_car = []
    one_car.append(car_model[0]) # pin the serial number of the car
    track_num = 0
    for track in tracks:
        track_num+=1
        current_time = 10000000000
        n_acc = []
        n_pit = []
           
        for i in range(len(acc_input_all)):
            acc_input = acc_input_all[i]
            acc_indicator = acc_indicator_all[i]
            acc, pit, times = one_car_run(track[0], car_model, acc_input,acc_indicator)
            # acc is 1-dimension list acceleration for one car one track 
            # pit is 1-dimension list pit position for one car one track
            # times is float point for one car one track
            
            if (times < current_time) & (times !=0) :
                n_acc = acc
                n_pit = pit
                current_time = times
        # collect result
    # put into one version: [car_model #,(track#, time, n_acc, n_pit), .... for 8 tracks
        one_car.append(tuple([track_num, current_time, n_acc, n_pit]))         
    
    #calculate score for this car
    score = 0
    for tup in one_car[1:]:
        if tup[0] == 1 | tup[0] == 7 | tup[0] == 8:
            score += tup[0]
        elif tup[0] == 2 | tup[0] == 3 | tup[0] == 4:
            score += tup[0]*0.25
        elif tup[0] == 5 | tup[0] == 6:
            score += tup[0]*0.5
    return score, one_car

def output_csv(name, pit, acc):
    acc_l = ["a"]
    acc_l.extend(list(acc))
    df = pd.DataFrame(acc_l)
    # df = df.T
    df.to_csv(name)
    name = "second"+name
    pit_l = ["pit_stop"]
    pit_l.extend(list(pit))
    df = pd.DataFrame(pit_l)
    # df = df.T
    df.to_csv(name)
    print(df)
    return df
    
    
def random_random_100_input(size):
    output = []
    indicator=[]
    for i in range (size):
        output.append(list(np.random.random(1001)))
        indicator.append(list(np.random.randint(3, size=1001)))
    return output, indicator 
    

init()
car_model = [tuple([0,0,1,3,4,4]),acceleration[0],breaking[0],v_max[1],gas[3],tire[4],handling[4]]

output, indicator = random_random_100_input(500)
score, one_car = one_car_training(data, car_model, output, indicator)
for i in range(len(one_car)-1):
    row = one_car[i+1]
    name = "instruction_{}.csv".format(row[0])
    pit = row[3]
    acc = row[2]
    df = output_csv(name, pit, acc)