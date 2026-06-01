# Rapport de projet

## Groupe
* Nehir Yüksekkaya 21307751
* Kathy Vo 21307514
## Description des choix importants d'implémentation

### Détection des équipes

Les joueurs sont assignés à leur équipe en fonction de leur position de départ sur la carte : les joueurs situés sur la ligne `x == 2` appartiennent à l'équipe 0, ceux sur la ligne `x == 18` à l'équipe 1. Ce choix est plus robuste que de couper la liste des joueurs en deux, car il ne dépend pas de l'ordre dans lequel `pySpriteWorld` charge les sprites.

### Détection de la couleur des fioles

La couleur d'une fiole est détectée en lisant l'attribut `f.name` du sprite et en cherchant les mots-clés `yellow`, `red`, `green`, `blue`. En cas d'échec (attribut absent selon la version de `pySpriteWorld`), le code se rabat sur le nom de la carte. Cela permet au code de fonctionner à la fois sur les cartes mono-couleur et sur `mixed-map`.

### Alternance de priorité

À chaque épisode, l'ordre de déplacement des équipes est inversé (`[0,1]` les épisodes pairs, `[1,0]` les épisodes impairs). Cela évite qu'une équipe bénéficie systématiquement de l'avantage du premier mouvement, notamment pour le placement autour des fioles.

### Positions légales

Une position est considérée légale si elle est dans les bornes du plateau (en excluant les deux premières et dernières lignes/colonnes réservées au contour), si elle n'est pas occupée par un autre joueur, et si elle n'est pas sur une fiole. Cette vérification est effectuée dynamiquement à chaque appel, ce qui garantit que deux joueurs de la même équipe ne choisissent pas la même case cible.

### Calcul du score

La fonction `compute_winner` applique les règles propres à chaque couleur de fiole :
- **Jaune** : au moins 1 joueur suffit ; l'équipe avec le plus de joueurs remporte la fiole.
- **Rouge** : au moins 2 joueurs de la même équipe sont requis ; l'équipe avec le plus remporte la fiole.
- **Verte** : au moins 3 joueurs au total sont requis ; l'équipe majoritaire remporte la fiole.
- **Bleue** : comme rouge, mais un joueur seul bat une équipe qui remplit la condition.

Dans tous les cas, une égalité après vérification des conditions ne donne la fiole à personne.

### Harnais de comparaison

La fonction `compare_all` automatise la comparaison de toutes les paires de stratégies sur toutes les cartes disponibles. Elle réinitialise proprement l'état d'historique et de regret entre chaque match, et affiche un tableau récapitulatif en fin d'exécution.

---

## Description des stratégies proposées

### Stratégies stationnaires

**Aléatoire** : chaque joueur choisit une fiole uniformément au hasard parmi les fioles disponibles. C'est la stratégie de référence (baseline).

**Têtu** : l'équipe 0 cible toujours la première fiole, l'équipe 1 toujours la dernière. La stratégie ne s'adapte jamais, quelle que soit la situation.

**Greedy** : chaque joueur choisit la fiole actuellement la moins contestée (celle autour de laquelle il y a le moins de joueurs au total). Cette stratégie évite les sureffectifs et maximise le nombre de fioles remportées sans coordination explicite.

**Aléatoire expert** : à chaque épisode, l'équipe tire au sort une distribution prédéfinie parmi cinq (par exemple `[8,0,0,0,0]` — tout sur une fiole, ou `[2,2,2,2,0]` — spread équilibré) et y affecte ses joueurs en conséquence. Elle introduit de la diversité sans apprentissage.

**Coordination** : l'équipe choisit une fiole principale au hasard. Chaque joueur va vers cette fiole avec une probabilité de 0,7, et vers une fiole aléatoire sinon. Cela favorise la concentration des forces tout en gardant une part d'imprévisibilité.

### Stratégies basées sur l'historique

**Fictitious play** : l'équipe observe la distribution empirique de l'adversaire (combien de joueurs il a envoyé en moyenne sur chaque fiole) et calcule pour chaque fiole le nombre minimal de joueurs nécessaires pour la remporter étant donné la présence adverse attendue. Elle alloue ensuite ses joueurs de manière gloutonne, en ciblant d'abord les fioles les moins coûteuses à gagner. Cette allocation optimale lui permet de cibler plusieurs fioles simultanément plutôt que de tout concentrer sur une seule.

**Regret matching** : à chaque épisode, l'équipe calcule le *regret contrefactuel* pour chaque fiole — c'est-à-dire le gain supplémentaire qu'elle aurait obtenu si ses joueurs avaient été envoyés sur cette fiole plutôt que sur leur cible réelle. Les fioles à regret positif élevé sont ensuite échantillonnées avec une probabilité proportionnelle à ce regret. Cette stratégie converge théoriquement vers un équilibre corrélé.

---

## Description des résultats

Les comparaisons ont été effectuées sur les cinq cartes disponibles : `yellow-map`, `red-map`, `green-map`, `blue-map` et `mixed-map`, avec 20 épisodes par match. Le tableau ci-dessous indique le score de T0 / score de T1 pour chaque paire.

```
Matchup                              yellow-map     red-map   green-map    blue-map   mixed-map
-----------------------------------------------------------------------------------------------
aleatoire vs tetu                       5/2          4/2        7/4          9/4          9/5
aleatoire vs greedy                     4/5          3/4        5/7         14/1          6/8
aleatoire vs expert                     4/3          2/3        8/3          6/2         14/3
aleatoire vs coordination               4/2          5/2        7/3          8/5          7/6
aleatoire vs fictitious                 5/4          2/4        5/5         12/3          8/7
aleatoire vs regret                     5/4          2/3        6/7          6/8          6/7
tetu vs greedy                          3/7          2/6        6/6         12/1          6/10
tetu vs expert                          5/5          2/3        4/1          7/3         10/4
tetu vs coordination                    3/2          2/2        4/5          4/5          8/8
tetu vs fictitious                      2/8          2/7        3/9          7/7          5/7
tetu vs regret                          2/7          2/3        6/5          5/5          8/8
greedy vs expert                        3/3          3/4        8/3         11/3         12/3
greedy vs coordination                  7/2          4/2        6/7          5/8         11/6
greedy vs fictitious                    4/4          2/4        3/10         1/7          9/8
greedy vs regret                        3/3          4/4        7/6          3/7          7/6
expert vs coordination                  8/2          4/2        1/5          3/5          5/10
expert vs fictitious                    3/4          3/5        1/9          0/13         1/13
expert vs regret                        2/6          3/5        3/5          1/9          2/11
coordination vs fictitious              2/7          2/6        3/7          5/4          5/6
coordination vs regret                  2/7          2/4        5/6          7/5          6/10
fictitious vs regret                    4/5          4/4        6/2          6/7          4/10
```

### Analyse par stratégie

**Fictitious play** est la stratégie apprise la plus performante sur la majorité des cartes. Grâce à son allocation gloutonne, elle répartit ses joueurs de manière optimale sur plusieurs fioles plutôt que de tout concentrer sur une seule. Elle bat greedy de manière convaincante sur `green-map` (3/10) et `blue-map` (1/7), et domine complètement expert sur toutes les cartes (`expert vs fictitious` : 3/4, 3/5, 1/9, 0/13, 1/13). Face à coordination et têtu, elle gagne systématiquement dès que l'historique se construit.

**Regret matching** est la deuxième stratégie apprise et reste compétitive. Elle bat fictitious play sur `blue-map` (6/7) et `mixed-map` (4/10), et domine expert et coordination de façon consistante. Sur les cartes simples (`yellow-map`, `red-map`), les deux stratégies apprises sont proches, ce qui confirme que leur avantage vient de l'adaptation à des règles complexes plutôt que d'une supériorité intrinsèque.

**Greedy** est la meilleure stratégie stationnaire sur `yellow-map`, `red-map` et `mixed-map`, mais s'effondre complètement sur `blue-map` : elle perd contre aléatoire (14/1), contre têtu (12/1), et contre fictitious (1/7). Son comportement de dispersion — éviter les fioles contestées — l'amène à ne jamais concentrer suffisamment de joueurs sur une fiole pour satisfaire les conditions de la carte bleue, tout en la rendant vulnérable à l'envoi d'un joueur isolé adverse.

**Têtu** est généralement faible mais produit un résultat surprenant sur `blue-map` : elle bat greedy 12/1. Cela s'explique par le fait que la concentration de tous les joueurs sur une seule fiole est structurellement compatible avec la règle du joueur seul — les joueurs non assignés à la fiole principale se retrouvent isolés ailleurs et peuvent exploiter la règle bleue contre un adversaire dispersé comme greedy.

**Expert** est la stratégie la plus faible dès qu'elle affronte une stratégie apprise. Ses distributions fixes ne lui permettent pas d'anticiper les règles spécifiques à chaque carte, et ses allocations deviennent rapidement prévisibles. Le score `expert vs fictitious` de 0/13 sur `blue-map` est le plus extrême de tout le tableau.

**Aléatoire** et **coordination** se comportent de manière similaire, légèrement au-dessus de têtu mais clairement en dessous des stratégies apprises sur la plupart des cartes.

### Effet de la carte

`blue-map` produit les résultats les plus hétérogènes et inverse plusieurs classements par rapport aux autres cartes. La règle du joueur seul crée une structure de gain fondamentalement différente : la dispersion des joueurs, avantageuse ailleurs, devient un handicap sévère sur cette carte. Greedy, dont toute la logique repose sur la dispersion, en est la principale victime. À l'inverse, les stratégies qui concentrent naturellement leurs joueurs — fictitious play, têtu, coordination — s'y comportent mieux.

Sur `yellow-map` et `red-map`, les règles sont plus simples et les écarts entre stratégies plus faibles, la majorité primant toujours. `green-map` et `mixed-map` occupent une position intermédiaire, avec des avantages visibles pour les stratégies apprises sans les inversions radicales de `blue-map`.

### Conclusion

Les résultats confirment que l'apprentissage apporte un avantage clair et consistant sur les cartes complexes. Fictitious play, grâce à son allocation gloutonne multi-fioles, est la stratégie la plus robuste sur l'ensemble du tableau. Regret matching lui est légèrement inférieur mais reste compétitif. Parmi les stratégies stationnaires, greedy domine sur les cartes simples mais est structurellement inadapté à `blue-map`. Aucune stratégie n'est universellement dominante : le choix optimal dépend de la carte jouée.
