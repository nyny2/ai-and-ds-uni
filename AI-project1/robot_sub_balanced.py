from robot import * 

nb_robots = 0
debug = False

class Robot_player(Robot):
    """
    Balanced strategy: smooth turns, constant movement, no oscillation
    """

    team_name = "Smooth Operators"
    robot_id = -1
    iteration = 0
    memory = 0  # Stuck counter

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # Separate sensors by type
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
        
        # ALWAYS MOVE FORWARD - this is critical
        translation = 1.0
        rotation = 0.0
        
        # Detect stuck situation (surrounded by walls)
        walls_very_close = sum(1 for s in sensor_to_wall if s < 0.3)
        
        if walls_very_close >= 4:
            self.memory = min(self.memory + 1, 100)
        else:
            self.memory = max(self.memory - 1, 0)
        
        # EMERGENCY ESCAPE: stuck for too long
        if self.memory > 25:
            # Do a complete 180-degree turn while moving
            translation = 0.6
            rotation = 2.5 if (self.robot_id % 2 == 0) else -2.5
            
            # Reset counter when done turning
            if self.memory > 40:
                self.memory = 0
            
            return translation, rotation, False
        
        # Get front and side distances
        front = sensor_to_wall[sensor_front]
        front_left = sensor_to_wall[sensor_front_left]
        front_right = sensor_to_wall[sensor_front_right]
        left = sensor_to_wall[sensor_left]
        right = sensor_to_wall[sensor_right]
        
        # Calculate how much space is on each side
        left_space = (front_left + left) / 2.0
        right_space = (front_right + right) / 2.0
        
        # DECISION LOGIC - no oscillation
        
        # CRITICAL ZONE: wall very close in front
        if front < 0.25:
            # Must turn NOW - pick a direction and commit
            translation = 0.8  # Slow down a bit but keep moving
            
            # Pick the more open side and turn HARD
            if left_space > right_space + 0.15:  # Left is clearly better
                rotation = -1.5
            elif right_space > left_space + 0.15:  # Right is clearly better
                rotation = 1.5
            else:  # Equal - use robot ID to avoid all choosing same direction
                rotation = 1.5 if (self.robot_id % 2 == 0) else -1.5
        
        # WARNING ZONE: wall approaching
        elif front < 0.5:
            # Start turning gently
            translation = 1.0
            
            if left_space > right_space + 0.1:
                rotation = -0.8
            elif right_space > left_space + 0.1:
                rotation = 0.8
            else:
                rotation = 0.8 if (self.robot_id % 2 == 0) else -0.8
        
        # SAFE ZONE: path is clear
        else:
            # Full speed ahead with gentle steering
            translation = 1.0
            
            # Smooth Braitenberg-style steering
            rotation = (front_left - front_right) * 0.5 + (left - right) * 0.2
            
            # Add robot-specific exploration pattern to spread out
            if self.robot_id == 0:
                rotation += 0.15  # Slight right tendency
            elif self.robot_id == 1:
                rotation -= 0.15  # Slight left tendency
            elif self.robot_id == 2:
                # Oscillate slowly
                rotation += 0.2 if (self.iteration % 120 < 60) else -0.2
            else:
                # Counter-oscillate
                rotation -= 0.2 if (self.iteration % 120 < 60) else 0.2
        
        # ENEMY INTERACTION: if enemy robot in front, push them
        if sensor_to_robot[sensor_front] < 0.6:
            # Keep going forward to push them
            translation = 1.0
            # Slight steering to track them
            if sensor_to_robot[sensor_front_left] < sensor_to_robot[sensor_front_right]:
                rotation += -0.3
            elif sensor_to_robot[sensor_front_right] < sensor_to_robot[sensor_front_left]:
                rotation += 0.3
        
        # TEAMMATE AVOIDANCE: if teammate very close, turn away
        if sensor_to_robot[sensor_front] < 0.4:
            if sensor_team[sensor_front] == self.team_name:
                # It's a teammate - turn away to spread out
                rotation += 1.0 if (self.robot_id % 2 == 0) else -1.0
        
        # Clamp rotation to prevent crazy spinning
        rotation = max(-2.0, min(2.0, rotation))
        
        self.iteration += 1
        return translation, rotation, False
