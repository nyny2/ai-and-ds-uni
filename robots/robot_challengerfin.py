from robot import *
import random
import math

nb_robots = 0
debug = False

def clip(x, lo=-1.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


class Robot_player(Robot):
    team_name = "YuVo"
    robot_id = -1
    memory = 0  # Seul entier autorisé pour stocker l'état interne du robot

    # Poids obtenus par optimisation génétique pour le contrôleur neuronal du robot 0.
    # Ces 8 valeurs représentent les poids des connexions utilisés dans le calcul
    # des ordres de translation et de rotation via la fonction tanh.
    # À remplacer par tes meilleurs paramètres GA obtenus lors de l'optimisation.
    GA_WEIGHTS_ROBOT0 = [0, 1, 1, 1, 0, 1, -1, -1]

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name="Robot " + str(self.robot_id), team=self.team_name)

    # Gestion du paquetage mémoire (Memory packing) 
    # Cette section gère l'encodage de plusieurs variables d'état dans un seul entier.
    # Chaque variable occupe un nombre de bits spécifique :
    #   - bits 0 à 8 : compteur global 0 à 511, incrément chaque étape pour la synchronisation
    #   - bit 9 : drapeau d'échappement, indique si le robot est bloqué et tente une fuite
    #   - bits 10 à 13 : compteur de durée du coup de pied (0 à 15 étapes de recul/rotation)
    #   - bits 14+ : dernière valeur du bucket de translation pour détection de blocage
    def get_counter(self): return self.memory & 511
    def set_counter(self, c): self.memory = (self.memory & ~511) | (c & 511)

    def get_escape(self): return (self.memory >> 9) & 1
    def set_escape(self, e):
        if e: self.memory |= (1 << 9)
        else: self.memory &= ~(1 << 9)

    def get_kick(self): return (self.memory >> 10) & 15
    def set_kick(self, k):
        self.memory = (self.memory & ~(15 << 10)) | ((k & 15) << 10)

    def get_last_bucket(self): return self.memory >> 14
    def set_last_bucket(self, b):
        self.memory = (self.memory & ((1 << 14) - 1)) | (b << 14)

    # Séparation des capteurs en catégories (Sensor split) 
    # Analyse et classifie les signaux des 8 capteurs de distance en trois catégories :
    # murs, robots alliés et robots adverses. Cela permet de traiter différemment chaque
    # type d'obstacle pour une réaction comportementale appropriée.
    def split_sensors(self, sensors, sensor_view, sensor_team):
        if sensor_view is None:
            sensor_view = [0] * 8

        my_team = getattr(self, "team", None)

        wall  = [1.0] * 8
        bot   = [1.0] * 8
        enemy = [1.0] * 8

        for i in range(8):
            if sensor_view[i] == 1:
                wall[i] = sensors[i]
            elif sensor_view[i] == 2:
                bot[i] = sensors[i]
                # enemy only if team known
                if (sensor_team is not None and my_team is not None
                        and isinstance(sensor_team, (list, tuple)) and len(sensor_team) == 8
                        and sensor_team[i] is not None
                        and sensor_team[i] != my_team):
                    enemy[i] = sensors[i]

        return wall, bot, enemy

    # Modules comportementaux type Braitenberg 
    # Ces fonctions implémentent des comportements réflexes simples basés sur la
    # neurobiologie Braitenberg : connexions sensorimotrices directes sans traitement
    # cognitif complexe, permettant une évolution rapide et une adaptation fine.
    def hate_wall(self, wall):
        t = clip(0.15 + 0.85 * wall[sensor_front])
        r = clip(2.4 * (wall[sensor_front_left] - wall[sensor_front_right]) + (1.0 - wall[sensor_front]))
        return t, r

    def hate_robot(self, bot):
        front = bot[sensor_front]
        t = clip(0.10 + 0.70 * front)
        if front < 0.18:
            t = -0.6
        r = clip(2.8 * (bot[sensor_front_left] - bot[sensor_front_right]) + (1.0 - front))
        return t, r

    def pursue_robot_8(self, bot):
        a = [1.0 - d for d in bot]  # activation
        left_sum  = a[sensor_front_left] + a[sensor_left] + a[sensor_rear_left]
        right_sum = a[sensor_front_right] + a[sensor_right] + a[sensor_rear_right]
        front_sum = a[sensor_front] + 0.5*(a[sensor_front_left] + a[sensor_front_right])

        t = clip(0.10 + 0.95 * front_sum)
        r = clip(2.2 * (left_sum - right_sum))
        r = clip(r + (random.random() - 0.5) * 0.05)
        return t, r

    def ga_controller(self, sensors):
        w = self.GA_WEIGHTS_ROBOT0
        fl = sensors[sensor_front_left]
        f  = sensors[sensor_front]
        fr = sensors[sensor_front_right]
        t = math.tanh(w[0] + w[1]*fl + w[2]*f + w[3]*fr)
        r = math.tanh(w[4] + w[5]*fl + w[6]*f + w[7]*fr)
        return clip(t), clip(r)

    # Exploration stratégique : choix de la direction ouverte 
    # Implémente une stratégie d'exploration qui privilégie les passages ouverts.
    # En fonction des distances détectées, le robot évalue les côtés gauche et droit
    # et se dirige vers l'espace le plus ouvert pour explorer efficacement l'arène.
    def explore_open_heading(self, wall, bias):
        # Calcul des scores de virage : préférence pour les plus grandes distances (espace plus ouvert)
        # Comparaison entre "ouvert à gauche" versus "ouvert à droite" en utilisant tous les capteurs
        left_open  = wall[sensor_left] + wall[sensor_front_left] + 0.7*wall[sensor_rear_left]
        right_open = wall[sensor_right] + wall[sensor_front_right] + 0.7*wall[sensor_rear_right]
        front_open = wall[sensor_front] + 0.4*(wall[sensor_front_left] + wall[sensor_front_right])

        # Translation avant : accélère lorsque l'espace avant est dégagé
        t = clip(0.20 + 0.85 * front_open)

        # Rotation : tourne vers le côté le plus ouvert en tenant compte du biais fourni
        r = clip(1.6 * (left_open - right_open) + bias)

        # Si l'avant est étroit (passage serré), ajoute une rotation plus forte pour éviter les boucles locales
        if wall[sensor_front] < 0.45:
            r = clip(r + 0.9 * (1.0 - wall[sensor_front]) * (1.0 if (left_open > right_open) else -1.0))

        # Petit bruit aléatoire pour améliorer la stochasticité (ne pas confondre avec l'anti-cycle principal)
        r = clip(r + (random.random() - 0.5) * 0.04)
        return t, r

    # Fonction principale de contrôle (Step) 
    # Exécutée à chaque pas de simulation. Cette fonction orchestre toute la logique
    # comportementale du robot en traversant une hiérarchie de priorités bien définie.
    # Chaque comportement est évalué et si ses conditions déclenchent, ill est exécuté.
    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        wall, bot, enemy = self.split_sensors(sensors, sensor_view, sensor_team)

        # Incrémentation du compteur global modulo 512 pour synchronisation et temporisation
        c = (self.get_counter() + 1) & 511
        self.set_counter(c)

        # Mécanisme anti-blocage puissant par coup de pied périodique 
        # Toutes les ~260 étapes, déclenche 12 étapes de "coup de pied" : recul rapide + rotation forte.
        # Ce mécanisme brise efficacement les cycles infinis et les situations de blocage persistant.
        if (c % 260) == 0:
            self.set_kick(12)

        k = self.get_kick()
        if k > 0:
            self.set_kick(k - 1)
            spin = 1.0 if (self.robot_id % 2 == 0) else -1.0
            # Coup de pied : recule à -0.5 et effectue une rotation forte selon l'identifiant du robot
            return -0.5, spin, False

        # Mécanisme de détection de blocage par analyse de progrès 
        # Vérifie si la somme cumulée de translation reste dans le même bucket.
        # Si aucun progrès n'est détecté après 100 étapes, déclenche un drapeau d'échappement.
        trans = getattr(self, "log_sum_of_translation", 0.0)
        bucket = int(trans * 15)

        if bucket == self.get_last_bucket():
            # Pas de progression détectée
            stuck = (c % 100)  # Réutilise la fenêtre du compteur pour la synchronisation
            if stuck == 99:
                self.set_escape(1)
        else:
            self.set_last_bucket(bucket)
            self.set_escape(0)

        if self.get_escape() == 1:
            spin = -1.0 if (self.robot_id % 2 == 0) else 1.0
            # Fuite d'urgence : recul à -0.7 avec rotation asymétrique selon l'identifiant
            return -0.7, spin, False

        #PRIORITÉ 1 : Collision imminente en avant avec les murs 
        # Si l'un des capteurs avant détecte une distance inférieure à 0.24, le robot
        # active immédiatement le comportement de haine des murs pour s'éloigner.
        if min(wall[sensor_front], wall[sensor_front_left], wall[sensor_front_right]) < 0.24:
            t, r = self.hate_wall(wall)
            return t, r, False

        #PRIORITÉ 2 : Collision imminente avec d'autres robots 
        # Si un robot allié ou adversaire est détecté trop proche (inférieur à 0.22),
        # le robot active le comportement de haine des robots pour l'éviter.
        # Une asymétrie supplémentaire est ajoutée selon l'identité pour différencier les réactions.
        if min(bot[sensor_front], bot[sensor_front_left], bot[sensor_front_right]) < 0.22:
            t, r = self.hate_robot(bot)
            # Asymétrie supplémentaire basée sur l'identifiant du robot pour diversifier les trajectoires
            r = clip(r + (0.2 if (self.robot_id % 2 == 0) else -0.2))
            return t, r, False

        #PRIORITÉ 3 : Poursuite des robots adverses ou alliés 
        # Détecte si des adversaires sont visibles et engage une stratégie de poursuite.
        # Le robot 1 a un rôle spécial : il charge aggressivement les adversaires détectés.
        # Les autres robots ne poursuivent que si la distance est suffisamment courte (< 0.75).
        enemy_seen = min(enemy) < 0.999
        any_seen   = min(bot) < 0.999

        if enemy_seen:
            if self.robot_id == 1:
                t, r = self.pursue_robot_8(enemy)
                return t, r, False
            if min(enemy) < 0.75:
                t, r = self.pursue_robot_8(enemy)
                return t, r, False
        elif self.robot_id == 1 and any_seen:
            # Secours : si les informations d'équipe ne fonctionnent pas correctement,
            # poursuit quand même un robot détecté pour rester combatif
            t, r = self.pursue_robot_8(bot)
            return t, r, False

        #PRIORITÉ 4 : Exploration coopérative de l'arène 
        # Lorsqu'aucune menace n'est détectée, chaque robot adopte une stratégie d'exploration.
        # Chaque robot a un rôle distinct défini par son identifiant pour maximiser la couverture.
        flip = 1.0 if (c % 400) < 200 else -1.0

        if self.robot_id == 0:
            # Robot 0 : utilise le contrôleur génétique optimisé pour une exploration guidée
            t, r = self.ga_controller(sensors)
            # Ajoute une dérive pour éviter les structures cycliques répétitives
            r = clip(r + 0.18 * flip)
            t = clip(t + 0.10)
            return t, r, False

        # Rôles distincts : biais différents permettent la répartition spatiale des robots
        if self.robot_id == 2:
            # Robot 2 : bias positif, explore préférentiellement vers la gauche
            bias = 0.35 * flip
            return (*self.explore_open_heading(wall, bias), False)

        if self.robot_id == 3:
            # Robot 3 : bias négatif, explore préférentiellement vers la droite
            bias = -0.35 * flip
            return (*self.explore_open_heading(wall, bias), False)

        # Robot 1 (quand ne poursuit pas) : explorateur rapide avec biais aléatoire
        bias = 0.10 * (1.0 if random.random() < 0.5 else -1.0) * flip
        t, r = self.explore_open_heading(wall, bias)
        t = clip(t + 0.20)  # Accélération supplémentaire pour la couverture rapide
        return t, r, False
