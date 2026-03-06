from robot import * 

nb_robots = 0
debug = False

class Robot_player(Robot):
    """
    ULTRA SIMPLE: Never stop moving, aggressive turning
    """

    team_name = "Never Stop"
    robot_id = -1
    iteration = 0
    memory = 0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # Separate sensors
        sensor_to_wall = []
        for i in range(8):
            if sensor_view[i] == 1:
                sensor_to_wall.append(sensors[i])
            else:
                sensor_to_wall.append(1.0)
        
        # SIMPLE RULE: Always move forward
        translation = 1.0
        rotation = 0.0
        
        # Count walls that are close
        close_walls = sum(1 for s in sensor_to_wall[:4] if s < 0.4)  # Only front half
        
        # Increment memory when stuck
        if close_walls >= 3:
            self.memory += 1
        else:
            self.memory = max(0, self.memory - 1)
        
        # EMERGENCY: stuck for 30+ iterations
        if self.memory >= 30:
            # Aggressive escape
            translation = 0.8
            rotation = 3.0 if (self.robot_id % 2 == 0) else -3.0
            # Reset memory
            if self.memory >= 50:
                self.memory = 0
        
        # Front is blocked - MUST turn
        elif sensor_to_wall[sensor_front] < 0.35:
            translation = 0.7
            # Turn toward more open side
            left_space = sensor_to_wall[sensor_left] + sensor_to_wall[sensor_front_left]
            right_space = sensor_to_wall[sensor_right] + sensor_to_wall[sensor_front_right]
            
            if left_space > right_space + 0.3:
                rotation = -2.0  # Turn left
            elif right_space > left_space + 0.3:
                rotation = 2.0   # Turn right
            else:
                # Equal - use robot ID
                rotation = 2.0 if (self.robot_id % 2 == 0) else -2.0
        
        # Getting close to wall ahead
        elif sensor_to_wall[sensor_front] < 0.6:
            translation = 1.0
            # Gentle turn toward more open side
            left_space = sensor_to_wall[sensor_front_left] + sensor_to_wall[sensor_left]
            right_space = sensor_to_wall[sensor_front_right] + sensor_to_wall[sensor_right]
            
            rotation = 1.0 if (right_space > left_space) else -1.0
        
        # Free space - explore
        else:
            translation = 1.0
            
            # Simple Braitenberg
            rotation = (sensor_to_wall[sensor_front_left] * 0.6 - 
                       sensor_to_wall[sensor_front_right] * 0.6 +
                       sensor_to_wall[sensor_left] * 0.3 - 
                       sensor_to_wall[sensor_right] * 0.3)
            
            # Add robot-specific bias to spread out
            if self.robot_id == 0:
                rotation += 0.2
            elif self.robot_id == 1:
                rotation -= 0.2
            elif self.robot_id == 2:
                rotation += 0.15 if (self.iteration % 80 < 40) else -0.15
            else:
                rotation -= 0.15 if (self.iteration % 80 < 40) else 0.15
        
        self.iteration += 1
        return translation, rotation, False
