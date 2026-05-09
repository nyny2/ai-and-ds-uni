"""
LU3IN025 - IA et Jeux - Projet 3 : main.py
Exécution de toutes les questions Q3 à Q10.
"""

import exemple as e

# ─────────────────────────────────────────────
#  Lecture des données
# ─────────────────────────────────────────────
print("Lecture des fichiers de données...")
prefEtu = e.lireCE("PrefEtu.txt")
prefSpe, cap = e.lireCP("PrefSpe.txt")

n = len(prefEtu)
m = len(prefSpe)
print(f"  {n} étudiants, {m} parcours, capacités = {cap}")
print(f"  Capacité totale = {sum(cap)}")

# ─────────────────────────────────────────────
#  Q5 – Appliquer GS côté étudiants
# ─────────────────────────────────────────────
print("\n" + "─"*60)
print("Q3/Q5 – Gale-Shapley côté ÉTUDIANTS (étudiants proposent)")
print("─"*60)
aff_etu, iters_etu = e.GSEtu(prefEtu, prefSpe, cap)
e.afficheAffectation(aff_etu, prefEtu, prefSpe, "GS côté étudiants")
print(f"\n  Nombre d'itérations : {iters_etu}")

# ─────────────────────────────────────────────
#  Q5 – Appliquer GS côté parcours
# ─────────────────────────────────────────────
print("\n" + "─"*60)
print("Q4/Q5 – Gale-Shapley côté PARCOURS (parcours proposent)")
print("─"*60)
aff_spe, iters_spe = e.GSSpe(prefEtu, prefSpe, cap)
e.afficheAffectation(aff_spe, prefEtu, prefSpe, "GS côté parcours")
print(f"\n  Nombre d'itérations : {iters_spe}")

# ─────────────────────────────────────────────
#  Q6 – Vérification de la stabilité
# ─────────────────────────────────────────────
print("\n" + "─"*60)
print("Q6 – Vérification de la stabilité")
print("─"*60)

instables_etu = e.pairesInstables(aff_etu, prefEtu, prefSpe, cap)
instables_spe = e.pairesInstables(aff_spe, prefEtu, prefSpe, cap)

if instables_etu:
    print(f"\n  GS côté étudiants : {len(instables_etu)} paire(s) instable(s) !")
    for (i, j) in instables_etu[:10]:
        print(f"    (Etu{i}, {e.NOM_PARCOURS[j]})")
else:
    print("\n  GS côté étudiants : affectation STABLE ✓")

if instables_spe:
    print(f"\n  GS côté parcours  : {len(instables_spe)} paire(s) instable(s) !")
    for (i, j) in instables_spe[:10]:
        print(f"    (Etu{i}, {e.NOM_PARCOURS[j]})")
else:
    print("\n  GS côté parcours  : affectation STABLE ✓")

# ─────────────────────────────────────────────
#  Q8–Q10 – Mesure du temps et des itérations
# ─────────────────────────────────────────────
print("\n" + "─"*60)
print("Q8–Q10 – Mesure des performances (n de 200 à 2000, 10 tests)")
print("─"*60)

n_values = list(range(200, 2001, 200))

print("\n  GS côté étudiants :")
temps_etu, iter_etu = e.mesureTemps(e.GSEtu, n_values, nb_tests=10)

print("\n  GS côté parcours :")
temps_spe, iter_spe = e.mesureTemps(e.GSSpe, n_values, nb_tests=10)

e.tracerCourbes(n_values, temps_etu, temps_spe, iter_etu, iter_spe)

print("\n" + "="*60)
print("Terminé. Pour Q11-Q15 (PLNE avec Gurobi), voir rapport.")
print("="*60)
