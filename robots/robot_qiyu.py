# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Qiyu LYU 21301461
#  Prénom Nom No_étudiant/e : _________
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import math
import random

nb_robots = 0

class Robot_player(Robot):

    team_name = "qiyu"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=team)


    def reset(self):
        super().reset()

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # ------------------------------------------------------------
        # Constraints respected:
        # - no comms, no map, no extra memory (only self.memory int)
        # - all logic inside step (helpers are defined inside step)
        # ------------------------------------------------------------

        # init once
        if not hasattr(self, "seeded"):
            self.seeded = True
            random.seed(2026 + 131 * self.robot_id)

        # safe defaults
        if sensor_view is None:
            sensor_view = [0] * 8
        if sensor_team is None:
            sensor_team = [None] * 8

        WALL = 1
        ROBOT = 2

        def clamp(x, lo=-1.0, hi=1.0):
            return lo if x < lo else (hi if x > hi else x)

        # ------------------------------------------------------------
        # Utility: distance arrays filtered by type/team (friend/enemy)
        # ------------------------------------------------------------
        def wall_distances():
            d = [1.0] * 8
            for i in range(8):
                if sensor_view[i] == WALL:
                    d[i] = sensors[i]
            return d

        def enemy_robot_distances():
            d = [1.0] * 8
            for i in range(8):
                if sensor_view[i] == ROBOT:
                    # enemy if team differs from self.team
                    if sensor_team[i] is not None and sensor_team[i] != self.team:
                        d[i] = sensors[i]
            return d

        # ------------------------------------------------------------
        # Braitenberg 1: avoider (wall + robot)  [your avoider idea]
        # ------------------------------------------------------------
        def braitenberg_avoider():
            to_wall = [1.0] * 8
            to_bot = [1.0] * 8
            for i in range(8):
                if sensor_view[i] == WALL:
                    to_wall[i] = sensors[i]
                elif sensor_view[i] == ROBOT:
                    to_bot[i] = sensors[i]

            aw = [1.0 - x for x in to_wall]
            ab = [1.0 - x for x in to_bot]
            a = [min(1.0, aw[i] + ab[i]) for i in range(8)]

            danger = (
                0.6 * a[sensor_front] +
                0.2 * a[sensor_front_left] +
                0.2 * a[sensor_front_right]
            )
            translation = 0.8 * (1.0 - danger)

            # danger in [0,1]
            translation = 0.85 * (1.0 - danger)

            left = a[sensor_left] + a[sensor_front_left]
            right = a[sensor_right] + a[sensor_front_right]

            # 动态转向增益：越危险，转得越狠
            k_rot = 1.2 + 1.8 * danger         # 1.2 -> 3.0
            rotation = k_rot * (right - left)

            # 靠墙时再额外降速，避免“贴墙高速抖动”
            translation *= (1.0 - 0.35 * danger)

            return clamp(translation), clamp(rotation)


        # ------------------------------------------------------------
        # Braitenberg 2: lovewall patrol (hug walls) [your lovewall]
        # ------------------------------------------------------------
        def braitenberg_lovewall():
            dw = wall_distances()
            a = [1.0 - x for x in dw]  # attraction

            translation = 0.2 + 0.8 * min(
                1.0,
                a[sensor_front] + 0.25 * (a[sensor_front_left] + a[sensor_front_right])
            )
            rotation = (
                (a[sensor_left] + a[sensor_front_left]) -
                (a[sensor_right] + a[sensor_front_right])
            )
            return clamp(translation), clamp(rotation)



        # ------------------------------------------------------------
        # Neutral exploration when no enemy is seen (safer than lovewall)
        # ------------------------------------------------------------
        def roam():
            # move forward when free, gently steer away from nearer side
            t = clamp(0.2 + 0.75 * sensors[sensor_front])
            r = clamp(0.6 * (sensors[sensor_right] - sensors[sensor_left]))
            return t, r


        # ------------------------------------------------------------
        # Braitenberg 3: love ENEMY only (like lovebot, but filtered)
        # uses sqrt shaping (from your friend) so it reacts earlier.
        # if no enemy -> returns (None, None)
        # ------------------------------------------------------------
        def braitenberg_love_enemy():
            de = enemy_robot_distances()
            if min(de) >= 1.0:
                return None, None

            a = [(1.0 - x) ** 0.5 for x in de]  # early attraction

            translation = 0.2 + 0.8 * min(
                1.0,
                a[sensor_front] + 0.25 * (a[sensor_front_left] + a[sensor_front_right])
            )
            rotation = (
                (a[sensor_left] + a[sensor_front_left]) -
                (a[sensor_right] + a[sensor_front_right])
            )
            return clamp(translation), clamp(rotation)

        # ------------------------------------------------------------
        # GA Perceptron controller (robot 0) with YOUR bestParam
        # ------------------------------------------------------------
        GA_WEIGHTS = [0, -1, 1, 1, -1, 1, 1, -1]

        def ga_perceptron():
            # only uses front triple like your GA code
            FL = sensors[sensor_front_left]
            F = sensors[sensor_front]
            FR = sensors[sensor_front_right]


            w = GA_WEIGHTS
            translation = math.tanh(w[0] + w[1] * FL + w[2] * F + w[3] * FR)
            rotation = math.tanh(w[4] + w[5] * FL + w[6] * F + w[7] * FR)
            return clamp(translation), clamp(rotation)

        # ============================================================
        # SUBSUMPTION LAYERS
        # ============================================================

        # -------------------------
        # Layer 0: escape if stuck (self.memory as counter+cooldown)
        # -------------------------
        counter = self.memory % 1000
        cooldown = self.memory // 1000

        self.memory = cooldown * 1000 + counter

        F = sensors[sensor_front]
        FL = sensors[sensor_front_left]
        FR = sensors[sensor_front_right]
        L = sensors[sensor_left]
        R = sensors[sensor_right]
        BR = sensors[sensor_rear_right]
        B  = sensors[sensor_rear]
        BL = sensors[sensor_rear_left]


        close_front = (F < 0.14) or (min(FL, FR) < 0.12)

        # 贴边卡死：沿左/右墙磨蹭
        edge_stall = (L < 0.10 and FL < 0.12) or (R < 0.10 and FR < 0.12)

        # 角落卡死：前方近 + 一侧近 + 对应后侧也近（典型“楔进角落”）
        corner_stall = (
            (close_front and L < 0.12 and BL < 0.12) or
            (close_front and R < 0.12 and BR < 0.12)
        )

        # 原来的 squeezed 可以保留，但不够用
        squeezed = (L < 0.10) or (R < 0.10)

        if cooldown > 0:
            cooldown -= 1

        if cooldown == 0 and (corner_stall or edge_stall or (close_front and squeezed)):
            counter += 1
        else:
            counter = max(0, counter - 1)

        if counter >= 10 and cooldown == 0:
            # 倒车 + 朝更空的一侧转（用左右距离判更空）
            turn = 1.0 if L < R else -1.0
            self.memory = 30 * 1000 + 0
            return -0.7, 1.0 * turn, False


        # -------------------------
        # Layer 1: emergency avoidance
        # -------------------------
        emergency = (F < 0.14) or (min(FL, FR) < 0.11)

        if emergency:
            t, r = braitenberg_avoider()
            return clamp(0.9 * t), clamp(1.0 * r), False

        # -------------------------
        # Layer 2: role behaviors (4 robots)
        # -------------------------
        if self.robot_id == 0:
            # Role 0: GA sweeper (fast expansion)
            translation, rotation = ga_perceptron()

            # 只要开始靠墙/靠边，就提前融合 avoider，避免进入“角落转圈吸引子”
            near_wall = (F < 0.30) or (min(FL, FR) < 0.26) or (L < 0.20) or (R < 0.20)
            if near_wall:
                at, ar = braitenberg_avoider()
                # 靠得越近，blend 越大（你可以按感觉调这两个阈值）
                blend = 0.35
                if F < 0.22 or min(FL, FR) < 0.18:
                    blend = 0.60
                translation = clamp((1 - blend) * translation + blend * at)
                rotation    = clamp((1 - blend) * rotation    + blend * ar)

        elif self.robot_id == 1:
            # Role 1: wall patrol (stable coverage along edges)
            translation, rotation = braitenberg_lovewall()
            # blend a bit of avoider when approaching obstacles
            if F < 0.25 or min(FL, FR) < 0.20:
                at, ar = braitenberg_avoider()
                translation = clamp(0.6 * translation + 0.4 * at)
                rotation = clamp(0.6 * rotation + 0.4 * ar)

        elif self.robot_id == 2:
            # Role 2: enemy hunter (steal last-visited cells)
            t, r = braitenberg_love_enemy()
            if t is not None:
                translation, rotation = t, r
                at, ar = braitenberg_avoider()
                translation = clamp(0.7 * translation + 0.3 * at)
                rotation = clamp(0.7 * rotation + 0.3 * ar)
            else:
                # no enemy in sight -> roam using wall patrol
                translation, rotation = roam()

        else:
            # Role 3: mixed disruptor
            t, r = roam()
            if t is not None:
                translation, rotation = t, r
                # small lateral bias to avoid head-on lock
                rotation = clamp(rotation + (0.22 if (self.robot_id % 2 == 0) else -0.22))
                at, ar = braitenberg_avoider()
                translation = clamp(0.6 * translation + 0.4 * at)
                rotation = clamp(0.6 * rotation + 0.4 * ar)
            else:
                # roam: forward when free, turn away from closer side
                translation = clamp(0.2 + 0.7 * F)
                rotation = clamp((R - L) * 0.8)



        # -------------------------
        # Universal safety blend:
        # Prevent goal behaviors (love_enemy / lovewall / GA) from sticking to walls.
        # -------------------------
        at, ar = braitenberg_avoider()

        wall_close = (
            (F < 0.25) or (min(FL, FR) < 0.22) or
            (L < 0.14) or (R < 0.14)
        )

        if wall_close:
            blend = 0.55
            if (F < 0.18) or (min(FL, FR) < 0.16) or (L < 0.10) or (R < 0.10):
                blend = 0.75
            translation = clamp((1 - blend) * translation + blend * at)
            rotation    = clamp((1 - blend) * rotation    + blend * ar)




        # -------------------------
        # Layer 3: tiny noise to break cycles
        # -------------------------
        rotation = clamp(rotation + (random.random() - 0.5) * 0.08)

        return translation, rotation, False
