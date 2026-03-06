# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Li Fernando 21303270
#  Prénom Nom No_étudiant/e : Li Kun 
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import math

nb_robots = 0

class Robot_player(Robot):

    team_name = "lily"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)


    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        sensor_to_wall = [] #liste des sensors en ne prennant en compte que les murs
        sensor_to_robot = [] #liste des sensors en ne prennant en compte que les robots
        sensor_to_advrobot= [] #liste des sensors en ne prennant en compte que les robots adverses
        for i in range (0,8): 
            if  sensor_view[i] == 1:
                sensor_to_wall.append(sensors[i])
                sensor_to_robot.append(1.0)
                sensor_to_advrobot.append(1.0) 
            elif sensor_view[i] ==2:
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(sensors[i])
                if sensor_team[i]!=self.team_name:
                    sensor_to_advrobot.append(sensors[i])
                else:
                    sensor_to_advrobot.append(1.0) 
                                    
            else:
                sensor_to_wall.append(1.0)  
                sensor_to_robot.append(1.0)
                sensor_to_advrobot.append(1.0)


        def near_ally():
            #retourne vrai si un allié est proche (distance inférieure à 0.20) et qu'il n'y a pas d'adversaire à proximité (distance supérieure à 1.0)
            for i in range(0,8):
                if(sensor_to_robot[i]<=0.7 and sensor_to_advrobot[i]==1.0):
                    return True
            return False
        
        def hate_ally():
            #retourne une translation et une rotation pour s'éloigner d'un allié proche
            rotation = 0
            translation =sensors[sensor_front]
            for i in range(0,8):
                d = sensor_to_robot[i]
                if d < 0.7:
                    strength = (0.7 - d)
                    if i < 4:
                        rotation -= strength
                    elif i > 4:
                        rotation += strength
            return translation,rotation,False
        
        def near_adv():
            #retourne vrai si un adversaire est proche (distance inférieure à 0.40)
            for i in range(0,8):
                if(sensor_to_advrobot[i]<=0.40):
                    return True
            return False
        
        def near_wall():
            for i in range(8):
                if(sensor_to_wall[i]<=0.40):
                    return True
            return False
        
        def follow_adv():
            #retourne une translation et une rotation pour suivre un adversaire proche
            rotation = 0
            for i in range(0,8):
                d = sensor_to_advrobot[i]
                if d < 1.0:
                    strength = (1 - d)
                    if i < 4:
                        rotation += strength
                    elif i > 4:
                        rotation -= strength
            translation = min(sensor_to_advrobot)
            return translation,rotation,False

        def anti_stuck_braitenberg():
            sensor_value = [7.061612619781, -9.53515116845, -8.5464354534532, -8.01565415615, 0.5456486156156, 8.00156151656, 8.5123486456, 8.001156115]
            rotation = 0.0
            for i in range(8):
                d= sensors[i]
                new_rotation = ((((1-d)*sensor_value[i]))*(random.random()*0.2))
                if abs(new_rotation) > abs(rotation):
                    rotation = new_rotation
            translation=sensors[sensor_front]*0.5
            return translation,rotation,False 

        def follow_wall():
            p=[3.229794906287786, 3.1224126097835487, 1.6015364825538114, 1.619527713398769, -1.4304767539948129, -4.3992293862626175, 1.5165160099038832, -0.5813754266134854]
            translation= sensors[sensor_front_left]* p[0]+sensors[sensor_front_right]* p[1]
            rotation =p[2] + p[3] * sensors[sensor_front_left] + p[4] * sensors[sensor_front] + p[5]*sensors[sensor_front_right]+p[6]*sensors[sensor_left]+p[7]*sensors[sensor_left]
            return translation, rotation, False



        def hate_wall():
            p=[-3.982388537439304, 1.0194463930705977, 3.783002402743694, -0.24013315661702972, 0.03606862786005216, 4.5455207437825, -4.666837493603312, 4.480902196286177]
            translation= sensors[sensor_front_left]* p[0]+sensors[sensor_front_right]* p[1]
            rotation =p[2] + p[3] * sensors[sensor_front_left] + p[4] * sensors[sensor_front] + p[5]*sensors[sensor_front_right]+p[6]*sensors[sensor_left]+p[7]*sensors[sensor_left]
            return translation, rotation, False

        # Stratégie de base : suivre le mur à droite, sauf si un adversaire est proche, auquel cas on le suit, et si un allié est proche, auquel cas on s'en éloigne.
        if(self.robot_id==0):   #  par défaut follow_wall_robot
            if near_adv() and self.memory == 0:
                self.memory = self.robot_id
                return follow_adv()
            if not near_adv() and self.memory==self.robot_id:
                self.memory=0
            if(near_ally()):
                return hate_ally()
            if(near_wall()):
                return follow_wall()
            else:
                translation = sensors[sensor_front]*0.5
                rotation = 1-sensors[sensor_front]+sensors[sensor_front_left]-sensors[sensor_front_right]+(random.random()-0.5)*0.5
                return translation,rotation,False

        if(self.robot_id==1):
            if near_adv() and self.memory == 0:
                self.memory = self.robot_id
                return follow_adv()
            if not near_adv() and self.memory==self.robot_id:
                self.memory=0
            if(near_ally()):
                return hate_ally()
            if(near_wall()):
                return anti_stuck_braitenberg()
            return hate_wall()
        

        if(self.robot_id==2):       
            if near_adv() and self.memory == 0:
                self.memory = self.robot_id
                return follow_adv()
            if not near_adv() and self.memory==self.robot_id:
                self.memory=0
            if(near_ally()):
                return hate_ally()
            if(near_wall()):
                return anti_stuck_braitenberg()
            translation = sensors[sensor_front]*0.5
            rotation = 1-sensors[sensor_front]+sensors[sensor_front_left]-sensors[sensor_front_right]+(random.random()-0.5)*0.5
            return translation,rotation,False

        if(self.robot_id==3):       # par défaut généré par l'algorithme génétique (faire des grands cercles)
            if near_adv() and self.memory == 0:
                self.memory = self.robot_id
                return follow_adv()
            if not near_adv() and self.memory==self.robot_id:
                self.memory=0
            if(near_ally()):
                return hate_ally()
            if(near_wall()):
                return anti_stuck_braitenberg()
            p = [0.04567141526258767, 0.8020188077713777, 0.9272264810865094, 1, -1, 0.748741299695503, 1, -0.7075465597198225]
            translation = sensors[sensor_front]
            rotation = (p[4] + p[5] * sensors[sensor_front_left] + p[6] * sensors[sensor_front] + p[7] * sensors[sensor_front_right])*0.8
            return translation, rotation, False

