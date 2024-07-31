from .VRP_instances_functions import get_missions_list_bydate

def get_firstTO2nd_sort(dates_list, df, nodes_dict):
    daily_small_parts_weights = []
    daily_weights = []
    for inst_date in dates_list:
        missions_obj_list = get_missions_list_bydate(inst_date, df, nodes_dict)
        daily_weights.extend([mission.weight for mission in missions_obj_list])
        daily_small_parts_weights.extend(
            [mission.node_pickup.perc_smallparts * mission.weight for mission in missions_obj_list])

    week_weight = sum(daily_weights)
    week_small_parts_weight = int(sum(daily_small_parts_weights))

    firstTO2nd_sort = round(week_small_parts_weight / week_weight, 3)

    return firstTO2nd_sort, week_weight


def allocate_SLWA_cost_and_features(dates_list, df, nodes_dict, obj_val, firstTO2nd_sort, week_weight,
                                    trash_cost):
    SLWA_costs = []
    for inst_date in dates_list:
        missions_obj_list = get_missions_list_bydate(inst_date, df, nodes_dict)
        for mission in missions_obj_list:
            node_name = mission.node_pickup.ID_name
            ID_name_delivery = mission.node_delivery.ID_name
            node_SWLA_cost = (mission.weight / week_weight) * obj_val * (1 + mission.node_pickup.perc_smallparts)
            node_SLWA_trahs_cost = (mission.node_pickup.perc_trash) * (mission.weight) * trash_cost
            node_SWLA_cost = round(node_SWLA_cost, 2) + round(node_SLWA_trahs_cost, 2)

            SLWA_costs.append([inst_date, node_name, ID_name_delivery, week_weight, max_operators, min_op_sort1, min_op_sort2, overfill_treshold, firstTO2nd_sort, node_SWLA_cost])

    return SLWA_costs