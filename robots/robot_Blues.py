# Projet "robotique" IA&Jeux 2026
#
# Binome:
#  Prénom Nom No_étudiant/e : Belkiss TISS 21231069
#  Prénom Nom No_étudiant/e : Mohamed GUERZOU 21320883 
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)


# Architecture: SUBSOMPTION + spécialisations par robot_id
# Robots: 4 (3 Braitenberg + 1 perceptron "GA" aux poids fixés)
#
# IMPORTANT:
# - Toute la logique est dans step (conforme à l'énoncé).
# - self.memory = unique mémoire (entier) utilisée comme mini-automate.

from robot import *
import random
import math


# Compteur global pour donner un identifiant unique à chaque robot
nb_robots = 0

class Robot_player(Robot):
    # Nom de l'équipe affiché dans le jeu
    team_name = "Blues"
    
    # Identifiant unique du robot (0, 1, 2, 3...)
    robot_id = -1
    
    # Mémoire persistante (un seul entier autorisé par le règlement)
    # Nous l'utiliserons pour stocker deux informations : un MODE et un TIMER
    memory = 0  
    
    # Compteur de tours de boucle
    iteration = 0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        # Initialisation de la classe parente avec un nom personnalisé
        super().__init__(x_0, y_0, theta_0, name="Robot " + str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        Fonction principale exécutée à chaque pas de temps (step).
        
        Arguments:
            sensors (list): 8 distances normalisées [0..1]. 1 = loin, 0 = collision immédiate.
            sensor_view (list): Type d'objet vu par chaque capteur (0=vide, 1=mur, 2=robot).
            sensor_robot (list): Nom du robot détecté (ex: "Robot 0").
            sensor_team (list): Nom de l'équipe du robot détecté.

        Retourne:
            translation (float): Vitesse linéaire [-1, 1].
            rotation (float): Vitesse angulaire [-1, 1].
            reset (bool): Toujours False (demande de réinitialisation).
        """

        # *************************************************************************
        # * FONCTIONS UTILITAIRES                           *
        # *************************************************************************

        def borner(valeur, min_val=-1.0, max_val=1.0):
            """Contraint une valeur entre un minimum et un maximum."""
            if valeur < min_val: return min_val
            if valeur > max_val: return max_val
            return valeur

        def obtenir_id_autre_robot(index_capteur):
            """
            Extrait l'ID numérique d'un robot détecté par un capteur donné.
            Gère le parsing de la chaîne de caractères 'Robot X'.
            """
            try:
                if sensor_robot and sensor_robot[index_capteur]:
                    nom_chaine = str(sensor_robot[index_capteur])
                    # On découpe "Robot 4" pour récupérer "4"
                    return int(nom_chaine.split()[-1])
            except:
                pass
            return -1 # Retourne -1 en cas d'erreur de lecture

        def est_ennemi(i):
            """Retourne Vrai si le capteur i voit un robot d'une autre équipe."""
            return (sensor_view[i] == 2) and (sensor_team is not None) and \
                   (sensor_team[i] != "n/a") and (sensor_team[i] != self.team_name)

        def est_allie(i):
            """Retourne Vrai si le capteur i voit un robot de mon équipe."""
            return (sensor_view[i] == 2) and (sensor_team is not None) and \
                   (sensor_team[i] == self.team_name)

        def separer_murs_robots():
            """
            Sépare les données sensorielles en deux tableaux distincts :
            - murs[] : contient les distances si c'est un mur (sinon 1.0)
            - robots[] : contient les distances si c'est un robot (sinon 1.0)
            """
            murs = [1.0] * 8
            robots = [1.0] * 8
            for i in range(8):
                if sensor_view[i] == 1:   # 1 = Mur
                    murs[i] = sensors[i]
                elif sensor_view[i] == 2: # 2 = Robot
                    robots[i] = sensors[i]
            return murs, robots

        def dist_min_type(type_objet):
            """Retourne la distance minimale détectée pour un type d'objet donné (1=mur, 2=robot)."""
            min_dist = 1.0
            for i in range(8):
                if sensor_view[i] == type_objet and sensors[i] < min_dist:
                    min_dist = sensors[i]
            return min_dist

        def dist_min_allie():
            """Retourne la distance minimale d'un allié et l'index du capteur associé."""
            min_dist = 1.0
            index = -1
            for i in range(8):
                if est_allie(i) and sensors[i] < min_dist:
                    min_dist = sensors[i]
                    index = i
            return min_dist, index

        def ennemi_en_vue():
            """Vérifie si au moins un ennemi est visible par l'un des capteurs."""
            for i in range(8):
                if est_ennemi(i):
                    return True
            return False

        def pression_ennemie_gauche_droite():
            """Calcule la 'masse' d'ennemis à gauche et à droite pour s'orienter."""
            P_gauche = 0.0
            P_droite = 0.0
            for i in range(8):
                if est_ennemi(i):
                    # Plus l'ennemi est proche (sensor petit), plus la pression est forte (1 - sensor)
                    activation = 1.0 - sensors[i]
                    if i <= 3: P_gauche += activation
                    else: P_droite += activation
            return P_gauche, P_droite

        def pression_alliee_gauche_droite():
            """Calcule la 'masse' d'alliés à gauche et à droite."""
            P_gauche = 0.0
            P_droite = 0.0
            for i in range(8):
                if est_allie(i):
                    activation = 1.0 - sensors[i]
                    if i <= 3: P_gauche += activation
                    else: P_droite += activation
            return P_gauche, P_droite

        # *************************************************************************
        # * COMPORTEMENTS (BRAITENBERG)                       *
        # *************************************************************************

        def braitenberg_hateWall():
            """
            Comportement répulsif envers les murs (hateWall).
            Le robot accélère si c'est libre devant et tourne à l'opposé des murs latéraux.
            """
            murs, _ = separer_murs_robots()
            
            # Somme des activations à gauche et à droite
            gauche =  murs[1] + murs[2] + murs[3]
            droite =  murs[5] + murs[6] + murs[7]
            devant = murs[sensor_front]
            
            # Plus il y a de place devant, plus on va vite
            translation = 0.20 + 0.80 * devant
            # Si mur à gauche > mur à droite, on tourne à droite  
            # Note: Dans ce simulateur, positif tourne à gauche, négatif à droite (ou inversement selon config).
            # Ici : (gauche - droite) génère une répulsion.
            rotation = 0.9 * (gauche - droite)
            
            return borner(translation), borner(rotation)

        def braitenberg_loveBot_ennemi():
            """
            Comportement attractif (LoveBot) envers les ennemis uniquement.
            Utile pour le robot 'Chasseur' qui doit repeindre par-dessus l'adversaire.
            """
            activations = [0.0] * 8
            for i in range(8):
                if est_ennemi(i):
                    activations[i] = 1.0 - sensors[i]

            gauche = activations[0] + activations[1] + activations[2] + activations[3]
            droite = activations[4] + activations[5] + activations[6] + activations[7]
            devant = activations[sensor_front]

            # On avance vite si l'ennemi est devant
            translation = 0.15 + 0.85 * devant
            # On tourne VERS le côté où l'activation est la plus forte (Attraction)
            rotation = 1.0 * (droite - gauche)
            
            return borner(translation), borner(rotation)

        def braitenberg_hateBot():
            """
            Comportement répulsif envers tous les robots (alliés et ennemis).
            Utilisé pour l'exploration et éviter les foules.
            """
            _, robots = separer_murs_robots()
            # On inverse la distance pour obtenir une répulsion (1 - distance)
            activations = [1.0 - robots[i] for i in range(8)]
            
            gauche = activations[0] + activations[1] + activations[2] + activations[3]
            droite = activations[4] + activations[5] + activations[6] + activations[7]
            devant = activations[sensor_front]
            
            # Si robot devant, on ralentit
            translation = 0.55 * (1.0 - devant) + 0.10
            # On fuit le côté le plus chargé
            rotation = 1.2 * (gauche - droite)
            
            return borner(translation), borner(rotation)

        def evitement_allie_prioritaire(index_allie_proche):
            """
            Comportement spécial anti-collision entre alliés (Anti-Tremblement).
            Utilise les identifiants (ID) pour décider qui va à gauche et qui va à droite.
            """
            id_autre = obtenir_id_autre_robot(index_allie_proche)
            
            # Sécurité si lecture ID échoue
            if id_autre == -1: id_autre = 999 

            # Règle de priorité déterministe :
            # Si mon ID est plus grand, je vais dans une direction (1.0).
            # Sinon, je vais dans l'autre (-1.0).
            # Cela garantit que les robots ne tournent pas du même côté.
            direction = 1.0 if self.robot_id > id_autre else -1.0
            
            rotation = 0.8 * direction
            translation = 0.0 # On s'arrête presque pour tourner
            
            # Si collision imminente, on recule légèrement
            if sensors[index_allie_proche] < 0.3:
                translation = -0.2

            return translation, rotation

        def controleur_perceptrone_genetique():
            """
            Réseau de neurones simple (Perceptron) dont les poids ont été
            optimisés par Algorithme Génétique (AG μ=1, λ=1) en amont.
            Les poids finaux utilisés dans le perceptron correspondent au meilleur individu trouvé durant l’optimisation.
            Ce contrôleur permet une navigation fluide.
            """
            # Génome (Poids synaptiques optimisés)
            poids = [1, 1, 1, 0, 0, 1, 1, -1]
            
            # Neurone 1 : Vitesse de translation
            # Entrées : Capteurs avant-gauche, avant, avant-droit
            t = math.tanh(
                poids[0]
                + poids[1] * sensors[sensor_front_left]
                + poids[2] * sensors[sensor_front]
                + poids[3] * sensors[sensor_front_right]
            )
            
            # Neurone 2 : Vitesse de rotation
            r = math.tanh(
                poids[4]
                + poids[5] * sensors[sensor_front_left]
                + poids[6] * sensors[sensor_front]
                + poids[7] * sensors[sensor_front_right]
            )
            return borner(t), borner(r)

        # *************************************************************************
        # * LOGIQUE DE DÉCISION (STEP)                           *
        # *************************************************************************

        # 1. DÉCODAGE DE LA MÉMOIRE
        # La mémoire est un entier unique codé sous la forme : MODE * 10000 + TIMER
        mode = self.memory // 10000 #état courant (0 normal, 1 panique, 2 crazy mode…)
        timer = self.memory % 10000
        
        # Gestion du timer (décrémentation)
        if timer > 0:
            timer -= 1
        else:
            mode = 0 # Retour au mode normal quand le timer est fini

        # 2. ARCHITECTURE DE SUBSOMPTION (PRIORITÉS)
        
        # --- Priorité 0 : MANOEUVRE DE DÉBLOCAGE FORCÉE ---
        # Si le robot est en mode "Panique" (mode 1) avec un timer actif, 
        # il exécute une manoeuvre aveugle pour sortir d'un cul-de-sac.
        if mode == 1 and timer > 0:
            self.memory = mode * 10000 + timer
            self.iteration += 1
            # Recule et tourne fort
            return -0.1, 1.0, False 

        # Seuils de déclenchement des comportements
        SEUIL_MUR_DANGER = 0.25 
        SEUIL_ALLIE_DANGER = 0.40 
        SEUIL_ROBOT_DANGER = 0.20

        dist_mur = dist_min_type(1)
        dist_allie, index_allie = dist_min_allie()
        dist_robot = dist_min_type(2)

        # --- Priorité 1 : ANTI-COLLISION ALLIÉ ROBUSTE ---
        # Empêche les robots de la même équipe de se bloquer mutuellement.
        if dist_allie < SEUIL_ALLIE_DANGER:
            t, r = evitement_allie_prioritaire(index_allie)
            self.memory = mode * 10000 + timer
            self.iteration += 1
            return t, r, False

        # --- Priorité 2 : DÉTECTION DE BLOCAGE (ANTI-STUCK) ---
        # Si le robot est très proche d'un mur et n'a pas de vitesse (devant bouché),
        # on déclenche le mode "Panique" (mode 1) pour 15 itérations.
        if dist_mur < 0.15 and sensors[sensor_front] < 0.2:
            mode = 1       # Activation du mode Panique
            timer = 15     # Durée de la manoeuvre
            self.memory = mode * 10000 + timer
            return -0.2, 1.0, False

        # --- Priorité 3 : ÉVITEMENT DE MUR STANDARD (braitenberg_hateWall) ---
        # Navigation de base pour ne pas heurter les murs.
        if dist_mur < SEUIL_MUR_DANGER:
            t, r = braitenberg_hateWall()
            # Ajout d'un bruit aléatoire pour éviter les cycles parfaits
            r = borner(r + (random.random() - 0.5) * 0.10)
            self.memory = mode * 10000 + timer
            self.iteration += 1
            return t, r, False

        # --- Priorité 4 : ÉVITEMENT GÉNÉRAL DES ROBOTS (braitenberg_hateBot) ---
        # Pour ne pas foncer dans les ennemis.
        if dist_robot < SEUIL_ROBOT_DANGER:
            t, r = braitenberg_hateBot()
            r = borner(r + (random.random() - 0.5) * 0.15)
            self.memory = mode * 10000 + timer
            self.iteration += 1
            return t, r, False
            
        #Si aucune des priorités 0–4 n’a déclenché, alors le robot est “en sécurité” et peut exécuter sa stratégie selon son ID.

        # *************************************************************************
        # * ATTRIBUTION DES RÔLES (STRATÉGIE)                    *
        # *************************************************************************

        # ROBOT 0 : L'OPTIMISÉ (Navigation par Perceptron / AG)
        if self.robot_id == 0:
            # Petit comportement aléatoire rare ("Crazy mode") pour sortir de boucles éventuelles
            if timer == 0 and mode == 0:
                if random.random() < 0.02: 
                    mode = 2
                    timer = 20

            t, r = controleur_perceptrone_genetique()
            
            if mode == 2:
                # Perturbation aléatoire de la rotation
                r = borner(r + 0.8 * (1 if random.random() < 0.5 else -1))
                
        # ROBOT 1 : LE CHASSEUR (Suit les ennemis)
        elif self.robot_id == 1:
            if ennemi_en_vue():
                # S'il voit un ennemi, il est attiré (LoveBot)
                t, r = braitenberg_loveBot_ennemi()
            else:
                # Sinon, il explore
                t, r = braitenberg_hateWall()
                r = borner(r + (random.random() - 0.5) * 0.06)

        # ROBOT 2 : L'EXPLORATEUR TACTIQUE
        elif self.robot_id == 2:
            t, r = braitenberg_hateWall()
            r = borner(r + (random.random() - 0.5) * 0.03)
            
            # Influence légère par la présence ennemie (pour aller vers les zones occupées)
            p_gauche, p_droite = pression_ennemie_gauche_droite()
            r = borner(r + 0.3 * (p_droite - p_gauche))

        # ROBOT 3 : L'HYBRIDE (Mélange évitement robots et murs)
        else:
            t1, r1 = braitenberg_hateBot()
            t2, r2 = braitenberg_hateWall()
            
            # Mélange pondéré des deux comportements selon la proximité des robots
            alpha = borner((1.0 - dist_robot) * 1.5, 0.0, 1.0)
            t = borner(alpha * t1 + (1 - alpha) * t2)
            r = borner(alpha * r1 + (1 - alpha) * r2)
            r = borner(r + (random.random() - 0.5) * 0.18)

        # --- Dispersion Proactive ---
        # Légère force répulsive permanente entre alliés pour qu'ils s'écartent
        # même sans danger immédiat (meilleure couverture de terrain).
        p_allie_gauche, p_allie_droite = pression_alliee_gauche_droite()
        r = borner(r + 0.20 * (p_allie_gauche - p_allie_droite))

        # 3. ENCODAGE DE LA MÉMOIRE ET FIN
        self.memory = mode * 10000 + timer
        self.iteration += 1
        
        return t, r, False
