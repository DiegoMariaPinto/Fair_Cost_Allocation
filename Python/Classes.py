class VRP_node:
    def __init__(self, ID_name, lat, long, tw_lb, tw_ub, s_time, perc_smallparts, perc_trash):
        self.ID_name = ID_name
        self.lat = lat
        self.long = long
        self.tw_lb = tw_lb   # time window lower bound for retrieval
        self.tw_ub = tw_ub   # time window upper bound for retrieval
        self.s_time = s_time  # service time for 1 container retrieval
        # --> arricchire formulazione scheduling
        self.perc_smallparts = perc_smallparts
        self.perc_trash = perc_trash           # --> arricchire formulazione scheduling


class VRP_mission:
    def __init__(self, date, node_picukp=None, node_delivery=None, demand=None, weight=None):
        self.date = date
        self.node_pickup = node_picukp  # picukp node object
        self.node_delivery = node_delivery  # delivery node object
        self.demand = demand  # number of containers to be retrieved
        self.weight = weight
        # self.CER --> distinguere weight che va in scheduling o altrimenti --> CER 150106

    def check_replicates(self):
        if self.demand <= 2:
            return False, []
        else:
            if (self.demand % 2) == 0:
                replicates_2 = self.demand/2
                replicates_1 = 0
                return True, [int(replicates_2), int(replicates_1)]
            else:
                replicates_2 = int(self.demand / 2)
                replicates_1 = 1
                return True, [int(replicates_2), int(replicates_1)]


class VRP_inst:
    def __init__(self, date=None, time_unit_cost=None, dist_unit_cost=None, missions_list=None):
        self.date = date
        self.time_unit_cost = time_unit_cost
        self.dist_unit_cost = dist_unit_cost
        self.missions_list = missions_list

class Inst_SLWA:
    def __init__(self, horizon_LB, horizon_UB, shift_1_hours, shift_2_hours,
                 operator_wage, max_operators, min_op_sort1, min_op_sort2, firstTO2nd_sort, setup_sort1, setup_sort2,
                 overfill_treshold, finalstock_treshold, sort1_capacity, sort2_capacity, sort1_maxstock, sort2_maxstock):
        self.horizon_LB = horizon_LB  #datetime.date field dytpe
        self.horizon_UB = horizon_UB  #datetime.date field dytpe
        self.shift_1_hours = shift_1_hours
        self.shift_2_hours = shift_2_hours
        self.operator_wage = operator_wage
        self.max_operators = max_operators
        self.min_op_sort1 = min_op_sort1
        self.min_op_sort2 = min_op_sort2
        self.firstTO2nd_sort = firstTO2nd_sort
        self.setup_sort1 = setup_sort1
        self.setup_sort2 = setup_sort2
        self.overfill_treshold = overfill_treshold
        self.finalstock_treshold = finalstock_treshold
        self.sort1_capacity =  sort1_capacity
        self.sort2_capacity =  sort2_capacity
        self.sort1_maxstock =  sort1_maxstock
        self.sort2_maxstock =  sort2_maxstock