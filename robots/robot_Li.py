# Projet "robotique" IA&Jeux 2025
#
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import random

nb_robots = 0

class Robot_player(Robot):

    team_name = "Les Iron 4"  # vous pouvez modifier le nom de votre équipe
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
        for i in range (0,8): #remplissage des listes 
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
                
        def is_near():#renvoie vrai si un obstacle est proche
            for i in (0,1,7):
                if sensors[i]<= 0.15:
                    return True
            return False

        def is_far():  
            return sensor_to_wall[sensor_right] >= 0.8 and sensor_to_wall[sensor_rear_right] >= 0.8
                 
        def is_adv_here():#renvoie vrai si un robot adverse est a porte
            for i in sensor_to_advrobot:
                if i != 1.0:
                    return True 
            return False
            
        def is_not_adv_near():#renvoie vrai si un obstacle autre qu'un adversaire est très proche
            for i in range (0,8):
                if sensors[i]<=0.20 and sensors[i]!= sensor_to_advrobot[i]:
                     return True
            return False
        
       	    
        def ally_near():#renvoie vrai si un obstacle autre qu'un adversaire est très proche
            for i in range (0,8):
                if sensors[i]<=0.20 and sensor_robot[i]==self.team_name:
                     return True
            return False
                     	
                 
        def hate_list(sensor_list):
            sensor_value = [7.0, -9.5, -8, -8, 0.5, 8, 8.5, 8]
            rotation = 0.0
            for i in range(8):
                d= sensor_list[i]
                new_rotation = ((((1-d)*sensor_value[i]*(1+(1-d))))*(random.random()*0.2))
                if abs(new_rotation) > abs(rotation):
                    rotation = new_rotation
            return rotation 
        
        
           
            
        def follow_wall(sensor_list):
            """Les capteurs front_left/front_right sont positifs pour s'éloigner du murs, les capteurs left/right sont négatif pour se rapprocher du murs, la somme fait qu'il reste a une distance un peu constante du mur"""
            sensor_value = [6.2,-8,5,0,0,0,-6.8,9.2]
            rotation = 0.0
            for i in range(8):
                d = sensor_list[i]
                rotation += (1-d)*sensor_value[i]
            return rotation

        
        def love_list(sensor_list):
            sensor_value = [7.0, -8, -6.5, -8, 0, 8.5, 8, 8.5]
            rotation = 0.0
            for i in range(8):
                d = sensor_list[i]
                rotation += ( d * sensor_value[i]*(1+(1-d)))
            return rotation

        
        if self.memory == 0:
            if self.robot_id==0:
                self.memory = 1
            else :
                self.memory = 0
        translation = sensors[sensor_front] + sensors[sensor_front_left] + sensors[sensor_front_right]

        if self.memory ==1:#mode passifique suivi de mur
            if is_near():
                rotation = hate_list(sensor_to_wall)
                translation = sensors[sensor_front]*0.5+0.2
            elif is_far():
                rotation = 0.3*love_list(sensor_to_wall)
                translation = sensors[sensor_front]*0.5+0.2
            else:
                rotation = 0.5 * follow_wall(sensor_to_wall)
                translation = sensors[sensor_front]*0.9+0.3

            if random.random() < 0.02:   
                self.memory = 2
            
        else:#mode aggressif 
            if is_not_adv_near():
                rotation = hate_list(sensors)
            else:
                if is_adv_here():
                    if ally_near():
                        #evite que deux robots en bloque qu'un seul
                        rotation = hate_list(sensors)
                    else:
                        rotation = love_list(sensor_to_advrobot)
                else:
                    rotation = hate_list(sensors)
        
            if ally_near():
                #evite que deux robots en bloque qu'un seul
                rotation = hate_list(sensors)

            if random.random() < 0.02:   
                self.memory = 1

        
        return translation, rotation, False

