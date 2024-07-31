#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  9 11:33:19 2021

@author: diego
"""

## [Clark and Wright] allocazione con Ci / Ctot secondo disuguaglianze trinagolari nodo precedente e successivo
## al nodo i_pickup e i_delivery --> costi di 4 archi in totale / Ctot.

import pandas as pd
import numpy as np
from datetime import datetime, date


def get_C_tot(df_truck_k,distance):
    
    df = df_truck_k
    C_tot = 0
    for index, row in df.iterrows():
        if index == (len(df)-1):
            break
        i = row['node number']
        j = df['node number'][index+1]
        C_tot += distance[i,j]
        
    return C_tot
    

def get_C_consecutivePD(df_truck_k,distance,node_p_index,node_d_index):
    
    df = df_truck_k
    cost = 0
    i = df['node number'][node_p_index-1]
    j = df['node number'][node_p_index]
    cost += distance[i,j]
    i = df['node number'][node_p_index]
    j = df['node number'][node_d_index]
    cost += distance[i,j]
    i = df['node number'][node_d_index]
    j = df['node number'][node_d_index+1]
    cost += distance[i,j]
    
    return cost

def get_C_non_consecutivePD(df_truck_k,distance,node_p_index,node_d_index):
    
    df = df_truck_k
    cost = 0
    i = df['node number'][node_p_index-1]
    j = df['node number'][node_p_index]
    cost += distance[i,j]
    i = df['node number'][node_p_index]
    j = df['node number'][node_p_index+1]
    cost += distance[i,j]
    
    i = df['node number'][node_d_index-1]
    j = df['node number'][node_d_index]
    cost += distance[i,j]
    i = df['node number'][node_d_index]
    j = df['node number'][node_d_index+1]
    cost += distance[i,j]
    
    return cost

def get_truck_k_of_mission_i(mission,VRP_results,distance):
    node_p = mission.node_pickup.ID_name
    node_d = mission.node_delivery.ID_name
    check = 'not found'
    for truck_k in range(len(VRP_results)):
        df_truck_k = 'not_found_yet'
        res = VRP_results[truck_k]
        if isinstance(res[2], str) == True:
            continue
        elif len(res[2]) < 4:
            continue
        else:
            if node_p in res[2]['node name'].values:
                if node_d in res[2]['node name'].values:
                    df_truck_k = res[2]
                    check = 'found'
                    break  
    return check, truck_k, df_truck_k, node_p, node_d


def get_C_k_i(mission,VRP_results,distance):
                    
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission,VRP_results,distance)
            
    if check == 'not found':
        return np.nan, np.nan, np.nan
    
    C_tot = get_C_tot(df_truck_k,distance)
    
    if len(df_truck_k) == 4:
        C_k_i = C_tot
    else:
        node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
        node_d_index = df_truck_k['node name'][df_truck_k['node name'] == node_d].index[0]
        if node_d_index == node_p_index + 1:
            C_k_i = get_C_consecutivePD(df_truck_k,distance,node_p_index,node_d_index)
        else:
            C_k_i = get_C_non_consecutivePD(df_truck_k,distance,node_p_index,node_d_index)

    return C_k_i, C_tot, truck_k


def get_ClarkeWright_distance(missions_obj_list,VRP_results,distance):
    
    ClarkeWright_list = []
    for mission in missions_obj_list:
        
        node_p = mission.node_pickup.ID_name
        node_d = mission.node_delivery.ID_name
        C_k_i, C_tot, truck_k = get_C_k_i(mission,VRP_results,distance)
        
        ClarkeWright_list.append([node_p,node_d,C_k_i,C_tot,truck_k])
    
    df_ClarkeWright = pd.DataFrame(ClarkeWright_list, columns = ['node_p','node_d','C_k_i','C_tot','truck_k'])
    df_ClarkeWright.astype({'node_p': int, 'node_d': int, 'C_k_i': float, 'C_tot': float})
    
    df_ClarkeWright.dropna(inplace = True)
        
    return df_ClarkeWright


def allocate_vrp_cost_distance(mission,VRP_results,distance,df_ClarkeWright,dist_unit_cost):
    
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission,VRP_results,distance)
    
    if check == 'not found':
        return np.nan
    
    df = df_ClarkeWright[df_ClarkeWright['truck_k'] == truck_k]
    
    sum_of_Cki = df['C_k_i'].sum()
        
    C_k_i = df[(df['node_p'] == node_p) & (df['node_d'] == node_d)]['C_k_i'].iloc[0]
    C_tot = df[(df['node_p'] == node_p) & (df['node_d'] == node_d)]['C_tot'].iloc[0]
    
    mission_distance_cost = (C_k_i/sum_of_Cki)*C_tot*dist_unit_cost ## da
    mission_truck_cost = 0

    mission_cost = mission_distance_cost + mission_truck_cost

    return mission_cost
    
    
    
def allocate_distance_features(mission,VRP_results,distance,df_ClarkeWright,dist_unit_cost):
    
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission,VRP_results,distance)
    
    if check == 'not found':
        return np.nan, np.nan, np.nan, np.nan
    
    node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
    node_d_index = df_truck_k['node name'][df_truck_k['node name'] == node_d].index[0]
    
    p = df_truck_k['node number'][node_p_index]
    d = df_truck_k['node number'][node_d_index]
    
    dist_to_pickup_node   = round(distance[0,p],2) # distanza nodo pick up  del cliente dal depot
    dist_to_delivery_node = round(distance[0,d],2) # distanza nodo delivery del cliente dal depot
    dist_from_p_to_d =      round(distance[p,d],2) # distanza nodo pick up e nodo delivery
        
    tour_len = int((len(df_truck_k) - 2) / 2) # lunghezza del tour --> numero dei clienti serviti dal truck 

    # la distanza dal deposito al pickup, quindi al delivery e quindi al deposito a rapporto con la c_tot del tour
    C_tot = get_C_tot(df_truck_k,distance)
    
    df = df_truck_k
    cost_p_and_d = 0 
    i = df['node number'][0]
    j = df['node number'][node_p_index]
    cost_p_and_d += distance[i,j]
    i = df['node number'][node_p_index]
    j = df['node number'][node_d_index]
    cost_p_and_d += distance[i,j]
    i = df['node number'][node_d_index]
    j = df['node number'][0]
    cost_p_and_d += distance[i,j]
    
    cost_p_and_d = round(cost_p_and_d/C_tot,2)
    
    return dist_to_pickup_node, dist_to_delivery_node, dist_from_p_to_d, tour_len, cost_p_and_d


 # capacità residua in termini di tempo residuo alla fine del tour prima della fine del turno (18:00)
def allocate_residual_time(mission,VRP_results,distance,df_ClarkeWright,duration,nodes_obj_list):
    
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission,VRP_results,distance)
    
    if check == 'not found':
        return np.nan

    departure_time = datetime.strptime(df_truck_k['departure time'].iloc[0], '%H:%M:%S').time()
    returning_time = datetime.strptime(df_truck_k['arrival time'].iloc[-1], '%H:%M:%S').time()

    travel_time = datetime.combine(date.today(), returning_time) - datetime.combine(date.today(), departure_time)
    travel_time = int(travel_time.total_seconds()/60) # minutes

    res_time = 8*60 - travel_time

    if res_time < 0:
        res_time = 0
            
    return res_time
    


        
    
    
    
# if __name__ == "__main__":

#     df = pd.read_excel("df_sol.xlsx")
#     distance = pd.read_excel("distance_example.xlsx")
        
    
    
    
    
    
    
    
    
    
    
    
    