# coding=utf-8

from workalendar.europe import Italy
from Functions_files.VRP_OSM_DistTime import OSM
# from OR_models.VRP_model_OR2_Gurobi import VRP_model
from OR_models.VRP_model_OR2_Gurobi_v2 import VRP_model_v2 as VRP_model
from datetime import datetime, timedelta, date, time
import numpy as np
from .Classes import VRP_node, VRP_inst, VRP_mission, Inst_SLWA
import pandas as pd
from json import *
import json


def create_nodes_dict(df_latlong, params):

    tw_LB            = params['tw_LB']
    tw_UB            = params['tw_UB']
    S_time           = params['s_time']
    Perc_smallparts  = params['perc_smallparts']
    Perc_trash       = params['perc_trash']

    ID = 1

    nodes_dict = {}

    for i, node in df_latlong.iterrows():

        tw_lb = time(int(tw_LB[i]), int(np.random.randint(0,50)), 0)
        tw_ub = time(int(tw_UB[i]), int(np.random.randint(0,50)), 0)
        s_time = time(0, int(S_time[i]), 0)
        perc_smallparts = round((Perc_smallparts[i]), 3)
        perc_trash = round((Perc_trash[i]), 3)

        object_node = VRP_node(ID, node['lat'], node['long'], tw_lb, tw_ub, s_time, perc_smallparts, perc_trash)

        nodes_dict[(node['lat'], node['long'])] = object_node
        ID += 1

    # # Sistema il nodo deposito sovrascivendo coerentemente le informazioni temporali
    # # del nodo (41.9552587, 12.7640889) smaltitore che di fatto è il deposito stesso
    # nodes_dict[(41.9552587, 12.7640889)].tw_lb = time(5, 0, 0)   # se cambi qua cambia pure sotto
    # nodes_dict[(41.9552587, 12.7640889)].tw_ub = time(18, 0, 0)  # se cambi qua cambia pure sotto

    nodes_dict[(41.9555557, 12.7643387)].s_time = time(0, 30, 0)

    return nodes_dict


def get_missions_list_bydate(inst_date, df, nodes_dict):
    # partendo da una data e dal df, mi estraggo tutte le missioni di quel giorno
    df_inst = df[df['data'] == inst_date]
    if df_inst.shape[0] == 0:
        return []
    missions_obj_list = []
    for _, row in df_inst.iterrows():
        mission = VRP_mission(inst_date)
        coord_P = (row["lat_P"], row["long_P"])
        coord_S = (row["lat_S"], row["long_S"])
        mission.node_pickup = nodes_dict[coord_P]
        mission.node_delivery = nodes_dict[coord_S]
        mission.demand = row['count_casse']
        mission.weight = row['peso_tot']
        missions_obj_list.append(mission)
    return missions_obj_list


def create_instance_bydate(inst_date, nodes_dict, df, time_unit_cost=15, dist_unit_cost=15):
    missions_obj_list = get_missions_list_bydate(inst_date, df, nodes_dict)
    instance = VRP_inst(inst_date, time_unit_cost,
                        dist_unit_cost, missions_obj_list)
    return instance


def get_disdur(df, dis_dict, dur_dict):

    rows = df.shape[0]

    distance = np.zeros((rows, rows))
    duration = np.zeros((rows, rows))

    for i in range(0, rows):  # i == from
        for j in range(0, rows):  # j == to

            lat_i, long_i = df.iloc[i, 0], df.iloc[i, 1]
            lat_j, long_j = df.iloc[j, 0], df.iloc[j, 1]

            # Trick per non far rigirare OSRM su tutti i nodi incluso il depot != delivery innocenti
            if lat_i == 41.9552587001:
                lat_i = 41.9555557
                long_i = 12.7643387
            if lat_j == 41.9552587001:
                lat_j = 41.9555557
                long_j = 12.7643387

            distance[i, j] = dis_dict[(lat_i, long_i, lat_j, long_j)]
            duration[i, j] = dur_dict[(lat_i, long_i, lat_j, long_j)]

    return distance, duration


def solve_VRP_inst(daily_instance, dis_dict, dur_dict, time_limit = 30, max_turno = 6):

    ################## DEPOT IS ADD THE REALLY BEGINNING OF MISSIONS LIST ##################################################

    ID_pick_up = 0
    ID_delivery = 0
    description_pickup = 0
    description_delivery = 0

    # (0,30,0) tempo servizio potrebbe non servire.
    depot = VRP_node(0, 41.9552587001, 12.7640889001, time(0, 0, 0), time(23, 59, 0), time(0, 25, 0), 0, 0)
    instance_pickup = [[0, ID_pick_up, description_pickup, depot.lat, depot.long, 0, time(0, 0, 0)]]
    time_info_pickup = [[depot.tw_lb, depot.tw_ub, time(0, 0, 0)]]

    instance_delivery = []
    time_info_delivery = []
    #########################################################################################################################

    ############### PICKUP PART OF MISSIONS INSTANCE ON ONE LIST,  DELIVERY ON DIFFERENT LIST ###############################################################
    for mission in daily_instance.missions_list:
        check, demand_list = mission.check_replicates()
        if check == False:

            ID_pick_up += 1
            description_pickup += 1
            instance_pickup.append([str(mission.node_pickup.ID_name), ID_pick_up, description_pickup, float(mission.node_pickup.lat),
                                    float(mission.node_pickup.long), float(
                                        mission.demand),
                                    mission.node_pickup.s_time])
            time_info_pickup.append([mission.node_pickup.tw_lb, mission.node_pickup.tw_ub,
                                     mission.node_pickup.s_time])

            ID_delivery += 1
            description_delivery += 1



            instance_delivery.append([str(mission.node_delivery.ID_name), ID_delivery, description_delivery, float(mission.node_delivery.lat),
                                      float(mission.node_delivery.long), -
                                      float(mission.demand),
                                      mission.node_delivery.s_time])

            if mission.node_delivery.ID_name == 226: #i.e. is the depot
                mission.node_delivery = depot
            time_info_delivery.append([mission.node_delivery.tw_lb, mission.node_delivery.tw_ub,mission.node_delivery.s_time])

        else:
            for i in range(demand_list[0]):
                ID_pick_up += 1
                description_pickup += 1
                instance_pickup.append([str(mission.node_pickup.ID_name), ID_pick_up, description_pickup, float(mission.node_pickup.lat),
                                        float(mission.node_pickup.long), float(
                                            2),
                                        mission.node_pickup.s_time])
                time_info_pickup.append([mission.node_pickup.tw_lb, mission.node_pickup.tw_ub,
                                         mission.node_pickup.s_time])

                ID_delivery += 1
                description_delivery += 1

                instance_delivery.append([str(mission.node_delivery.ID_name), ID_delivery, description_delivery, float(mission.node_delivery.lat),
                                          float(
                                              mission.node_delivery.long), - float(2),
                                          mission.node_delivery.s_time])

                if mission.node_delivery.ID_name == 226:  # i.e. is the depot
                    mission.node_delivery = depot
                time_info_delivery.append([mission.node_delivery.tw_lb, mission.node_delivery.tw_ub, mission.node_delivery.s_time])

            if demand_list[1] == 1:
                ID_pick_up += 1
                description_pickup += 1
                instance_pickup.append([str(mission.node_pickup.ID_name), ID_pick_up, description_pickup, float(mission.node_pickup.lat),
                                        float(mission.node_pickup.long), 1,
                                        mission.node_pickup.s_time])
                time_info_pickup.append([mission.node_pickup.tw_lb, mission.node_pickup.tw_ub,
                                         mission.node_pickup.s_time])

                ID_delivery += 1
                description_delivery += 1
                instance_delivery.append([str(mission.node_delivery.ID_name), ID_delivery, description_delivery, float(mission.node_delivery.lat),
                                          float(mission.node_delivery.long), -1,
                                          mission.node_delivery.s_time])
                time_info_delivery.append([mission.node_delivery.tw_lb, mission.node_delivery.tw_ub,
                                           mission.node_delivery.s_time])

    #########################################################################################################################
    ################## DEPOT IS ADD THE REALLY END OF MISSIONS LIST #########################################################
    ID_delivery += 1
    description_delivery += 1
    instance_delivery.append([0, ID_delivery, description_delivery, depot.lat, depot.long, 0, time(0, 0, 0)])
    time_info_delivery.append([depot.tw_lb, depot.tw_ub, time(0, 0, 0)])
    #########################################################################################################################
    ################## CONCATENATE PICK UP AND DELIVERY LIST  #########################################################

    instance = instance_pickup + instance_delivery
    time_info = time_info_pickup + time_info_delivery

    instance = pd.DataFrame(instance, columns=[
                            'node_name', "ID", "description", "lat", "long", "demand", "service time"])
    instance = instance.astype({'node_name': str, 'ID': int, 'description': int,
                               'lat': np.float64, 'long': np.float64, 'demand': int})

    instance.loc[ID_pick_up+1:, ['ID', 'description']] += ID_pick_up

    demand = instance["demand"].to_list()

    # get dis & dur matrixes for given instance from dis&dur dictionaries with the distances between all the nodes
    distance, duration = get_disdur(instance[["lat", "long"]], dis_dict, dur_dict)

    # trucks_info = np.ones(int(len(instance)/2))*2

    trucks_info = 2*np.ones(int((len(instance)-2)/2))

    trucks_info = trucks_info.tolist()  # truck.load_capacity

    n = int((len(distance) - 2) / 2)  # numero di clienti totali
    K = len(trucks_info)

    gap = 1e-5

    status, performances, var_results, x_opt, t_opt, l_opt, y_opt, z_opt, o_opt, gamma_opt = VRP_model(distance, duration, demand, time_info, trucks_info, gap, time_limit, max_turno)
    obj_val = performances[0]
    gap = performances[2]

    return status, obj_val, gap, var_results, x_opt, t_opt, l_opt, y_opt, z_opt, o_opt, gamma_opt, n, K, instance, distance, duration


def create_disdur_dict(nodes_dict, dataset_name):

    nodes_tuples = list(nodes_dict.keys())

    df_OSM = pd.DataFrame(nodes_tuples, columns=['lat', 'long'])
    df_OSM.insert(0, 'ID',          np.arange(0, df_OSM.shape[0]))
    df_OSM.insert(1, 'description', np.arange(0, df_OSM.shape[0]))

    distance, duration, dis_dict, dur_dict = OSM(df_OSM)

    # Save distance and duration dictionaries:
    # 1)
    # convert each tuple key to a string before saving as json object
    dis_dict_to_save = {str(k): v for k, v in dis_dict.items()}
    dur_dict_to_save = {str(k): v for k, v in dur_dict.items()}

    # 2) dump dictionary as a .json
    with open('dis_dict_'+str(dataset_name)+'.json', 'w') as f:
        json.dump(dis_dict_to_save, f)
    with open('dur_dict_'+str(dataset_name)+'.json', 'w') as f:
        json.dump(dur_dict_to_save, f)

    print(str(dataset_name)+' dis & dur dictionaries have been saved to local memory')

    return


def create_waste_arrival(daily_instance, VRP_results):
    optimal_arrivals = [[],[]] # morning and afternoon arrivals
    for mission in daily_instance.missions_list:
        if mission.node_delivery.ID_name == 226: # i.e. depot
            lat_pickup  = mission.node_pickup.lat
            long_pickup = mission.node_pickup.long
            for result in VRP_results:
                if isinstance(result[2], str) == True:
                    continue
                else:
                    df = result[2]
                    arrival_time = df.loc[(df["lat"] == lat_pickup) & (df["long"] == long_pickup)]['arrival time']
                    if arrival_time.size != 0:
                        arrival_time = arrival_time.iloc[0]
                        arrival_time = datetime.strptime(arrival_time, '%H:%M:%S').time()
                        if arrival_time <= time(11,0,0):
                            optimal_arrivals[0].append(mission.weight)
                        else:
                            optimal_arrivals[1].append(mission.weight)
    optimal_arrivals[0] = sum(optimal_arrivals[0])
    optimal_arrivals[1] = sum(optimal_arrivals[1])
    return [daily_instance.date, optimal_arrivals[0], optimal_arrivals[1]]


def create_working_weeks(start_date, end_date):
    delta = end_date - start_date
    days_list = []
    for i in range(delta.days + 1):
        days_list.append(start_date + timedelta(days=i))

    cal = Italy()

    weeks_list = []
    for day in days_list:
        if day.weekday() == 0:  # i.e. if day is a monday
            week = []
            if cal.is_working_day(day) == True:
                week.append(day)
        else:
            if cal.is_working_day(day) == True:
                week.append(day)
                if day.weekday() == 4:  # i.e. if day is friday
                    weeks_list.append(week)

    return weeks_list

