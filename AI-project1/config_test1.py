# Configuration file.

import arenas

# general -- first three parameters can be overwritten with command-line arguments (cf. "python tetracomposibot.py --help")

display_mode = 0
arena = 1
position = False 
max_iterations = 1000 #401*500

# affichage

display_welcome_message = False
verbose_minimal_progress = True # display iterations
display_robot_stats = False
display_team_stats = False
display_tournament_results = False
display_time_stats = True

# initialization : create and place robots at initial positions (returns a list containing the robots)

import robot_subsomption, robot_wanderer, robot_braitenberg_avoider

def initialize_robots(arena_size=-1, particle_box=-1): # particle_box: size of the robot enclosed in a square
    x_center = arena_size // 2 - particle_box / 2
    y_center = arena_size // 2 - particle_box / 2
    robots = []
    robots.append(robot_subsomption.Robot_player(x_center-7, y_center+40, 45, name="", team="B"))
    robots.append(robot_wanderer.Robot_player(x_center-40, y_center-30, 90, name="", team="B"))
    robots.append(robot_braitenberg_avoider.Robot_player(x_center, y_center, 0, name="", team="A"))
    robots.append(robot_subsomption.Robot_player(x_center+35, y_center-5, 180, name="", team="A"))

    return robots
