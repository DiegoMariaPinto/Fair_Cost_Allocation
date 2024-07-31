from Functions_files.VRP_cost_allocation_appro_SHAPLEY_O1 import appro_1
from Functions_files.VRP_cost_allocation_appro_SHAPLEY_O2 import appro_2
from Functions_files.VRP_cost_allocation_SHAPLEY import shapley
import pandas as pd
pd.options.mode.chained_assignment = None
from Functions_files.VRP_instances_functions import get_missions_list_bydate
import numpy as np

def allocate_VRP_Shapleys(inst_date, df, nodes_dict, VRP_results, gap, distance, duration, dist_unit_cost, time_unit_cost, o_opt, gamma_opt, dis_dict):

    missions_obj_list = get_missions_list_bydate(inst_date, df, nodes_dict)

    approach = 'shapley' # shapley
    df_distance_shapley = allocate_travel_disdur_shapleys(missions_obj_list, VRP_results, distance, approach)
    df_duration_shapley = allocate_travel_disdur_shapleys(missions_obj_list, VRP_results, duration, approach)
    approach = 'appro_1' # appro_1
    df_distance_appro_1 = allocate_travel_disdur_shapleys(missions_obj_list, VRP_results, distance, approach)
    df_duration_appro_1 = allocate_travel_disdur_shapleys(missions_obj_list, VRP_results, duration, approach)
    approach = 'appro_2' # appro_2
    df_distance_appro_2 = allocate_travel_disdur_shapleys(missions_obj_list, VRP_results, distance, approach)
    df_duration_appro_2 = allocate_travel_disdur_shapleys(missions_obj_list, VRP_results, duration, approach)

    VRP_costs = []
    mission_num = 0
    for mission in missions_obj_list:

        mission_allocated_km_shapley = get_C_star(mission, VRP_results, df_distance_shapley)
        mission_allocated_km_appro_1 = get_C_star(mission, VRP_results, df_distance_appro_1)
        mission_allocated_km_appro_2 = get_C_star(mission, VRP_results, df_distance_appro_2)

        mission_allocated_min_shapley = get_C_star(mission, VRP_results, df_duration_shapley)
        mission_allocated_min_appro_1 = get_C_star(mission, VRP_results, df_duration_appro_1)
        mission_allocated_min_appro_2 = get_C_star(mission, VRP_results, df_duration_appro_2)

        # get pick up node data
        ID_name_P = mission.node_pickup.ID_name
        lat_P , long_P = mission.node_pickup.lat, mission.node_pickup.long

        # get delivery node data
        ID_name_D = mission.node_delivery.ID_name
        lat_D , long_D = mission.node_delivery.lat, mission.node_delivery.long

        VRP_costs.append([inst_date, ID_name_P, ID_name_D,
                          lat_P, long_P, lat_D, long_D,
                          mission_allocated_km_shapley, mission_allocated_km_appro_1, mission_allocated_km_appro_2,
                          mission_allocated_min_shapley, mission_allocated_min_appro_1, mission_allocated_min_appro_2])

        mission_num += 1

    return VRP_costs



def allocate_travel_disdur_shapleys(missions_obj_list, VRP_results, disdur, approach):

    # get each TSP dataframe of the overall instance dataframe
    df_TSP_list = []
    for mission in missions_obj_list:
        check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)
        if [truck_k, df_truck_k] not in df_TSP_list:
            df_TSP_list.append([truck_k, df_truck_k])

    # get each TSP matrix of the overall dis or dur matrix, according to disdur input
    df_TSP_res_list = []
    for df_TSP in df_TSP_list:
        df_TSP = df_TSP[1] # actually the df is the second element of each list component, 0 is the truck
        TSP_indexes = df_TSP['node number'].to_list()
        TSP_matrix = disdur[np.ix_(TSP_indexes, TSP_indexes)]

        ##############################################################
        if approach == 'shapley':
            res = shapley(TSP_matrix=TSP_matrix)
            print(res)
            df_TSP_res = df_TSP[df_TSP['node name'] != 0]
            df_TSP_res = df_TSP_res[['truck #','node name', 'node number', 'lat', 'long']]
            df_TSP_res[approach + '_val'] = res
            df_TSP_res_list.append(df_TSP_res)

        elif approach == 'appro_1':
            res = appro_1(TSP_matrix=TSP_matrix)
            df_TSP_res = df_TSP[df_TSP['node name'] != 0]
            df_TSP_res = df_TSP_res[['truck #','node name', 'node number', 'lat', 'long']]
            df_TSP_res[approach + '_val'] = res
            df_TSP_res_list.append(df_TSP_res)

        elif approach == 'appro_2':
            res = appro_2(TSP_matrix=TSP_matrix)
            df_TSP_res = df_TSP[df_TSP['node name'] != 0]
            df_TSP_res = df_TSP_res[['truck #','node name', 'node number', 'lat', 'long']]
            df_TSP_res[approach + '_val'] = res
            df_TSP_res_list.append(df_TSP_res)

        ##############################################################

    df_TSP_res = pd.concat(df_TSP_res_list)

    disdur_list = []
    for mission in missions_obj_list:
        # devo prednere il c_k_i (ossia il costo del camion k associato secondo l'approccio scelto al cliente i)
        # data una missione, riconoscere quale truck k la ha svolta
        check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)
        # e' il camion truck_k che ha percorso un totale di c_tot (km o ore)
        C_tot = get_C_tot(df_truck_k, disdur)
        mission_res = df_TSP_res[df_TSP_res['truck #'] == truck_k]
        C_k_i_P = mission_res[mission_res['node name'] == node_p][approach + '_val'].iloc[0]
        C_k_i_D = mission_res[mission_res['node name'] == node_d][approach + '_val'].iloc[0]
        C_k_i = C_k_i_P + C_k_i_D

        disdur_list.append([node_p, node_d, C_k_i_P, C_k_i_D, C_k_i, C_tot, truck_k])

    df_disdur_approach = pd.DataFrame(disdur_list, columns=['node_p', 'node_d', 'C_k_i_P', 'C_k_i_D','C_k_i', 'C_tot', 'truck_k'])
    df_disdur_approach.astype({'node_p': int, 'node_d': int, 'C_k_i_P': float,'C_k_i_D': float, 'C_k_i': float, 'C_tot': float})

    return df_disdur_approach


def get_C_star(mission, VRP_results, df_disdur_approach):
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    if check == 'not found':
        return np.nan

    df = df_disdur_approach[df_disdur_approach['truck_k'] == truck_k]

    sum_of_Cki = df['C_k_i'].sum()

    C_k_i = df[(df['node_p'] == node_p) & (df['node_d'] == node_d)]['C_k_i'].iloc[0]
    C_tot = df[(df['node_p'] == node_p) & (df['node_d'] == node_d)]['C_tot'].iloc[0]

    if sum_of_Cki < 0.00005:
        print('AOO00')

    try:
        c_i_star = (C_k_i / sum_of_Cki) * C_tot
    except Exception as e:
        print(df)
        print('C_k_i :' + str(C_k_i))
        print('sum_of_Cki :'+str(sum_of_Cki))
        print('C_tot :' + str(C_tot))

    return c_i_star

def get_truck_k_of_mission_i(mission, VRP_results):
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


def get_C_tot(df_truck_k, disdur):
    df = df_truck_k
    C_tot = 0
    for index, row in df.iterrows():
        if index == (len(df) - 1):
            break
        i = row['node number']
        j = df['node number'][index + 1]
        C_tot += disdur[i, j]

    return C_tot

def get_C_k_i(mission, VRP_results):
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    if check == 'not found':
        return np.nan, np.nan, np.nan
        print('truck not found')

    node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
    node_d_index = df_truck_k['node name'][df_truck_k['node name'] == node_d].index[0]


    C_k_i = shapley_res[node_d_index-1] + shapley_res[node_p_index-1]



    return C_k_i
