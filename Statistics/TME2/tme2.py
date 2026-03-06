#Léna Husse 21212867
#Nehir Yüksekkaya 21307751

import numpy as np
from collections import defaultdict
from reversi import Reversi, play_game
import tme1

def get_mask_one(x,y):
    """
        Renvoie le masque pour un coup en (x,y)
    """
    board = Reversi()
    n = board.size
    res = 0
    
    if(0<=x<n and 0<=y<n):
        res |= 1 << (x * n + y)
    
    return res

def get_mask(I):
    """
        Renvoie le masque pour une configuration I
    """
    res = 0
    for i in range(len(I)):
        x,y = I[i]
        res += get_mask_one(x,y)
    
    return res

def rollout(game, turn=1, nb_moves=100):

    player = tme1.AgentRandom(game)

    for i in range(nb_moves):
        move = player.play(turn)
        x, y = move
        game.make_move(x, y, turn)
        turn *= -1
    
    res = game.board_to_int()
    return res

def simu_mc(game, turn=1, nb_simu=10000, nb_moves=100):
    list_res = []
    for i in range(nb_simu):
        game_copy = game.copy()
        res = rollout(game_copy, turn, nb_moves)
        list_res.append(res)

    return list_res


def estime_coins(simus, nb_coins):

    coin_left_up = (0,0)
    coin_left_down = (0,7)  
    coin_right_up = (7,0)
    coin_right_down = (7,7)
    liste_coins = [coin_left_down, coin_left_up, coin_right_down, coin_right_up]

    list_mask = get_mask(liste_coins)

    lose = 0
    res = 0

    for nb_simu in range(len(simus)):
        points_1 = (simus[nb_simu][0]).bit_count()
        points_2 = (simus[nb_simu][1]).bit_count()
        coins1 = (list_mask & simus[nb_simu][0]).bit_count()
        coins2 = (list_mask & simus[nb_simu][1]).bit_count()
        if points_1 > points_2 and coins1==nb_coins: 
            res+=1
        elif points_1 < points_2 and coins1==nb_coins:
            lose +=1
        elif points_2 < points_1 and coins2==nb_coins:
            lose +=1
        elif points_2 >points_1 and coins2==nb_coins:
            res +=1

    

    return res/(res+lose)

def cdt_one_corner(game):
    coin_left_up = (0,0)
    coin_left_down = (0,7)  
    coin_right_up = (7,0)
    coin_right_down = (7,7)
    liste_coins = [coin_left_down, coin_left_up, coin_right_down, coin_right_up]

    list_mask = get_mask(liste_coins)

    simu = simu_mc(game)
    for nb_simu in range(len(simu)):
        coins1 = (list_mask & simu[nb_simu][0]).bit_count()
        coins2 = (list_mask & simu[nb_simu][1]).bit_count()

    if coins1==1 and coins2==0:
        return True
    else : 
        return False
    
def play_until(game, cdt, turn=1):
    while not cdt(game):
        player = tme1.AgentRandom(game)
        move = player.play(turn)
        x, y = move
        game.make_move(x, y, turn)
        turn *= -1
        if game.game_over():
            return -1
    return game

def find_game(cdt):
    game = Reversi()
    game = play_until(game, cdt)
    if game == -1:
        game = find_game(cdt)
    return game

def compute_win_cdt(cdt, nb_games=100, nb_simu=100):
    res = 0
    for i in range(nb_games):
        game = find_game(cdt)
        simu = simu_mc(game, nb_simu=nb_simu)
        if estime_coins(simu, 1) > 0.5:
            res += 1
    return res/nb_games
    