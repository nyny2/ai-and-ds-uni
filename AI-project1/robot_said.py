from robot import *
import math
import random

class Robot_player(Robot):
    team_name = "FS_YS"
    robot_id = -1
    memory = 0  # UNIQUE entier autorisé

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        super().__init__(x_0, y_0, theta_0, name=name, team=self.team_name)

   
    

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # Récup état

        # --------- helpers d'encodage dans self.memory (int) ----------
        # On pack 3 compteurs dans un int:
        # iteration:   0..4095  (12 bits)
        # stuck:       0..63    (6 bits)
        # escape:      0..63    (6 bits)
        # memory = iteration | (stuck<<12) | (escape<<18)

        def _unpack():
            it = self.memory & 0xFFF
            stuck = (self.memory >> 12) & 0x3F
            esc = (self.memory >> 18) & 0x3F
            return it, stuck, esc

        def _pack(it, stuck, esc):
            it = max(0, min(4095, int(it)))
            stuck = max(0, min(63, int(stuck)))
            esc = max(0, min(63, int(esc)))
            self.memory = it | (stuck << 12) | (esc << 18)


        iteration, stuck_counter, escape_timer = _unpack()


        # 1. VALEURS PAR DÉFAUT : VITESSE MAXIMALE
        translation = 1.0
        rotation = 0.0

        
        
        
        def aimer(sensor_data):
            """
            Cherche l'ennemi le plus proche et tourne vers lui.
            """
            min_dist = min(sensor_data)
            if min_dist > 0.99: # Pas d'ennemi visible
                return 0.0
            
            target_idx = sensor_data.index(min_dist)
            target_proximity = 1.0 - min_dist
            
            # Mapping des indices vers une rotation souhaitée
            # On veut centrer l'ennemi sur le capteur 0 (Front)

            rotation_map = {
                0: 0.0,   # Devant
                1: 0.5,   # FL -> Tourne gauche léger
                2: 1.0,   # L  -> Tourne gauche fort
                3: 1.5,   # RL -> Demi-tour gauche
                4: 2.0,   # Rear
                5: -1.5,  # RR -> Demi-tour droite
                6: -1.0,  # R  -> Tourne droite fort
                7: -0.5   # FR -> Tourne droite léger
            }
            
            # Gain proportionnel : plus on est proche, plus on ajuste vite
            rot = rotation_map.get(target_idx, 0.0) * (1.0 + target_proximity)
            
            return rot
        
        
        def peur(sensor_list):

            sensor_value = [7.0, -9.5, -8, -8, 0.5, 8, 8.5, 8]
            rotation = 0.0
            for i in range(8):
                d= sensor_list[i]
                random_factor = 0.3 + (random.random() * 0.5)

                new_rotation = (((1-d)*sensor_value[i]*(1+(1-d))))*random_factor
                if abs(new_rotation) > abs(rotation):
                    rotation = new_rotation

            return rotation 

        

        # 2. FILTRAGE RAPIDE
        walls = [1.0] * 8
        enemies = [1.0] * 8
        allies = [1.0] * 8

        for i in range(8):
            if sensor_view[i] == 1:
                walls[i] = sensors[i]
            elif sensor_view[i] == 2:
                if sensor_team[i] != self.team_name:
                    enemies[i] = sensors[i]
                else:
                    allies[i] = sensors[i]

        # 3. DÉTECTION DE BLOCAGE (adaptée sans mémoire float)
        # Idée équivalente: si l'avant + côtés sont très proches, on considère "pas de mouvement utile".
        # Même effet: stuck_counter monte vite quand tu es coincé.
        blocked_like = (
            min(walls[0], walls[1], walls[7],walls[6],walls[2], allies[0], allies[1], allies[7]) < 0.10
            or min(sensors) < 0.08
        )

        if blocked_like:
            stuck_counter += 1
        else:
            stuck_counter = 0

        # 4. LOGIQUE DE DÉCISION "TURBO"

        # CAS A : MANOEUVRE D'ÉCHAPPEMENT (Si vraiment bloqué)
        if stuck_counter > 1 or escape_timer > 0:
            
            # 1. DÉCLENCHEMENT DU TIMER
            if escape_timer == 0:
                escape_timer = 10
                stuck_counter = 0  # On reset le compteur pour laisser le timer gérer la séquence

            
            translation = sensors[sensor_front]*0.5+0.2   
            
            rotation = peur(sensors)



            # 3. DÉCOMPTE
            escape_timer -= 1



        # CAS B : ÉVITEMENT ALLIÉS ET MURS (Plus serré)
        elif min(walls) < 0.25 or min(allies) < 0.3:
            translation = 0.8
            rotation = peur(sensors)



        # CAS C : CHASSE AUX ENNEMIS (Full Speed)
        elif min(enemies) < 1.0:
            translation = 1.0
            rotation = aimer(enemies)



                # CAS D : EXPLORATION (ouverte vs labyrinthe)
        else:
            translation = 1.0

            # Détecter couloir/labyrinthe : murs proches sur les côtés ou devant
            corridor = (min(walls[2], walls[6]) < 0.4) or (min(walls[1], walls[7]) < 0.4)

            if corridor:
                # Follow-wall léger (garde la vitesse, évite les oscillations inutiles)
                # Plus mur proche => plus on tourne pour rester centré / longer
                dist_gauche = min(walls[1], walls[2])
                dist_droite = min(walls[6], walls[7])
                rotation = (dist_gauche - dist_droite) * 2.2  # un peu moins violent que notre CAS B
            else:
                translation = 1.0

                # On regarde où est l'espace le plus profond (le couloir)
                # Capteurs Gauche : 1 (Avant-Gauche), 2 (Gauche)
                # Capteurs Droite : 7 (Avant-Droit), 6 (Droit)
                
                space_left = sensors[1] + sensors[2]
                space_right = sensors[7] + sensors[6]
                
                # Si plus d'espace à gauche, on tourne à gauche (Positif)
                # Si plus d'espace à droite, on tourne à droite (Négatif)
                # Le facteur 1.0 permet une rotation fluide vers le trou
                rotation = (space_left - space_right) * 1.0
                
                # STABILISATEUR :
                # Si on est déjà bien aligné avec le vide (gauche et droite équilibrés),
                # on réduit la rotation pour foncer tout droit dans le couloir.
                if abs(space_left - space_right) < 0.2:
                    rotation = 0.0

                else:
                    # Zone ouverte : ta sinusoïde inchangée
                    rotation = 0.05 * math.sin(iteration * 0.2)


        # Mise à jour itération (ton sinus)
        iteration = (iteration + 1) & 0xFFF  # modulo 4096

        # Sauvegarde état dans l'unique entier mémoire
        _pack(iteration, stuck_counter, escape_timer)

        # Sécurité finale
        final_trans = max(-1.0, min(1.0, translation))
        final_rot = max(-1.0, min(1.0, rotation))
        return final_trans, final_rot, False