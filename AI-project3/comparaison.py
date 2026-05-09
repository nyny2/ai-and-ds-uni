"""
LU3IN025 - IA et Jeux - Projet 3
Question 15 : comparaison des cinq solutions obtenues sur l'instance fournie
(PrefEtu.txt, PrefSpe.txt) :

    1. Gale-Shapley côté étudiants    (Q3)
    2. Gale-Shapley côté parcours     (Q4)
    3. PLNE max-min utilité (Q11)
    4. PLNE max somme       (Q12)
    5. PLNE max somme avec contrainte k-premiers, plus petit k (Q14)

Critères : utilité moyenne, utilité minimale (étudiants), nombre de paires
instables.
"""

import exemple as e
import plne as p


NOM_PARCOURS = e.NOM_PARCOURS


def utilites(affectation, prefEtu, prefSpe):
    """Renvoie (util_moy_etu, util_min_etu, util_moy_total, nb_affectes)."""
    n = len(prefEtu)
    m = len(prefSpe)
    rankEtu = e.buildRankEtu(prefEtu)
    rankSpe = e.buildRankSpe(prefSpe)

    util_etu = []
    util_tot = []
    for j, etudiants in enumerate(affectation):
        for i in etudiants:
            uE = m - rankEtu[i][j]
            uP = n - rankSpe[j][i]
            util_etu.append(uE)
            util_tot.append(uE + uP)

    nb = len(util_etu)
    if nb == 0:
        return 0.0, 0, 0.0, 0
    return (sum(util_etu) / nb,
            min(util_etu),
            sum(util_tot) / nb,
            nb)


def affichage_court(label, affectation, prefEtu, prefSpe, cap):
    n = len(prefEtu)
    m = len(prefSpe)
    rankEtu = e.buildRankEtu(prefEtu)

    aff_etu = {}
    for j, etudiants in enumerate(affectation):
        for i in etudiants:
            aff_etu[i] = j

    print(f"\n  {label}")
    print("  " + "─" * 56)
    pairs = []
    for i in range(n):
        if i in aff_etu:
            j = aff_etu[i]
            pairs.append(f"Etu{i:02d}→{NOM_PARCOURS[j]}({rankEtu[i][j]+1})")
        else:
            pairs.append(f"Etu{i:02d}→∅")
    # 4 par ligne
    for k in range(0, len(pairs), 4):
        print("  " + "  ".join(f"{x:<14}" for x in pairs[k:k + 4]))


def _trouver(nom):
    """Cherche le fichier dans new/, puis dans le dossier parent."""
    import os
    for d in (os.path.dirname(__file__), os.path.dirname(os.path.dirname(__file__))):
        chemin = os.path.join(d, nom)
        if os.path.isfile(chemin):
            return chemin
    return nom


def main():
    prefEtu = e.lireCE(_trouver("PrefEtu.txt"))
    prefSpe, cap = e.lireCP(_trouver("PrefSpe.txt"))

    n, m = len(prefEtu), len(prefSpe)
    print(f"Instance : n={n} étudiants, m={m} parcours, "
          f"capacité totale = {sum(cap)}")

    # 1. GS côté étudiants
    aff_GE, _ = e.GSEtu(prefEtu, prefSpe, cap)
    # 2. GS côté parcours
    aff_GP, _ = e.GSSpe(prefEtu, prefSpe, cap)
    # 3. Q11 : max-min
    aff_Q11, U_min_Q11 = p.plne_max_min(prefEtu, prefSpe, cap)
    # 4. Q12 : max somme (sans contrainte)
    aff_Q12, val_Q12 = p.plne_max_somme(prefEtu, prefSpe, cap)
    # 5. Q14 : plus petit k tel que PLNE Q13 a un mariage parfait
    k_star, aff_Q14, val_Q14 = p.plus_petit_k_parfait(prefEtu, prefSpe, cap)
    print(f"\nQ14 : plus petit k donnant un mariage parfait = {k_star}\n")

    solutions = [
        ("GS côté étudiants",          aff_GE),
        ("GS côté parcours",           aff_GP),
        ("PLNE Q11 (max-min)",         aff_Q11),
        ("PLNE Q12 (max somme)",       aff_Q12),
        (f"PLNE Q14 (k={k_star} parfait)", aff_Q14),
    ]

    print("=" * 72)
    print(f"{'Solution':<30}{'u_moy':>8}{'u_min':>8}{'u_tot/aff':>12}"
          f"{'#aff':>6}{'#inst':>6}")
    print("─" * 72)
    for label, aff in solutions:
        u_moy, u_min, u_tot, nb = utilites(aff, prefEtu, prefSpe)
        instables = e.pairesInstables(aff, prefEtu, prefSpe, cap)
        print(f"{label:<30}{u_moy:>8.2f}{u_min:>8d}{u_tot:>12.2f}"
              f"{nb:>6d}{len(instables):>6d}")
    print("=" * 72)

    # Affectations détaillées
    for label, aff in solutions:
        affichage_court(label, aff, prefEtu, prefSpe, cap)


if __name__ == "__main__":
    main()
