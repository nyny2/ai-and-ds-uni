"""
LU3IN025 - IA et Jeux - Projet 3
Algorithme de Gale-Shapley : affectation étudiants/parcours
"""

import random
import time
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────
#  Lecture des fichiers
# ─────────────────────────────────────────────

def lectureFichier(s):
    monFichier = open(s, "r", encoding="utf-8-sig")
    contenu = monFichier.readlines()
    monFichier.close()
    contenu[0] = contenu[0].split()
    contenu[1] = contenu[1].split()
    return contenu


def createFichierLP(nomFichier, nombreVariables):
    monFichier = open(nomFichier, "w")
    monFichier.write("Maximize\n")
    for i in range(nombreVariables):
        monFichier.write("x" + str(i) + " ")
        if i < nombreVariables - 1:
            monFichier.write("+ ")
        else:
            monFichier.write("\n")
    monFichier.write("st\n")
    monFichier.write("Binary\n")
    for i in range(nombreVariables):
        monFichier.write("x" + str(i) + " ")
    monFichier.write("\n")
    monFichier.write("end")
    monFichier.close()


def lireCE(nomFichier):
    """Retourne prefEtu[i] = liste des parcours dans l'ordre de préférence de l'étudiant i."""
    contenu = lectureFichier(nomFichier)
    res = []
    for s in contenu[1:]:
        if type(s) == str:
            s = s.split()
        prefs = [int(x) for x in s[2:]]
        res.append(prefs)
    return res


def lireCP(nomFichier):
    """Retourne (prefSpe, cap) où :
      - prefSpe[j] = liste des étudiants dans l'ordre de préférence du parcours j
      - cap[j]     = capacité d'accueil du parcours j
    """
    contenu = lectureFichier(nomFichier)
    # contenu[0] = ["NbEtu", "13"]
    # contenu[1] = ["Cap", "2", "1", ...]
    cap = [int(x) for x in contenu[1][1:]]
    res = []
    for s in contenu[2:]:
        if type(s) == str:
            s = s.split()
        prefs = [int(x) for x in s[2:]]
        res.append(prefs)
    return res, cap


# ─────────────────────────────────────────────
#  Structures auxiliaires rapides
# ─────────────────────────────────────────────

def buildRankSpe(prefSpe):
    """rankSpe[j][i] = rang de l'étudiant i dans la liste du parcours j (0 = meilleur).
    Complexité construction : O(n*m). Accès : O(1).
    """
    rankSpe = []
    for prefs in prefSpe:
        rank = {}
        for r, etu in enumerate(prefs):
            rank[etu] = r
        rankSpe.append(rank)
    return rankSpe


def buildRankEtu(prefEtu):
    """rankEtu[i][j] = rang du parcours j dans la liste de l'étudiant i (0 = meilleur).
    Complexité construction : O(n*m). Accès : O(1).
    """
    rankEtu = []
    for prefs in prefEtu:
        rank = {}
        for r, spe in enumerate(prefs):
            rank[spe] = r
        rankEtu.append(rank)
    return rankEtu


# ─────────────────────────────────────────────
#  Q3 – Gale-Shapley côté étudiants
# ─────────────────────────────────────────────

def GSEtu(prefEtu, prefSpe, cap):
    """
    Gale-Shapley où les étudiants proposent (problème des hôpitaux/résidents).

    Structures de données choisies :
      - next_prop[i]   : entier = prochain indice de proposition de l'étudiant i
                         → accès O(1), mise à jour O(1)
      - affectation[j] : liste des étudiants tentativement acceptés par j
                         (taille ≤ cap[j]) → accès O(1), ajout O(1)
      - rankSpe[j][i]  : dict → rang de i chez j, accès O(1)
      - libre          : file (list) des étudiants sans affectation

    Complexité totale : O(n² × m) dans le pire cas (n = nb étudiants, m = nb parcours)
    car chaque étudiant peut faire jusqu'à m propositions.
    En pratique bien plus rapide.

    Retourne (affectation, nb_iterations).
    """
    n = len(prefEtu)
    m = len(prefSpe)

    rankSpe = buildRankSpe(prefSpe)

    next_prop = [0] * n
    libre = list(range(n))
    affectation = [[] for _ in range(m)]

    iterations = 0

    while libre:
        i = libre.pop(0)
        if next_prop[i] >= len(prefEtu[i]):
            continue  # i a épuisé toutes ses propositions, reste non affecté

        j = prefEtu[i][next_prop[i]]
        next_prop[i] += 1
        iterations += 1

        if len(affectation[j]) < cap[j]:
            # Place disponible : acceptation directe
            affectation[j].append(i)
        else:
            # Parcours plein : comparer i avec le moins bon actuel
            pire = max(affectation[j], key=lambda x: rankSpe[j][x])
            if rankSpe[j][i] < rankSpe[j][pire]:
                # i est préféré au pire : remplacement
                affectation[j].remove(pire)
                affectation[j].append(i)
                libre.append(pire)
            else:
                # i est rejeté
                libre.append(i)

    return affectation, iterations


# ─────────────────────────────────────────────
#  Q4 – Gale-Shapley côté parcours
# ─────────────────────────────────────────────

def GSSpe(prefEtu, prefSpe, cap):
    """
    Gale-Shapley où les parcours proposent (adaptation hôpital côté hôpitaux).

    Structures de données :
      - next_prop[j]    : entier = prochain indice de proposition du parcours j  O(1)
      - tenu_par[i]     : dict → parcours qui détient l'offre de i (None si libre)
      - rankEtu[i][j]   : dict → rang de j chez i, accès O(1)
      - places_dispo[j] : entier = capacité restante de j                        O(1)
      - actifs          : file des parcours ayant encore des places et candidats

    Complexité : O(n² × m) dans le pire cas.

    Retourne (affectation, nb_iterations).
    """
    n = len(prefEtu)
    m = len(prefSpe)

    rankEtu = buildRankEtu(prefEtu)

    next_prop = [0] * m
    places_dispo = list(cap)
    tenu_par = [None] * n

    actifs = [j for j in range(m) if cap[j] > 0]
    iterations = 0

    while actifs:
        j = actifs.pop(0)
        if places_dispo[j] <= 0 or next_prop[j] >= len(prefSpe[j]):
            continue

        i = prefSpe[j][next_prop[j]]
        next_prop[j] += 1
        iterations += 1

        if tenu_par[i] is None:
            # i libre : acceptation
            tenu_par[i] = j
            places_dispo[j] -= 1
            if places_dispo[j] > 0 and next_prop[j] < len(prefSpe[j]):
                actifs.append(j)
        else:
            j_actuel = tenu_par[i]
            if rankEtu[i].get(j, m) < rankEtu[i].get(j_actuel, m):
                # i préfère j : abandon de j_actuel
                tenu_par[i] = j
                places_dispo[j] -= 1
                places_dispo[j_actuel] += 1
                # j_actuel récupère une place → peut re-proposer
                if next_prop[j_actuel] < len(prefSpe[j_actuel]):
                    actifs.append(j_actuel)
                if places_dispo[j] > 0 and next_prop[j] < len(prefSpe[j]):
                    actifs.append(j)
            else:
                # i garde j_actuel : j tente le suivant
                if next_prop[j] < len(prefSpe[j]):
                    actifs.append(j)

    affectation = [[] for _ in range(m)]
    for i, j in enumerate(tenu_par):
        if j is not None:
            affectation[j].append(i)

    return affectation, iterations


# ─────────────────────────────────────────────
#  Q6 – Vérification de la stabilité
# ─────────────────────────────────────────────

def pairesInstables(affectation, prefEtu, prefSpe, cap):
    """
    Retourne la liste des paires instables (i, j) telles que :
      - l'étudiant i préfère le parcours j à son affectation actuelle, ET
      - le parcours j préfère i à au moins un de ses affectés
        (ou bien j n'est pas encore plein).

    Complexité : O(n × m) grâce aux tables de rangs O(1).
    """
    rankSpe = buildRankSpe(prefSpe)
    rankEtu = buildRankEtu(prefEtu)
    n = len(prefEtu)
    m = len(prefSpe)

    aff_etu = {}
    for j, etudiants in enumerate(affectation):
        for i in etudiants:
            aff_etu[i] = j

    instables = []

    for i in range(n):
        j_actuel = aff_etu.get(i, None)
        for j in range(m):
            if j == j_actuel:
                continue
            # i préfère-t-il j à son affectation actuelle ?
            rang_j = rankEtu[i].get(j, n)
            rang_act = rankEtu[i].get(j_actuel, n) if j_actuel is not None else n
            if rang_j >= rang_act:
                continue

            # j préfère-t-il i à au moins un de ses affectés ?
            if len(affectation[j]) < cap[j]:
                instables.append((i, j))
            else:
                pire = max(affectation[j], key=lambda x: rankSpe[j].get(x, n))
                if rankSpe[j].get(i, n) < rankSpe[j].get(pire, n):
                    instables.append((i, j))

    return instables


# ─────────────────────────────────────────────
#  Q7 – Génération aléatoire de préférences
# ─────────────────────────────────────────────

def genPrefsEtu(n, m=10):
    """Génère les préférences aléatoires de n étudiants sur m parcours.
    Retourne prefEtu[i] = permutation aléatoire de range(m).
    """
    parcours = list(range(m))
    return [random.sample(parcours, m) for _ in range(n)]


def genPrefsSpe(n, m=10):
    """Génère les préférences aléatoires de m parcours sur n étudiants,
    et des capacités équilibrées dont la somme vaut n.
    Retourne (prefSpe, cap).
    """
    etudiants = list(range(n))
    prefs = [random.sample(etudiants, n) for _ in range(m)]
    base = n // m
    reste = n % m
    cap = [base + (1 if j < reste else 0) for j in range(m)]
    return prefs, cap


# ─────────────────────────────────────────────
#  Q8–Q10 – Mesure du temps et des itérations
# ─────────────────────────────────────────────

def mesureTemps(algo, n_values, nb_tests=10, m=10):
    """Mesure le temps moyen d'exécution et le nombre moyen d'itérations."""
    temps_moyens = []
    iter_moyens = []

    for n in n_values:
        temps_list = []
        iter_list = []
        for _ in range(nb_tests):
            prefEtu = genPrefsEtu(n, m)
            prefSpe, cap = genPrefsSpe(n, m)
            t0 = time.perf_counter()
            _, iters = algo(prefEtu, prefSpe, cap)
            t1 = time.perf_counter()
            temps_list.append(t1 - t0)
            iter_list.append(iters)
        temps_moyens.append(sum(temps_list) / nb_tests)
        iter_moyens.append(sum(iter_list) / nb_tests)
        print(f"  n={n:4d} : t_moy={temps_moyens[-1]:.4f}s, iter_moy={iter_moyens[-1]:.0f}")

    return temps_moyens, iter_moyens


def tracerCourbes(n_values, temps_etu, temps_spe, iter_etu, iter_spe):
    """Trace et sauvegarde les courbes temps/itérations pour les deux algorithmes."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(n_values, temps_etu, 'b-o', label='GS côté étudiants')
    axes[0].plot(n_values, temps_spe, 'r-s', label='GS côté parcours')
    axes[0].set_xlabel("Nombre d'étudiants n")
    axes[0].set_ylabel("Temps moyen (secondes)")
    axes[0].set_title("Q8 – Temps de calcul en fonction de n")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(n_values, iter_etu, 'b-o', label='GS côté étudiants')
    axes[1].plot(n_values, iter_spe, 'r-s', label='GS côté parcours')
    axes[1].set_xlabel("Nombre d'étudiants n")
    axes[1].set_ylabel("Nombre moyen d'itérations")
    axes[1].set_title("Q10 – Nombre d'itérations en fonction de n")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.savefig("courbes_GS.png", dpi=150)
    plt.show()
    print("→ Courbes sauvegardées dans courbes_GS.png")


# ─────────────────────────────────────────────
#  Utilitaires d'affichage
# ─────────────────────────────────────────────

NOM_PARCOURS = ["AI2D", "BIM", "CCA", "IMA", "MIND", "QI", "RES", "SAR", "SESI", "STL"]


def afficheAffectation(affectation, prefEtu, prefSpe, label=""):
    """Affiche l'affectation avec rangs et utilités."""
    rankEtu = buildRankEtu(prefEtu)
    rankSpe = buildRankSpe(prefSpe)
    m = len(prefSpe)
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    util_etu_total = 0
    util_spe_total = 0
    util_etu_min = float('inf')
    total_affectes = 0

    for j, etudiants in enumerate(affectation):
        nom = NOM_PARCOURS[j] if j < len(NOM_PARCOURS) else f"Spe{j}"
        for i in etudiants:
            rang_etu = rankEtu[i].get(j, -1)
            rang_spe = rankSpe[j].get(i, -1)
            nb_parcours = len(prefEtu[i])
            nb_etu_spe = len(prefSpe[j])
            util_e = nb_parcours - rang_etu
            util_s = nb_etu_spe - rang_spe
            util_etu_total += util_e
            util_spe_total += util_s
            util_etu_min = min(util_etu_min, util_e)
            total_affectes += 1
            print(f"  Etu{i:02d} → {nom:5s}  "
                  f"(rang_etu={rang_etu}, util_etu={util_e} | "
                  f"rang_spe={rang_spe}, util_spe={util_s})")

    if total_affectes > 0:
        print(f"\n  Étudiants affectés     : {total_affectes}/{len(prefEtu)}")
        print(f"  Utilité moy. étudiants : {util_etu_total/total_affectes:.2f}")
        print(f"  Utilité min. étudiants : {util_etu_min}")
        print(f"  Utilité totale (é+p)   : {util_etu_total + util_spe_total}")
