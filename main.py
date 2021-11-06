import pygame
import random
import time
import sys
import numpy as np
import math
from pygame.draw import rect
from pygame.constants import MOUSEBUTTONDOWN


##################### CLASES #######################

#Nodos Frontier
class Node():
    def __init__(self, parent, state, action):
        self.parent = parent #Nodo
        self.state = state #Tupla
        self.action = action #Tupla

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
            raise Exception('Fronteras vacías')
        else:
            node = self.frontier[-1]
            self.frontier.remove(node)
            return [node]

#Amplitud
class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception('Fronteras vacías')
        else:
            node = self.frontier[0] 
            self.frontier.remove(node)
            return [node]

#A*
class ManhattanFrontier(StackFrontier):
    def remove(self, cost):
        if self.empty():
            raise Exception('Fronteras vacías')
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
            raise Exception('Fronteras vacías')
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

#Objeto/Laberinto
class Maze():
    def __init__(self, board, algorithm):
        self.board = board
        self.start = (0,0)
        self.goal = (9,9)
        self.algorithm = algorithm
        self.walls = []
        self.height = self.width = len(self.board)

        for i in range(self.height):
            row = []
            for j in range(self.width):
                if self.board[i][j] and (i,j) not in (self.start, self.goal):
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
        elif self.algorithm == 5:
            pass                    #Conecta 3

            
            ###### INICIA CONECTA 3 ######
            #Colores del juego
            BLUE = (0,255,0)
            BLACK = (0,0,0) #Café
            COFFEE = (102,51,0)
            RED = (204,102,0) #Color IA
            YELLOW = (255,255,0) #Color Usuario (Amarillo)
            #Tamaño del tablero
            ROW_COUNT = 3
            COLUMN_COUNT = 3
            #Identificadores(Saber turno)
            PLAYER = 0
            AI = 1
            #Identificadores(Para saber de quien es cada pieza)
            PLAYER_PIECE = 1
            AI_PIECE = 2
            #Usado para la IA(calculo y evaluación de movimientos) 
            WINDOW_LENGTH = 3
            EMPTY = 0

            #Flag para verificar si hubo un ganador
            winner = False

            #Método de numpy para crear array de 2 dimensiones(Tablero)
            def create_board():
                board2 = np.zeros((ROW_COUNT,COLUMN_COUNT))
                return board2
            #Movimientos
            def drop_piece(board2, row, col, piece):
                board2[row][col] = piece
            #Valida si hay espacio para que "caiga" la pieza
            def is_valid_location(board2, col):
                return board2[ROW_COUNT-1][col] == 0

            def get_next_open_row(board2, col):
                for r in range(ROW_COUNT):
                    if board2[r][col] == 0:
                        return r

            def print_board(board2):
                print(np.flip(board2,0))

            def winning_move(board2, piece):
                #Verifica horizontal de 3
                for c in range(COLUMN_COUNT-2):
                    for r in range(ROW_COUNT):
                        if board2[r][c] == piece and board2[r][c+1] == piece and board2[r][c+2] == piece:
                            return True
                #Verifica vertical de 3
                for c in range(COLUMN_COUNT):
                    for r in range(ROW_COUNT-2):
                        if board2[r][c] == piece and board2[r+1][c] == piece and board2[r+2][c] == piece:
                            return True
                #Verifica las diagonales de 3
                for c in range(COLUMN_COUNT-2):
                    for r in range(ROW_COUNT-2):
                        if board2[r][c] == piece and board2[r+1][c+1] == piece and board2[r+2][c+2] == piece:
                            return True

                #Verifica diagonales invertidas de 3
                for c in range(COLUMN_COUNT-2):
                    for r in range(2,ROW_COUNT):
                        if board2[r][c] == piece and board2[r-1][c+1] == piece and board2[r-2][c+2] == piece:
                            return True

            def evaluate_window(window, piece):
                score = 0
                opp_piece = PLAYER_PIECE
                if piece == PLAYER_PIECE:
                    opp_piece = AI_PIECE

                if window.count(piece) == 2:
                    score += 100
                elif window.count(piece) == 1 and window.count(EMPTY) == 0:
                    score += 5
                elif window.count(piece) == 1 and window.count(EMPTY) == 1:
                    score += 2

                if window.count(opp_piece) == 2 and window.count(EMPTY) == 0:
                    score -= 4

                return score 

            def score_position(board2, piece):
                score = 0
                #Da preferencia a movimientos en el centro del tablero(da mayor potencial de combinaciones)
                center_array = [int(i) for i in list(board2[:, COLUMN_COUNT//2])]
                center_count = center_array.count(piece)
                score += center_count * 3

                #Calcula puntaje horizontal
                
                for r in range(ROW_COUNT):
                    row_array = [int(i) for i in list(board2[r,:])]
                    for c in range(COLUMN_COUNT-3):
                        window = row_array[c:c+WINDOW_LENGTH]
                        score += evaluate_window(window, piece)
                
                ##Calcula puntaje Vertical
                for c in range(COLUMN_COUNT):
                    col_array = [int(i) for i in list(board2[:,c])]
                    for r in range(ROW_COUNT-3):
                        window = col_array[r:r+WINDOW_LENGTH]
                        score += evaluate_window(window, piece)

                for r in range(ROW_COUNT-3):
                    for c in range(COLUMN_COUNT-3):
                        window = [board2[r+i][c+i] for i in range(WINDOW_LENGTH)]
                        score += evaluate_window(window, piece)

                for r in range(ROW_COUNT-3):
                    for c in range(COLUMN_COUNT-3):
                        window = [board2[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
                        score += evaluate_window(window, piece)

                return score

            def is_terminal_node(board2):
                return winning_move(board2, PLAYER_PIECE) or winning_move(board2, AI_PIECE) or len(get_valid_locations(board2)) == 0

            #Minimax
            def minimax(board2,depth, alpha, beta, maximizingPlayer):
                valid_locations = get_valid_locations(board2)
                is_terminal = is_terminal_node(board2)
                if depth == 0 or is_terminal:
                    if is_terminal:
                        if winning_move(board2, AI_PIECE):
                            return (None, 100000000000)
                        elif winning_move(board2, PLAYER_PIECE):
                            return (None, -10000000000)   
                        else: #game over no more moves  
                            return (None, 0)
                    else: #depth is zero
                        return (None, score_position(board2, AI_PIECE))

                if maximizingPlayer:
                    value = -math.inf
                    column = random.choice(valid_locations)
                    for col in valid_locations:
                        row = get_next_open_row(board2, col)
                        b_copy = board2.copy()
                        drop_piece(b_copy, row, col, AI_PIECE)
                        new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
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
                        row = get_next_open_row(board2, col)
                        b_copy = board2.copy()
                        drop_piece(board2, row, col, PLAYER_PIECE)
                        new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
                        if new_score < value:
                            value = new_score
                            column = col
                        beta = min(beta, value)
                        if alpha >= beta:
                            break
                    return column, value
                



            def get_valid_locations(board2):
                valid_locations = []
                for col in range(COLUMN_COUNT):
                    if is_valid_location(board2, col):
                        valid_locations.append(col)
                return valid_locations


            def pick_best_move(board2, piece):
                valid_locations = get_valid_locations(board2)
                best_score = 0
                best_col = random.choice(valid_locations)
                for col in valid_locations:
                    row = get_next_open_row(board2, col)
                    temp_board = board2.copy()
                    drop_piece(temp_board, row, col, piece)
                    score = score_position(temp_board, piece)
                    #Actualizacion de puntajes despues de cada turno
                    if score > best_score:
                        best_score = score
                        best_col = col
                        
                return best_col


            def draw_board(board2):
                for c in range(COLUMN_COUNT):
                    for r in range(ROW_COUNT):
                        pygame.draw.rect(screen2, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE+10, SQUARESIZE+10))
                        pygame.draw.circle(screen2, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS+4.5)
                
                for c in range(COLUMN_COUNT):
                    for r in range(ROW_COUNT):		
                        if board2[r][c] == PLAYER_PIECE:
                            pygame.draw.circle(screen2, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                        elif board2[r][c] == AI_PIECE: 
                            pygame.draw.circle(screen2, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                pygame.display.update()


            board2 = create_board()
            print_board(board2)
            game_over = False

            pygame.init()

            SQUARESIZE = 150

            width = COLUMN_COUNT * SQUARESIZE
            height = (ROW_COUNT+1) * SQUARESIZE

            size = (width, height)
            RADIUS = int(SQUARESIZE/2 - 32)
            size2 = (width + 150, height + 50)
            size3 = (width + 50, height + 50)

            screen = pygame.display.set_mode(size2)
            screen2 = pygame.display.set_mode(size3)
            draw_board(board2)
            pygame.display.update()

            myfont = pygame.font.SysFont("segoeuisemibold", 40)

            turn = random.randint(PLAYER, AI)
            firstTurn = turn
            if firstTurn == 0:
                turnNum = 1 #Contador para cuando inicie el juego el usuario y no la IA
            else:
                turnNum = -1

            while not game_over:

                for event in pygame.event.get():
                    
                    if event.type == pygame.QUIT:
                        sys.exit()

                    if event.type == pygame.MOUSEMOTION:
                        pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                        posx = event.pos[0]
                        if turn == PLAYER:
                            pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                            pygame.display.update()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pygame.draw.rect(screen, COFFEE, (0,0, width, SQUARESIZE))
                        
                        #Input del usuario
                        if turn == PLAYER:
                            posx = event.pos[0]
                            col = int(math.floor(posx/SQUARESIZE))  

                            if is_valid_location(board2,col):
                                row = get_next_open_row(board2, col)
                                drop_piece(board2, row, col, PLAYER_PIECE)
                                print_board(board2) 
                                draw_board(board2)

                                if winning_move(board2,PLAYER_PIECE):
                                    label = myfont.render("Usuario Ganó", 1, BLUE)
                                    screen.blit(label, (10,10))
                                    game_over = True
                                    winner = True

                                turn += 1
                                turn = turn % 2 

                                print_board(board2) 
                                draw_board(board2)

                                if game_over:
                                    pygame.time.wait(3000)
                    #Input de la IA   
                    if turn == AI and not game_over:
                        pick_best_move(board2, AI_PIECE)

                        #Aumentar Depth al minimax() para mayor dificultad
                        col, minimax_score = minimax(board2, 2, -math.inf, math.inf, True)

                        try: 
                            if is_valid_location(board2,col):
                            # pygame.time.wait(500)
                                row = get_next_open_row(board2, col)
                                drop_piece(board2, row, col, AI_PIECE)
                        except ValueError as ve:
                            label = myfont.render("Empate", 1, BLUE)
                            screen.blit(label, (10,10))
                            game_over = True
                            pygame.time.wait(3000)
                            
                        if winning_move(board2, AI_PIECE):
                            label = myfont.render("IA Ganó", 1, RED)
                            screen.blit(label, (10,10))
                            game_over = True
                            winner = True
                            print_board(board2) 
                            draw_board(board2)
                            pygame.time.wait(3000)

                        print_board(board2) 

                        if 0 not in board2 and winner == False:
                            #print("Test")
                            label = myfont.render("Empate", 1, BLUE)
                            screen.blit(label, (10,10))
                            game_over = True

                        turnNum += 1
                        if turnNum == 5 and winner == False:
                            label = myfont.render("Empate", 1, BLUE)
                            screen.blit(label, (10,10))
                            game_over = True
                        print(turnNum)
                        
                        draw_board(board2)
                        if 0 not in board2:
                            pygame.time.wait(3000)

                        if turnNum == 6:
                            pygame.time.wait(3000)

                        
                        turn += 1
                        turn = turn % 2

                        
                        if game_over:
                            if winner == False:
                                label = myfont.render("Empate", 1, BLUE)
                                screen.blit(label, (10,10))
                                game_over = True
                                pygame.time.wait(3000)






        frontier.add(start)
        
        while True:
            if frontier.empty():
                return None

            self.cost += 1

            nodes = frontier.remove(self.cost) if (self.algorithm == 3 or self.algorithm == 4)else frontier.remove()

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

#Menu(Dropdown) de Algoritmos de Búsqueda
class DropDown():

    def __init__(self, x,y,w,h,color, highlight_color, font, options, selected = 0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x,y,w,h)
        self.font = font
        self.options = options
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2) #border
        msg = self.font.render(self.options[self.selected], 1, (255, 255, 255) if self.menu_active else (0, 0, 0))
        surface.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                if i == 0:
                    pygame.draw.rect(surface, (200,200,200), rect)
                else:
                    pygame.draw.rect(surface, self.highlight_color if i == self.active_option else self.color, rect)

                msg = self.font.render(text, 1, (0,0,0))
                surface.blit(msg, msg.get_rect(center = rect.center))
            outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * (len(self.options)))
            pygame.draw.rect(surface, (0,0,0), outer_rect, 2) 

        else:
            for i in range(len(self.options)):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surface, (0,0,0), rect)


        
    def update(self, events):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
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
        self.rect = rect
        self.fill_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width // 1.6, self.rect.height // 1.6)
        self.selected = False
        self.hovered = False
        self.font = font
        self.filled_color = (0,0,0)
        self.empty_color = (255,255,255)
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, self.empty_color, self.rect)
        if self.hovered:
            pygame.draw.rect(surface, self.filled_color, self.fill_rect)
        if self.selected:
            pygame.draw.rect(surface, self.filled_color, self.fill_rect)
        msg = self.font.render(self.text, 1, (255,255,255))
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

size = (900,600)
w,h = size

YELLOW = (255,255,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLACK = (33, 47, 60)
RED = (255,0,0)
ORANGE = (255,125,123)
PURPLE = (113, 125, 126)

pygame.init()
pygame.font.init()
screen  = pygame.display.set_mode(size)
pygame.display.set_caption('Proyecto IA: Búsquedas')

running = True
cursor_drag = False
board_drawn = False
algo_list_drawn = False
homepage = True
checkbox_filled = False

algorithm = 0

def draw_board():
    for row in range(1,11):
        boxes = []
        for col in range(1,11):
            box = pygame.Rect(50*row,50*col,50,50)
            if (row, col) not in ((1,1),(10,10)):
                pygame.draw.rect(screen, ORANGE, box, 3)
            else:
                pygame.draw.rect(screen, RED, box)
                pygame.draw.rect(screen, ORANGE, box, 3)
            boxes.append(False)
            coordinates.append((50*row,50*col))
        board.append(boxes)

board = []
coordinates = []



LARGE_TEXT = pygame.font.SysFont('segoeuisemibold', 30)
BTN_TEXT = pygame.font.SysFont('segoeuisemibold', 22) 


reset_button = pygame.Rect(600,50,100,50)
algo_list = DropDown(600,120,190,40, WHITE, RED, BTN_TEXT, ['¿Cuál Algoritmo?','Profundidad','Amplitud','A*','Primero el Mejor','Ir a Conecta 3'])
solve_button = pygame.Rect(600,475,100,50)
checkbox = Checkbox(pygame.Rect(600,425,25,25), '¿Visualizar Camino?', BTN_TEXT)
play_button = pygame.Rect(w/2/2+20,450,400,50)

while running:  
    events = pygame.event.get()
    for event in events:

        #Cerrar Programa
        if event.type == pygame.QUIT:
            running = False
            break

        #Presentación Inicial
        if homepage:
            #Titulo
            title = LARGE_TEXT.render("Proyecto IA: Búsquedas", 1, WHITE)
            title_rect = title.get_rect()
            title_rect.center = (w/2, 40)
            screen.blit(title, title_rect)

            #Integrantes
            integrantes = ["INTEGRANTES", "Bañuelos Camacho Itzel Carolina", "Castro Domínguez Xaviel", "Lopez Capistran Enrique Ariel", "Quintero Aguilar Jesús Emilio", "Rendon Ochoa Javier Iran", "Sotelo Rivas Manuel Alberto"]
            for i, text in enumerate(integrantes):
                line = BTN_TEXT.render(text, 1, WHITE)
                line_rect = line.get_rect()
                line_rect.center = (w/2, 150 + i*40)
                screen.blit(line, line_rect)

            #Iniciar(Botón)
            pygame.draw.rect(screen, WHITE, play_button)
            play = BTN_TEXT.render('Iniciar Búsqueda(Caminos/Laberinto)', 1, BLACK)
            screen.blit(play, (play_button.x + 25, play_button.y + 12.5))

            mpos = pygame.mouse.get_pos()

            if play_button.collidepoint(mpos):
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    homepage = False
                    screen.fill(BLACK)
                elif event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, RED, play_button)
                    play = BTN_TEXT.render('Iniciar Búsqueda(Caminos/Laberinto)', 1, WHITE)
                    screen.blit(play, (play_button.x + 25, play_button.y + 12.5))


        else:

            #Dibujar tablero nuevo(todo en BLACK)
            if not board_drawn:
                draw_board()
                board_drawn = True

            #Dibujar Botón de Borrar(RESET)
            pygame.draw.rect(screen, WHITE, reset_button)
            reset_button_text = BTN_TEXT.render("Borrar", 1, (BLACK))
            screen.blit(reset_button_text, (reset_button.x + 22.5, reset_button.y + 12.5))

            #Dibujar Botón Iniciar
            pygame.draw.rect(screen, WHITE, solve_button)
            solve_button_text = BTN_TEXT.render('Iniciar',1,BLACK)
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
            if event.type == pygame.MOUSEMOTION:

                if solve_button.collidepoint(mousePos): # Botón iniciar
                    pygame.draw.rect(screen, RED, solve_button)
                    solve_button_text = BTN_TEXT.render('Iniciar', 1, WHITE)
                    screen.blit(solve_button_text, (solve_button.x + 22.5, solve_button.y + 12.5))

                elif reset_button.collidepoint(mousePos): # Botón borrar
                    pygame.draw.rect(screen, RED, reset_button)
                    reset_button_text = BTN_TEXT.render("Borrar", 1, WHITE)
                    screen.blit(reset_button_text, (reset_button.x + 22.5, reset_button.y + 12.5))


            #Si el mouse está presionado...
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                cursor_drag = True
                button = event.button

                #Boton(Iniciar/Resolver)
                if solve_button.collidepoint(mousePos):
                    
                    #Pocos Muros
                    if sum(sum(row) for row in board) < 1 and algorithm in (2,3):
                        
                        rect = pygame.Rect(600,535,100,50)
                        msg = BTN_TEXT.render('Advertencia 2(Pocas paredes)', 1, RED)
                        screen.blit(msg, (rect.x,rect.y))

                    else:
                        #Demasiados Muros
                        
                        #rect = pygame.Rect(600,565,100,50)
                        msg = BTN_TEXT.render('Advertencia 3(Demasiadas paredes)', 1, BLACK)
                        #screen.blit(msg, (rect.x,rect.y))

                        #Tablero Nuevo
                        for i in range(len(board)):
                            for j in range(len(board)):
                                if not board[i][j] and (i,j) not in ((0,0),(9,9)):
                                    box = pygame.Rect((j+1)*50, (i+1)*50, 50, 50)
                                    pygame.draw.rect(screen, BLACK, box)
                                    pygame.draw.rect(screen, ORANGE, box, 3)
                                    
                        if algorithm != 0:

                            #Elegir algoritmo
                            rect = pygame.Rect(600,535,100,50)
                            msg = BTN_TEXT.render('¿Cuál Algoritmo?', 1, BLACK)
                            screen.blit(msg, (rect.x,rect.y))

                            #Generando Objeto Laberinto
                            maze = Maze(board, algorithm)
                            pygame.display.set_caption('Cargando...')
                            solved = maze.solve(checkbox_filled)

                            #Prevenir al usuario usar el click durante la generación del camino
                            pygame.event.set_blocked(MOUSEBUTTONDOWN)

                            if solved and checkbox_filled:

                                #Irresolvible
                                rect = pygame.Rect(600,535,100,50)
                                msg = BTN_TEXT.render('Advertencia 1(Irresolvible)', 1, BLACK)
                                screen.blit(msg, (rect.x,rect.y))

                                #Mostrar Pathfinding
                                pygame.display.set_caption('Proyecto IA: Búsquedas')
                                steps, solution = solved
                                for step in steps:
                                    if step not in ((0,0),(9,9)):
                                        time.sleep(0.1)
                                        i,j  = step
                                        box = pygame.Rect((j+1)*50, (i+1)*50, 50, 50)
                                        pygame.draw.rect(screen, YELLOW, box)
                                        pygame.draw.rect(screen, ORANGE, box, 3)
                                        pygame.display.update()

                            if solved:
                                solution = solution if checkbox_filled else solved
                                #Mostrar Solución FINAL
                                for move in solution:
                                    if move not in ((0,0),(9,9)):
                                        time.sleep(0.1)
                                        i,j = move
                                        box = pygame.Rect((j+1)*50, (i+1)*50, 50, 50)
                                        pygame.draw.rect(screen, GREEN, box)
                                        pygame.draw.rect(screen, ORANGE, box, 3)
                                        pygame.display.update()
                            
                            #Si es IRRESOLVIBLE
                            else:
                                rect = pygame.Rect(600,535,100,50)
                                msg = BTN_TEXT.render('Error 1', 1, RED)
                                screen.blit(msg, (rect.x,rect.y))

                            pygame.event.set_allowed(MOUSEBUTTONDOWN)

                        #Si el algoritmo no fue seleccionado no dejar proseguir el programa
                        else:
                            rect = pygame.Rect(600,50,100,50)
                            msg = BTN_TEXT.render('¿Cuál Algoritmo?', 1, RED)
                            screen.blit(msg, (rect.x,rect.y))

                #Boton Borrar
                if reset_button.collidepoint(mousePos):
                    board_drawn = False
                    board = []
                    coordinates = []
                    screen.fill(BLACK)
                    if not board_drawn:
                        draw_board()
                        board_drawn = True
                    

                #Click = Cuadrados/YELLOW/PURPLE/ORANGE/   
                else:
                    for x,y in coordinates:
                        if (x,y) not in ((50,50),(500,500)):
                            box = pygame.Rect(x,y,50,50)
                            if box.collidepoint(mousePos):
                                if event.button == 1:
                                    pygame.draw.rect(screen, PURPLE, box)
                                    pygame.draw.rect(screen, ORANGE, box,3)
                                    board[int(y/50-1)][int(x/50-1)] = True
                                elif event.button == 3:
                                    pygame.draw.rect(screen, BLACK, box)
                                    pygame.draw.rect(screen, ORANGE, box,3)
                                    board[int(y/50-1)][int(x/50-1)] = False                        
                                break
            
            #Muros fijos iniciales
            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,100,50,50))
            board[int(100/50-1)][int(100/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,150,50,50))     
            board[int(150/50-1)][int(100/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,200,50,50))
            board[int(200/50-1)][int(100/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(100,250,50,50))
            board[int(250/50-1)][int(100/50-1)] = True

            pygame.draw.rect(screen, PURPLE, pygame.Rect(250,150,50,50))
            board[int(150/50-1)][int(250/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(300,150,50,50))
            board[int(150/50-1)][int(300/50-1)] = True

            pygame.draw.rect(screen, PURPLE, pygame.Rect(250,250,50,50))
            board[int(250/50-1)][int(250/50-1)] = True
            
            pygame.draw.rect(screen, PURPLE, pygame.Rect(250,350,50,50))
            board[int(350/50-1)][int(250/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(200,350,50,50))
            board[int(350/50-1)][int(200/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(300,350,50,50))
            board[int(350/50-1)][int(300/50-1)] = True

            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,350,50,50))
            board[int(350/50-1)][int(400/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,400,50,50))
            board[int(400/50-1)][int(400/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,450,50,50))
            board[int(450/50-1)][int(400/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(400,500,50,50))
            board[int(500/50-1)][int(400/50-1)] = True

            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,250,50,50))
            board[int(250/50-1)][int(450/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,200,50,50))
            board[int(200/50-1)][int(450/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,150,50,50))
            board[int(150/50-1)][int(450/50-1)] = True
            pygame.draw.rect(screen, PURPLE, pygame.Rect(450,100,50,50))
            board[int(100/50-1)][int(450/50-1)] = True
            
            #Mouse "Release"
            if event.type == pygame.MOUSEBUTTONUP:
                cursor_drag = False
            
            #Mouse "Arrastrado con click"
            if event.type == pygame.MOUSEMOTION:
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
                                break   
        pygame.display.update()