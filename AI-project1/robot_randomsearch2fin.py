from robot import *
import math
import random

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "Optimizer"
    robot_id = -1
    iteration = 0

    param = []
    bestParam = []
    it_per_evaluation = 400
    trial = 0

    x_0 = 0
    y_0 = 0
    theta_0 = 0  # in [0,360]

    best_score = -999999
    current_score = 0
    log_file = "randomsearch2_run0.csv"
    evaluation_id = 0
    best_so_far = -999999


    last_trans = 0
    last_rot = 0

    # --- EX2: 3 fixed initial orientations (must be the same for all strategies) ---
    fixed_orientations = [0, 120, 240]   # degrees
    sub_trial = 0                        # 0,1,2 which orientation we are testing
    strategy_score_sum = 0.0             # sum of 3 runs for current param set
    # -----------------------------------------------------------------------------


    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=0, it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1

        self.x_0 = x_0
        self.y_0 = y_0

        # start always with the first fixed orientation
        self.theta_0 = self.fixed_orientations[0]

        self.param = [random.randint(-1, 1) for i in range(8)]
        self.it_per_evaluation = it_per_evaluation

        super().__init__(x_0, y_0, self.theta_0, name=name, team=team)
        with open(self.log_file, "w") as f:
            f.write("eval,score_current,best_so_far\n")


    def reset(self):
        """
        Reset the robot AND enforce the chosen initial orientation.
        Depending on your framework, super().reset() may reset to initial pose.
        We set self.theta_0 before asking for reset (in step()).
        """
        super().reset()
        # reset scoring buffers for the new run
        self.last_rot = 0
        self.last_trans = 0
        self.current_score = 0


    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        # --- score increment (same as your code) ---
        eff_trans = self.log_sum_of_translation - self.last_trans
        eff_rot   = self.log_sum_of_rotation - self.last_rot

        self.current_score += eff_trans * (1 - abs(eff_rot))

        self.last_trans = self.log_sum_of_translation
        self.last_rot   = self.log_sum_of_rotation


        # --- every X iterations: end of one run ---
        if self.iteration % self.it_per_evaluation == 0:

            if self.iteration > 0:
                # End of one run: add its score to the 3-run sum
                self.strategy_score_sum += self.current_score

                print("Evaluation no.", self.trial, "(sub-trial", self.sub_trial+1, "/3)")
                print("\trun score =", self.current_score)
                print("\tparams    =", self.param)

                # move to next orientation
                self.sub_trial += 1

                # If we still have orientations to test for SAME params:
                if self.sub_trial < 3:
                    # change starting orientation, keep SAME param
                    self.theta_0 = self.fixed_orientations[self.sub_trial]

                    # IMPORTANT: we must re-instantiate the robot pose with this theta
                    # The simulator will call reset when we return True
                    self.iteration += 1
                    return 0, 0, True

                # Otherwise: 3 runs done -> full strategy score is sum of 3 run scores
                total_score = self.strategy_score_sum
                print("\tTOTAL strategy score (sum of 3) =", total_score)

                if total_score > self.best_score:
                    self.best_score = total_score
                    self.bestParam = self.param[:]
                    print("\tNew best found, score =", self.best_score)
                # update best so far
                if self.current_score > self.best_so_far:
                    self.best_so_far = self.current_score

                # write in file
                with open(self.log_file, "a") as f:
                    f.write(f"{self.evaluation_id},{self.current_score},{self.best_so_far}\n")

                self.evaluation_id += 1

                # Prepare next strategy
                self.sub_trial = 0
                self.strategy_score_sum = 0.0
                self.theta_0 = self.fixed_orientations[0]


                # Budget & next params (same structure as your code)
                if self.trial < 500:
                    self.param = [random.randint(-1, 1) for i in range(8)]
                    self.trial += 1
                else:
                    print("budget exhausted")
                    self.param = self.bestParam[:]
                    self.it_per_evaluation = 1000

                self.iteration += 1
                return 0, 0, True

            # iteration == 0: just start normally
            self.iteration += 1
            return 0, 0, False


        # --- control function (same as your code) ---
        translation = math.tanh(
            self.param[0]
            + self.param[1] * sensors[sensor_front_left]
            + self.param[2] * sensors[sensor_front]
            + self.param[3] * sensors[sensor_front_right]
        )

        rotation = math.tanh(
            self.param[4]
            + self.param[5] * sensors[sensor_front_left]
            + self.param[6] * sensors[sensor_front]
            + self.param[7] * sensors[sensor_front_right]
        )

        if debug == True:
            if self.iteration % 100 == 0:
                print("Robot", self.robot_id, "(team " + str(self.team_name) + ")", "at step", self.iteration, ":")
                print("\tsensors (distance, max is 1.0)  =", sensors)
                print("\ttype (0:empty, 1:wall, 2:robot) =", sensor_view)
                print("\trobot's name (if relevant)      =", sensor_robot)
                print("\trobot's team (if relevant)      =", sensor_team)

        self.iteration = self.iteration + 1
        return translation, rotation, False
