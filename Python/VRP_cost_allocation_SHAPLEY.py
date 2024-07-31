import math
import numpy as np
from itertools import permutations
from Functions_files.VRP_v_kk import funzione_vij



def shapley (TSP_matrix):

    TSP_matrix_simm_1 = np.zeros_like(TSP_matrix)
    TSP_matrix_simm = TSP_matrix_simm_1.astype(float)

    for i in range(len(TSP_matrix)):
        for j in range(len(TSP_matrix)):
            TSP_matrix_simm[i][j] = (TSP_matrix[i][j] + TSP_matrix[j][i]) / 2

    matrice_distanze = {}

    TSP_matrix_simm = TSP_matrix_simm[:-1, :-1]

    for i in range(len(TSP_matrix_simm)):
        for j in range(len(TSP_matrix_simm[i])):
            if i != j:
                key = f"d_{i}{j}"
                matrice_distanze[key] = TSP_matrix_simm[i][j]

    for i in range(len(TSP_matrix_simm)):
        key = f"d_{i}{i}"
        matrice_distanze[key] = 0

    nodi = list(range(1, TSP_matrix_simm.shape[0]))
    n = TSP_matrix_simm.shape[0] - 1

    #print('nodi:', nodi)
    #print('n:', n)

    # --- Questo mi permette di cambiare la scrittura della matrice delle distanze in una cosa del tipo:
    # distances = {
    #     0: {0: 0,   1: 11,  2: 12,  3: 10,  4: 5},
    #     1: {0: 11,  1: 0,   2: 3,   3: 15,  4: 17},
    #     2: {0: 12,  1: 3,   2: 0,   3: 6,   4: 19},
    #     3: {0: 10,  1: 15,  2: 6,   3: 0,   4: 4},
    #     4: {0: 5,   1: 17,  2: 19,   3: 4,   4: 0}
    # }

    nn = n + 1  # number of nodes
    distances = {i: {} for i in range(nn)}  # initialize the nested dictionary

    for i in range(nn):
        for j in range(nn):
            if i == j:
                distances[i][j] = 0
            else:
                key = "d_{}{}".format(min(i, j), max(i, j))
                distances[i][j] = matrice_distanze[key]

    # print(distances)




    # richiamo la funzione v_ij per crearmi il dict funzione costo dalla matrice delle distanze, con una serie di TSP

    funzione_costo = funzione_vij(distances=distances, nodi=nodi)

    #print(funzione_costo)


    # ----------- DA qui inizia il vero codice per calcolare lo shapley value

    numbers = list(range(1, n + 1))
    permutation_list = list(permutations(numbers))
    n_fattoriale = math.factorial(n)
    shapley_value = []

    # --- ciclo while che esegue tutte le operazioni per ogni nodo x, fino a n

    x = 1

    while x <= n:
        i = 0
        somma = []
        # print("sto calcolando il nodo: ", x)

        # --- ciclo while che esegue operazioni per ogni permutazione

        while i < n_fattoriale:
            t = list(permutation_list[i])

            index_t = t.index(int(x))  # --- posizione del nodo x nella permutazione t
            # print("la posizione di ", x, "è:", index_t)

            # ---------------------------------
            posizione1 = t[0:index_t + 1]
            posizione1.sort()

            my_variable = 'v'
            result1 = "{}_{}".format(my_variable, posizione1)
            #print(result1)
            # ---------------------------------

            # ---------------------------------
            posizione2 = t[0:index_t]
            posizione2.sort()

            my_variable = 'v'
            result2 = "{}_{}".format(my_variable, posizione2)
            #print(result2)
            # ---------------------------------

            z = funzione_costo[result1] - funzione_costo[result2]
            somma.append(z)

            i += 1

        # print(somma)
        s = sum(somma)
        shapley = s / n_fattoriale
        shapley_value.append(shapley)

        x += 1

    return shapley_value
    #print("")
    #print("il risultato shapley è:      ", shapley_value)


