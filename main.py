import pygame
import random
import time
import sys
import numpy as np
import math
from pygame.draw import rect
from pygame.constants import MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP


##################### CLASES #######################
#Nodos frontera
class Node():
    def __init__(self, parent, state, action):
        self.parent = parent #nodo
        self.state = state #tupla
        self.action = action #tupla

#Profundidad
class StackFrontier():
    def __init__(self):
        self.frontier = []
        
    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception('Frontera ya vacia')
        else:
            node = self.frontier[-1]
            self.frontier.remove(node)
            return [node]

#Amplitud
class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception('Frontera ya vacia')
        else:
            node = self.frontier[0] 
            self.frontier.remove(node)
            return [node]

#A*
class ManhattanFrontier(StackFrontier):
    def remove(self, cost):
        if self.empty():
            raise Exception('Frontera ya vacia')
        else:
            best_neighbor = set()
            best_neighbor_cost = 0
            for node in self.frontier:
                x,y = node.state
                absolute_cost = cost + abs(x-9) + abs(y-9)
                if len(best_neighbor) == 0 or absolute_cost < best_neighbor_cost:
                    best_neighbor = {node}
                    best_neighbor_cost = absolute_cost
                elif absolute_cost == best_neighbor_cost:
                    best_neighbor.add(node)

            for neighbor in best_neighbor:
                self.frontier.remove(neighbor)

            return best_neighbor

#Primero el mejor
class BestFirstFrontier(StackFrontier):
    def remove(self, cost):
        if self.empty():
            raise Exception('Frontera ya vacia')
        else:
            pass

#Objeto/Laberinto
class Maze():
    def __init__(self, board, algorithm, boardStart, boardFinish):
        
        indexStart = []
        indexFinish = []

        index1Start = -1
        for i in np.array(boardStart):
            index1Start += 1
            index2Start = -1
            for j in np.array(i):
                index2Start += 1
                if j:
                    indexStart.append(index1Start)
                    indexStart.append(index2Start)

        index1Finish = -1
        for k in np.array(boardFinish):
            index1Finish += 1
            index2Finish = -1
            for l in np.array(k):
                index2Finish += 1
                if l:
                    indexFinish.append(index1Finish)
                    indexFinish.append(index2Finish)

        print(f'Inicio: {indexStart[0]}, fin: {indexStart[1]}')
        print(f'Inicio2: {indexFinish[0]}, fin2: {indexFinish[1]}')
        
        self.board = board
        self.start = (indexStart[0], indexStart[1])
        self.goal = (indexFinish[0], indexFinish[1])
        self.algorithm = algorithm
        self.walls = []
        self.height = self.width = len(self.board)

        for i in range(0, 9):
            row = []
            for j in range(0, 9):
                if self.board[i][j] and (i, j) not in (self.start, self.goal):
                    row.append(True)
                else:
                    row.append(False)
            self.walls.append(row)

    def find_neighbors(self, state):

        self.neighbors = []

        x,y = state

        possible_actions = [
            ('down', (x, y+1)),
            ('right', (x+1, y)),
            ('up', (x, y-1)),
            ('left', (x-1, y))
        ]

        random.shuffle(possible_actions)

        for action, result in possible_actions:
            x, y = result
            try:
                if not self.walls[x][y] and (0 <= x < self.width) and (0 <= y < self.height):
                    self.neighbors.append((action, result))
            except IndexError:
                continue

        return self.neighbors

    def solve(self, show_steps):

        self.cost = 0
        
        self.cells = list() if show_steps else set()

        start = Node(parent = None, state = self.start, action = None)

        if self.algorithm == 1:
            frontier = StackFrontier() #Profundidad
        elif self.algorithm == 2:
            frontier = QueueFrontier() #Amplitud
        elif self.algorithm == 3:
            frontier = ManhattanFrontier() #A*
        elif self.algorithm == 4:
            frontier = BestFirstFrontier() #Primero el Mejor

        frontier.add(start)
        
        while True:
            if frontier.empty():
                return None

            self.cost += 1

            nodes = frontier.remove(self.cost) if self.algorithm == 3 else frontier.remove()

            for node in nodes:

                if self.goal == node.state:
                    moves = []
                    while node.parent != None:
                        moves.append(node.state)
                        node = node.parent
                    moves.reverse()
                    if show_steps:
                        return (self.cells, moves)
                    else:
                        return moves

                if show_steps and node.state not in self.cells:
                    self.cells.append(node.state)
                if not show_steps:
                    self.cells.add(node.state)


                for action, state in self.find_neighbors(node.state):
                    if not frontier.contains_state(self.goal) and state not in self.cells:
                        child = Node(parent = node, state = state, action = action)
                        frontier.add(child)

class Conecta3(object):

    def __init__(self):
        ###### INICIA CONECTA 3 ######
        #Colores del juego
        self.BLUE = (0,0,255)
        self.BLACK = (0,0,0)
        self.RED = (255,0,0)
        self.YELLOW = (255,255,0)
        #Tamaño del tablero
        self.ROW_COUNT = 3
        self.COLUMN_COUNT = 3
        #Identificadores(Saber turno)
        self.PLAYER = 0
        self.AI = 1
        #Identificadores(Para saber de quien es cada pieza)
        self.PLAYER_PIECE = 1
        self.AI_PIECE = 2
        #Usado para la IA(calculo y evaluación de movimientos) 
        self.WINDOW_LENGTH = 4
        self.EMPTY = 0

        #Flag para verificar si hubo un ganador
        winner = False

        board2 = self.create_board()
        self.print_board(board2)
        self.game_over = False

        pygame.init()

        self.SQUARESIZE = 120

        self.width = self.COLUMN_COUNT * self.SQUARESIZE
        self.height = (self.ROW_COUNT+1) * self.SQUARESIZE

        self.size = (self.width, self.height)
        self.RADIUS = int(self.SQUARESIZE/2 - 5)

        self.screen = pygame.display.set_mode(size)
        self.draw_board(board2)
        pygame.display.update()

        self.myfont = pygame.font.SysFont("monospace", 40)

        self.turn = random.randint(self.PLAYER, self.AI)

        while not self.game_over:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, self.BLACK, (0,0, self.width, self.SQUARESIZE))
                    posx = event.pos[0]
                    if self.turn == self.PLAYER:
                        pygame.draw.circle(screen, self.RED, (posx, int(self.SQUARESIZE/2)), self.RADIUS)
                        pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, self.BLACK, (0,0, self.width, self.SQUARESIZE))
                    
                    #Input del usuario
                    if self.turn == self.PLAYER:
                        posx = event.pos[0]
                        col = int(math.floor(posx/self.SQUARESIZE))  

                        if self.is_valid_location(board2,col):
                            row = self.get_next_open_row(board2, col)
                            self.drop_piece(board2, row, col, self.PLAYER_PIECE)

                            if self.winning_move(board2,self.PLAYER_PIECE):
                                label = self.myfont.render("Usuario Ganó", 1, self.BLUE)
                                screen.blit(label, (10,10))
                                self.game_over = True
                                winner = True

                            self.turn += 1
                            self.turn = self.turn % 2 

                            self.print_board(board2) 
                            self.draw_board(board2)

                            if self.game_over:
                                pygame.time.wait(3000)
                #Input de la IA   
                if self.turn == self.AI and not self.game_over:

                    #Aumentar Depth al minimax() para mayor dificultad
                    col, minimax_score = self.minimax(board2, 3, -math.inf, math.inf, True)

                    try: 
                        if self.is_valid_location(board2,col):
                        # pygame.time.wait(500)
                            row = self.get_next_open_row(board2, col)
                            self.drop_piece(board2, row, col, self.AI_PIECE)
                    except ValueError as ve:
                        label = self.myfont.render("Empate", 1, self.BLUE)
                        screen.blit(label, (10,10))
                        self.game_over = True
                        pygame.time.wait(3000)
                        
                    if self.winning_move(board2, self.AI_PIECE):
                        label = self.myfont.render("IA Ganó", 1, self.RED)
                        screen.blit(label, (10,10))
                        self.game_over = True
                        winner = True
                            

                    self.print_board(board2) 
                    self.draw_board(board2)

                    self.turn += 1
                    self.turn = self.turn % 2 

                    if self.game_over:
                        if winner == False:
                            label = self.myfont.render("Empate", 1, self.BLUE)
                            screen.blit(label, (10,10))
                            self.game_over = True
                        pygame.time.wait(3000)

    #Método de numpy para crear array de 2 dimensiones(Tablero)
    def create_board(self):
        board2 = np.zeros((self.ROW_COUNT,self.COLUMN_COUNT))
        return board2
    #Movimientos
    def drop_piece(self, board2, row, col, piece):
        board2[row][col] = piece
    #Valida si hay espacio para que "caiga" la pieza
    def is_valid_location(self, board2, col):
        return board2[self.ROW_COUNT-1][col] == 0

    def get_next_open_row(self, board2, col):
        for r in range(self.ROW_COUNT):
            if board2[r][col] == 0:
                return r

    def print_board(self, board2):
        print(np.flip(board2,0))

    def winning_move(self, board2, piece):
        #Verifica horizontal de 3
        for c in range(self.COLUMN_COUNT-2):
            for r in range(self.ROW_COUNT):
                if board2[r][c] == piece and board2[r][c+1] == piece and board2[r][c+2] == piece:
                    return True
        #Verifica vertical de 3
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT-2):
                if board2[r][c] == piece and board2[r+1][c] == piece and board2[r+2][c] == piece:
                    return True
        #Verifica las diagonales de 3
        for c in range(self.COLUMN_COUNT-2):
            for r in range(self.ROW_COUNT-2):
                if board2[r][c] == piece and board2[r+1][c+1] == piece and board2[r+2][c+2] == piece:
                    return True

        #Verifica diagonales invertidas de 3
        for c in range(self.COLUMN_COUNT-3):
            for r in range(3,self.ROW_COUNT):
                if board2[r][c] == piece and board2[r-1][c+1] == piece and board2[r-2][c+2] == piece:
                    return True

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = self.PLAYER_PIECE
        if piece == self.PLAYER_PIECE:
            opp_piece = self.AI_PIECE

        if window.count(piece) == 3:
            score += 100
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4

        return score 

    def score_position(self, board2, piece):
        score = 0
        #Da preferencia a movimientos en el centro del tablero(da mayor potencial de combinaciones)
        center_array = [int(i) for i in list(board2[:, self.COLUMN_COUNT//2])]
        center_count = center_array.count(piece)
        score += center_count * 4

        #Calcula puntaje horizontal
        
        for r in range(self.ROW_COUNT):
            row_array = [int(i) for i in list(board2[r,:])]
            for c in range(self.COLUMN_COUNT-3):
                window = row_array[c:c+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)
        
        ##Calcula puntaje Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [int(i) for i in list(board2[:,c])]
            for r in range(self.ROW_COUNT-3):
                window = col_array[r:r+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board2[r+i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board2[r+3-i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score

    def is_terminal_node(self, board2):
        return self.winning_move(board2, self.PLAYER_PIECE) or self.winning_move(board2, self.AI_PIECE) or len(self.get_valid_locations(board2)) == 0

    #Minimax
    def minimax(self, board2,depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations(board2)
        is_terminal = self.is_terminal_node(board2)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board2, self.AI_PIECE):
                    return (None, 100000000000)
                elif self.winning_move(board2, self.PLAYER_PIECE):
                    return (None, -10000000000)   
                else: #game over no more moves  
                    return (None, 0)
            else: #depth is zero
                return (None, self.score_position(board2, self.AI_PIECE))

        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board2, col)
                b_copy = board2.copy()
                self.drop_piece(b_copy, row, col, self.AI_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else: #minimizing al oponente
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board2, col)
                b_copy = board2.copy()
                self.drop_piece(board2, row, col, self.PLAYER_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
        



    def get_valid_locations(self, board2):
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(board2, col):
                valid_locations.append(col)
        return valid_locations


    def pick_best_move(self, board2, piece):
        valid_locations = self.get_valid_locations(board2)
        best_score = 0
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = self.get_next_open_row(board2, col)
            temp_board = board2.copy()
            self.drop_piece(temp_board, row, col, piece)
            score = self.score_position(temp_board, piece)
            #Actualizacion de puntajes despues de cada turno
            if score > best_score:
                best_score = score
                best_col = col
                
        return best_col


    def draw_board(self, board2):
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT):
                pygame.draw.rect(screen, self.BLUE, (c*self.SQUARESIZE, r*self.SQUARESIZE+self.SQUARESIZE, self.SQUARESIZE, self.SQUARESIZE))
                pygame.draw.circle(screen, BLACK, (int(c*self.SQUARESIZE+self.SQUARESIZE/2), int(r*self.SQUARESIZE+self.SQUARESIZE+self.SQUARESIZE/2)), self.RADIUS)
        
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT):		
                if board2[r][c] == self.PLAYER_PIECE:
                    pygame.draw.circle(screen, RED, (int(c*self.SQUARESIZE+self.SQUARESIZE/2), self.height-int(r*self.SQUARESIZE+self.SQUARESIZE/2)), self.RADIUS)
                elif board2[r][c] == self.AI_PIECE: 
                    pygame.draw.circle(screen, YELLOW, (int(c*self.SQUARESIZE+self.SQUARESIZE/2), self.height-int(r*self.SQUARESIZE+self.SQUARESIZE/2)), self.RADIUS)
        pygame.display.update()

#Menu(Dropdown) de Algoritmos de Búsqueda
class DropDown():

    def __init__(self, x, y, w, h, color, highlight_color, font, options, selected = 0):
        self.color           = color
        self.highlight_color = highlight_color
        self.rect            = pygame.Rect(x, y, w, h)
        self.font            = font
        self.options         = options
        self.selected        = selected
        self.draw_menu       = False
        self.menu_active     = False
        self.active_option   = -1
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surface, (0 ,0 , 0), self.rect, 2)
        msg = self.font.render(self.options[self.selected], 1, (255, 255, 255) if self.menu_active else (0, 0, 0))
        surface.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                if i == 0:
                    pygame.draw.rect(surface, (200, 200, 200), rect)
                else:
                    pygame.draw.rect(surface, self.highlight_color if i == self.active_option else self.color, rect)

                msg = self.font.render(text, 1, (0, 0, 0))
                surface.blit(msg, msg.get_rect(center = rect.center))
            outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * (len(self.options)))
            pygame.draw.rect(surface, (0, 0, 0), outer_rect, 2) 
        else:
            for i in range(len(self.options)):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surface, (0, 0, 0), rect)

    def update(self, events):
        mpos             = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                if i != 0:
                    self.active_option = i
                    break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option

        return -1

#Opción de mostrar animación completa o no(Checkbox)
class Checkbox():
    def __init__(self, rect, text, font):
        self.rect         = rect
        self.fill_rect    = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width // 1.6, self.rect.height // 1.6)
        self.selected     = False
        self.hovered      = False
        self.font         = font
        self.filled_color = (0, 0, 0)
        self.empty_color  = (255, 255, 255)
        self.text         = text

    def draw(self, surface):
        pygame.draw.rect(surface, self.empty_color, self.rect)
        if self.hovered:
            pygame.draw.rect(surface, self.filled_color, self.fill_rect)
        if self.selected:
            pygame.draw.rect(surface, self.filled_color, self.fill_rect)
        msg = self.font.render(self.text, 1, (255, 255, 255))
        surface.blit(msg, (self.rect.x + 30, self.rect.y + 2.5))
        

    def update(self, events):
        mpos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mpos):
            self.hovered = True
        else:
            self.hovered = False

        for event in events:
            if self.rect.collidepoint(mpos):
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.selected = not self.selected
                    break

        return self.selected
        

################# Programa Principal #####################
size = (900, 600)
w, h = size

YELLOW = (255, 255, 0)
WHITE  = (255, 255, 255)
GREEN  = (0, 255, 0)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
ORANGE = (255 ,125 , 123)
PURPLE = (81, 61, 130)

pygame.init()
pygame.font.init()
screen  = pygame.display.set_mode(size)
pygame.display.set_caption('Proyecto IA: Búsquedas')

running         = True
cursor_drag     = False
board_drawn     = False
algo_list_drawn = False
homepage        = True
secondpage      = False
checkbox_filled = False

algorithm       = 0

def draw_board():
    for row in range(1, 11):
        boxes = []
        boxesStart = []
        boxesFinish = []

        for col in range(1, 11):
            box = pygame.Rect(50 * row, 50 * col, 50, 50)
            if (row, col) not in ((1 , 1),(10, 10)):
                pygame.draw.rect(screen, ORANGE, box, 3)
            else:
                pygame.draw.rect(screen, ORANGE, box, 3)
            boxes.append(False)
            boxesStart.append(False)
            boxesFinish.append(False)
            coordinates.append((50 * row,50 * col))
        board.append(boxes)
        boardStart.append(boxesStart)
        boardFinish.append(boxesFinish)

board       = []
boardStart  = []
boardFinish = []
isStart = False
isFinish = False
coordinates = []

LARGE_TEXT = pygame.font.SysFont('segoeuisemibold', 30)
BTN_TEXT   = pygame.font.SysFont('segoeuisemibold', 22) 

reset_button = pygame.Rect(600, 50, 100, 50)
algo_list    = DropDown(600, 120, 190, 40, WHITE, RED, BTN_TEXT, ['¿Cuál Algoritmo?','Profundidad','Amplitud','A*','Primero el Mejor'])
solve_button = pygame.Rect(600, 475, 100, 50)
checkbox     = Checkbox(pygame.Rect(600, 425, 25, 25), '¿Visualizar Camino?', BTN_TEXT)
play_button  = pygame.Rect(w/2/2+20, 350, 400, 50)
play_button_2  = pygame.Rect(w/2/2+20, 450, 400, 50)

while running:

    events = pygame.event.get()

    for event in events:

        #Cerrar Programa
        if event.type == pygame.QUIT:
            running = False
            break

        #Presentación Inicial
        if homepage:
            #Título
            title = LARGE_TEXT.render("Proyecto IA: Búsquedas", 1, WHITE)
            title_rect = title.get_rect()
            title_rect.center = (w/2, 40)
            screen.blit(title, title_rect)

            #Integrantes
            integrantes = ["INTEGRANTES", "Bañuelos Camacho Itzel Carolina", "Lopez Capistran Enrique Ariel", "Sotelo Rivas Manuel Alberto"]
            for i, text in enumerate(integrantes):
                line = BTN_TEXT.render(text, 1, WHITE)
                line_rect = line.get_rect()
                line_rect.center = (w/2, 150 + i*40)
                screen.blit(line, line_rect)

            #Iniciar(Botón)
            pygame.draw.rect(screen, WHITE, play_button)
            play = BTN_TEXT.render('Caminos', 1, BLACK)
            screen.blit(play, (play_button.x + 25, play_button.y + 12.5))

            #Iniciar(Botón 2)
            pygame.draw.rect(screen, WHITE, play_button_2)
            play2 = BTN_TEXT.render('Conecta 3', 1, BLACK)
            screen.blit(play2, (play_button_2.x + 25, play_button_2.y + 12.5))

            mpos = pygame.mouse.get_pos()

            if play_button.collidepoint(mpos):
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    homepage = False
                    screen.fill(BLACK)
                elif event.type == MOUSEMOTION:
                    pygame.draw.rect(screen, RED, play_button)
                    play = BTN_TEXT.render('Caminos', 1, WHITE)
                    screen.blit(play, (play_button.x + 25, play_button.y + 12.5))

            if play_button_2.collidepoint(mpos):
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    homepage = False
                    secondpage = True
                    screen.fill(BLACK)
                elif event.type == MOUSEMOTION:
                    pygame.draw.rect(screen, RED, play_button_2)
                    play2 = BTN_TEXT.render('Conecta 3', 1, WHITE)
                    screen.blit(play2, (play_button_2.x + 25, play_button_2.y + 12.5))

        elif secondpage:
            resize = (300, 300)
            screen  = pygame.display.set_mode(resize)
            conecta = Conecta3()

        else: #Pantalla secundaria de los juegos
            #Dibujar tablero nuevo(todo en BLACK)
            if not board_drawn:
                draw_board()
                board_drawn = True

            #Dibujar Botón de Borrar(RESET)
            pygame.draw.rect(screen, WHITE, reset_button)
            reset_button_text = BTN_TEXT.render("Borrar", 1, BLACK)
            screen.blit(reset_button_text, (reset_button.x + 22.5, reset_button.y + 12.5))

            #Dibujar Botón Iniciar
            pygame.draw.rect(screen, WHITE, solve_button)
            solve_button_text = BTN_TEXT.render('Iniciar', 1, BLACK)
            screen.blit(solve_button_text, (solve_button.x + 22.5, solve_button.y + 12.5))
            
            #Dibujar Menu(Dropdown)
            selected_option = algo_list.update(events)
            if selected_option > 0:
                algorithm = selected_option
            algo_list.draw(screen)

            #Dibujar el Checkbox
            checkbox_filled = checkbox.update(events)
            checkbox.draw(screen)

            mousePos = pygame.mouse.get_pos()

            # Efecto hover
            if event.type == MOUSEMOTION:

                if solve_button.collidepoint(mousePos): # Botón iniciar
                    pygame.draw.rect(screen, RED, solve_button)
                    solve_button_text = BTN_TEXT.render('Iniciar', 1, WHITE)
                    screen.blit(solve_button_text, (solve_button.x + 22.5, solve_button.y + 12.5))

                elif reset_button.collidepoint(mousePos): # Botón borrar
                    pygame.draw.rect(screen, RED, reset_button)
                    reset_button_text = BTN_TEXT.render("Borrar", 1, WHITE)
                    screen.blit(reset_button_text, (reset_button.x + 22.5, reset_button.y + 12.5))

            #Si el mouse está presionado...
            if event.type == MOUSEBUTTONDOWN:
                
                cursor_drag = True
                button = event.button

                #Boton(Iniciar/Resolver)
                if solve_button.collidepoint(mousePos):
                               
                    #Pocos Muros
                    if sum(sum(row) for row in board) < 1 and algorithm in (2, 3, 4, 5):
                        rect = pygame.Rect(600, 535, 100, 50)
                        msg = BTN_TEXT.render('Advertencia 2(Pocas paredes)', 1, RED)
                        screen.blit(msg, (rect.x, rect.y))
                    else:   #Demasiados Muros
                        
                        #rect = pygame.Rect(600,565,100,50)
                        msg = BTN_TEXT.render('Advertencia 3(Demasiadas paredes)', 1, BLACK)
                        #screen.blit(msg, (rect.x,rect.y))

                        #Tablero Nuevo
                        for i in range(len(board)):
                            for j in range(len(board)):
                                if not board[i][j] and (i,j) not in ((0, 0), (9, 9)):
                                    box = pygame.Rect((j + 1) * 50, (i + 1) *50, 50, 50)
                                    pygame.draw.rect(screen, BLACK, box)
                                    pygame.draw.rect(screen, ORANGE, box, 3)
                                    
                        if algorithm != 0:

                            #Elegir algoritmo
                            '''rect = pygame.Rect(600, 535, 100, 50)
                            msg = BTN_TEXT.render('¿Cuál Algoritmo?', 1, BLACK)
                            screen.blit(msg, (rect.x,rect.y))'''

                            if isStart and isFinish:

                                #Generando Objeto Laberinto
                                maze = Maze(board, algorithm, boardStart, boardFinish)
                                pygame.display.set_caption('Cargando...')
                                solved = maze.solve(checkbox_filled)

                                #Prevenir al usuario usar el click durante la generación del camino
                                pygame.event.set_blocked(MOUSEBUTTONDOWN)

                                if solved and checkbox_filled:

                                    #Irresolvible
                                    rect = pygame.Rect(600, 535, 100, 50)
                                    msg = BTN_TEXT.render('Advertencia 1(Irresolvible)', 1, BLACK)
                                    screen.blit(msg, (rect.x, rect.y))

                                    #Mostrar Pathfinding
                                    pygame.display.set_caption('Proyecto IA: Búsquedas')
                                    steps, solution = solved
                                    for step in steps:
                                        if step not in ((0, 0), (9, 9)):
                                            time.sleep(0.1)
                                            i, j  = step
                                            box = pygame.Rect((j + 1) * 50, (i + 1) * 50, 50, 50)
                                            pygame.draw.rect(screen, YELLOW, box)
                                            pygame.draw.rect(screen, ORANGE, box, 3)
                                            pygame.display.update()

                                if solved:
                                    solution = solution if checkbox_filled else solved
                                    #Mostrar Solución FINAL
                                    for move in solution:
                                        if move not in ((0, 0), (9, 9)):
                                            time.sleep(0.1)
                                            i,j = move
                                            box = pygame.Rect((j + 1) * 50, (i + 1) * 50, 50, 50)
                                            pygame.draw.rect(screen, GREEN, box)
                                            pygame.draw.rect(screen, ORANGE, box, 3)
                                            pygame.display.update()
                                '''else: 
                                    #Si es IRRESOLVIBLE
                                    rect = pygame.Rect(600, 535, 100, 50)
                                    msg = BTN_TEXT.render('Error 1', 1, RED)
                                    screen.blit(msg, (rect.x, rect.y))'''

                                pygame.event.set_allowed(MOUSEBUTTONDOWN)
                            else:
                                rect = pygame.Rect(600, 535, 100, 50)
                                msg = BTN_TEXT.render('Indica el inicio y el fin', 1, RED)
                                screen.blit(msg, (rect.x, rect.y))
                        else:  #Si el algoritmo no fue seleccionado no dejar proseguir el programa
                            rect = pygame.Rect(600, 535, 100, 50)
                            msg = BTN_TEXT.render('Elige un algoritmo', 1, RED)
                            screen.blit(msg, (rect.x, rect.y))

                #Boton Borrar
                if reset_button.collidepoint(mousePos):
                    board_drawn = False
                    board = []
                    boardStart = []
                    boardFinish = []
                    isStart = False
                    isFinish = False
                    coordinates = []
                    screen.fill(BLACK)
                    if not board_drawn:
                        draw_board()
                        board_drawn = True
                    
                #Click = Click izquiero inicio / Click derecho final 
                else:
                    for x, y in coordinates:
                        box = pygame.Rect(x, y, 50, 50)
                        if box.collidepoint(mousePos):
                            if event.button == 1 and isStart == False:
                                pygame.draw.rect(screen, GREEN, box)
                                pygame.draw.rect(screen, GREEN, box, 3)
                                boardStart[int(y / 50 - 1)][int(x / 50 - 1)] = True
                                isStart = True
                            elif event.button == 3 and isFinish == False:
                                pygame.draw.rect(screen, RED, box)
                                pygame.draw.rect(screen, RED, box, 3)
                                boardFinish[int(y / 50 - 1)][int(x / 50 - 1)] = True
                                isFinish = True                 
                            break

            #Muros fijos iniciales
            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,100,50,50))
            board[int(100/50-1)][int(100/50-1)] = True
            boardStart[int(100/50-1)][int(100/50-1)] = False
            boardFinish[int(100/50-1)][int(100/50-1)] = False

            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,150,50,50))     
            board[int(150/50-1)][int(100/50-1)] = True
            boardStart[int(150/50-1)][int(100/50-1)] = False
            boardFinish[int(150/50-1)][int(100/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,200,50,50))
            board[int(200/50-1)][int(100/50-1)] = True
            boardStart[int(200/50-1)][int(100/50-1)] = False
            boardFinish[int(200/50-1)][int(100/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,250,50,50))
            board[int(250/50-1)][int(100/50-1)] = True
            boardStart[int(250/50-1)][int(100/50-1)] = False
            boardFinish[int(250/50-1)][int(100/50-1)] = False

            pygame.draw.rect(screen, PURPLE, pygame.Rect(250,150,50,50))
            board[int(150/50-1)][int(250/50-1)] = True
            boardStart[int(150/50-1)][int(250/50-1)] = False
            boardFinish[int(150/50-1)][int(250/50-1)] = False

            pygame.draw.rect(screen, PURPLE, pygame.Rect(300,150,50,50))
            board[int(150/50-1)][int(300/50-1)] = True
            boardStart[int(150/50-1)][int(300/50-1)] = False
            boardFinish[int(150/50-1)][int(300/50-1)] = False

            pygame.draw.rect(screen, PURPLE, pygame.Rect(250,250,50,50))
            board[int(250/50-1)][int(250/50-1)] = True
            boardStart[int(250/50-1)][int(250/50-1)] = False
            boardFinish[int(250/50-1)][int(250/50-1)] = False
            
            pygame.draw.rect(screen, PURPLE, pygame.Rect(250,350,50,50))
            board[int(350/50-1)][int(250/50-1)] = True
            boardStart[int(350/50-1)][int(250/50-1)] = False
            boardFinish[int(350/50-1)][int(250/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(200,350,50,50))
            board[int(350/50-1)][int(200/50-1)] = True
            boardStart[int(350/50-1)][int(200/50-1)] = False
            boardFinish[int(350/50-1)][int(200/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(300,350,50,50))
            board[int(350/50-1)][int(300/50-1)] = True
            boardStart[int(350/50-1)][int(300/50-1)] = False
            boardFinish[int(350/50-1)][int(300/50-1)] = False

            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,350,50,50))
            board[int(350/50-1)][int(400/50-1)] = True
            boardStart[int(350/50-1)][int(400/50-1)] = False
            boardFinish[int(350/50-1)][int(400/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,400,50,50))
            board[int(400/50-1)][int(400/50-1)] = True
            boardStart[int(400/50-1)][int(400/50-1)] = False
            boardFinish[int(400/50-1)][int(400/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,450,50,50))
            board[int(450/50-1)][int(400/50-1)] = True
            boardStart[int(450/50-1)][int(400/50-1)] = False
            boardFinish[int(450/50-1)][int(400/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,500,50,50))
            board[int(500/50-1)][int(400/50-1)] = True
            boardStart[int(500/50-1)][int(400/50-1)] = False
            boardFinish[int(500/50-1)][int(400/50-1)] = False

            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,250,50,50))
            board[int(250/50-1)][int(450/50-1)] = True
            boardStart[int(250/50-1)][int(450/50-1)] = False
            boardFinish[int(250/50-1)][int(450/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,200,50,50))
            board[int(200/50-1)][int(450/50-1)] = True
            boardStart[int(200/50-1)][int(450/50-1)] = False
            boardFinish[int(200/50-1)][int(450/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,150,50,50))
            board[int(150/50-1)][int(450/50-1)] = True
            boardStart[int(150/50-1)][int(450/50-1)] = False
            boardFinish[int(150/50-1)][int(450/50-1)] = False
            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,100,50,50))
            board[int(100/50-1)][int(450/50-1)] = True
            boardStart[int(100/50-1)][int(450/50-1)] = False
            boardFinish[int(100/50-1)][int(450/50-1)] = False
            
            #Mouse "Release"
            '''if event.type == MOUSEBUTTONUP:
                cursor_drag = False'''
            
            #Mouse "Arrastrado con click"
            '''if event.type == MOUSEMOTION:
                if cursor_drag:
                    mousePos_x, mousePos_y = pygame.mouse.get_pos()
                    x, y = round(mousePos_x / 50) * 50, round(mousePos_y / 50) * 50
                    if (x, y) in coordinates and (x,y) not in ((50,50),(500,500)):
                        box = pygame.Rect(x, y, 50,50)    
                        if box.collidepoint(x, y):
                            if button == 1:
                                pygame.draw.rect(screen, PURPLE, box)
                                pygame.draw.rect(screen, ORANGE, box,3)
                                board[int(y/50-1)][int(x/50-1)] = True
                                pygame.display.update()
                                break
                            elif button == 3:
                                pygame.draw.rect(screen, BLACK, box)
                                pygame.draw.rect(screen, ORANGE, box,3)
                                board[int(y/50-1)][int(x/50-1)] = False
                                pygame.display.update()
                                break'''
        pygame.display.update()