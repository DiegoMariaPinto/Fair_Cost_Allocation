"""
Created on Mon Aug 31 12:56:16 2020
@author: Diego Maria Pinto
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def get_node(x):

    i = 0
    j = 0
    k = 0

    count = 0
    for s in x.split('_'):
        if s.isdigit():
            if count == 0:
                i = int(s)
                count += 1
                continue
            if count == 1:
                j = int(s)
                count += 1
                continue
            if count == 2:
                k = int(s)
                count += 1
                continue

    return [i,j,k]

def get_node_TL(x):

    i = 0
    k = 0

    count = 0
    for s in x.split('_'):
        if s.isdigit():
            if count == 0:
                i = int(s)
                count += 1
                continue
            if count == 1:
                k = int(s)
                count += 1
                continue

    return [i,k]


def VRP_interpreter(instance, K, x_opt, t_opt, l_opt, dis_dict, dur_dict):

    trucks = []
    for k in range(K):
        trucks.append(["motrice_" + str(k), "rimorchio_" + str(k)])
    trucks = pd.DataFrame(trucks, columns=['head', "trailer"])
    trucks = trucks.astype({'head': str, 'trailer': str})

    N = len(instance)
    K = len(trucks)
    paths = [[]]*K
    VRP_results = trucks.values.tolist()
    for k in range(K):

        x_k = x_opt.loc[x_opt["variable"].str.endswith('_'+str(k))]
        t_k = t_opt.loc[t_opt["variable"].str.endswith('_'+str(k))]
        l_k = l_opt.loc[l_opt["variable"].str.endswith('_'+str(k))]

        x_k = x_k.loc[x_opt["value"] == 1]
        if len(x_k.index) == 0:
            paths[k] = "truck not used"
            VRP_results[k].append(paths[k])
        else:
            x_k['node i']  = x_k['variable'].apply(lambda x: get_node(x)[0])
            x_k['node j']  = x_k['variable'].apply(lambda x: get_node(x)[1])
            x_k['truck k'] = x_k['variable'].apply(lambda x: get_node(x)[2])

            t_k["node i"]  = t_k["variable"].apply(lambda x: get_node_TL(x)[0])
            t_k["truck k"] = t_k["variable"].apply(lambda x: get_node_TL(x)[1])
            
            l_k["node i"]  = l_k["variable"].apply(lambda x: get_node_TL(x)[0])
            l_k["truck k"] = l_k["variable"].apply(lambda x: get_node_TL(x)[1])

            visit_order = 0

            paths[k] = [[k,visit_order,0,0,41.9552587, 12.7640889,0]]

            departure_node = 0

            ### this loop creates path info for truck k ###
            for i in range(len(x_k)):

                if departure_node == N-1:
                    break

                if len(x_k.loc[x_k['node i'] == departure_node, 'node j']) != 0:
                
                    arrival_node = x_k.loc[x_k['node i'] == departure_node, 'node j'].iloc[0]
                    
                    arrival_node_name   = instance.loc[instance['ID'] == arrival_node, 'node_name'].iloc[0]
                    arrival_node_lat    = instance.loc[instance['ID'] == arrival_node,       'lat'].iloc[0]
                    arrival_node_long   = instance.loc[instance['ID'] == arrival_node,      'long'].iloc[0]
                    arrival_node_demand = instance.loc[instance['ID'] == arrival_node,    'demand'].iloc[0]
    
                    visit_order += 1
    
                    paths[k].append([k,visit_order,arrival_node_name,arrival_node,arrival_node_lat,arrival_node_long,arrival_node_demand])
    
                    departure_node = arrival_node

            ### this loop adds time info to path of truck k ###
            for i in range(len(paths[k])):

                node = paths[k][i][3]

                arrival_time = t_k.loc[t_k["node i"] == node, "value"].iloc[0]
                node_demand  = instance.loc[instance['ID'] == node,  'demand'].iloc[0]
                if node_demand == 1:
                    service_time = (instance.loc[instance['ID'] == node,'service time'].iloc[0].minute)
                    departure_time = arrival_time + service_time/60
                elif node_demand == 2:
                    service_time = (instance.loc[instance['ID'] == node,'service time'].iloc[0].minute)*abs(node_demand)
                    departure_time = arrival_time + service_time/60
                elif node_demand == -1:
                    service_time = (instance.loc[instance['ID'] == node,'service time'].iloc[0].minute) - 5
                    departure_time = arrival_time + service_time/60
                elif node_demand == -2:
                    service_time = (instance.loc[instance['ID'] == node,'service time'].iloc[0].minute)*abs(node_demand) - 10
                    departure_time = arrival_time + service_time/60
                else:
                    departure_time = arrival_time


                hours = int(arrival_time)
                if hours > 23:
                    hours = 23
                minutes = int((arrival_time - int(arrival_time))*60)
                arrival_time = datetime.time(hour=hours, minute=minutes)

                hours = int(departure_time)
                if hours > 23:
                    hours = 23
                minutes = int((departure_time - int(departure_time))*60)
                departure_time = datetime.time(hour=hours, minute=minutes)

                leaving_load = l_k.loc[l_k["node i"] == node, "value"].iloc[0]


                paths[k][i].append(arrival_time)
                paths[k][i].append(departure_time)
                paths[k][i].append(leaving_load)

            # save complete path info as a dataframe
            paths[k] = pd.DataFrame(paths[k],columns =['truck #',"visit order","node name","node number","lat","long","load_unload","arrival time","departure time","leaving load"])
            paths[k] = paths[k].astype({'truck #': int, 'visit order': int, 'node name': int, 'node number': int,'lat':float, 'long':float, 'load_unload': int,'arrival time':str,'departure time':str,'leaving load': int})

            #####################  some time fixes regardi depot ######################
            depot_lat = 41.9555557
            depot_long = 12.7643387

            # correggo la partenza dal deposito verso il primo nodo di pickup
            depot_node = 0
            first_visit_node = paths[k].loc[1,'node number']
            lat_first_visit = instance.loc[instance['ID'] == first_visit_node, 'lat'].iloc[0]
            long_first_visit = instance.loc[instance['ID'] == first_visit_node, 'long'].iloc[0]
            temp = dur_dict[(depot_lat, depot_long, lat_first_visit, long_first_visit)]  # float of hours
            departure_time_from_depot = t_k.loc[t_k["node i"] == first_visit_node, "value"].iloc[0] - temp

            hours = int(departure_time_from_depot)
            minutes = int((departure_time_from_depot - int(departure_time_from_depot)) * 60)
            departure_time_from_depot = datetime.time(hour=hours, minute=minutes)
            paths[k].loc[0, "departure time"] = departure_time_from_depot

            if (paths[k].iloc[-2]["lat"] == depot_lat) and (paths[k].iloc[-2]["long"] == depot_long):
                paths[k].loc[len(paths[k])-1,"arrival time"]   = paths[k].iloc[-2]['departure time']
                paths[k].loc[len(paths[k])-1,"departure time"] = paths[k].iloc[-2]['departure time']

            else:
                lat_from = paths[k].loc[len(paths[k]) - 2,'lat']
                long_from = paths[k].loc[len(paths[k]) - 2,'long']
                if (lat_from,long_from,depot_lat,depot_long) in dur_dict.keys():
                    temp = dur_dict[(lat_from,long_from,depot_lat,depot_long)] # float of hours
                    last_departure = datetime.datetime.strptime(paths[k].iloc[-2]['departure time'], '%H:%M:%S').time() # from string to datetime.time
                    last_departure = last_departure.hour + last_departure.minute/60 # from datetime.time to float of hours (e.g., 1.5 = 1 hours and 30 minutes)
                    last_arrival   = last_departure + temp # float of hours
                    hours   = int(last_arrival)
                    minutes = int((last_arrival - int(last_arrival))*60)
                    last_arrival = str(datetime.time(hour=hours, minute=minutes)) # from float of hours to datetime.time to string
                    paths[k].loc[len(paths[k]) - 1, "arrival time"] = last_arrival

            ############################################################

            VRP_results[k].append(paths[k])

    return VRP_results
