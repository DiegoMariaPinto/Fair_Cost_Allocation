import pandas as pd
import numpy as np
import math
from itertools import permutations
import itertools
from Functions_files.VRP_s_kk import funzione_sij


def appro_2 (TSP_matrix):

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

    # print("la funzione costo s_ij è: ", funzione_costo)
    # print("")

    # ---- questo for è per prendere il primo termine s_kk per ogni k = n-1 nodi escluso il deposito ------------------------------------------

    termine1 = []

    for x in nodi:
        kk = 's'
        result = "{}_{}{}".format(kk, x, x)

        risultato = funzione_costo[result]
        termine1.append(risultato)

    # ---- questo while è il secondo termine, la sommatoria per ogni nodo x S_xi cambiando tutti gli i nei restanti nodi -----------------------

    x = 1
    termine2 = []
    y = []

    # print('il primo termine è: ', termine1) ------------------------------------------ IMPORTANTE

    while x <= n:

        nodi.remove(x)

        for ij in nodi:
            k = 's'
            order = [x, ij]
            order.sort()
            order = ''.join(str(x) for x in order)
            result1 = "{}_{}".format(k, order)
            # print(nodi)
            # print(result1)
            y.append(funzione_costo[result1])

        nodi.append(x)
        total = - sum(y) / 2
        termine2.append(total)
        # print(total)

        y.clear()

        x += 1

    # print('il secondo termine è: ', termine2) ------------------------------------------ IMPORTANTE

    # ---- questo while è il terzo termine, la sommatoria con il dividendo rango e l'incrocio della matrice I  ------------------------------------------

    x = 1
    termine3 = []

    while x <= n:

        nodi.remove(x)

        y = []

        # ---------- 2 cicli for: il primo per creare le combo s_ki e s_kj
        # ---------- il secondo per creare s_ij

        # ---------- questo perchè può succedere che se x = 2, s_12 s_25 sono in ordine e quindi per avere s_15
        # ---------- devo lavorare con s_21 e s_25 per tirare fuori s_15 con il secondo ciclo for

        for ij in nodi:
            k = 's'
            order = [x, ij]
            order.sort()
            order = ''.join(str(x) for x in order)
            result2 = "{}_{}".format(k, order)
            # print(result2)
            y.append(result2)

        combinations_in_order = list(itertools.combinations(y, 2))
        # print("tutte le combinazione presi a 2 a 2 IN ORDINE: ", combinations_in_order)

        asso = []

        for ij in nodi:
            k = 's'
            order1 = [x, ij]
            order1 = ''.join(str(x) for x in order1)
            result3 = "{}_{}".format(k, order1)
            # print(result2)
            asso.append(result3)

        # print("preso k, terna s_k e tutti gli altri nodi: ", y)

        # ----------- combinazioni dei 3 s in gruppi da 2 per la matrice

        combinations_NOT_in_order = list(itertools.combinations(asso, 2))
        # print("tutte le combinazione presi a 2 a 2 NON IN ORDINE: ", combinations_NOT_in_order)

        # ----------- ciclo while che unisce i 2 cicli for in una lista e tira fuori il minimo per inserirlo nella matrice I

        z = 0
        t = []
        matrice_I = []

        while z < len(combinations_in_order):
            s = list(combinations_NOT_in_order[z])

            beta = 's_' + str(x)

            new_str1 = s[0].replace(beta, "")
            # print(new_str1)
            primo1 = int(new_str1)

            # print(primo1)
            t.append(primo1)

            new_str3 = s[1].replace(beta, "")
            # print(new_str3)
            primo2 = int(new_str3)

            # print(primo2)
            t.append(primo2)

            t.sort()
            # print(t)
            t.clear()

            terzo = 's_' + str(new_str1) + str(new_str3)  # il terzo è il terzo elemento s_ij di: s_ki, s_kj, s_ij
            # print(terzo)

            total = list(combinations_in_order[z])

            total.append(terzo)
            # print(total)

            minimo = min(funzione_costo[total[0]], funzione_costo[total[1]], funzione_costo[total[2]])
            matrice_I.append(minimo)
            matrice_I.sort()
            # print("valori da inserire in matrice: ", minimo)

            z += 1

        # print(matrice_I)

        # ----- creo r_ij

        r_ij = []
        for i in range(n - 2):
            r_ij.append(i)

        # print(r_ij)

        matrice_I.sort()
        # print(matrice_I)

        # ----- creo divisore partendo da r_ij

        divisore = []
        for num in r_ij:
            divisore.append(2 / ((num + 1) * (num + 2) * (num + 3)))

        divisore.sort()
        # print(divisore)

        l_matrice = len(matrice_I)
        l_divisore = len(divisore)

        z = 0

        # ------ prende la matrice I e la divide: orig_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] to: [[1], [2, 3], [4, 5, 6], [7, 8, 9, 10]]

        result = []
        i = 1
        while len(matrice_I) > 0:
            sublist = matrice_I[:i]
            result.append(sublist)
            matrice_I = matrice_I[i:]
            i += 1
        # print(result)

        # ---- lista di lista con i vari risutati della sommatoria di O(2)

        risultato = [num * divisore[i] for i in range(len(divisore)) for num in result[i]]
        # print(risultato)

        # ----- sommo tutto per aggiungerlo insime agli altri pezzi dell'algoritmo

        total = sum(risultato)

        termine3.append(total)

        nodi.append(x)
        nodi.sort()

        x += 1

    # print('il terzo termine è: ', termine3) ------------------------------------------ IMPORTANTE

    appro2 = [sum(x) for x in zip(termine1, termine2, termine3)]

    return appro2
    # print("")
    #print('il risultato appro O(2) è:   ', appro2)
