# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : _________
#  Prénom Nom No_étudiant/e : _________
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "YNL"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
                # -- Liste des directions des capteurs, pour faciliter les boucles
        dirs = [sensor_front, sensor_front_left, sensor_front_right, sensor_left, sensor_right]

        # 1) Priorité à la poursuite
        enemies = [d for d in dirs
                if sensor_view[d] == 2 and sensor_team[d] != self.team_name]
        if enemies:
            # Poursuivre l'ennemi le plus proche
            best_dir    = min(enemies, key=lambda d: sensors[d])
            dist        = sensors[best_dir]
            translation = max(0.2, min(dist * 0.8, 0.6))
            rot_map = {
                sensor_front:       0.0,
                sensor_front_left:  +0.4,
                sensor_left:        +0.8,
                sensor_front_right: -0.4,
                sensor_right:       -0.8
            }
            rotation = rot_map.get(best_dir, 0.0)

        else:
            # 2) Croisière + évitement amélioré des murs
            # Vitesse de translation dynamique : la distance par rapport au mur le plus proche détermine la vitesse
            d_min = min(sensors[d] for d in dirs)
            translation = 0.6 + 0.6 * d_min  # Plus la distance est grande, plus on peut aller vite

            # Évitement standard du mur (linéaire)
            rot_avoid = (
                +0.3 * sensors[sensor_left]
            +0.5 * sensors[sensor_front_left]
            -0.3 * sensors[sensor_right]
            -0.5 * sensors[sensor_front_right]

            )

            # Détection des coins : si devant+avant-gauche trop proches, tourner brusquement à droite ;
            # ou si devant+avant-droit trop proches, tourner brusquement à gauche
            if sensors[sensor_front] < 0.2 and sensors[sensor_front_left] < 0.2:
                rotation = -1.0
            elif sensors[sensor_front] < 0.2 and sensors[sensor_front_right] < 0.2:
                rotation = +1.0
            else:
                # Évitement normal + légère perturbation
                jitter = (random.random() - 0.5) * 0.02

                # 3) Stratégie de suivi de mur :
                # si devant trop proche, avancer le long du mur de l'autre côté (celui avec plus d'espace)
                if sensors[sensor_front] < 0.25:
                    if sensors[sensor_left] > sensors[sensor_right]:
                        # Suivre le mur de gauche
                        rotation = +0.6
                    else:
                        # Suivre le mur de droite
                        rotation = -0.6
                else:
                    # Évitement linéaire + jitter
                    rotation = rot_avoid + jitter
            """
            # 4) Séparation des coéquipiers (optionnel, pour éviter de se bloquer mutuellement)
            sep = 0.0
            for d, sign in ((sensor_front_left, -1), (sensor_left, -1),
                            (sensor_front_right, +1),(sensor_right, +1),
                            (sensor_front,  0)):
                if sensor_view[d] == 2 and sensor_team[d] == self.team_name:
                    w = max(0.0, 0.4 - sensors[d])
                    if d == sensor_front:
                        sep += random.choice([-1, 1]) * w
                    else:
                        sep += sign * w
            rotation += sep
            """
            # 5) Protection contre le blocage en bord de mur :
            # si devant très proche, mémoriser une direction jusqu'à dégagement
            if sensors[sensor_front] < 0.15:
                if self.memory == 0:
                    self.memory = random.choice([-1, +1])
                rotation = self.memory * 0.8
            else:
                self.memory = 0

        # 6) Assurer que les sorties sont dans les plages légales
        translation = max(0.0, min(1.0, translation))
        rotation    = max(-1.0, min(1.0, rotation))
        return translation, rotation, False
       
        """
        translation = sensors[sensor_front]
        rotation = 1.0 * sensors[sensor_front_left] - 1.0 * sensors[sensor_front_right] + (random.random()-0.5)*0.1
        return translation, rotation, False"""
