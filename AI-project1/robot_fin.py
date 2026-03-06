# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiante : Nehir Yüksekkaya 21307751
#  Prénom Nom No_étudiante : Nguyen Hanh Dung Vo 21307514

from robot import * # Ne pas modifier nb_robots ni __init__ si possible pour garantir la compatibilité
nb_robots = 0

class Robot_player(Robot):

    team_name = "YuVo" 
    robot_id = -1
    memory = 0 # Seule mémoire autorisée

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # 1. Utilisation de self.memory au lieu de self.iteration
        self.memory += 1 
        
        # Préparation des senseurs (votre logique originale)
        sensor_to_wall = []
        sensor_to_robot = []
        
        # Note: sensor_view, sensor_robot, sensor_team peuvent être None selon l'appel,
        # mais le template suggère qu'ils sont fournis. On garde votre logique.
        if sensor_view is not None:
            for i in range (0,8):
                if sensor_view[i] == 1: # Mur
                    sensor_to_wall.append(sensors[i])
                    sensor_to_robot.append(1.0)
                elif sensor_view[i] == 2: # Robot
                    if sensor_team is not None and sensor_team[i] == self.team_name:
                        sensor_to_robot.append(1.0)      # Ami => ignoré
                        sensor_to_wall.append(sensors[i]) # Considéré comme mur ou ignoré?
                    else:
                        sensor_to_robot.append(sensors[i])  # Ennemi => suivi
                        sensor_to_wall.append(1.0)
                else: # Rien
                    sensor_to_wall.append(1.0)
                    sensor_to_robot.append(1.0)
        else:
            # Sécurité si les arguments optionnels ne sont pas passés
            sensor_to_wall = list(sensors)
            sensor_to_robot = [1.0] * 8

        # --- activations robots (proche => grand) ---
        bFL = 1 - sensor_to_robot[sensor_front_left]
        bF  = 1 - sensor_to_robot[sensor_front]
        bFR = 1 - sensor_to_robot[sensor_front_right]
        bRL = 1 - sensor_to_robot[sensor_rear_left]
        bR  = 1 - sensor_to_robot[sensor_rear]
        bRR = 1 - sensor_to_robot[sensor_rear_right]

        # --- activations murs (proche => grand) ---
        wFL = 1 - sensor_to_wall[sensor_front_left]
        wF  = 1 - sensor_to_wall[sensor_front]
        wFR = 1 - sensor_to_wall[sensor_front_right]

        # --- Comportement par défaut (Braitenberg complexe) ---
        rot_follow = (bFL + bRL) - (bFR + bRR)
        rot_follow = rot_follow + (bF + bR)
        rot_avoid_wall = (wFR - wFL) + wF

        translation = 1.0
        rotation = rot_follow + rot_avoid_wall
        
        # Evitement simple si mur devant
        if sensor_to_wall[sensor_front] < 1.0:
            translation = min(translation, sensor_to_wall[sensor_front])

        # --- Spécialisation du Robot 0 (Algorithme Génétique ?) ---
        # ATTENTION: Assurez-vous que ces poids viennent d'une optimisation
        if self.robot_id == 0:
            translation = sensors[sensor_front] * 1.0
            # Formule optimisée (?)
            rotation = (sensors[sensor_front_left] * 1) + \
                       (sensors[sensor_front_right] * -1) + \
                       (1 - sensors[sensor_front] * 1.0)
     
        return translation, rotation, False