from robot import * 

nb_robots = 0
debug = False

class Robot_player(Robot):
    """
    Simple, robust strategy: ALWAYS KEEP MOVING
    No complex wall following - just explore and avoid obstacles
    """

    team_name = "Explorers"
    robot_id = -1
    iteration = 0
    memory = 0  # Used as: stuck counter in bits 0-7, direction preference in bit 8

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        Simple priority system:
        1. If too many walls close → FORCE turn
        2. If front blocked → turn toward most open side
        3. Otherwise → explore with slight bias
        """
        
        # Separate sensors
        sensor_to_wall = []
        sensor_to_robot = []
        
        for i in range(8):
            if sensor_view[i] == 1:  # Wall
                sensor_to_wall.append(sensors[i])
                sensor_to_robot.append(1.0)
            elif sensor_view[i] == 2:  # Robot
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(sensors[i])
            else:  # Empty
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)

        # Count close walls
        very_close_walls = sum(1 for s in sensor_to_wall if s < 0.35)
        
        # Update stuck counter (lower 8 bits of memory)
        stuck_counter = self.memory & 0xFF
        if very_close_walls >= 4:  # Surrounded
            stuck_counter = min(stuck_counter + 3, 255)
        else:
            stuck_counter = max(stuck_counter - 1, 0)
        
        # Extract direction preference (bit 8)
        prefer_right = (self.memory & 0x100) != 0
        
        # Update memory
        self.memory = stuck_counter | (0x100 if prefer_right else 0)
        
        # FORCED ESCAPE if stuck too long
        if stuck_counter > 40:
            translation = 0.5  # Slow but steady
            rotation = 2.5 if prefer_right else -2.5  # VERY sharp turn
            # Flip preference for next time
            self.memory = 0 | (0 if prefer_right else 0x100)
            return translation, rotation, False
        
        # Calculate openness in each direction
        front_open = sensor_to_wall[sensor_front]
        left_open = (sensor_to_wall[sensor_left] + sensor_to_wall[sensor_front_left]) / 2.0
        right_open = (sensor_to_wall[sensor_right] + sensor_to_wall[sensor_front_right]) / 2.0
        
        # ALWAYS move forward
        translation = 1.0
        
        # Decision tree for rotation
        if sensor_to_wall[sensor_front] < 0.3:
            # WALL DIRECTLY AHEAD - must turn
            if left_open > right_open:
                rotation = -1.8  # Turn left strongly
            elif right_open > left_open:
                rotation = 1.8   # Turn right strongly
            else:
                # Both equal - use robot specialization
                rotation = self.get_turn_bias() * 1.8
                
        elif sensor_to_wall[sensor_front] < 0.6:
            # Something ahead but not immediate - start turning
            if left_open > right_open:
                rotation = -1.2
            elif right_open > left_open:
                rotation = 1.2
            else:
                rotation = self.get_turn_bias() * 1.2
                
        else:
            # Path is clear - explore with gentle steering
            # Use Braitenberg-style but simpler
            rotation = 0.5 * (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right])
            
            # Add robot-specific exploration bias
            rotation += self.get_exploration_bias()
            
            # Add small random element
            if self.iteration % 50 == 0:
                rotation += (random.random() - 0.5) * 0.4
        
        # Enemy interaction - push them
        if sensor_to_robot[sensor_front] < 0.7:
            # Enemy in front - try to push them
            translation = 1.0
            # Slight correction to face them
            for i in range(8):
                if sensor_to_robot[i] < 0.7 and sensor_team[i] != self.team_name:
                    angle_correction = [0, -0.3, -0.6, -0.9, 0, 0.9, 0.6, 0.3][i]
                    rotation += angle_correction * 0.3
                    break
        
        self.iteration += 1
        return translation, rotation, False
    
    def get_turn_bias(self):
        """
        Each robot has a preferred turn direction when stuck
        """
        if self.robot_id == 0:
            return 1.0   # Prefer right
        elif self.robot_id == 1:
            return -1.0  # Prefer left
        elif self.robot_id == 2:
            return 1.0   # Prefer right
        else:
            return -1.0  # Prefer left
    
    def get_exploration_bias(self):
        """
        Each robot has a different exploration pattern
        """
        if self.robot_id == 0:
            # Slightly right bias
            return 0.15
        elif self.robot_id == 1:
            # Slightly left bias
            return -0.15
        elif self.robot_id == 2:
            # Oscillating pattern
            return 0.2 if (self.iteration % 100 < 50) else -0.2
        else:
            # Counter-oscillating pattern
            return -0.2 if (self.iteration % 100 < 50) else 0.2
