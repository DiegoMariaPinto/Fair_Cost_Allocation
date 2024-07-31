# coding=utf-8


from Functions_files.ClarkeWright_distance_cost_allocation import allocate_distance_features
from Functions_files.VRP_instances_functions import get_missions_list_bydate
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np



def allocate_VRP_costs_and_features(inst_date, df, nodes_dict, VRP_results, gap, distance, duration, dist_unit_cost, time_unit_cost, o_opt, gamma_opt, dis_dict):

    missions_obj_list = get_missions_list_bydate(inst_date, df, nodes_dict)

    approach = 'SA' # StandAlone
    df_distance_SA = allocate_travel_disdur(missions_obj_list, VRP_results, distance, approach)
    df_duration_SA = allocate_travel_disdur(missions_obj_list, VRP_results, duration, approach)
    approach = 'NS' # Neighbour Savings
    df_distance_NS = allocate_travel_disdur(missions_obj_list, VRP_results, distance, approach)
    df_duration_NS = allocate_travel_disdur(missions_obj_list, VRP_results, duration, approach)
    approach = 'ENS' # Extreme Neighbour Savings
    df_distance_ENS = allocate_travel_disdur(missions_obj_list, VRP_results, distance, approach)
    df_duration_ENS = allocate_travel_disdur(missions_obj_list, VRP_results, duration, approach)

    VRP_costs = []
    mission_num = 0
    for mission in missions_obj_list:

        # SA:= standalone: approccio che alloca il costo considerando il tour standalone indipendente dagli altri clienti
        # Vantaggio: se il cliente è vicino o lontano dal deposito gli risconosce un costo proporzionale
        # Svantaggio: non considera la riduzione dei costi dovuta alla vicinanza ad altri clienti serviti:
        # esempio, dati 3 clienti equidistanti del deposito con 2 di questi molto vicini, questo metodo alloca lo stesso 
        # costo a tutti e 3 anche se i due vicini dovrebbero pagare di meno

        # NS:= neighbour savings: approccio che alloca il costo al cliente i considerando la media di
        # tutti i costi dei tour j con j != i dove il costo del tour j è ottenuto sottrando al percorso totale le deviazioni
        # utili a servire i nodi P&D di j e aggiungendo gli archi di raccordo.
        # Vantaggio: se due o più clienti sono tra loro vicini questo approaccio ne considera il risparmio che il tour permette
        # Svantaggio: se un cliente è vicino e due sono lontani, questo approccio alloca un costo elevato anche al cliente vicino
        # questo perchè i tour dove lui è presente hanno comunque un'elevata distanza percorsa

        # ENS:= extreme neighbour savings: c_k_i = c_dev - c_link

        # AVG_mission_allocated_km = np.mean([c_star_distance_SA, c_star_distance_NS, c_star_distance_ENS])
        # AVG_mission_allocated_min = np.mean([c_star_duration_SA, c_star_duration_NS, c_star_duration_ENS])

        mission_allocated_km_SA = get_C_star(mission, VRP_results, df_distance_SA)
        mission_allocated_km_NS = get_C_star(mission, VRP_results, df_distance_NS)
        mission_allocated_km_ENS = get_C_star(mission, VRP_results, df_distance_ENS)

        mission_allocated_min_SA = get_C_star(mission, VRP_results, df_duration_SA)
        mission_allocated_min_NS = get_C_star(mission, VRP_results, df_duration_NS)
        mission_allocated_min_ENS = get_C_star(mission, VRP_results, df_duration_ENS)

        # get pick up node data
        ID_name_P = mission.node_pickup.ID_name
        lat_P , long_P = mission.node_pickup.lat, mission.node_pickup.long
        tw_lb_P, tw_ub_P = mission.node_pickup.tw_lb, mission.node_pickup.tw_ub
        s_time_P = mission.node_pickup.s_time

        # get delivery node data
        ID_name_D = mission.node_delivery.ID_name
        lat_D , long_D = mission.node_delivery.lat, mission.node_delivery.long
        tw_lb_D, tw_ub_D = mission.node_delivery.tw_lb, mission.node_delivery.tw_ub
        s_time_D = mission.node_delivery.s_time

        demand, weight = mission.demand, mission.weight
        perc_smallparts = mission.node_pickup.perc_smallparts
        perc_trash = mission.node_pickup.perc_trash
        clients_served = len(missions_obj_list)

        dist_to_pickup_node, dist_to_delivery_node, dist_from_p_to_d, tour_len, km_i, km_tot = allocate_distance_features(mission, VRP_results, distance)
        dur_to_pickup_node,  dur_to_delivery_node,  dur_from_p_to_d,  tour_len, hours_i, min_tot = allocate_duration_features(mission, VRP_results, duration)

        overnight_cost, window_enlargement_cost = allocate_additional_VRP_costs(mission, mission_num, VRP_results, o_opt, gamma_opt, tour_len, clients_served, df_distance_SA)

        closest_nodes = []
        for max_dist in [5, 10, 20, 50, 100]:
            num = get_closest_instance_nodes_num(lat_P, long_P, dis_dict, missions_obj_list, max_dist)
            closest_nodes.append(num)

        VRP_costs.append([inst_date, ID_name_P, ID_name_D,
                          lat_P, long_P, tw_lb_P, tw_ub_P, s_time_P, demand, weight, perc_smallparts, perc_trash,
                          lat_D, long_D, tw_lb_D, tw_ub_D, s_time_D,
                          clients_served, dist_to_pickup_node, dist_to_delivery_node, dist_from_p_to_d,
                          tour_len,
                          km_i,  mission_allocated_km_SA, mission_allocated_km_NS, mission_allocated_km_ENS, km_tot,
                          hours_i, mission_allocated_min_SA, mission_allocated_min_NS, mission_allocated_min_ENS,
                          overnight_cost, window_enlargement_cost, gap, closest_nodes[0], closest_nodes[1], closest_nodes[2], closest_nodes[3], closest_nodes[4]])

        mission_num += 1

    return VRP_costs


def allocate_additional_VRP_costs(mission, mission_num, VRP_results, o_opt, gamma_opt, tour_len, clients_served, df_distance_SA):

    enlarge_window_unit_cost = 100 # cost of relaxing tw upper bound of a node
    overnight_cost = 190 # cost of overnight

    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    overnights = o_opt.iloc[truck_k]['value']
    if overnights > 0:
        df = df_distance_SA.copy()
        truck_mask = df['truck_k'] == truck_k
        C_k_i_sum = df[truck_mask]['C_k_i'].sum()
        df.loc[truck_mask, "C_k_i"] = df.loc[truck_mask, "C_k_i"]/C_k_i_sum

        overnight_cost = overnights*overnight_cost*df.loc[mission_num,'C_k_i']
    else:
        overnight_cost = 0

    window_enlargement_cost = 0
    node_p_index = mission_num # gamma esiste solo for i in N, non in Nod, quindi il primo elemento "0" di gamma è riferito al primo nodo di pickup
    node_d_index = node_p_index + clients_served
    window_enlargements = [gamma_opt.iloc[node_p_index]['value'],gamma_opt.iloc[node_d_index]['value']]
    if (window_enlargements[0] > 0) or (window_enlargements[1] > 0):
        window_enlargement_cost += enlarge_window_unit_cost*window_enlargements[0] + enlarge_window_unit_cost*window_enlargements[1]

    return round(overnight_cost,2), round(window_enlargement_cost,2)


def allocate_travel_disdur(missions_obj_list, VRP_results, disdur, approach):
    disdur_list = []
    for mission in missions_obj_list:
        node_p = mission.node_pickup.ID_name
        node_d = mission.node_delivery.ID_name
        if approach == 'SA':
            C_k_i, C_tot, truck_k = get_C_k_i_SA(mission, VRP_results, disdur)
            disdur_list.append([node_p, node_d, C_k_i, C_tot, truck_k])
        elif approach == 'NS':
            C_deviation, C_link, C_tot, truck_k = get_C_k_i_NS(mission, VRP_results, disdur)
            C_i_bar = C_tot - C_deviation + C_link # dis o dur totali di soluzione senza "deviazione" per il cliente i
            disdur_list.append([node_p, node_d, C_i_bar, C_tot, truck_k])
        elif approach == 'ENS':
            C_deviation, C_link, C_tot, truck_k = get_C_k_i_NS(mission, VRP_results, disdur)
            if C_link == C_deviation:
                C_k_i = C_link/2
            else:
                C_k_i = max(0,C_deviation - C_link)
            if (C_deviation == 0) and (C_link == 0): # one client only in tour
                C_k_i = C_tot
            disdur_list.append([node_p, node_d, C_k_i, C_tot, truck_k])

    if (approach == 'SA') or (approach == 'ENS'):
        df_disdur = pd.DataFrame(disdur_list, columns=['node_p', 'node_d', 'C_k_i', 'C_tot', 'truck_k'])
        df_disdur.astype({'node_p': int, 'node_d': int, 'C_k_i': float, 'C_tot': float})
    elif approach == 'NS':
        df_disdur = pd.DataFrame(disdur_list, columns=['node_p', 'node_d', 'C_i_bar', 'C_tot', 'truck_k'])
        df_disdur.astype({'node_p': int, 'node_d': int, 'C_i_bar': float, 'C_tot': float})
        for truck_k in list(df_disdur['truck_k'].unique()):
            truck_mask = df_disdur['truck_k'] == truck_k
            if len(df_disdur[truck_mask]) > 1:
                C_bar_sum = df_disdur[truck_mask]['C_i_bar'].sum()
                div = len(df_disdur[truck_mask]) - 1
                C_bar_i = df_disdur[truck_mask]['C_i_bar']
                C_bar_i_star = (C_bar_sum-C_bar_i)/div
                df_disdur.loc[truck_mask, "C_i_bar"]=C_bar_i_star

        df_disdur.rename(columns={'C_i_bar': 'C_k_i'}, inplace=True)

    df_disdur.dropna(inplace=True)

    return df_disdur


def get_C_star(mission, VRP_results, df_disdur):
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    if check == 'not found':
        return np.nan

    df = df_disdur[df_disdur['truck_k'] == truck_k]

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


def get_C_k_i_SA(mission, VRP_results, disdur):
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    if check == 'not found':
        return np.nan, np.nan, np.nan
        print('truck not found')

    C_tot = get_C_tot(df_truck_k, disdur)

    if len(df_truck_k) == 4:
        C_k_i = C_tot
    else:
        node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
        node_d_index = df_truck_k['node name'][df_truck_k['node name'] == node_d].index[0]
        C_k_i = 0
        i = df_truck_k['node number'][0]
        j = df_truck_k['node number'][node_p_index]
        C_k_i += disdur[i, j]
        i = df_truck_k['node number'][node_p_index]
        j = df_truck_k['node number'][node_d_index]
        C_k_i += disdur[i, j]
        i = df_truck_k['node number'][node_d_index]
        j = df_truck_k['node number'].iloc[-1]
        C_k_i += disdur[i, j]

    return C_k_i, C_tot, truck_k


def get_C_k_i_NS(mission, VRP_results, disdur):
    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    if check == 'not found':
        return np.nan, np.nan, np.nan, np.nan
        print('truck not found')

    C_tot = get_C_tot(df_truck_k, disdur)

    if len(df_truck_k) == 4:
        C_deviation = 0
        C_link = 0
    else:
        node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
        node_d_index_list = list(df_truck_k['node name'][df_truck_k['node name'] == node_d].index)
        node_d_index = next(b for (a,b) in enumerate(node_d_index_list) if b > node_p_index)
        if node_d_index == node_p_index + 1:
            C_deviation, C_link = get_C_consecutivePD(df_truck_k, disdur, node_p_index, node_d_index)
        else:
            C_deviation, C_link = get_C_non_consecutivePD(df_truck_k, disdur, node_p_index, node_d_index)

    return C_deviation, C_link, C_tot, truck_k


def get_C_consecutivePD(df_truck_k, disdur, node_p_index, node_d_index):
    df = df_truck_k
    C_deviation = 0
    i = df['node number'][node_p_index - 1]
    j = df['node number'][node_p_index]
    C_deviation += disdur[i, j]
    i = df['node number'][node_p_index]
    j = df['node number'][node_d_index]
    C_deviation += disdur[i, j]
    i = df['node number'][node_d_index]
    j = df['node number'][node_d_index + 1]
    C_deviation += disdur[i, j]

    C_link = 0
    i = df['node number'][node_p_index - 1]
    j = df['node number'][node_d_index + 1]
    C_link += disdur[i, j]

    return C_deviation, C_link

def get_C_non_consecutivePD(df_truck_k, disdur, node_p_index, node_d_index):
    df = df_truck_k
    C_deviation = 0
    i = df['node number'][node_p_index - 1]
    j = df['node number'][node_p_index]
    C_deviation += disdur[i, j]
    i = df['node number'][node_p_index]
    j = df['node number'][node_p_index + 1]
    C_deviation += disdur[i, j]
    i = df['node number'][node_d_index - 1]
    j = df['node number'][node_d_index]
    C_deviation += disdur[i, j]
    i = df['node number'][node_d_index]
    j = df['node number'][node_d_index + 1]
    C_deviation += disdur[i, j]

    C_link = 0
    i = df['node number'][node_p_index - 1]
    j = df['node number'][node_p_index + 1]
    C_link += disdur[i, j]
    i = df['node number'][node_d_index - 1]
    j = df['node number'][node_d_index + 1]
    C_link += disdur[i, j]

    return C_deviation, C_link

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


def allocate_distance_features(mission, VRP_results, distance):

    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    if check == 'not found':
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

    node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
    node_d_index = df_truck_k['node name'][df_truck_k['node name'] == node_d].index[0]

    p = df_truck_k['node number'][node_p_index]
    d = df_truck_k['node number'][node_d_index]

    dist_to_pickup_node = round(distance[0, p], 2)  # distanza nodo pick up  del cliente dal depot
    dist_to_delivery_node = round(distance[0, d], 2)  # distanza nodo delivery del cliente dal depot
    dist_from_p_to_d = round(distance[p, d], 2)  # distanza nodo pick up e nodo delivery

    tour_len = int((len(df_truck_k) - 2) / 2)  # lunghezza del tour --> numero dei clienti serviti dal truck

    # la distanza dal deposito al pickup, quindi al delivery e quindi al deposito a rapporto con la c_tot del tour
    km_i, km_tot, _ = get_C_k_i_SA(mission, VRP_results, distance)


    return dist_to_pickup_node, dist_to_delivery_node, dist_from_p_to_d, tour_len, round(km_i,2), round(km_tot,2)


def allocate_duration_features(mission, VRP_results, duration):

    check, truck_k, df_truck_k, node_p, node_d = get_truck_k_of_mission_i(mission, VRP_results)

    if check == 'not found':
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

    node_p_index = df_truck_k['node name'][df_truck_k['node name'] == node_p].index[0]
    node_d_index = df_truck_k['node name'][df_truck_k['node name'] == node_d].index[0]

    p = df_truck_k['node number'][node_p_index]
    d = df_truck_k['node number'][node_d_index]

    dur_to_pickup_node = round(duration[0, p], 2)  # distanza nodo pick up  del cliente dal depot
    dur_to_delivery_node = round(duration[0, d], 2)  # distanza nodo delivery del cliente dal depot
    dur_from_p_to_d = round(duration[p, d], 2)  # distanza nodo pick up e nodo delivery

    tour_len = int((len(df_truck_k) - 2) / 2)  # lunghezza del tour --> numero dei clienti serviti dal truck

    # la distanza dal deposito al pickup, quindi al delivery e quindi al deposito a rapporto con la c_tot del tour
    hours_i, min_tot, _ = get_C_k_i_SA(mission, VRP_results, duration)


    return dur_to_pickup_node, dur_to_delivery_node, dur_from_p_to_d, tour_len, round(hours_i,2), round(min_tot,2)



def get_closest_instance_nodes_num(lat_from, long_from, dis_dict, missions_obj_list, max_dist):
    count = -1
    for mission in missions_obj_list:
        lat_to, long_to = mission.node_pickup.lat, mission.node_pickup.long
        if dis_dict[(lat_from,long_from,lat_to,long_to)] < max_dist:
            count += 1

    return  count