#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 15:57:07 2021

@author: administrator
"""


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

# df = pd.read_excel("df_sol.xlsx")
# duration = pd.read_excel("duration_example.xlsx")

def get_C_tot_duration(df_truck_k,duration):
    
    df = df_truck_k
    C_tot = 0
    for index, row in df.iterrows():
        if index == (len(df)-1):
            break
        i = row['node number']
        j = df['node number'][index+1]
        C_tot += duration[i,j]
        
    return C_tot
    

def get_C_consecutivePD_duration(df_truck_k,duration,node_p_index,node_d_index):
    
    df = df_truck_k
    cost = 0
    i = df['node number'][node_p_index-1]
    j = df['node number'][node_p_index]
    cost += duration[i,j]
    i = df['node number'][node_p_index]
    j = df['node number'][node_d_index]
    cost += duration[i,j]
    i = df['node number'][node_d_index]
    j = df['node number'][node_d_index+1]
    cost += duration[i,j]
    
    return cost

def get_C_non_consecutivePD_duration(df_truck_k,duration,node_p_index,node_d_index):
    
    df = df_truck_k
    cost = 0
    i = df['node number'][node_p_index-1]
    j = df['node number'][node_p_index]
    cost += duration[i,j]
    i = df['node number'][node_p_index]
    j = df['node number'][node_p_index+1]
    cost += duration[i,j]
    
    i = df['node number'][node_d_index-1]
    j = df['node number'][node_d_index]
    cost += duration[i,j]
    i = df['node number'][node_d_index]
    j = df['node number'][node_d_index+1]
    cost += duration[i,j]
    
    return cost

def get_truck_k_of_mission_i_duration(mission,VRP_results,duration):
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


def get_C_k_i_duration(mission,VRP_results,duration):
                    
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i_duration(mission,VRP_results,duration)
            
    if check == 'not found':
        return np.nan, np.nan, np.nan
    
    C_tot = get_C_tot_duration(df_truck_k,duration)
    
    if len(df_truck_k) == 4:
        C_k_i = C_tot
    else:
        node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
        node_d_index = df_truck_k['node name'][df_truck_k['node name'] == node_d].index[0]
        if node_d_index == node_p_index + 1:
            C_k_i = get_C_consecutivePD_duration(df_truck_k,duration,node_p_index,node_d_index)
        else:
            C_k_i = get_C_non_consecutivePD_duration(df_truck_k,duration,node_p_index,node_d_index)

    return C_k_i, C_tot, truck_k


def get_ClarkeWright_duration(missions_obj_list,VRP_results,duration):
    
    ClarkeWright_list = []
    for mission in missions_obj_list:
        
        node_p = mission.node_pickup.ID_name
        node_d = mission.node_delivery.ID_name
        C_k_i, C_tot, truck_k = get_C_k_i_duration(mission,VRP_results,duration)
        
        ClarkeWright_list.append([node_p,node_d,C_k_i,C_tot,truck_k])
    
    df_ClarkeWright_duration = pd.DataFrame(ClarkeWright_list, columns = ['node_p','node_d','C_k_i','C_tot','truck_k'])
    df_ClarkeWright_duration.astype({'node_p': int, 'node_d': int, 'C_k_i': float, 'C_tot': float})
    
    df_ClarkeWright_duration.dropna(inplace = True)
        
    return df_ClarkeWright_duration


def allocate_vrp_cost_duration(mission,VRP_results,duration,df_ClarkeWright_duration,time_unit_cost):
    
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i_duration(mission,VRP_results,duration)
    
    if check == 'not found':
        return np.nan
    
    df = df_ClarkeWright_duration[df_ClarkeWright_duration['truck_k'] == truck_k]
    
    sum_of_Cki = df['C_k_i'].sum()
        
    C_k_i = df[(df['node_p'] == node_p) & (df['node_d'] == node_d)]['C_k_i'].iloc[0]
    C_tot = df[(df['node_p'] == node_p) & (df['node_d'] == node_d)]['C_tot'].iloc[0]
    
    mission_cost = (C_k_i/sum_of_Cki)*C_tot
        
    return mission_cost*time_unit_cost 
    
    
        
   

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    