from robot import * 

nb_robots = 0
debug = False

class Robot_player(Robot):
    """
    Fixed robot with anti-stuck mechanisms and better maze coverage
    """

    team_name = "Maze Masters"
    robot_id = -1
    iteration = 0
    memory = 0  # Single integer memory - used as stuck counter

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        Improved step with anti-stuck behavior
        """
        
        # Separate sensors by type
        sensor_to_wall = []
        sensor_to_robot = []
        enemy_detected = False
        teammate_detected = False
        
        for i in range(8):
            if sensor_view[i] == 1:  # Wall
                sensor_to_wall.append(sensors[i])
                sensor_to_robot.append(1.0)
            elif sensor_view[i] == 2:  # Robot
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(sensors[i])
                if sensor_team[i] != self.team_name:
                    enemy_detected = True
                else:
                    teammate_detected = True
            else:  # Empty
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)

        # Detect if stuck (multiple walls close + low movement expected)
        walls_close = sum(1 for s in sensor_to_wall if s < 0.5)
        is_stuck = walls_close >= 3
        
        # Update memory: increment when stuck, reset when free
        if is_stuck:
            self.memory = min(self.memory + 1, 200)
        else:
            self.memory = max(0, self.memory - 2)
        
        # If stuck for too long, execute escape behavior
        if self.memory > 50:
            translation, rotation = self.escape_behavior(sensor_to_wall)
        # Different strategies per robot
        elif self.robot_id == 0:
            translation, rotation = self.aggressive_explorer(sensor_to_wall, sensor_to_robot, enemy_detected)
        elif self.robot_id == 1:
            translation, rotation = self.wall_follower_adaptive(sensor_to_wall, sensor_to_robot, enemy_detected, hand="right")
        elif self.robot_id == 2:
            translation, rotation = self.wall_follower_adaptive(sensor_to_wall, sensor_to_robot, enemy_detected, hand="left")
        else:  # robot_id == 3
            translation, rotation = self.territory_denier(sensor_to_wall, sensor_to_robot, enemy_detected, teammate_detected)

        self.iteration += 1
        return translation, rotation, False

    def escape_behavior(self, sensor_to_wall):
        """
        Emergency behavior to escape stuck situations
        """
        # Fast backward movement with sharp turn
        translation = -0.5  # Move backward
        
        # Turn toward most open direction
        front_blocked = sensor_to_wall[sensor_front] < 0.4
        left_blocked = sensor_to_wall[sensor_left] < 0.4
        right_blocked = sensor_to_wall[sensor_right] < 0.4
        
        if not left_blocked and right_blocked:
            rotation = -2.0  # Turn hard left
        elif not right_blocked and left_blocked:
            rotation = 2.0   # Turn hard right
        elif front_blocked:
            # Both sides blocked, turn based on memory state
            rotation = 2.0 if (self.memory % 4 < 2) else -2.0
        else:
            rotation = 1.5   # Default escape turn
            
        return translation, rotation

    def aggressive_explorer(self, sensor_to_wall, sensor_to_robot, enemy_detected):
        """
        Fast, aggressive exploration that pushes into enemy territory
        """
        translation = 1.0
        rotation = 0.0
        
        # Emergency wall avoidance
        if sensor_to_wall[sensor_front] < 0.25:
            translation = 0.3
            rotation = 1.8 if sensor_to_wall[sensor_left] > sensor_to_wall[sensor_right] else -1.8
        # Push toward enemies
        elif enemy_detected:
            # Calculate direction to nearest enemy
            enemy_weights = [0, -0.7, -1.2, -1.8, 0, 1.8, 1.2, 0.7]
            rotation = sum(enemy_weights[i] * (1.0 - sensor_to_robot[i]) 
                          for i in range(8) if sensor_to_robot[i] < 1.0) * 0.5
            translation = 1.0
        # Braitenberg exploration with forward bias
        else:
            rotation = (0.8 * sensor_to_wall[sensor_front_left] - 
                       0.8 * sensor_to_wall[sensor_front_right] +
                       0.4 * sensor_to_wall[sensor_left] - 
                       0.4 * sensor_to_wall[sensor_right])
            
            # Add periodic variation to avoid loops
            if self.iteration % 80 < 40:
                rotation += 0.2
            else:
                rotation -= 0.2
                
            translation = 1.0
        
        return translation, rotation

    def wall_follower_adaptive(self, sensor_to_wall, sensor_to_robot, enemy_detected, hand="right"):
        """
        Improved wall following that doesn't get stuck in corners
        """
        translation = 1.0
        rotation = 0.0
        
        # Choose which sensors to use based on hand preference
        if hand == "right":
            main_sensor = sensor_right
            front_main = sensor_front_right
            opposite_sensor = sensor_left
            turn_bias = 1.0  # Positive = turn right
        else:
            main_sensor = sensor_left
            front_main = sensor_front_left
            opposite_sensor = sensor_right
            turn_bias = -1.0  # Negative = turn left
        
        main_dist = sensor_to_wall[main_sensor]
        front_main_dist = sensor_to_wall[front_main]
        front_dist = sensor_to_wall[sensor_front]
        
        # CRITICAL: Detect corner/dead-end situation
        in_corner = (front_dist < 0.4 and main_dist < 0.4)
        
        if in_corner:
            # In a corner - turn away aggressively
            translation = 0.3
            rotation = -turn_bias * 2.0  # Turn AWAY from followed wall
        elif front_dist < 0.3:
            # Wall directly ahead - turn away from followed wall
            translation = 0.4
            rotation = -turn_bias * 1.5
        elif enemy_detected and sensor_to_robot[sensor_front] < 0.6:
            # Enemy ahead - push through or evade
            translation = 0.9
            rotation = 0.4 * (sensor_to_robot[sensor_left] - sensor_to_robot[sensor_right])
        elif main_dist > 0.9 and front_main_dist > 0.9:
            # Lost the wall - turn to find it
            translation = 1.0
            rotation = turn_bias * 1.0
        elif main_dist < 0.3:
            # Too close to wall - turn away
            translation = 0.8
            rotation = -turn_bias * 0.7
        elif front_main_dist < 0.4:
            # Front corner approaching - prepare to turn
            translation = 0.7
            rotation = -turn_bias * 0.5
        else:
            # Normal wall following - maintain distance
            target_distance = 0.5
            distance_error = main_dist - target_distance
            
            translation = 1.0
            rotation = turn_bias * distance_error * 0.6
            
            # Fine-tune with front sensor
            if front_dist < 0.7:
                rotation -= turn_bias * 0.3
        
        return translation, rotation

    def territory_denier(self, sensor_to_wall, sensor_to_robot, enemy_detected, teammate_detected):
        """
        Focuses on denying territory to enemies - paints over their tiles
        """
        translation = 1.0
        rotation = 0.0
        
        # Emergency avoidance
        if sensor_to_wall[sensor_front] < 0.25:
            translation = 0.3
            rotation = 1.5 if sensor_to_wall[sensor_left] > sensor_to_wall[sensor_right] else -1.5
        # Avoid teammates to spread out
        elif teammate_detected and sensor_to_robot[sensor_front] < 0.5:
            translation = 0.7
            # Turn away from teammate
            rotation = -1.2 if sensor_to_robot[sensor_left] < sensor_to_robot[sensor_right] else 1.2
        # Chase enemies aggressively
        elif enemy_detected:
            # Calculate weighted direction to enemies
            enemy_rotation = 0.0
            for i in range(8):
                if sensor_to_robot[i] < 0.9:
                    angle_weights = [0, -0.8, -1.3, -1.8, 2.5, 1.8, 1.3, 0.8]
                    enemy_rotation += angle_weights[i] * (1.0 - sensor_to_robot[i])
            
            translation = 1.0
            rotation = enemy_rotation * 0.4
        # Random exploration with coverage pattern
        else:
            rotation = (0.7 * sensor_to_wall[sensor_front_left] - 
                       0.7 * sensor_to_wall[sensor_front_right] +
                       0.3 * sensor_to_wall[sensor_left] - 
                       0.3 * sensor_to_wall[sensor_right])
            
            # Add circular pattern based on iteration
            pattern_phase = (self.iteration % 200) / 200.0 * 6.28  # 0 to 2π
            rotation += 0.3 * (1.0 if pattern_phase < 3.14 else -1.0)
            
            translation = 1.0
        
        return translation, rotation
