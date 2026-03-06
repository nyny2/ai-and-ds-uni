from robot import *
import math

nb_robots = 0
debug = False

class Robot_player(Robot):
    team_name = "Optimizer"
    robot_id = -1
    iteration = 0

    param = []
    
    # --- Optimization Variables ---
    best_param = []
    best_score = -100000.0
    max_strategies = 500      # Test 500 different strategies
    
    # --- New Variables for Ex 2 ---
    fixed_orientations = [0, 120, 240] # The 3 fixed starting angles
    sub_trial_index = 0       # 0, 1, or 2
    current_strategy_score = 0 # Accumulator for the score over 3 runs
    strategy_count = 0        # Counts how many full strategies (sets of 3) we've tested
    # -----------------------------

    it_per_evaluation = 400
    
    x_0 = 0
    y_0 = 0
    theta_0 = 0 

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=0, it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        self.x_0 = x_0
        self.y_0 = y_0
        
        # Initialize with the first mandatory orientation
        self.theta_0 = self.fixed_orientations[0]
        
        self.param = [random.randint(-1, 1) for i in range(8)]
        self.it_per_evaluation = it_per_evaluation
        super().__init__(x_0, y_0, self.theta_0, name=name, team=team)

    def reset(self):
        # We modify theta_0 dynamically in 'step', so simple reset works fine
        super().reset()

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # Check if current run (400 steps) is finished
        if self.iteration % self.it_per_evaluation == 0:
            
            if self.iteration > 0:
                # 1. Calculate Score for this single run
                # Score = Translation * (1 - |Rotation|)
                run_score = self.log_sum_of_translation * (1 - abs(self.log_sum_of_rotation))
                self.current_strategy_score += run_score
                
                # 2. Advance to next sub-trial (orientation)
                self.sub_trial_index += 1

                # CASE A: We haven't finished all 3 orientations yet
                if self.sub_trial_index < 3:
                    # Keep same params, but change starting angle for next reset
                    self.theta_0 = self.fixed_orientations[self.sub_trial_index]
                    
                    # (Note: self.iteration keeps going up, which is fine, 
                    # we just need to trigger the reset below)
                    return 0, 0, True 

                # CASE B: We have finished all 3 orientations (A full strategy test is done)
                else:
                    # Print result for this strategy
                    print(f"Strategy {self.strategy_count} total score: {self.current_strategy_score:.4f}")

                    # Check if this is the new best
                    if self.current_strategy_score > self.best_score:
                        self.best_score = self.current_strategy_score
                        self.best_param = list(self.param)
                        print(f"*** New Best Strategy found! Score: {self.best_score} ***")
                        print(f"Params: {self.best_param}")

                    # Reset buffers for the next strategy
                    self.sub_trial_index = 0
                    self.current_strategy_score = 0
                    self.strategy_count += 1
                    
                    # Reset angle to the first one for the new strategy
                    self.theta_0 = self.fixed_orientations[0]

                    # CHECK TERMINATION
                    if self.strategy_count >= self.max_strategies:
                        print("Optimization finished. Switching to REPLAY mode.")
                        self.param = list(self.best_param)
                        self.it_per_evaluation = 1000 # Longer runs for replay
                        self.iteration = 0
                        # We can stick to one orientation or cycle them for replay; 
                        # usually just keeping one is fine for demo.
                        return 0, 0, True

                    # Generate NEW parameters for the next strategy
                    self.param = [random.randint(-1, 1) for i in range(8)]
                    return 0, 0, True

            # If iteration == 0 (start of simulation), just ensure we ask for reset/start clean
            return 0, 0, False # Or True, doesn't matter much at t=0

        # --- Control Loop (Perceptron) ---
        translation = math.tanh(self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right])
        rotation = math.tanh(self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right])

        self.iteration += 1        

        return translation, rotation, False