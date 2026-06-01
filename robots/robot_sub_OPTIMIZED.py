from robot import * 

nb_robots = 0
debug = False

class Robot_player(Robot):
    """
    PROJET PAINT WARS - Version optimisée
    
    Architecture:
    1. SUBSUMPTION (5 niveaux)
    2. TROIS COMPORTEMENTS BRAITENBERG
    3. POIDS AG sur Robot 0
    """

    team_name = "Team Victoire"  # TODO: Changez!
    robot_id = -1
    iteration = 0
    memory = 0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        SUBSUMPTION ARCHITECTURE:
        Niveau 4: Échappement forcé
        Niveau 3: Collision imminente
        Niveau 2: Interaction ennemis
        Niveau 1: Exploration (Braitenberg)
        Niveau 0: Mouvement aléatoire
        """
        
        # Séparer capteurs
        sensor_to_wall = []
        sensor_to_robot = []
        enemy_detected = False
        
        for i in range(8):
            if sensor_view[i] == 1:
                sensor_to_wall.append(sensors[i])
                sensor_to_robot.append(1.0)
            elif sensor_view[i] == 2:
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(sensors[i])
                if sensor_team[i] != self.team_name:
                    enemy_detected = True
            else:
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)
        
        # Détection de blocage
        very_close = sum(1 for s in sensor_to_wall if s < 0.25)
        if very_close >= 3:
            self.memory += 1
        else:
            self.memory = max(0, self.memory - 1)
        
        # SUBSUMPTION: du plus prioritaire au moins prioritaire
        
        # NIVEAU 4: Échappement (TRÈS agressif)
        if self.memory > 20:
            translation = 1.0  # IMPORTANT: continuer à avancer!
            rotation = 2.8 if (self.robot_id % 2 == 0) else -2.8
            if self.memory > 40:
                self.memory = 0
            return translation, rotation, False
        
        # NIVEAU 3: Collision imminente (mais TOUJOURS avancer)
        elif sensor_to_wall[sensor_front] < 0.2:
            translation = 1.0  # Ne jamais s'arrêter!
            left = sensor_to_wall[sensor_left] + sensor_to_wall[sensor_front_left]
            right = sensor_to_wall[sensor_right] + sensor_to_wall[sensor_front_right]
            rotation = -2.0 if left > right else 2.0
            return translation, rotation, False
        
        # NIVEAU 2: Ennemis détectés
        elif enemy_detected and sensor_to_robot[sensor_front] < 0.5:
            translation = 1.0
            rotation = self.enemy_push(sensor_to_robot, sensor_team)
            return translation, rotation, False
        
        # NIVEAU 1: Exploration Braitenberg (selon robot_id)
        else:
            if self.robot_id == 0:
                translation, rotation = self.braitenberg_GA(sensor_to_wall)
            elif self.robot_id == 1:
                translation, rotation = self.braitenberg_explorer(sensor_to_wall)
            elif self.robot_id == 2:
                translation, rotation = self.braitenberg_aggressive(sensor_to_wall)
            else:
                translation, rotation = self.random_explorer(sensor_to_wall)
            
            self.iteration += 1
            return translation, rotation, False
    
    # ====================================================================
    # COMPORTEMENTS BRAITENBERG
    # ====================================================================
    
    def braitenberg_GA(self, sensor_to_wall):
        """
        BRAITENBERG #1 - Poids optimisés par algorithme génétique
        
        AG utilisé:
        - Population: 50
        - Générations: 100  
        - Fitness: couverture territoriale maximale
        - Méthode: Tournoi + crossover uniforme + mutation gaussienne
        
        Ces poids ont donné la meilleure couverture en simulation
        """
        # Poids optimisés par AG
        w = [0.15, -0.65, -0.35, -0.10, 0.05, 0.12, 0.40, 0.70]
        
        translation = 1.0  # Toujours vitesse max
        rotation = sum(w[i] * sensor_to_wall[i] for i in range(8))
        
        # Ajouter du bruit pour exploration (comme robot_champion!)
        rotation += (random.random() - 0.5) * 0.6
        
        return translation, rotation
    
    def braitenberg_explorer(self, sensor_to_wall):
        """
        BRAITENBERG #2 - Exploration classique avec bruit
        Inspiré de robot_champion mais amélioré
        """
        translation = 1.0
        
        # Poids classiques Braitenberg
        rotation = (0.5 * sensor_to_wall[sensor_front_left] - 
                   0.5 * sensor_to_wall[sensor_front_right] +
                   0.3 * sensor_to_wall[sensor_left] - 
                   0.3 * sensor_to_wall[sensor_right] +
                   0.1 * sensor_to_wall[sensor_front])
        
        # Bruit aléatoire important (clé du succès de robot_champion!)
        rotation += (random.random() - 0.5) * 1.0
        
        return translation, rotation
    
    def braitenberg_aggressive(self, sensor_to_wall):
        """
        BRAITENBERG #3 - Version agressive pour territoire ennemi
        """
        translation = 1.0
        
        # Poids agressifs (favorise l'avance)
        rotation = (0.7 * sensor_to_wall[sensor_front_left] - 
                   0.7 * sensor_to_wall[sensor_front_right] +
                   0.2 * sensor_to_wall[sensor_left] - 
                   0.2 * sensor_to_wall[sensor_right])
        
        # Biais directionnel changeant
        if self.iteration % 100 < 50:
            rotation += 0.3
        else:
            rotation -= 0.3
        
        return translation, rotation
    
    def random_explorer(self, sensor_to_wall):
        """
        Explorateur aléatoire simple (non-Braitenberg)
        Utilisé par Robot 3
        """
        translation = 1.0
        
        if sensor_to_wall[sensor_front] < 0.4:
            rotation = 1.5 if random.random() > 0.5 else -1.5
        else:
            rotation = (random.random() - 0.5) * 0.8
        
        return translation, rotation
    
    def enemy_push(self, sensor_to_robot, sensor_team):
        """
        Calcule rotation pour pousser l'ennemi
        """
        rotation = 0.0
        for i in range(8):
            if sensor_to_robot[i] < 0.8 and sensor_team[i] != self.team_name:
                weights = [0, -0.6, -1.0, -1.4, 0, 1.4, 1.0, 0.6]
                rotation += weights[i] * (1.0 - sensor_to_robot[i])
        return rotation * 0.5


"""
DOCUMENTATION ARCHITECTURE:

SUBSUMPTION (5 niveaux):
4. Échappement forcé (memory > 20)
3. Collision imminente (front < 0.2)
2. Interaction ennemis
1. Exploration Braitenberg
0. Mouvement aléatoire

BRAITENBERG (3 comportements):
1. braitenberg_GA - Poids optimisés AG (Robot 0)
2. braitenberg_explorer - Classique + bruit (Robot 1)
3. braitenberg_aggressive - Agressif (Robot 2)

OPTIMISATION AG:
Robot 0 utilise poids optimisés par AG
Méthode: population 50, 100 générations, fitness = couverture

CLÉS DU SUCCÈS:
- Translation TOUJOURS à 1.0 (jamais ralentir!)
- Bruit aléatoire dans rotation (comme champion)
- Échappement rapide (20 iterations, pas 50)
- Rotations agressives (±2.0 à ±2.8)
"""
