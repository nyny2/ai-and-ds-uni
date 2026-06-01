# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Ceren Bektas 21303252 
#  Prénom Nom No_étudiant/e : Eda Bayraktar 21313631
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import math
nb_robots = 0

class Robot_player(Robot):

    team_name = "Robo EdaCeren"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        timer = (self.memory >> 20) & 0x3FF
        stuck_count = (self.memory >> 14) & 0x3F
        prev_pos = self.memory & 0x3FFF
        
        curr_x, curr_y = int(self.x), int(self.y)
        curr_pos = curr_x + curr_y * 100
        
        if curr_pos == prev_pos:
            stuck_count = min(63, stuck_count + 1)
        else:
            stuck_count = 0
            
        timer = (timer + 1) % 1024
        self.memory = (timer << 20) | (stuck_count << 14) | curr_pos

        f = sensors[sensor_front]
        fl = sensors[sensor_front_left]
        fr = sensors[sensor_front_right]
        l = sensors[sensor_left]
        r = sensors[sensor_right]

        #Subsumption
        if timer < 20:
            return 1.0, (self.robot_id * 0.5), False

        #rescue
        if stuck_count > 15 or f < 0.2:
            translation = -0.7
            rotation = 1.0 if (self.robot_id % 2 == 0) else -1.0
            return translation, rotation, False

        # BRAITENBERG 
        # hateWall
        if fl < 0.4 or fr < 0.4:
            translation = 0.6
            rotation = (fl - fr) * 2.5
            return translation, rotation, False
  
        if l < 0.5 and r < 0.5:
            translation = 0.9
            rotation = (l - r) * 3.0
            return translation, rotation, False

        local_id = self.robot_id % 4

        # ROBOT 0: GA 
        if local_id == 0:
            # parametres Optimizes 
            p = [0, 0, 1, 0, -1, 1, 0, 1] 

            translation = math.tanh(p[0] + p[1]*fl + p[2]*f + p[3]*fr)
            rotation = math.tanh(p[4] + p[5]*fl + p[6]*f + p[7]*fr)

        # ROBOT 2:explorer + avoider
        elif local_id == 2:
            translation = 1.0
            rotation = math.sin(timer * 0.1) * 0.3

        # ROBOT 1 & 3: lovebot & hateWall
        else:
            #zigzag
            translation = 0.8
            rotation = math.sin(timer * 0.05) * 0.2
            
            # suivre un ennemi
            for i in range(8):
                if sensor_view[i] == 2 and sensor_team[i] != self.team:
                    translation = 1.0
                    if i == 0: rotation = 0
                    elif i < 4: rotation = 0.8 # rotation gauche
                    else: rotation = -0.8      # rotation droite
                    break

        return translation, rotation, False