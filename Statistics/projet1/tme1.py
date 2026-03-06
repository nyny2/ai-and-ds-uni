#Léna Husse 21212867
#Nehir Yüksekkaya 21307751

import numpy as np
from collections import defaultdict
from reversi import Reversi, play_game

class AgentRandom:

    def __init__(self, board):
        """
            Attribue un plateau de jeu au joueur
        """
        self.board=board
    
    def play(self, player):
        moves=self.board.valid_moves(player)
        if not moves : 
            return (-1,-1)
        rdm=np.random.randint(0,len(moves))
        return moves[rdm]


    def count_moves_mc(self, nb, size, nb_simu):
        dico = defaultdict(list)

        for i in range(nb_simu):
            board = Reversi(size)
            player_1 = AgentRandom(board)
            player_2 = AgentRandom(board)
            cur_player = 1
            cpt = 0

            while cpt < nb and not board.game_over():
                cpt += 1
                moves = board.valid_moves(cur_player)
                dico[cpt].append(len(moves))

                if cur_player == 1:
                    mouv_suiv = player_1.play(cur_player)
                else:
                    mouv_suiv = player_2.play(cur_player) 

                x, y = mouv_suiv
                board.make_move(x, y, cur_player)
                cur_player *= -1

        # On cherche les moyennes de coups possibles pour chaque coup
        result_moy = {}
        for i in range(1, nb+1):
            if i in dico:
                result_moy[i] = np.mean(dico[i])
            else:
                result_moy[i] = 0

        return result_moy


    def count_config_mc(self, nb, size, nb_simu):

        configs = defaultdict(set)

        for _ in range(nb_simu):
            board = Reversi(size)
            player_1 = AgentRandom(board)
            player_2 = AgentRandom(board)
            cur_player = 1
            cpt = 0

            while cpt < nb and not board.game_over():
                cpt += 1
                bits_1, bits_2 = board.board_to_int()
                configs[cpt].add((bits_1, bits_2))

                if cur_player == 1:
                    move = player_1.play(cur_player)
                else:
                    move = player_2.play(cur_player)

                if move != (-1, -1):
                    board.make_move(*move, cur_player)

                cur_player *= -1

        return {i: len(configs[i]) for i in range(1, nb+1)}
    
    def count_moves(self, nb, size):
        from collections import defaultdict
        counts = defaultdict(list)

        initial = Reversi(size)
        queue = [(initial, 1, 0)]

        while queue:
            board, player, coups_joues = queue.pop()
            if coups_joues >= nb or board.game_over():
                continue

            moves = board.valid_moves(player)
            counts[coups_joues + 1].append(len(moves))

            for move in moves:
                new_board = board.copy()
                new_board.make_move(move[0], move[1], player)
                queue.append((new_board, -player, coups_joues + 1))

        return {i: np.mean(vals) for i, vals in counts.items()}
    
    def count_config(self, nb, size):
        from collections import defaultdict
        configs_dict = defaultdict(set)

        initial = Reversi(size)
        queue = [(initial, 1, 0)]

        while queue:
            board, player, coups_joues = queue.pop()
            if coups_joues >= nb or board.game_over():
                continue

            moves = board.valid_moves(player)
            for move in moves:
                new_board = board.copy()
                new_board.make_move(move[0], move[1], player)

                conf = new_board.board_to_int()
                configs_dict[coups_joues + 1].add(conf)

                queue.append((new_board, -player, coups_joues + 1))

        return {i: len(configs) for i, configs in configs_dict.items()}

                    