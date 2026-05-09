"""
LU3IN025 - IA et Jeux - Projet 3
Q11 à Q15 : formulations PLNE résolues avec Gurobi.

Convention de Borda utilisée dans tout le projet :
    u_E[i][j] = m - rang_etu[i][j]   (1er choix de i  -> u = m,  dernier -> u = 1)
    u_P[j][i] = n - rang_spe[j][i]   (1er choix de j  -> u = n,  dernier -> u = 1)

Avec cette convention, l'indication de Q13 « u >= m - k équivaut à i obtient un
de ses k premiers choix » est satisfaite.
"""

import gurobipy as gp
from gurobipy import GRB

import exemple as e


# ─────────────────────────────────────────────────────────────────────
#  Utilitaires : matrices d'utilité (Borda)
# ─────────────────────────────────────────────────────────────────────

def utilite_etu(prefEtu):
    """u_E[i][j] = m - rang du parcours j chez l'étudiant i (m = nb parcours)."""
    n = len(prefEtu)
    m = len(prefEtu[0])
    rankEtu = e.buildRankEtu(prefEtu)
    return [[m - rankEtu[i][j] for j in range(m)] for i in range(n)]


def utilite_spe(prefSpe, n):
    """u_P[j][i] = n - rang de l'étudiant i chez le parcours j."""
    m = len(prefSpe)
    rankSpe = e.buildRankSpe(prefSpe)
    return [[n - rankSpe[j][i] for i in range(n)] for j in range(m)]


def affectation_depuis_x(x_vals, n, m):
    """Convertit la matrice x (binaires) en liste affectation[j] = [étudiants]."""
    affectation = [[] for _ in range(m)]
    for i in range(n):
        for j in range(m):
            if x_vals[i, j] > 0.5:
                affectation[j].append(i)
    return affectation


# ─────────────────────────────────────────────────────────────────────
#  Q11 : Maximiser l'utilité minimale des étudiants
# ─────────────────────────────────────────────────────────────────────

def plne_max_min(prefEtu, prefSpe, cap, verbose=False):
    """
    PLNE Q11.

        max  U
        s.c. sum_j x[i,j] = 1                pour tout étudiant i
             sum_i x[i,j] <= cap[j]          pour tout parcours j
             U <= sum_j u_E[i][j] x[i,j]     pour tout étudiant i
             x[i,j] in {0,1}

    Comme sum(cap) = n, on impose un mariage parfait pour que U_min ait du sens.
    """
    n, m = len(prefEtu), len(prefSpe)
    uE = utilite_etu(prefEtu)

    mdl = gp.Model("Q11_max_min")
    mdl.setParam("OutputFlag", 1 if verbose else 0)

    x = mdl.addVars(n, m, vtype=GRB.BINARY, name="x")
    U = mdl.addVar(vtype=GRB.INTEGER, lb=0, ub=m, name="U")

    # Mariage parfait
    for i in range(n):
        mdl.addConstr(gp.quicksum(x[i, j] for j in range(m)) == 1, name=f"etu{i}")
    for j in range(m):
        mdl.addConstr(gp.quicksum(x[i, j] for i in range(n)) <= cap[j], name=f"spe{j}")

    # Définition de U comme min des utilités étudiants
    for i in range(n):
        mdl.addConstr(U <= gp.quicksum(uE[i][j] * x[i, j] for j in range(m)),
                      name=f"min{i}")

    mdl.setObjective(U, GRB.MAXIMIZE)
    mdl.optimize()

    x_vals = {(i, j): x[i, j].X for i in range(n) for j in range(m)}
    return affectation_depuis_x(x_vals, n, m), int(round(U.X))


# ─────────────────────────────────────────────────────────────────────
#  Q12 : Maximiser la somme des utilités
# ─────────────────────────────────────────────────────────────────────

def plne_max_somme(prefEtu, prefSpe, cap, verbose=False):
    """
    PLNE Q12.

        max  sum_{i,j} (u_E[i][j] + u_P[j][i]) x[i,j]
        s.c. sum_j x[i,j] <= 1
             sum_i x[i,j] <= cap[j]
             x[i,j] in {0,1}
    """
    n, m = len(prefEtu), len(prefSpe)
    uE = utilite_etu(prefEtu)
    uP = utilite_spe(prefSpe, n)

    mdl = gp.Model("Q12_max_somme")
    mdl.setParam("OutputFlag", 1 if verbose else 0)

    x = mdl.addVars(n, m, vtype=GRB.BINARY, name="x")

    for i in range(n):
        mdl.addConstr(gp.quicksum(x[i, j] for j in range(m)) <= 1)
    for j in range(m):
        mdl.addConstr(gp.quicksum(x[i, j] for i in range(n)) <= cap[j])

    mdl.setObjective(
        gp.quicksum((uE[i][j] + uP[j][i]) * x[i, j]
                    for i in range(n) for j in range(m)),
        GRB.MAXIMIZE,
    )
    mdl.optimize()

    x_vals = {(i, j): x[i, j].X for i in range(n) for j in range(m)}
    return affectation_depuis_x(x_vals, n, m), mdl.ObjVal


# ─────────────────────────────────────────────────────────────────────
#  Q13 : Maximiser la somme des utilités, chaque étudiant dans ses k
#        premiers choix
# ─────────────────────────────────────────────────────────────────────

def plne_max_somme_kfirst(prefEtu, prefSpe, cap, k,
                          mariage_parfait=False, verbose=False):
    """
    PLNE Q13.

        max  sum_{i,j} (u_E[i][j] + u_P[j][i]) x[i,j]
        s.c. sum_j x[i,j] <= 1                                (ou = 1)
             sum_i x[i,j] <= cap[j]
             x[i,j] = 0   si rang_etu[i][j] >= k
             x[i,j] in {0,1}

    Si `mariage_parfait` est True, on force sum_j x[i,j] = 1, ce qui rend le
    PLNE infaisable lorsque k est trop petit (utile pour Q14).
    """
    n, m = len(prefEtu), len(prefSpe)
    uE = utilite_etu(prefEtu)
    uP = utilite_spe(prefSpe, n)
    rankEtu = e.buildRankEtu(prefEtu)

    mdl = gp.Model(f"Q13_kfirst_k{k}")
    mdl.setParam("OutputFlag", 1 if verbose else 0)

    x = mdl.addVars(n, m, vtype=GRB.BINARY, name="x")

    # Affectation (parfaite ou non)
    for i in range(n):
        if mariage_parfait:
            mdl.addConstr(gp.quicksum(x[i, j] for j in range(m)) == 1)
        else:
            mdl.addConstr(gp.quicksum(x[i, j] for j in range(m)) <= 1)
    for j in range(m):
        mdl.addConstr(gp.quicksum(x[i, j] for i in range(n)) <= cap[j])

    # Contrainte k-premiers : on annule x[i,j] si j n'est pas dans le top-k de i.
    for i in range(n):
        for j in range(m):
            if rankEtu[i][j] >= k:
                mdl.addConstr(x[i, j] == 0)

    mdl.setObjective(
        gp.quicksum((uE[i][j] + uP[j][i]) * x[i, j]
                    for i in range(n) for j in range(m)),
        GRB.MAXIMIZE,
    )
    mdl.optimize()

    if mdl.Status == GRB.INFEASIBLE:
        return None, None

    x_vals = {(i, j): x[i, j].X for i in range(n) for j in range(m)}
    return affectation_depuis_x(x_vals, n, m), mdl.ObjVal


# ─────────────────────────────────────────────────────────────────────
#  Q14 : Plus petit k donnant un mariage parfait
# ─────────────────────────────────────────────────────────────────────

def plus_petit_k_parfait(prefEtu, prefSpe, cap, verbose=False):
    """
    Cherche le plus petit k tel que le PLNE de Q13 admet un mariage parfait
    (chaque étudiant affecté à un de ses k premiers choix).
    """
    m = len(prefSpe)
    for k in range(1, m + 1):
        aff, val = plne_max_somme_kfirst(prefEtu, prefSpe, cap, k,
                                         mariage_parfait=True, verbose=verbose)
        if aff is not None:
            return k, aff, val
    return None, None, None
