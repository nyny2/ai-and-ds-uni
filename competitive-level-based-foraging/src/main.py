from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain, combinations


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game,name
    name = _boardname if _boardname is not None else 'mixed-map'
    #game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 500  # frames per second
    game.mainiteration()
    player = game.player


def get_fiole_color(f):
    """
    Detect fiole color from its sprite name.
    Falls back to the map name for single-color maps.
    If neither works, run print(dir(items[0])) to find the right attribute.
    """
    try:
        n = f.name.lower()
        for color in ('yellow', 'red', 'green', 'blue'):
            if color in n:
                return color
    except AttributeError:
        pass
    for color in ('yellow', 'red', 'green', 'blue'):
        if color in name:
            return color
    return 'yellow'  # default fallback

# -------------------------------
# Calcul des scores
# -------------------------------
def compute_winner(fiole, n1, n2):
    color = get_fiole_color(fiole)

    # Fiole jaune
    if color == 'yellow':
        if n1 > n2 and n1 >= 1:
            return 0
        if n2 > n1 and n2 >= 1:
            return 1

    # Fiole rouge
    if color == 'red':
        cond1 = n1 >= 2
        cond2 = n2 >= 2

        if cond1 and not cond2:
            return 0
        if cond2 and not cond1:
            return 1
        if cond1 and cond2:
            if n1 > n2:
                return 0
            if n2 > n1:
                return 1
    
    # Fiole verte
    if color == 'green':
        if (n1 + n2) >= 3:
            if n1 > n2:
                return 0
            if n2 > n1:
                return 1

    # Fiole bleue
    if color == 'blue':
        cond1 = n1 >= 2
        cond2 = n2 >= 2

        if n1 == 1 and cond2:
            return 0
        if n2 == 1 and cond1:
            return 1

        if cond1 and not cond2:
            return 0
        if cond2 and not cond1:
            return 1
        if cond1 and cond2:
            if n1 > n2:
                return 0
            if n2 > n1:
                return 1

    return None

def run_match(strat_name_0, strat_name_1, nb_episodes=20, verbose=False):
    #for arg in sys.argv:
    #iterations = 40 # nb de pas max par episode
    #if len(sys.argv) == 2:
    #    iterations = int(sys.argv[1])
    #print ("Iterations: ")
    #print (iterations)
    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nb_lignes = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize
    assert nb_lignes == nb_cols # a priori on souhaite un plateau carre
    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker le contour)
    lMax=nb_lignes-2
    cMin=2
    cMax=nb_cols-2
   
    
    players = [o for o in game.layers['joueur']]
    nb_players = len(players)


    items = [o for o in game.layers["ramassable"]]  #
    nb_fioles = len(items)

    nb_episodes = 2


    #-------------------------------
    # Fonctions permettant de récupérer les listes des coordonnées
    # d'un ensemble d'objets ou de joueurs
    #-------------------------------

    def item_states(items):
        # donne la liste des coordonnees des items
        return [o.get_rowcol() for o in items]
    
    def player_states(players):
        # donne la liste des coordonnees des joueurs
        return [p.get_rowcol() for p in players]
    


    #-------------------------------
    # Rapport de ce qui est trouve sut la carte
    #-------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print('joueurs:', nb_players)
    print("fioles:",nb_fioles)
    print("lignes:", nb_lignes)
    print("colonnes:", nb_cols)
    print("-------------------------------------------")

    #-------------------------------
    # Carte demo yellow
    # 2 x 8 joueurs
    # 5 fioles jaunes
    #-------------------------------

    team = [[], []]  # 2 équipes
    for o in players:
        (x, y) = o.get_rowcol()
        if x == 2:  # les joueurs de team0 sur la ligne du haut
            team[0].append(o)
        elif x == 18:  # les joueurs de team1 sur la ligne du bas
            team[1].append(o)

    assert len(team[0]) == len(team[1])  # on veut un match équilibré donc équipe de même taille
    nb_players_team = int(nb_players / 2)

    init_states = [[],[]]
    # print(teamA)
    init_states[0] = player_states(team[0])

    # print(teamB)
    init_states[1] = player_states(team[1])


    #-------------------------------

    #-------------------------------
    # Fonctions definissant les positions legales et placement aléatoire
    #-------------------------------

    def around_pos(pos):
        # donne la liste des positions autour d'une pos (x,y) donnee
        x,y=pos
        return [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]

    def around_pos_free(pos):
        return [pos for pos in around_pos(pos) if legal_position(pos)]

    def busy(pos):
        return around_pos_free(pos) == []

    def legal_position(pos):
        row,col = pos
        # une position legale est dans la carte et pas sur une fiole ni sur un joueur
        return ((pos not in item_states(items)) and (pos not in player_states(players)) and row>lMin and row<lMax-1 and col>=cMin and col<cMax)


    def players_around_item(f):
        """
        :param f: objet fiole
        :return: nombre d'objet de chaque team
        """
        are_here = [0,0]
        pos = f.get_rowcol()
        for i in [0,1]:
            for j in team[i]:
                if j.get_rowcol() in around_pos(pos):
                    are_here[i]+=1
        return are_here


    def move(p,f,choix_fiole,choix_pos,t,path):
        while busy(f.get_rowcol()): # si plus de place on choisit une autre fiole
            f = random.choice(items)
        choix_fiole.append(f)
        # choisir une position libre autour de la fiole choisie
        chosen_pos = random.choice(around_pos_free(f.get_rowcol()))
        choix_pos.append(chosen_pos)
        pos_player = team[t][p].get_rowcol()
        print("Player ", p, " starting from ", pos_player, " going to potion ", choix_fiole[p].get_rowcol(), " at ", choix_pos[p])

        # A*
        g = np.ones((nb_lignes, nb_cols), dtype=bool)
        for i in range(nb_lignes):
            g[0][i] = g[1][i] = g[nb_lignes-1][i] = g[nb_lignes-2][i] = False
            g[i][0] = g[i][1] = g[i][nb_lignes-1] = g[i][nb_lignes-2] = False

        prob = ProblemeGrid2D(pos_player, chosen_pos, g, 'manhattan')
        new_path = probleme.astar(prob, verbose=False)
        path.append(new_path)
        # on fait bouger le joueur jusqu'à son but
        # en suivant le chemin trouve avec A*
        for (row, col) in new_path:
            team[t][p].set_rowcol(row, col)
            game.mainiteration()


    # -------------------------------
    # Strategie aleatoire
    # -------------------------------
    def strategie_aleatoire(t):
        print("Team ",t)
        path = []
        choix_fiole = []
        choix_pos = []

        for p in range(0,nb_players_team):
            f = random.choice(items)
            move(p,f,choix_fiole,choix_pos,t,path)



    # -------------------------------
    # Strategie tetu
    # -------------------------------
    def strategie_tetu(t):
        # chaque équipe choisit UNE fiole fixe (toujours la même)
        target_fioles = [items[0], items[-1]]  
        # ex: team 0 → fiole 0, team 1 → dernière fiole
        print("Team ", t)
        path = []
        choix_pos = []
        choix_fiole = []

        f = target_fioles[t]

        for p in range(nb_players_team):
            move(p,f,choix_fiole,choix_pos,t,path)


    # -------------------------------
    # Strategie greedy
    # -------------------------------
    def strategie_greedy(t):    
        print("Team ", t)
        path = []
        choix_fiole = []
        choix_pos = []

        for p in range(nb_players_team):
            # Choix de la meilleure fiole
            # trier les fioles par nombre de joueurs autour (croissant)
            sorted_fioles = sorted(items, key=lambda f: sum(players_around_item(f)))
            # trouver une fiole non saturée
            f = None

            for f in sorted_fioles:
                if not busy(f.get_rowcol()):
                    break

            if f is None:
                f = random.choice(items)

            move(p,f,choix_fiole,choix_pos,t,path)


    # -------------------------------
    # Strategie aleatoire expert
    # -------------------------------
    def strategie_aleatoire_expert(t):
        # distributions prédéfinies (somme = nb_players_team)
        distributions = [
            [8,0,0,0,0],   # tout sur une fiole
            [4,4,0,0,0],   # split 2 fioles
            [3,3,2,0,0],
            [2,2,2,2,0],
            [2,2,1,1,2]
        ]
        print("Team ", t)
        path = []
        choix_fiole = []
        choix_pos = []

        # choisir une distribution aléatoire
        dist = random.choice(distributions)
        print("Distribution choisie :", dist)

        p = 0

        for i, nb in enumerate(dist):
            if i >= len(items):
                break

            f = items[i]

            for _ in range(nb):
                if p >= nb_players_team:
                    break

                move(p,f,choix_fiole,choix_pos,t,path)
                p += 1


    # -------------------------------
    # Strategie coordination
    # -------------------------------
    def strategie_coordination(t):
        print("Team ", t)
        path = []
        choix_fiole = []
        choix_pos = []

        # choisir UNE fiole principale
        main_target = random.choice(items)

        for p in range(nb_players_team):

            # probabilité de coordination
            if random.random() < 0.7:
                f = main_target
            else:
                f = random.choice(items)

            move(p,f,choix_fiole,choix_pos,t,path)


    #-------------------------------
    # History state for learned strategies
    # (declared for fictitious and regret)
    #-------------------------------
 
    # historique[t][i] = cumulative number of players team t sent to fiole i
    historique = [np.zeros(nb_fioles), np.zeros(nb_fioles)]
    # nb_obs[t] = number of episodes observed so far for team t
    nb_obs = [0, 0]
    # regrets[t][i] = cumulative counterfactual regret of team t for fiole i
    regrets = [np.zeros(nb_fioles), np.zeros(nb_fioles)]


    #-------------------------------
    # Strategy — fictitious play
    #-------------------------------
    def strategie_fictitious(t):
        """
        Fictitious play: best-respond to the opponent's empirical distribution.
 
        We compute how often the opponent has sent players to each fiole on
        average, then we concentrate all our players on the fiole where the
        opponent is present the LEAST (maximises our chance of winning it
        uncontested, or with a majority).
        """
        print("Team ", t, "— fictitious play")
        opp = 1 - t
 
        if nb_obs[opp] > 0:
            opp_avg = historique[opp] / nb_obs[opp]
        else:
            opp_avg = np.ones(nb_fioles) / nb_fioles
 
        def min_players_to_win(i):
            """Minimum players of team t needed to win fiole i given expected opp."""
            exp_opp = int(round(opp_avg[i]))
            for k in range(1, nb_players_team + 1):
                n = [0, 0]
                n[t]   = k
                n[1-t] = exp_opp
                if compute_winner(items[i], n[0], n[1]) == t:
                    return k
            return nb_players_team + 1  # unwinnable given expected opp
 
        # Sort fioles by cost (cheapest to win first)
        costs = sorted(range(nb_fioles), key=min_players_to_win)
 
        # Greedily allocate players
        allocation = np.zeros(nb_fioles, dtype=int)
        remaining = nb_players_team
        for i in costs:
            cost = min_players_to_win(i)
            if cost <= remaining:
                allocation[i] = cost
                remaining -= cost
            if remaining == 0:
                break
 
        # Spread leftover players across already-targeted fioles
        if remaining > 0:
            for i in costs:
                if allocation[i] > 0:
                    allocation[i] += remaining
                    break
 
        # Move players according to allocation
        path, choix_fiole, choix_pos = [], [], []
        p = 0
        for i in range(nb_fioles):
            f = items[i]
            for _ in range(allocation[i]):
                if p >= nb_players_team: break
                if busy(f.get_rowcol()):
                    f = next((x for x in items if not busy(x.get_rowcol())),
                             random.choice(items))
                move(p, f, choix_fiole, choix_pos, t, path)
                p += 1
 
        # Fallback for any unassigned players
        while p < nb_players_team:
            move(p, random.choice(items), choix_fiole, choix_pos, t, path)
            p += 1


    #-------------------------------
    # Strategy — regret matching
    #-------------------------------
    def strategie_regret(t):
        """
        Regret matching: sample fioles proportionally to accumulated
        positive counterfactual regrets.
 
        Counterfactual regret for fiole i at episode e:
            R_i = (score we would have gotten if ALL players went to fiole i)
                  - (score we actually got this episode)
 
        Over time, positive regret means "I should have gone there more".
        Sampling proportionally to positive regrets converges to a
        correlated equilibrium.
        """
        print("Team ", t, "— regret matching")
 
        path, choix_fiole, choix_pos = [], [], []

        for p in range(nb_players_team):
            r     = np.maximum(regrets[t], 0)
            total = r.sum()
            probs = r / total if total > 0 else np.ones(nb_fioles) / nb_fioles
            idx = int(np.random.choice(nb_fioles, p=probs))
            f   = items[idx]
            if busy(f.get_rowcol()):
                f = next((x for x in items if not busy(x.get_rowcol())),
                         random.choice(items))
            move(p, f, choix_fiole, choix_pos, t, path)


    def update_history_and_regrets(scores):
        """
        Called once per episode AFTER scoring.
        Updates historique and regrets for both teams.
        """
        for t in [0, 1]:
            # --- update historique ---
            counts = np.zeros(nb_fioles)
            for p in team[t]:
                for i, f in enumerate(items):
                    if p.get_rowcol() in around_pos(f.get_rowcol()):
                        counts[i] += 1
            historique[t] += counts
            nb_obs[t] += 1
 
            # --- update regrets ---
            # actual score this team got this episode
            actual = scores[t]
 
            for i, f in enumerate(items):
                # Counterfactual: what if ALL nb_players_team players of team t
                # had gone to fiole i instead of wherever they actually went?
                n = list(players_around_item(f))   # [n0, n1] as currently placed
                n_cf = n.copy()
                n_cf[t] = nb_players_team           # hypothetical: all go to fiole i
 
                cf_winner = compute_winner(f, n_cf[0], n_cf[1])
                cf_score  = 1 if cf_winner == t else 0
 
                # Regret = what we would have gained − what we actually got
                regrets[t][i] += cf_score - actual


    # -------------------------------
    # Jouer les épisodes
    # -------------------------------
    strategy_map = {
        'aleatoire':        strategie_aleatoire,
        'tetu':             strategie_tetu,
        'greedy':           strategie_greedy,
        'expert':           strategie_aleatoire_expert,
        'coordination':     strategie_coordination,
        'fictitious':       strategie_fictitious,
        'regret':           strategie_regret,
    }
    score_tot = [0,0]
    for e in range(nb_episodes):
        # -------------------------------
        # Affectation de la stratégie à chaque équipe
        # -------------------------------
        priority = [0, 1] if e % 2 == 0 else [1, 0]
        for t in priority:
            if t == 0: strategy_map[strat_name_0](t)
            else:      strategy_map[strat_name_1](t)

        # calcul du nombre de joueurs autour de chaque fiole
        for o in items:
            print(players_around_item(o))

        # calcul des points
        scores = [0,0]
        for o in items:
            n1, n2 = players_around_item(o)
            winner = compute_winner(o, n1, n2)

            if winner is not None:
                scores[winner] += 1

        print("Score épisode ", e, ": ", scores)

        update_history_and_regrets(scores)
        print(f"  Historique T0: {historique[0]}")
        print(f"  Historique T1: {historique[1]}")
        print(f"  Regrets T0: {regrets[0]}")
        print(f"  Regrets T1: {regrets[1]}")

        score_tot[0] += scores[0]
        score_tot[1] += scores[1]
        # remettre les joueurs à leur pos initiale a la fin de l'episode
        for i in [0,1]:
            j=0
            for p in team[i]:
                x,y = init_states[i][j]
                p.set_rowcol(x,y)
                j+=1
        game.mainiteration()

    return score_tot


# -------------------------------------------------------
# compare_all: runs every pair of strategies on every map
# and prints a results table.
# -------------------------------------------------------
def compare_all(nb_episodes=20):
    MAPS = ['yellow-map', 'red-map', 'green-map', 'blue-map', 'mixed-map']
    STRATEGIES = ['aleatoire', 'tetu', 'greedy', 'expert', 'coordination', 'fictitious', 'regret']
 
    # results[map][s0 vs s1] = [score_t0, score_t1]
    results = {}
 
    for map_name in MAPS:
        print(f"\n{'='*60}")
        print(f"MAP: {map_name}")
        print(f"{'='*60}")
        results[map_name] = {}
 
        # Re-initialise the game for this map
        init(map_name)
 
        for s0, s1 in combinations(STRATEGIES, 2):
            print(f"  {s0:15s} vs {s1:15s} ... ", end='', flush=True)
            score = run_match(s0, s1, nb_episodes=nb_episodes)
            results[map_name][f"{s0} vs {s1}"] = score
 
            if score[0] > score[1]:   winner = f"{s0} wins"
            elif score[1] > score[0]: winner = f"{s1} wins"
            else:                      winner = "draw"
            print(f"{score}  →  {winner}")
 
        pygame.quit()
 
    # ---- summary table ----
    print(f"\n{'='*60}")
    print("SUMMARY TABLE  (score T0 / score T1)")
    print(f"{'='*60}")
    header = f"{'Matchup':35s}" + "".join(f"{m[:10]:>12s}" for m in MAPS)
    print(header)
    print("-" * len(header))
 
    all_matchups = [f"{s0} vs {s1}" for s0, s1 in combinations(STRATEGIES, 2)]
    for matchup in all_matchups:
        row = f"{matchup:35s}"
        for m in MAPS:
            s = results[m].get(matchup, ['-', '-'])
            row += f"  {s[0]:>4}/{s[1]:<4}"
        print(row)
 
    return results
 
 
# -------------------------------------------------------
# Entry point
# -------------------------------------------------------
def main():
    # ---- Option A: run a single match ----
    # init('mixed-map')
    # score = run_match('regret', 'fictitious', nb_episodes=20, verbose=True)
    # print("Final:", score)
    # pygame.quit()
 
    # ---- Option B: run full comparison across all maps ----
    compare_all(nb_episodes=5)
 
if __name__ == '__main__':
    main()