
import pandas as pd
import numpy as np
import math
from itertools import permutations
import itertools

# --------------- s_ij = d_0i + d_0j - d_ij


#matrice delle distanze:


#nodi = [1, 2, 3, 4, 5]
#n = len(nodi)



def funzione_sij (matrice_distanze, nodi, n):

    values = []
    x = 1
    y = 1

    while x <= n:

        while y <= n:
            s_ij = matrice_distanze["d_0" + str(x)] + matrice_distanze["d_0" + str(y)] - matrice_distanze[
                "d_" + str(x) + str(y)]
            values.append(s_ij)
            #print(s_ij)
            y += 1

        y = x + 1
        x += 1

    # print(values)

    funzione_costo = {f"s_{i}{j}": values.pop(0) for i in nodi for j in nodi if i <= j}
    #print(funzione_costo)
    return funzione_costo



