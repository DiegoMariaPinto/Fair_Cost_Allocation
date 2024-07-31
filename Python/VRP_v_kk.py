
import pandas as pd
import numpy as np
import math
from itertools import permutations
import itertools



def funzione_vij (distances, nodi):

    funzione_costo = {}

    all_combinations = []
    for length in range(len(nodi) + 1):
        for combination in itertools.combinations(nodi, length):
            all_combinations.append(list(combination))

    # print(all_combinations)

    for nodes in all_combinations:

        def tsp(start_node, nodes, distances):
            # Genera tutti i percorsi possibili che visitano ogni nodo esattamente una volta
            all_paths = itertools.permutations(nodes)
            shortest_distance = float('inf')
            shortest_path = None

            # Passa attraverso tutti i percorsi possibili e calcola la loro distanza totale
            for path in all_paths:
                current_distance = 0
                source_node = start_node
                for node in path:
                    current_distance += distances[source_node][node]
                    source_node = node
                current_distance += distances[source_node][start_node]

                # Controlla se il percorso corrente è più breve del percorso più breve corrente
                if current_distance < shortest_distance:
                    shortest_distance = current_distance
                    shortest_path = (start_node,) + path + (start_node,)

            # Restituisce il percorso più breve e la sua distanza totale
            return shortest_path, shortest_distance

        shortest_path, shortest_distance = tsp(0, nodes, distances)

        # print('Shortest path:', shortest_path)
        v = "{}_{}".format("v", nodes)
        funzione_costo.update({v: shortest_distance})

        # print('V_', nodes,"=", shortest_distance)

    return funzione_costo
