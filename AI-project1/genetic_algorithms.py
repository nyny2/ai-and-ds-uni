from robot import *
import math
import random

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "Optimizer"
    robot_id = -1
    iteration = 0
    #ex4
    log_file = "ga_run0.csv"
    evaluation_id = 0
    best_so_far = -999999


    # --- evaluation settings ---
    it_per_evaluation = 400
    max_generations = 500

    # --- initial pose ---
    x_0 = 0
    y_0 = 0
    theta_0 = 0  # degrees in your comments

    # --- EX2: fixed initial orientations for fair comparison ---
    fixed_orientations = [0, 120, 240]  # keep same for everyone
    sub_trial = 0                       # 0,1,2
    strategy_score_sum = 0.0            # sum of 3 runs for current individual

    # --- score bookkeeping (same spirit as your file) ---
    current_score = 0.0
    last_trans = 0.0
    last_rot = 0.0

    # --- (1+1)-GA state ---
    parent = []             # current best individual
    parent_score = -999999  # fitness of parent

    child = []              # mutated child
    generation = 0          # how many children evaluated

    # genes domain (like your randomsearch)
    gene_values = [-1, 0, 1]

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=0, it_per_evaluation=400):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1

        self.x_0 = x_0
        self.y_0 = y_0
        self.it_per_evaluation = it_per_evaluation

        # start with first fixed orientation
        self.theta_0 = self.fixed_orientations[0]

        # init parent randomly (8 params)
        self.parent = [random.choice(self.gene_values) for _ in range(8)]
        self.parent_score = -999999

        # first evaluated individual = parent
        self.param = self.parent[:]   # controller uses self.param

        super().__init__(x_0, y_0, self.theta_0, name=name, team=team)
        
        #ex4
        with open(self.log_file, "w") as f:
            f.write("eval,score_parent,best_so_far\n")

    def reset(self):
        super().reset()
        self.last_rot = 0.0
        self.last_trans = 0.0
        self.current_score = 0.0

    # --- mutation operator: change ONE parameter to a DIFFERENT value ---
    def mutate_one_gene(self, indiv):
        child = indiv[:]  # copy
        i = random.randrange(len(child))
        old = child[i]

        # pick a new value != old (without replacement)
        choices = [v for v in self.gene_values if v != old]
        child[i] = random.choice(choices)
        return child

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        # --- incremental scoring (same as your randomsearch) ---
        eff_trans = self.log_sum_of_translation - self.last_trans
        eff_rot   = self.log_sum_of_rotation - self.last_rot

        self.current_score += eff_trans * (1 - abs(eff_rot))

        self.last_trans = self.log_sum_of_translation
        self.last_rot   = self.log_sum_of_rotation

        # --- end of a run every it_per_evaluation steps ---
        if self.iteration % self.it_per_evaluation == 0:

            if self.iteration > 0:
                # end of one run => add to sum for 3 orientations
                self.strategy_score_sum += self.current_score

                print(f"Gen {self.generation} (sub-trial {self.sub_trial+1}/3) score_run={self.current_score:.4f}")
                print("\tparams =", self.param)

                # next orientation
                self.sub_trial += 1

                # still runs to do for same individual
                if self.sub_trial < 3:
                    self.theta_0 = self.fixed_orientations[self.sub_trial]
                    self.iteration += 1
                    return 0, 0, True

                # ----- after 3 runs => we have fitness of the evaluated individual -----
                fitness = self.strategy_score_sum
                print(f"\tTOTAL fitness (sum 3 runs) = {fitness:.4f}")

                # Which individual was evaluated? (child if exists, else parent)
                # We evaluate: parent first, then child each generation.
                if self.generation == 0 and self.parent_score == -999999:
                    # first evaluation => it's the parent
                    self.parent_score = fitness
                    print(f"\tParent initialized. parent_score = {self.parent_score:.4f}")

                else:
                    # we just evaluated the child of current generation
                    # Selection (μ=1 + λ=1): replace parent if child is better
                    if fitness > self.parent_score:
                        self.parent = self.child[:]
                        self.parent_score = fitness
                        print("\tCHILD wins -> becomes new PARENT!")
                        print(f"\tNew parent_score = {self.parent_score:.4f}")
                    else:
                        print("\tParent kept (child discarded).")
                    #ex4
                    # update best so far
                    if self.parent_score > self.best_so_far:
                        self.best_so_far = self.parent_score

                    # write in file
                    with open(self.log_file, "a") as f:
                        f.write(f"{self.evaluation_id},{self.parent_score},{self.best_so_far}\n")

                    self.evaluation_id += 1

                # prepare next evaluation cycle
                self.sub_trial = 0
                self.strategy_score_sum = 0.0
                self.theta_0 = self.fixed_orientations[0]

                # stop condition
                if self.generation >= self.max_generations:
                    print("Budget exhausted -> replay best parent")
                    self.param = self.parent[:]
                    self.it_per_evaluation = 1000
                    self.iteration += 1
                    return 0, 0, True

                # Create next child (λ=1): mutate one gene from parent
                self.child = self.mutate_one_gene(self.parent)
                self.param = self.child[:]      # evaluate the child next
                self.generation += 1

                self.iteration += 1
                return 0, 0, True

            # iteration == 0 start
            self.iteration += 1
            return 0, 0, False

        # --- controller (perceptron) ---
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

        if debug == True and self.iteration % 100 == 0:
            print("Robot", self.robot_id, "(team " + str(self.team_name) + ")", "at step", self.iteration, ":")
            print("\tsensors (distance, max is 1.0)  =", sensors)

        self.iteration += 1
        return translation, rotation, False
