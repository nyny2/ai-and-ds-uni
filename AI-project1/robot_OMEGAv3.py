# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Belgacem Smaali 28717867
#  Prénom Nom No_étudiant/e : Khaled Bouhabel 21306362

from robot import *
import math

nb_robots = 0


class Robot_player(Robot):

    team_name = "OMEGAv3"
    robot_id = -1
    memory = 0
    

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1

        self.memory = 0

        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)


    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        # Encodage de toute la memoire dans un seul entier (self.memory)
        # on a besoin de memoriser 5 infos importantes :
        # la position precedente du robot (prev_x, prev_y), l'etat du robot (status),
        # le compteur blocage, et le compteur de pas (t)
        #
        # Layout binaire :
        #   bits  0-20  : prev_x (position X : round(x * 10000)) 21 bits
        #   bits 21-41  : prev_y (position Y : round(y * 10000)) 21 bits
        #   bit  42     : status  (0 = EXPLORE, 1 = Couloir)  1 bit
        #   bits 43-51  : blocage  (compteur d'immobilisation) 9 bits
        #   bits 52+    : t (compteur de pas : illimite)

        # Constantes de bit-packing
        PX_MASK  = (1 << 21) - 1   # masque 21 bits pour prev_x
        PY_SHIFT = 21              # prev_y commence au bit 21
        PY_MASK  = (1 << 21) - 1   # masque 21 bits pour prev_y
        ST_SHIFT = 42              # status commence au bit 42
        SK_SHIFT = 43              # blocage commence au bit 43
        SK_MASK  = (1 << 9) - 1    # masque 9 bits pour blocage (max 511)
        T_SHIFT  = 52              # t commence au bit 52

        # Fonction d'encodage : compresse les 5 valeurs dans un seul entier
        def pack(t, blocage, status, x, y):
            px = int(round(x * 10000)) & PX_MASK
            py = int(round(y * 10000)) & PY_MASK
            return (px | (py << PY_SHIFT) | (status << ST_SHIFT) | (min(blocage, SK_MASK) << SK_SHIFT) | (t << T_SHIFT))

        # Decodage de self.memory pour extraire les informations
        mem    = self.memory
        prev_x = (mem & PX_MASK) / 10000.0           # le mask isole les 21 bits de prev_x
        prev_y = ((mem >> PY_SHIFT) & PY_MASK) / 10000.0  # le shift decale puis le mask isole prev_y
        status  = (mem >> ST_SHIFT) & 1               # le & 1 isole le bit de status
        blocage  = (mem >> SK_SHIFT) & SK_MASK        # le mask isole les 9 bits de blocage
        t      = (mem >> T_SHIFT) + 1                 # on incremente le compteur de pas

        front  = sensors[sensor_front]
        left   = sensors[sensor_left]
        right  = sensors[sensor_right]
        fl     = sensors[sensor_front_left]
        fr     = sensors[sensor_front_right]

        # Detection de blocage : si le robot est bloque on increment le compteur de blocage

        dx = abs(self.x - prev_x)
        dy = abs(self.y - prev_y)

        if dx+dy < 0.0005:
            blocage = min(blocage + 1, SK_MASK)

        else:
            blocage = 0

        if blocage > 10:

            self.memory = pack(t, blocage, status, self.x, self.y)

            return 1, ((self.robot_id*2)-3)*0.8, False

        # Detection de couloir : si le robot est dans un couloir on set le status a 1

        couloir = left < 0.35 and right < 0.35 and front > 0.5

        if couloir:
            status = 1


        
        # evitement avec principe de braitenberg

        if front < 0.30 or fl < 0.22 or fr < 0.22:

            translation = 0.95

            rotation = (
                +1.4*fl
                -1.4*fr
                +0.6*left
                -0.6*right
            )

            if front < 0.25:
                # rotation en fonction de la difference entre les capteurs de gauche et de droite
                if left > right:
                    rotation += 1.2

                else:
                    rotation -= 1.2

            self.memory = pack(t, blocage, status, self.x, self.y)

            return translation, max(-1,min(1,rotation)), False
        
        # Evitement des robots de l'equipe
        # on implemente ca car sinon sans mecanisme de coordination les 4 robots tendent à explorer les mm zones 
        
        repel = 0 # force repulsive

        if sensor_view is not None: 

            for i in range(8):

                if sensor_view[i]==2 and sensor_team[i]==self.team_name: # si le sensor voit un robot et que c'est le notre
                    force = (1-sensors[i]) # force repulsive en fonction de la distance

                    if i < 4: 
                        repel += force # la je crois faut qu'on inverse le signe ici car si y'a un truc à gauche faut qu'on bouge a droite donc négatif
                    else: 
                        repel -= force # la je crois faut qu'on inverse le signe ici car si y'a un truc à droite faut qu'on bouge a gauche donc positif
        # Track des ennemis

        closest_enemy_dist = 1.0
        closest_enemy_index = -1
        
        for i in range(8):
            if sensor_view[i] == 2 and sensor_team[i] != "n/a" :
                if sensors[i] < closest_enemy_dist and sensor_team[i] != self.team_name:
                    closest_enemy_dist = sensors[i]
                    closest_enemy_index = i
            
        # if enemy detected, go towards them
        if closest_enemy_index != -1:
            # Calculate rotation based on sensor position
            # sensor 0=front, 1=front-left, 2=left, 3=back-left, etc.
            angle_offset = closest_enemy_index * 45  # degrees from front
            if angle_offset > 180:
                angle_offset -= 360
            rotation = angle_offset / 180.0  # normalize to [-1, 1]
            translation =  0.0 + closest_enemy_dist # move slower when closer
            return translation,rotation,False
        
        # Comportements par robot :

        # 0 - EXPLORATEUR
        if self.robot_id == 0:

            translation = sensors[sensor_front]*1+0.2
        
            rotation = (
                +0.5 * sensors[sensor_front_left] +
                -0.5 * sensors[sensor_front_right] +
                +1 * sensors[sensor_left] +
                -1 * sensors[sensor_right]+(random.choice([0,0.1])) )

        # 1 - CHASSEUR DE COULOIRS
        elif self.robot_id == 1:

            if status:
                translation = 1
                rotation = 0
            else:
                translation = 1
                rotation = (right-left)*0.8 + math.sin(t*0.03)*0.2

        # 2 - INFILTRATEUR :
        elif self.robot_id == 2:

            if status:
                translation = 1
                rotation = (right-left)*0.2
            else:
                translation = 1
                rotation = 0.32 + math.sin(t*0.04)*0.1

        # 3 - SWEEPER :
        else:

            # Comportement principal hand-tuned
            translation = 1
            rotation = (left-right)*0.7 + math.sin(t*0.06)*0.25

            # Contribution partielle du perceptron GA (poids optimises, score: 345.33)
            _W = [1.2565, -0.7026, 1.7263, 1.3229, -1.6513, 0.2276, 1.5360, -0.1227]
            ga_rot = math.tanh(_W[4] + _W[5]*fl + _W[6]*front + _W[7]*fr)
            rotation += ga_rot * 0.1

        # Application de la force repulsive 


        rotation += repel*0.8

        # Attraction des bords : si on est proche d'un bord on tourne pour etre a distance

        if left < 0.4: rotation += 0.15
        if right < 0.4: rotation -= 0.15

        # Normaliser la rotation entre -1 et 1

        rotation = max(-1,min(1,rotation))

        # Encodage de self.memory

        self.memory = pack(t, blocage, status, self.x, self.y)

        return translation, rotation, False