from robot import * 

nb_robots = 0
debug = True

class Robot_player(Robot):

    team_name = "Sub"
    robot_id = -1
    iteration = 0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)
    
    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        sensor_to_wall = []
        sensor_to_robot = []
        for i in range (0,8):
            if  sensor_view[i] == 1:
                sensor_to_wall.append( sensors[i] )
                sensor_to_robot.append(1.0)
            elif  sensor_view[i] == 2:
                sensor_to_wall.append( 1.0 )
                sensor_to_robot.append( sensors[i] )
            else:
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)
        

        translation = sensor_to_wall[sensor_front] * \
                      sensor_to_wall[sensor_front_left] * \
                      sensor_to_wall[sensor_front_right] * 1.4

        def enemy(i):
            return sensor_view[i] == 2 and sensor_team[i] != self.team

        def r(i):
            return 1.0 - sensor_to_robot[i]

        # ---------- ENEMY PRESENT ----------
        if (enemy(sensor_front) or enemy(sensor_front_left) or enemy(sensor_front_right) or
            enemy(sensor_left) or enemy(sensor_right) or
            enemy(sensor_rear_left) or enemy(sensor_rear_right) or enemy(sensor_rear)):

            rotation = (
                r(sensor_left) * 2.0 +
                r(sensor_front_left) * 1.5 +
                r(sensor_front_right) * -1.5 +
                r(sensor_right) * -2.0
            )

        # ---------- WALL AVOID ----------
        else:
            rotation = (
                (1 - sensor_to_wall[sensor_front]) * 2.5 +
                (1 - sensor_to_wall[sensor_front_left]) * 2.0 +
                (1 - sensor_to_wall[sensor_front_right]) * -2.0 +
                (1 - sensor_to_wall[sensor_left]) * 0.8 +
                (1 - sensor_to_wall[sensor_right]) * -0.8
            )

        if self.robot_id % 2 == 1:
            rotation += 0.25

        return translation, rotation, False
