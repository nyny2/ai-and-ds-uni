import numpy as np

class Reversi:
    def __init__(self, size=8):
        """ 
            Implémentation simple du jeu de reversi (Othello) : https://fr.wikipedia.org/wiki/Othello_(jeu). Le plateau est codé par un tableau numpy, les case vides sont encodées par des 0, les cases occupées par les pions du premier joueur par 1, et celles du deuxième joueur -1.
            :size: taille du plateau
        """
        self.size = size
        # Direction pour chercher les coups possibles (diagonales, verticales, horizontales)
        self.dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        self.reset()

    def reset(self):
        """
            Initialisation d'un jeu
        """
        # Position initiale
        self.board = np.zeros((self.size, self.size),dtype=int)
        mid = self.size // 2
        self.board[mid-1][mid-1] = 1
        self.board[mid][mid] = 1
        self.board[mid-1][mid] = -1
        self.board[mid][mid-1] = -1
        
    def print_board(self):
        """
            Affichage du plateau
        """
        print("  " + " ".join(map(str, range(self.size))))
        for i in range(self.size):
            row = ["X.O"[self.board[i,j]+1] for j in range(self.size)]
            print(f"{i} " + " ".join(row))
        

    def on_board(self, x, y):
        """
            Test si les coordonnées sont dans le plateau
        """
        return 0 <= x < self.size and 0 <= y < self.size

    def valid_moves(self,player):
        """
            Renvoie la liste des coups valides pour un joueur (1 ou -1)
        """
        moves = []
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x,y] == 0 and self.can_flip(x,y,player):
                    moves.append((x,y))
        return moves

    def can_flip(self, x, y,player):
        """
            Teste si le coup est valide pour un joueur (1 ou -1)
        """
        for dx, dy in self.dirs:
            nx, ny = x+dx, y+dy
            found_opponent = False
            while self.on_board(nx, ny) and self.board[nx, ny] == -player:
                nx += dx
                ny += dy
                found_opponent = True
            if found_opponent and self.on_board(nx, ny) and self.board[nx, ny] == player:
                return True
        return False

    def make_move(self, x, y, player):
        """ 
            Joue le coup pour le joueur
        """
        if (x<0) or (y<0):
            return
        self.board[x,y] = player
        for dx, dy in self.dirs:
            nx, ny = x+dx, y+dy
            to_flip = []
            while self.on_board(nx, ny) and self.board[nx, ny] == -player:
                to_flip.append((nx, ny))
                nx += dx
                ny += dy
            if to_flip and self.on_board(nx, ny) and self.board[nx, ny] == player:
                for fx, fy in to_flip:
                    self.board[fx, fy] = player
        
    def game_over(self):
        """
            Teste si le jeu est fini
        """
        return not self.valid_moves(1) and not self.valid_moves(-1)

    def score(self):
        """
            Renvoie le score
        """
        return np.sum(self.board)
    
    def copy(self):
        """
            Réalise le clone de la partie
        """
        reversi = Reversi(self.size)
        reversi.board = np.copy(self.board)
        return reversi
    
    def board_to_int(self):
        """
            Renvoie la représentation sous la forme d'un couple d'entier de la configuration d'un plateau
        """
        n = len(self.board)
        bits_1 = 0
        bits_2 = 0
        for i in range(n):
            for j in range(n):
                if self.board[i][j]==1:
                    bits_1 |= 1 << (i * n + j)
                elif self.board[i][j]==-1:
                    bits_2 |= 1 << (i*n+j)
        return bits_1, bits_2
    
    def bitboards_to_board(self,player1, player2):
        """
            Reconstitue un plateau à partir de la représentation en entier
        """
        self.reset()
        for i in range(self.size*self.size):
            x, y = divmod(i, self.size)
            if player1 & (1 << i):
                self.board[x][y] = 1
            elif player2 & (1 << i):
                self.board[x][y] = -1
    def nb_moves(self):
        """
            Renvoie le nombre de coups joués
        """
        return np.abs(self.board).sum()-4
    


def play_game(board,player_1,player_2,display=False):
    players = {1:player_1,-1:player_2}
    cur_player = 1
    board.reset()
    while not board.game_over():
        board.make_move(*players[cur_player].play(cur_player),cur_player)
        cur_player *= -1
        if display: board.print_board()
    return board.score()

