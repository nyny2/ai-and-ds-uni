# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Felix XU 21312879_______
#  Prénom Nom No_étudiant/e : Harouna Sissoko 21301629________
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import math 
nb_robots = 0
GA_PARAM = [-1, 1, 0, -1, 1, 1, -1, -1]

class Robot_player(Robot):

    team_name = "XU_SIS"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier
    param = GA_PARAM

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)
        
    # ================= BRAITENBERG =================
    def hateWall(self, sensors, sensor_to_wall):
    
        front = sensor_to_wall[sensor_front]
        front_left = sensor_to_wall[sensor_front_left]
        front_right = sensor_to_wall[sensor_front_right]
        left = sensor_to_wall[sensor_left]
        right = sensor_to_wall[sensor_right]
        
        if front < 0.15: # Mur devant
            translation = 0.2
            rotation = 1.0 if left > right else -1.0 # tourne a g si lobstacle est plus loin de d

        else: 
            translation = 1.0
            rotation = (front_left-front)+(front_left-front_right) # evite sinon
        
        return translation, rotation

    def loveBot(self, sensors, sensor_to_robot, sensor_team, sensor_view):
        front_right = sensor_to_robot[sensor_front_right]
        front_left = sensor_to_robot[sensor_front_left]
        front = sensor_to_robot[sensor_front]

        is_ally = False
        for idx in [sensor_front, sensor_front_left, sensor_front_right]: # notre robot ?
            if sensor_view[idx] == 2 and sensor_team[idx] == self.team_name:
                    is_ally = True
                    break
        if self.is_ally(self,sensor_to_robot, sensor_team, sensor_view):
            translation =  1.0
            rotation = (front_left-front)+(front_left-front_right)# Evite si notre robot
        
        else :
            translation =  1.0
            rotation = (front_right-front_left)+(front-front_left)# sinon le suit

        return translation, rotation
    
    def hateBot(self, sensors, sensor_to_robot, sensor_team, sensor_view):

        front = sensor_to_robot[sensor_front]
        front_left = sensor_to_robot[sensor_front_left]
        front_right = sensor_to_robot[sensor_front_right]

        if self.is_ally(sensors,sensor_to_robot, sensor_team, sensor_view):
            # allie evite
            translation = 0.4
            rotation = (front_left-front_right)+(front_left-front)
        else:
            # attaque 
            translation = 1.0
            rotation = (front_right-front_left)+(front-front_left)

        return translation, rotation

    def is_ally(self, sensors, sensor_to_robot, sensor_team, sensor_view) :
        for idx in [sensor_front, sensor_front_left, sensor_front_right]:
            if sensor_view[idx] == 2 and sensor_team[idx] == self.team_name:
                return True
        return False
    # =================Algo Genetique=================
    def explorer(self, sensors, sensor_to_wall, sensor_to_robot):

        front_wall = sensor_to_wall[sensor_front]
        left_wall = sensor_to_wall[sensor_front_left]
        right_wall = sensor_to_wall[sensor_front_right]
        rear_wall = sensor_to_wall[sensor_rear]
        rear_left_wall = sensor_to_wall[sensor_rear_left]
        rear_right_wall = sensor_to_wall[sensor_rear_right]
        
      
        front_robot = sensor_to_robot[sensor_front]
        front_left_robot = sensor_to_robot[sensor_front_left]
        front_right_robot = sensor_to_robot[sensor_front_right]
        
        if front_wall < 0.15 or front_robot < 0.15:
            translation = 0.2  
            rotation = 1.0 if left_wall > right_wall else -1.0

        elif left_wall < 0.3 or front_left_robot < 0.3:
            # gauche -> tourne à droite
            translation = 1
            rotation = -0.8
        elif right_wall < 0.3 or front_right_robot < 0.3:
            # droite -> tourne à gauche
            translation = 1
            rotation = 0.8
        
        elif rear_wall < 0.3 or rear_left_wall < 0.3 or rear_right_wall < 0.3:
            # derriere -> avance
            translation = 1
            rotation = 0.0
        
        else:
            # Paramètres GA            
            translation = -1*math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
            rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )
        
        return translation, rotation
    
    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # ================= BRAITENBERG =================
        def hateWall(self, sensors, sensor_to_wall):
        
            front = sensor_to_wall[sensor_front]
            front_left = sensor_to_wall[sensor_front_left]
            front_right = sensor_to_wall[sensor_front_right]
            left = sensor_to_wall[sensor_left]
            right = sensor_to_wall[sensor_right]
            
            if front < 0.15: # Mur devant
                translation = 0.2
                rotation = 1.0 if left > right else -1.0 # tourne a g si lobstacle est plus loin de d

            else: 
                translation = 1.0
                rotation = (front_left-front)+(front_left-front_right) # evite sinon
            
            return translation, rotation

        def loveBot(self, sensors, sensor_to_robot, sensor_team, sensor_view):
            front_right = sensor_to_robot[sensor_front_right]
            front_left = sensor_to_robot[sensor_front_left]
            front = sensor_to_robot[sensor_front]

            is_ally = False
            for idx in [sensor_front, sensor_front_left, sensor_front_right]: # notre robot ?
                if sensor_view[idx] == 2 and sensor_team[idx] == self.team_name:
                        is_ally = True
                        break
            if self.is_ally(self,sensor_to_robot, sensor_team, sensor_view):
                translation =  1.0
                rotation = (front_left-front)+(front_left-front_right)# Evite si notre robot
            
            else :
                translation =  1.0
                rotation = (front_right-front_left)+(front-front_left)# sinon le suit

            return translation, rotation
        
        def hateBot(self, sensors, sensor_to_robot, sensor_team, sensor_view):

            front = sensor_to_robot[sensor_front]
            front_left = sensor_to_robot[sensor_front_left]
            front_right = sensor_to_robot[sensor_front_right]

            if self.is_ally(sensors,sensor_to_robot, sensor_team, sensor_view):
                # allie evite
                translation = 0.4
                rotation = (front_left-front_right)+(front_left-front)
            else:
                # attaque 
                translation = 1.0
                rotation = (front_right-front_left)+(front-front_left)

            return translation, rotation

        def is_ally(self, sensors, sensor_to_robot, sensor_team, sensor_view) :
            for idx in [sensor_front, sensor_front_left, sensor_front_right]:
                if sensor_view[idx] == 2 and sensor_team[idx] == self.team_name:
                    return True
            return False
        # =================Algo Genetique=================
        def explorer(self, sensors, sensor_to_wall, sensor_to_robot):

            front_wall = sensor_to_wall[sensor_front]
            left_wall = sensor_to_wall[sensor_front_left]
            right_wall = sensor_to_wall[sensor_front_right]
            rear_wall = sensor_to_wall[sensor_rear]
            rear_left_wall = sensor_to_wall[sensor_rear_left]
            rear_right_wall = sensor_to_wall[sensor_rear_right]
            
        
            front_robot = sensor_to_robot[sensor_front]
            front_left_robot = sensor_to_robot[sensor_front_left]
            front_right_robot = sensor_to_robot[sensor_front_right]
            
            if front_wall < 0.15 or front_robot < 0.15:
                translation = 0.2  
                rotation = 1.0 if left_wall > right_wall else -1.0

            elif left_wall < 0.3 or front_left_robot < 0.3:
                # gauche -> tourne à droite
                translation = 1
                rotation = -0.8
            elif right_wall < 0.3 or front_right_robot < 0.3:
                # droite -> tourne à gauche
                translation = 1
                rotation = 0.8
            
            elif rear_wall < 0.3 or rear_left_wall < 0.3 or rear_right_wall < 0.3:
                # derriere -> avance
                translation = 1
                rotation = 0.0
            
            else:
                # Paramètres GA            
                translation = -1*math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
                rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )
            
            return translation, rotation
        sensor_to_wall = []
        sensor_to_robot = []
        for i in range (0,8):
            if  sensor_view[i] == 1:
                sensor_to_wall.append( sensors[i] )
                sensor_to_robot.append(1.0)
            elif  sensor_view[i] == 2:
                sensor_to_wall.append( 1.0 )
                sensor_to_robot.append( sensors[i] )
            else:
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)


        existe_mur = sensors[sensor_front] < 0.3 or (sensors[sensor_front] < 0.3 and sensors[sensor_front_right] < 0.3 and sensors[sensor_front_left] < 0.3)
        existe_robot = True if self.is_ally(sensors, sensor_to_robot, sensor_team, sensor_view) else False

        # --------- SUBSOMPTION ---------
        if existe_mur :
          translation, rotation = self.hateWall(sensors, sensor_to_wall)  
        elif existe_robot:
            translation,rotation = self.hateBot(sensors, sensor_to_robot, sensor_team, sensor_view)
        elif self.robot_id == 0 :
            translation,rotation = self.loveBot(sensors, sensor_to_robot, sensor_team, sensor_view)
        else:
            translation, rotation = self.explorer(sensors, sensor_to_wall, sensor_to_robot)

        if(self.memory % 50 == 0) : # refresh 
                translation, rotation = -1, 0.5
                
        self.memory += 1  
        return translation, rotation, False
