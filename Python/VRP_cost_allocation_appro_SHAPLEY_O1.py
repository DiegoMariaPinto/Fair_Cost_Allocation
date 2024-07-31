import pandas as pd
import numpy as np
import math
from itertools import permutations
from Functions_files.VRP_s_kk import funzione_sij



#def appro_1 (matrice_distanze, nodi, n):

def appro_1 (TSP_matrix):

    # richiamo la funzione s_ij per crearmi il dict funzione costo dalla matrice delle distanze
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

    funzione_costo = funzione_sij(matrice_distanze=matrice_distanze, nodi=nodi, n=n)

    #print("la funzione costo s_ij è: ", funzione_costo)
    #print("")

    # ----- ciclo while per creare appro O(1)

    x = 1
    appro1 = []

    while x <= n:

        # ------ estraggo il primo termine s_kk

        kk = 's'
        result = "{}_{}{}".format(kk, x, x)
        nodi.remove(x)

        y = 0
        sc = []

        # ------ estraggo tutti gli s_ij del secondo termine Sc(....)

        while y <= int(n - 2):
            k1 = 's'
            order1 = [x, nodi[y]]
            order1.sort()
            order1 = ''.join(str(x) for x in order1)
            result1 = "{}_{}".format(k1, order1)
            # print(result1)
            sc.append(result1)

            y += 1

        nodi.append(x)

        # -- metto insieme la prima parte e la seconda parte dell'equazione O(1)

        #print("l'equazione O(1) è: ", result, " - ", sc) ------------------------------------------ IMPORTANTE

        # -- y prende da Sc e li ordina in maniera decrescente

        y = [funzione_costo[item] for item in sc]
        y.sort()
        y.reverse()

        # sommatoria che mi da il dividendo che andrà usato per Sc:

        k = 1
        i = 1
        total = 0.0

        while k <= int(n - 1):
            for g in y:
                i = k * (k + 1)
                r = g / i
                total += r
                k += 1

        # print(total)

        appro = funzione_costo[result] - total

        appro1.append(appro)

        # ----------------------------------------------

        x += 1

    return appro1
    #print("")
    #print("il risultato appro O(1) è:   ", appro1)

