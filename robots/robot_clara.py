# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Clara Carvalho Da Silva 21302449
#  Prénom Nom No_étudiant/e : Céline JIN 21315668
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import *
import math

nb_robots = 0

class Robot_player(Robot):
    team_name = "CelineClara" 
    robot_id = -1             
    memory = 0                

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)


    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
            
            # bruit pour casser la symétrie pr débloquer
            noise =  0.2

            gauche = sensors[sensor_left] + sensors[sensor_front_left]
            droite = sensors[sensor_right] + sensors[sensor_front_right]
            rot_base = 0.2 * (gauche - droite) + noise
            
            # Priorité 1 : déblocage pour manoeuvre de sortie
            if self.memory != 0: 
                sens = 1 if self.memory > 0 else -1
                self.memory -= sens
                return -0.3, sens, False

            #Priorité 2 : Danger imminent devant : on recule et lance une manoeuvre memory
            if (sensors[sensor_front] < 0.2) or ((sensors[sensor_front_left] < 0.15) and (sensors[sensor_front_right] < 0.15)):
                sens = 1 if sensors[sensor_front_right] > sensors[sensor_front_left] else -1
                self.memory = 50 * sens
                return -0.2, 0.85 * sens, False


            #Priorité 3: couloir / tunnel (cotes proches mais devant libre)
            if (sensors[sensor_left] < 0.25 and sensors[sensor_right] < 0.25 and sensors[sensor_front] > 0.25):
                rot_tunnel = 0.20 * (sensors[sensor_right] - sensors[sensor_left])    # si droite plus libre 
                return 0.60, rot_tunnel, False #on avance


            # Priorité 4 : mur proche mais pas coller : tourner + avancer doucement
            if sensors[sensor_front] < 0.28:
                sens = 1 if sensors[sensor_front_right] > sensors[sensor_front_left] else -1
                return 0.2, 0.6*sens, False


            # Robot 2 : LoveBot
            if self.robot_id == 2:
                for i in range(8):
                    if sensor_view[i] == 2 and sensor_team[i] != self.team_name:
                        force = 1.0 - sensors[i]
                        if i in [1,2,3]:        # côté gauche
                            direction = -1
                        elif i in [7,6,5]:      # côté droit
                            direction = 1
                        else:                   # i=0 (devant) ou i=4 (derrière)
                            direction = 0
                        return 0.5, 2*force * direction, False

            # Robot 3 : GA 
            if self.robot_id == 3:
                p = [1, 1, 0, 1, -1, 0, -1, 1]

                # rotation GA
                rot_ga = math.tanh(p[4] + p[5]*sensors[sensor_front_left] + p[6]*sensors[sensor_front]+ p[7]*sensors[sensor_front_right])

                rot_ga *= (1.0 - sensors[sensor_front])   # si devant libre on ne tourne pas

                tr = 0.15 + 0.55 * sensors[sensor_front]   #on avance plus vite si c'est libre, lent si proche

                rot = 0.8 * rot_ga + 0.2 * rot_base #petit stabilisateur couloir

                # secours si collé
                if sensors[sensor_front]< 0.12:
                    sens = 1 if sensors[sensor_front_right] > sensors[sensor_front_left] else -1
                    return -0.2, 0.85 * sens, False

                return tr, rot, False



            # robots 0 et 1 : exploration (Base + Biais)

            biais = -0.1 if self.robot_id == 0 else 0.1
            return 0.7, rot_base + biais, False
