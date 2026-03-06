# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Deborah Levi Acobas 21311039
#  Prénom Nom No_étudiant/e : Angèle Coutant 21307920 
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import math 


nb_robots = 0

class Robot_player(Robot):

    team_name = "DreamTeam"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        BEST_PARAM = [0,1,0,1,0,0,0,0]  # meilleurs paramètres trouvés grâce à robot_randomsearch2.py puis genetic_algorithms, testés sur les 5 arènes différentes
        sensor_to_wall = [] 
        sensor_to_robot = []
        for i in range (0,8):
            if  sensor_view[i] == 1: #voit mur 
                sensor_to_wall.append( sensors[i] )
                sensor_to_robot.append(1.0)
            elif  sensor_view[i] == 2: #voit robot 
                sensor_to_wall.append( 1.0 )
                sensor_to_robot.append( sensors[i] )
            else: #voit aucun 
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)
        
        if self.robot_id == 0: #robot qui hate wall mais évite quand meme de rentrer dans tous les autres robots
            close_robot = min(sensor_to_robot[sensor_front], sensor_to_robot[sensor_front_left], sensor_to_robot[sensor_front_right])
        
            translation = sensors[sensor_front] * 0.8 
            rotation = (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right]) * 5.0 + (1.0 - sensor_to_wall[sensor_front]) * 0.3  + (random.random()-0.5)*0.5 #si le mur est plus proche vers la gauche -> va vers la droite ect ET si mur est tout droit en face, (1.0 - sensor_to_wall[sensor_front]) impose une rotation 

            if close_robot<0.4 : #si robot vraiment tres proche --> éviter 
                rotation = (sensor_to_robot[sensor_front_left] - sensor_to_robot[sensor_front_right])*5.0 + (1.0 - sensor_to_robot[sensor_front]) * 0.3 + (random.random()-0.5)*0.5  
    
        if self.robot_id == 1: #robot avec les meilleurs parametres trouvés grace à robot_randomsearch2.py puis genetic_algorithms, testés sur les 5 arènes différentes ET qui évite les murs 
            close_wall = min(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right])
            
        
            if close_wall < 0.5:  # couche 1 : éviter les murs --> inspiré de robot_braintenberg_hateWall 
                translation = 0.8 
                rotation = (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right]) * 5.0 + (1.0 - sensor_to_wall[sensor_front]) * 0.3 + (random.random()-0.5)*0.5
            
         
            else:   #couche 2 : explorer l'arène avec les parametres trouvés grace à robot_randomsearch2.py puis genetic_algorithms, testés sur les 5 arènes différentes
                translation = math.tanh (BEST_PARAM[0] + BEST_PARAM[1] * sensor_to_wall[sensor_front_left] + BEST_PARAM[2] * sensor_to_wall[sensor_front] + BEST_PARAM[3] * sensor_to_wall[sensor_front_right] ) 
                rotation = math.tanh (BEST_PARAM[4] + BEST_PARAM[5] * sensor_to_wall[sensor_front_left] + BEST_PARAM[6] * sensor_to_wall[sensor_front] + BEST_PARAM[7] * sensor_to_wall[sensor_front_right] ) + (random.random()-0.5)*0.5

        if self.robot_id == 2  : #il est a la fois chasseur et peintre --> mis en place par subsomption 
            close_wall = min(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right])
            close_robot = min(sensor_to_robot[sensor_front], sensor_to_robot[sensor_front_left], sensor_to_robot[sensor_front_right])
        
            if close_wall < 0.4:  # couche 1 : éviter les murs --> inspiré de robot_braintenberg_hateWall 
                translation = 0.3 
                rotation = (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right]) * 5.0 + (1.0 - sensor_to_wall[sensor_front]) * 0.3 + (random.random()-0.5)*0.6
            
            
            elif close_robot < 0.8: # couche 2 : chasser robots --> inspiré de robot_braintenberg_loveBot.py du TP1 
                translation = 0.3
                rotation = (random.random() - 0.5) * 1
                for i in range(8):
                    if sensor_view[i] == 2 and sensor_team[i] != self.team_name: #robot de l'autre équipe détécté 
                        translation = 0.8 # foncer vers la cible 
                        rotation = (sensor_to_robot[sensor_front_right] - sensor_to_robot[sensor_front_left]) * 3.0 
                        break 
         
            else:   #couche 3 : explorer l'arène aléatoirement 
                translation = 1.0 
                rotation = (random.random() - 0.5) * 1 

        if self.robot_id == 3 : # son but est de chasser les robots de l'autre équipe

            close_wall = min(sensor_to_wall[sensor_front], sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_front_right])
            
            translation = 0.3
            rotation = 0.5 + (random.random() - 0.5) * 2

            if close_wall < 0.5:  #  éviter les murs --> inspiré de robot_braintenberg_hateWall 
                translation = 0.3 
                rotation = (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right]) * 5.0 + (1.0 - sensor_to_wall[sensor_front]) * 0.3 + (random.random()-0.5)*0.6

            for i in range(8):
                if sensor_view[i] == 2 and sensor_team[i] != self.team_name: #robot de l'autre équipe détécté 
                    translation = 0.8 # foncer vers la cible 
                    rotation = (sensor_to_robot[sensor_front_right] - sensor_to_robot[sensor_front_left]) * 3.0 
                    break 
        

        

        #translation = sensors[sensor_front]
        #rotation = 1.0 * sensors[sensor_front_left] - 1.0 * sensors[sensor_front_right] + (random.random()-0.5)*0.1
        return translation, rotation, False 
