import pygame
import sys
import random
from button import Button

class Nodo:
    def __init__(self, posicion):
        self.posicion = posicion
        self.conexiones = {}
        self.valor = float('inf')
        self.nodoAnterior = None

    def agregarConexion(self, nodo, peso):
        self.conexiones[nodo] = peso
        
    def getNext(self, grafo, nodoFinal, enemies, libres, nodos, users, enemigo, distancia_pursue, special):
        dijkstra(grafo, self, enemies)
        if enemigo.destination == None or (enemigo.row == enemigo.destination[0] and enemigo.col == enemigo.destination[1]):
            enemigo.destination = random.choice(libres)
        jugador_cercano = None
        for jugador in users:
            user = nodos[jugador.row][jugador.col]
            if jugador_cercano is None or jugador_cercano.valor >= user.valor:
                jugador_cercano = user
        user = jugador_cercano
        if user.valor > distancia_pursue or special:
            destino = enemigo.destination
            current_node = nodos[destino[0]][destino[1]]
        else:
            current_node = user
        
        shortest_path = []
        while current_node:
            shortest_path.insert(0, current_node.posicion)
            current_node = current_node.nodoAnterior
        if len(shortest_path)>1:
            return shortest_path[1]
        return shortest_path[0]

def dijkstra(grafo, nodoInicial, enemies):
    nodoInicial.valor = 0
    nodosAbiertos = list(grafo.values())
    for nodo in nodosAbiertos:
        nodo.nodoAnterior = None
        if nodo != nodoInicial:
            nodo.valor = float('inf')
    nodosCerrados = []

    while nodosAbiertos:
        nodoActivo = min(nodosAbiertos, key=lambda node: node.valor)
        nodosAbiertos.remove(nodoActivo)
        nodosCerrados.append(nodoActivo)

        for nodo, peso in nodoActivo.conexiones.items():
            distancia = nodoActivo.valor + peso
            
            # Check if the target node is occupied by an enemy
            for enemy in enemies:
                if enemy.row == nodo.posicion[0] and enemy.col == nodo.posicion[1]:
                    # Increase the weight for the node if an enemy is present
                    distancia += 100
            
            if distancia < nodo.valor:
                nodo.valor = distancia
                nodo.nodoAnterior = nodoActivo

def crearGrafo(nodos, grid, grid_rows, grid_cols):
    grafo = {}
    cont = 0
    for i in range(0,grid_rows):
        for j in range(0, grid_cols):
            if i > 0:
                nodos[i][j].agregarConexion(nodos[i-1][j], max(grid[i][j],grid[i-1][j]))
            if j > 0:
                nodos[i][j].agregarConexion(nodos[i][j-1], max(grid[i][j],grid[i][j-1]))
            if i < grid_rows-1:                
                nodos[i][j].agregarConexion(nodos[i+1][j], max(grid[i][j],grid[i+1][j]))
            if j < grid_cols-1:                
                nodos[i][j].agregarConexion(nodos[i][j+1], max(grid[i][j],grid[i][j+1]))
            grafo[cont] = nodos[i][j]
            cont+=1
    return grafo

class Usuario:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.orientation = "right"
        self.vidas = 3
        self.puntos = 0
        self.puntos2 = 0
    
    def getX(self, g_size):
        return self.col * g_size + g_size // 2

class Enemigo:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.destination = None
    
    def pursue(self, grafo, nodos, users, enemies, libres, distancia_pursue, special):
        nextNode = nodos[self.row][self.col].getNext(grafo, users, enemies, libres, nodos, users, self, distancia_pursue, special)
        self.row = nextNode[0]
        self.col = nextNode[1]
        
class Item:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color

def getNeighbours(grid, grid_rows, grid_cols, row, column, b):
    openNeighbours = 0
    min_neighbours = 2
    if row > 0:
        if grid[row-1][column] == 1:
            if b:
                if getNeighbours(grid, grid_rows, grid_cols, row-1, column, False) > min_neighbours:
                    openNeighbours += 1
            else:
                openNeighbours += 1
    if row < grid_rows-1:
        if grid[row+1][column] == 1:
            if b:
                if getNeighbours(grid, grid_rows, grid_cols, row+1, column, False) > min_neighbours:
                    openNeighbours += 1
            else:
                openNeighbours += 1
    if column > 0:
        if grid[row][column-1] == 1:
            if b:
                if getNeighbours(grid, grid_rows, grid_cols, row, column-1, False) > min_neighbours:
                    openNeighbours += 1
            else:
                openNeighbours += 1
    if column < grid_cols-1:
        if grid[row][column+1] == 1:
            if b:
                if getNeighbours(grid, grid_rows, grid_cols, row, column+1, False) > min_neighbours:
                    openNeighbours += 1
            else:
                openNeighbours += 1
    return openNeighbours
    
def randomWall():
    n = random.randint(1,100)
    return n<=70

def draw_square(screen, center_x, center_y, side_length, triangle_position, mouth, color):
    # Calculate the coordinates of the square's top-left corner
    top_left_x = center_x - side_length // 2
    top_left_y = center_y - side_length // 2

    # Draw the square with a filled yellow background
    pygame.draw.rect(screen, color, (top_left_x, top_left_y, side_length, side_length))

    # Draw the black border
    pygame.draw.rect(screen, (0, 0, 0), (top_left_x, top_left_y, side_length, side_length), 2)

    # Calculate the coordinates of the vertices of the black triangle based on the specified position
    left_x = center_x - side_length // 2
    right_x = center_x + side_length // 2
    top_y = center_y - side_length // 2
    bottom_y = center_y + side_length // 2
    # Calculate the position of the eye
    eye_radius = side_length // 8
    if triangle_position == 'right':
        triangle_vertices = [(right_x, top_y), (right_x, bottom_y), (center_x, center_y)]
        eye_x = top_left_x + eye_radius * 2
        eye_y = top_left_y + eye_radius * 2
    elif triangle_position == 'bottom':
        triangle_vertices = [(right_x, bottom_y), (left_x, bottom_y), (center_x, center_y)]
        eye_x = right_x - eye_radius * 2
        eye_y = top_left_y + eye_radius * 2
    elif triangle_position == 'left':
        triangle_vertices = [(left_x, top_y), (left_x, bottom_y), (center_x, center_y)]
        eye_x = right_x - eye_radius * 2
        eye_y = top_left_y + eye_radius * 2
    elif triangle_position == 'top':
        triangle_vertices = [(right_x, top_y), (left_x, top_y), (center_x, center_y)]
        eye_x = left_x + eye_radius * 2
        eye_y = bottom_y - eye_radius * 2
    
    if mouth:
        pygame.draw.polygon(screen, (0, 0, 0), triangle_vertices)
    
    # Draw the black eye
    pygame.draw.circle(screen, (0, 0, 0), (eye_x, eye_y), eye_radius)

def drawEnemy(screen, center, radius, special):
    special_colors = [
        (255, 0, 0),     # Red
        (255, 165, 0),   # Orange
        (255, 255, 0),   # Yellow
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (75, 0, 130),    # Indigo
        (148, 0, 211),   # Violet
        (255, 182, 193), # Pink
        (0, 255, 255),   # Cyan
        (128, 0, 128)    # Purple
    ]
    if special:
        color = random.choice(special_colors)
        pygame.draw.rect(screen, color, (center[0]-radius//2, center[1]-radius//2, radius, radius*1.8))  # Body
        color = random.choice(special_colors)
        pygame.draw.circle(screen, color, center, radius)  # Head
        color = random.choice(special_colors)
        pygame.draw.circle(screen, color, (center[0]-radius//2, center[1]), radius//4)  # Left eye
        color = random.choice(special_colors)
        pygame.draw.circle(screen, color, (center[0]+radius//2, center[1]), radius//4)  # Left eye
    else:
        pygame.draw.rect(screen, (255,0,0), (center[0]-radius//2, center[1]-radius//2, radius, radius*1.8))  # Body
        pygame.draw.circle(screen, (240,190,180), center, radius)  # Head
        pygame.draw.circle(screen, (0,0,0), (center[0]-radius//2, center[1]), radius//4)  # Left eye
        pygame.draw.circle(screen, (0,0,0), (center[0]+radius//2, center[1]), radius//4)  # Left eye

def paintFooter(screen, grid_size, grid_rows, grid_cols, total_jugadores, jugadores):
    pygame.draw.rect(screen, (0,0,0), (0, grid_size * grid_rows, grid_size * grid_cols, grid_size * grid_rows * 0.2))
    # Draw the black border
    pygame.draw.rect(screen, (255,0,0), (0, grid_size * grid_rows, grid_size * grid_cols, grid_size * grid_rows * 0.2), 2)

    rows = 5
    current_row = 1
    cols = total_jugadores + 2
    current_col = 1
    cell_width = (grid_size*grid_cols) // cols
    cell_height = (grid_size * grid_rows * 0.2) // rows
    font_size = int(min(cell_width / 10, cell_height / 5) * 5)
    for jugador in jugadores:
        x = current_col * cell_width
        y = current_row * cell_height + (grid_size * grid_rows)
        # Draw a square in the center of the cell
        square_size = min(cell_width, cell_height) * 1.2
        square_x = x + (cell_width) // 2
        square_y = y + (cell_height) // 2
        draw_square(screen, square_x, square_y, square_size, jugador.orientation, True, jugador.color)
        #pygame.draw.rect(screen, jugador.color, (square_x, square_y, square_size, square_size))
        current_row += 1
        # Draw a string in the center of the cell
        y = current_row * cell_height + (grid_size * grid_rows)
        text1 = "Points: " + str(jugador.puntos)
        font = pygame.font.Font(None, font_size)
        text1_surface = font.render(text1, True, (255, 255, 255))
        text1_rect = text1_surface.get_rect(center=(x + cell_width // 2, y + cell_height // 2))
        screen.blit(text1_surface, text1_rect)
        current_row += 1
        # Draw a string in the center of the cell
        y = current_row * cell_height + (grid_size * grid_rows)
        text2 = "Lifes: " + str(jugador.vidas)
        font = pygame.font.Font(None, font_size)
        text2_surface = font.render(text2, True, (255, 255, 255))
        text2_rect = text2_surface.get_rect(center=(x + cell_width // 2, y + cell_height // 2))
        screen.blit(text2_surface, text2_rect)
        
        current_col += 1
        current_row = 1

def loadingScreen(screen, width, height):
    screen.fill((65,172,57))
    # Choose a font and size
    font = pygame.font.Font(None, 36)  # You can replace "None" with a specific font file if needed
    
    # Create a text surface
    text = font.render("Loading Map...", True, (0,0,0))
    
    # Get the rect of the text surface
    text_rect = text.get_rect(center=(width // 2, height // 2))

    # Blit the text onto the screen
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()    

def pauseMenu(screen, width, height):
    paused = True
    end = False
    while paused:                    
        # Define the rectangle dimensions
        menu_width, menu_height = width//2, height*0.8
        
        # Calculate the position of the top-left corner of the rectangle
        menu_x = (width - menu_width) // 2
        menu_y = (height - menu_height) // 2
        
        # Draw the rectangle
        pygame.draw.rect(screen, (120, 120, 120), (menu_x, menu_y, menu_width, menu_height))

        # Render and draw text at the top
        font = pygame.font.Font(None, 36)
        text = font.render("Pause Menu", True, (0,0,0))
        text_rect = text.get_rect(center=(width // 2, menu_y * 3))
        screen.blit(text, text_rect)

        # Define button dimensions
        button_width, button_height = 150, 50

        # Calculate button positions
        button1_x = (width - button_width) // 2
        button1_y = menu_y * 3 + 50

        #button2_x = (width - button_width) // 2
        button2_y = button1_y + button_height + 20

        button3_x = (width - button_width) // 2
        button3_y = button2_y + button_height + 20

        # Draw buttons
        pygame.draw.rect(screen, (0, 255, 0), (button1_x, button1_y, button_width, button_height))
        #pygame.draw.rect(screen, (0, 0, 255), (button2_x, button2_y, button_width, button_height))
        pygame.draw.rect(screen, (255, 0, 0), (button3_x, button3_y, button_width, button_height))

        # Render and draw text on buttons
        button_font = pygame.font.Font(None, 24)
        button1_text = button_font.render("Continue", True, (0,0,0))
        #button2_text = button_font.render("Settings", True, (0,0,0))
        button3_text = button_font.render("Back", True, (0,0,0))

        screen.blit(button1_text, (button1_x + 10, button1_y + 10))
        #screen.blit(button2_text, (button2_x + 10, button2_y + 10))
        screen.blit(button3_text, (button3_x + 10, button3_y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if mouse click is within the boundaries of the buttons
                if (
                    button1_x <= mouse_x <= button1_x + button_width
                    and button1_y <= mouse_y <= button1_y + button_height
                ):
                    paused = False
                    # Add your onClick logic for Button 1 here

                #elif (
                #    button2_x <= mouse_x <= button2_x + button_width
                #    and button2_y <= mouse_y <= button2_y + button_height
                #):
                #    print("Settings")
                    # Add your onClick logic for Button 2 here

                elif (
                    button3_x <= mouse_x <= button3_x + button_width
                    and button3_y <= mouse_y <= button3_y + button_height
                ):
                    paused = False
                    end = True

        # Update the display
        pygame.display.flip()
    return end
    
def resultsMenu(screen, width, height, total_jugadores, jugadores):
    paused = True
    while paused:
        # Define the rectangle dimensions
        if width <= 200:
            width_factor = 0.8
        else:
            width_factor = 0.5
            
        if height <= 200:
            height_factor = 0.6
        else:
            height_factor = 0.5
        menu_width, menu_height = width * width_factor, height * height_factor

        # Calculate the position of the top-left corner of the rectangle
        menu_x = (width - menu_width) // 2
        menu_y = (height - menu_height) // 2

        # Add a background color to the menu
        menu_color = (50, 50, 50)  # Adjust the color as needed
        pygame.draw.rect(screen, menu_color, (menu_x, menu_y, menu_width, menu_height))

        # Define the title dimensions and position
        font_size = int(min(menu_width / 10, menu_height / 5) * 1)
        title_text = "Results"
        title_text_surface = pygame.font.Font(None, font_size).render(title_text, True, (255, 255, 255))
        title_y = menu_y * 1.2
        title_text_rect = title_text_surface.get_rect(center=(width // 2, title_y))

        # Draw the title
        screen.blit(title_text_surface, title_text_rect)

        cols = total_jugadores + 2
        current_col = 1
        rows = 2
        current_row = 0
        cell_width = menu_width // cols
        cell_height = (menu_height * 0.5) // rows
        font_size = int(min(cell_width / 10, cell_height / 5) * 3)

        for jugador in jugadores:
            x = current_col * cell_width + menu_x
            y = current_row * cell_height + title_y * 1.3  # Adjusted to remove unnecessary parentheses

            cell_color = (100, 100, 100)  # Adjust the color as needed
            pygame.draw.rect(screen, cell_color, (x, y, cell_width, cell_height))

            # Draw a square in the center of the cell
            square_size = min(cell_width, cell_height) * 0.8
            square_x = x + (cell_width) // 2
            square_y = y + (cell_height) // 2
            draw_square(screen, square_x, square_y, square_size, "right", True, jugador.color)

            # Draw Points
            y += cell_height  # Adjusted to move to the next row

            text1 = "Points: " + str(jugador.puntos)
            font = pygame.font.Font(None, font_size)
            text1_surface = font.render(text1, True, (255, 255, 255))
            text1_rect = text1_surface.get_rect(center=(x + cell_width // 2, y + cell_height // 4))
            screen.blit(text1_surface, text1_rect)

            current_col += 1.2
            current_row = 0  # Reset current_row for the next iteration
        
        # Define button dimensions
        button_width, button_height = menu_width // 2, menu_height * 0.1

        # Calculate button positions
        button1_x = (width - button_width) // 2
        button1_y = menu_y + menu_height - menu_height*0.2
        
        # Draw buttons
        pygame.draw.rect(screen, (0, 255, 0), (button1_x, button1_y, button_width, button_height))

        # Render and draw text on buttons
        font_size = int(min(cell_width / 10, cell_height / 5) * 3)
        button_font = pygame.font.Font(None, font_size)
        button1_text = button_font.render("Main Menu", True, (0, 0, 0))
        
        # Calculate the position to center the text within the button
        text_x = button1_x + (button_width - button1_text.get_width()) // 2
        text_y = button1_y + (button_height - button1_text.get_height()) // 2
        
        screen.blit(button1_text, (text_x, text_y))

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if mouse click is within the boundaries of the buttons
                if (
                    button1_x <= mouse_x <= button1_x + button_width
                    and button1_y <= mouse_y <= button1_y + button_height
                ):
                    paused = False

        # Update the display
        pygame.display.flip()
    pygame.mixer.music.load("./assets/musicMenu.mp3")
    pygame.mixer.music.play(-1)

def setGame():
    # Set up display
    width, height = 720, 620
    window = pygame.display.set_mode((width, height))
    
    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)
    
    # Font for title, labels, and button
    font_title = pygame.font.Font(None, 48)
    font_label = pygame.font.Font(None, 36)
    font_button = pygame.font.Font(None, 24)
    
    # Main title
    title_text = font_title.render("Game Settings", True, black)
    title_rect = title_text.get_rect(center=(width // 2, 50))
    
    # Row labels
    row_labels = ["Players", "Enemies", "Map Size"]
    row_label_texts = [font_label.render(label, True, black) for label in row_labels]
    
    # Button
    button_width, button_height = width // 2, height // 15
    button_x = (width - button_width) // 2
    button_y = height - button_height - 20
    button_text = font_button.render("Start Game", True, black)
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Back button
    back_button_width, back_button_height = 100, 40
    back_button_x, back_button_y = 20, 20
    back_button_text = font_button.render("Back", True, black)
    back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
    
    # Square data
    square_size = 50
    padding = 10
    squares = []  # List to store information about each square
    
    for i in range(3):
        row_squares = []
        for j in range(3):
            square_rect = pygame.Rect(0, 0, square_size, square_size)
            square_rect.x = j * (square_size + padding) + (width - 3 * (square_size + padding)) // 2
            square_rect.y = height // 4 + i * (height // 5) + padding
            row_squares.append(square_rect)
        squares.append(row_squares)
    
    # Main loop
    running = True
    startGame = False
    map_sizes = ["S", "M", "L"]
    actives = [[True, False, False], [True, False, False], [True, False, False]]
    players = 1
    enemies = 2
    size = "S"
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if the click is within the back button rectangle
                    if back_button_rect.collidepoint(event.pos):
                        running = False
                    elif button_rect.collidepoint(event.pos):
                        running = False
                        startGame = True
                    else:
                        for i, row in enumerate(squares):
                            for j, square_rect in enumerate(row):
                                if square_rect.collidepoint(event.pos):
                                    actives[i] = [False, False, False]
                                    actives[i][j] = True
                                    if i == 0:
                                        players = j+1
                                    elif i == 1:
                                        enemies = (j+1)*2
                                    else:
                                        size = map_sizes[j]
    
        # Clear the screen
        window.fill((100,100,100))
    
        # Draw main title
        window.blit(title_text, title_rect)
    
        # Draw back button
        pygame.draw.rect(window, (255, 0, 0), back_button_rect)
        back_button_rect_text = back_button_text.get_rect(center=back_button_rect.center)
        window.blit(back_button_text, back_button_rect_text)
    
        # Draw rows and columns
        for i, row_label_text in enumerate(row_label_texts):
            row_y = height // 4 + i * (height // 5)
    
            # Draw row label
            row_label_rect = row_label_text.get_rect(center=(width // 2, row_y - row_label_text.get_height()))
            window.blit(row_label_text, row_label_rect)
    
            for j, square_rect in enumerate(squares[i]):
                if actives[i][j]:
                    pygame.draw.rect(window, black, square_rect)
                else:
                    pygame.draw.rect(window, white, square_rect)
                if i == 0:
                    if actives[i][j]:
                        square_text = font_label.render(str(j+1), True, white)
                    else:
                        square_text = font_label.render(str(j+1), True, black)
                elif i == 1:
                    if actives[i][j]:
                        square_text = font_label.render(str((j+1)*2), True, white)
                    else:
                        square_text = font_label.render(str((j+1)*2), True, black)
                else:
                    if actives[i][j]:
                        square_text = font_label.render(str(map_sizes[j]), True, white)
                    else:
                        square_text = font_label.render(str(map_sizes[j]), True, black)
                square_text_rect = square_text.get_rect(center=square_rect.center)
                window.blit(square_text, square_text_rect)
    
        # Draw button
        pygame.draw.rect(window, (0, 255, 0), button_rect)
        button_rect_text = button_text.get_rect(center=button_rect.center)
        window.blit(button_text, button_rect_text)
    
        # Update the display
        pygame.display.flip()
    return [startGame, players, enemies, size]

    
def game(seed, players_amount, enemies_amount, map_size):
    pygame.mixer.music.load("./assets/musicGame.mp3")
    pygame.mixer.music.play(-1)
    random.seed(seed)
    playing = True
    # Define grid properties
    if map_size == "S":
        grid_rows, grid_cols = 10,20
    if map_size == "M":
        grid_rows, grid_cols = 20,30
    if map_size == "L":
        grid_rows, grid_cols = 30,35
    grid_size = 600 // grid_rows
    # Define screen properties
    width, height = grid_size * grid_cols, grid_size * grid_rows * 1.2
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("PacMan")

    clock = pygame.time.Clock()

    loadingScreen(screen, width, height)

    # Define circle properties
    circle_radius = grid_size//2
    circle_row, circle_col = 0, 0
    circle_x, circle_y = circle_col * grid_size + grid_size // 2, circle_row * grid_size + grid_size // 2

    last_update_time = pygame.time.get_ticks()
    last2_update_time = pygame.time.get_ticks()
    last3_update_time = pygame.time.get_ticks()
    laste_update_time = pygame.time.get_ticks()

    grid = [[1 for _ in range(grid_cols)] for _ in range(grid_rows)]
    nodos = [[1 for _ in range(grid_cols)] for _ in range(grid_rows)]
    libres = []
    nuevos_puntos = True
    if map_size == "S":
        distancia_pursue = 5
    if map_size == "M":
        distancia_pursue = 7
    if map_size == "L":
        distancia_pursue = 9
    ### Create Map
    for i in range(0, grid_rows):
        for j in range(0, grid_cols):
            libres.append((i,j))
            if i < distancia_pursue and j < distancia_pursue and i != 0 and j != 0:
                grid[i][j] = 5
                libres.pop()
            elif (i == distancia_pursue and j <= distancia_pursue) or (j == distancia_pursue and i < distancia_pursue) or (i <= distancia_pursue and j == grid_cols-1) or (j <= distancia_pursue and j == grid_rows-1) or (i <= distancia_pursue and j == 0) or (j <= distancia_pursue and i == 0) or (i == grid_rows-1 and j <= distancia_pursue):
                grid[i][j] = 500
                libres.pop()
            else:
                if i != grid_rows//2 and j != grid_cols//2:
                    if getNeighbours(grid, grid_rows, grid_cols, i,j, True) > 2:
                        if (i == distancia_pursue and j <= distancia_pursue) or (j == distancia_pursue and i < distancia_pursue):
                            pass
                        else:
                            if randomWall():
                                grid[i][j] = 1000
                                libres.pop()
                if i == grid_rows//2 and j == grid_cols//2:
                    grid[i][j] = 0
                    libres.pop()
            nodos[i][j] = Nodo((i,j))
                
    grafo = crearGrafo(nodos, grid, grid_rows, grid_cols)

    dijkstra(grafo, nodos[grid_rows//2][grid_cols//2], [])
    for i in range(0, grid_rows):
        for j in range(0, grid_cols):
            if grid[i][j] == 1:
                if nodos[i][j].valor > 800:
                    grid[i][j] = 1000
                    libres.remove((i,j))
                    grafo = crearGrafo(nodos, grid, grid_rows, grid_cols)
                    dijkstra(grafo, nodos[grid_rows//2][grid_cols//2], [])

    enemigos = []
    for i in range(0,enemies_amount):
        enemigos.append(Enemigo(grid_rows//2, grid_cols//2, (255,0,0)))

    mouth_timer = pygame.time.get_ticks()
    mouth = True
    totalPuntos = len(libres)

    items = []
    items_posiciones = []
    items_timer = pygame.time.get_ticks()
    
    special_item = False
    special_item_posicion = (-1,-1)
    special_item_timer = pygame.time.get_ticks()

    user_speed = 100
    enemies_speed = 700

    jugadores =[]
    player_colors = [(255,0,255), (0,255,255), (255,255,0)]
    for i in range(0, players_amount):
        # Get a random element from the list
        rand_color = random.choice(player_colors)
        # Remove the random element from the list
        player_colors.remove(rand_color)
        jugadores.append(Usuario(i+1, i+1, rand_color))
    #jugadores.append(Usuario(2, 2, (0,255,255)))
    #jugadores.append(Usuario(3, 3, (255,255,0)))
    #jugadores.append(Usuario(4, 4, (255,0,255)))


    jugadores_posiciones = []
    for jugador in jugadores:
        jugadores_posiciones.append((jugador.row,jugador.col))

    todos_jugadores = []
    for jugador in jugadores:
        todos_jugadores.append(jugador)
        
    special_colors = [
        (255, 0, 0),     # Red
        (255, 165, 0),   # Orange
        (255, 255, 0),   # Yellow
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (75, 0, 130),    # Indigo
        (148, 0, 211),   # Violet
        (255, 182, 193), # Pink
        (0, 255, 255),   # Cyan
        (128, 0, 128)    # Purple
    ]

    special_time_timer = pygame.time.get_ticks()
    special_time = False

    enemies_respawn_timer = pygame.time.get_ticks()    

    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pauseMenu(screen, width, height):
                        playing = False
                
        screen.fill((255, 255, 255))  # Clear the screen
        
        #Paint Footer
        paintFooter(screen, grid_size, grid_rows, grid_cols, len(todos_jugadores), todos_jugadores)
        # Paint Grid
        for i in range(0,grid_rows):
            for j in range(0, grid_cols):
                # Calculate the center of the cell
                cell_center_x = j * grid_size + grid_size // 2
                cell_center_y = i * grid_size + grid_size // 2
                            
                if grid[i][j] == 500:
                    pygame.draw.rect(screen, (154, 225, 249), (j*grid_size, i*grid_size, grid_size, grid_size))
                if grid[i][j] == 1000:
                    pygame.draw.rect(screen, (0, 0, 0), (j*grid_size, i*grid_size, grid_size, grid_size))
                if nuevos_puntos or grid[i][j] == 1:
                    # Draw a circle in the center of the cell
                    if nuevos_puntos and grid[i][j] not in {1000,0,3,4,5,500}:
                        grid[i][j] = 1
                    pygame.draw.circle(screen, (255, 165, 0), (cell_center_x, cell_center_y), circle_radius//2)
                if grid[i][j] == 3:
                    pygame.draw.circle(screen, (0, 255, 0), (cell_center_x, cell_center_y), circle_radius//2)
                if grid[i][j] == 4:
                    pygame.draw.circle(screen, random.choice(special_colors), (cell_center_x, cell_center_y), circle_radius//2)
                if grid[i][j] == 0:
                    pygame.draw.circle(screen, (100,100,100), (cell_center_x, cell_center_y), circle_radius//2)
        if nuevos_puntos:
            totalPuntos = len(libres)-len(items)
            if special_item:
                totalPuntos-=1
            nuevos_puntos = False
        
        # Calculate elapsed time since the last update
        curr_time = pygame.time.get_ticks()
        time_pased = curr_time - mouth_timer

        # Update the variable every 2 seconds
        if time_pased >= 200:  # 2000 milliseconds = 2 seconds
            mouth = not mouth
            mouth_timer = curr_time  # Update the last update time

        # Handle player input
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if current_time - laste_update_time > enemies_speed:
            for enemigo in enemigos:
                enemigo.pursue(grafo, nodos, jugadores, enemigos, libres, distancia_pursue, special_time)
            laste_update_time = current_time

        # Use a delay to control movement speed
        if todos_jugadores[0].vidas>0 and current_time - last_update_time > user_speed:
            if keys[pygame.K_LEFT]:
                todos_jugadores[0].orientation = "left"
                if todos_jugadores[0].col > 0:
                    if grid[todos_jugadores[0].row][todos_jugadores[0].col-1] in {0,1,2,3,4,5,500} and ((todos_jugadores[0].row,todos_jugadores[0].col-1) not in jugadores_posiciones):
                        todos_jugadores[0].col -= 1
                else:
                    if todos_jugadores[0].row > distancia_pursue or todos_jugadores[0].col > distancia_pursue:
                        if grid[todos_jugadores[0].row][grid_cols-1] in {0,1,2,3,4} and ((todos_jugadores[0].row,grid_cols-1) not in jugadores_posiciones):
                            todos_jugadores[0].col = grid_cols-1
            elif keys[pygame.K_RIGHT]:
                todos_jugadores[0].orientation = "right"
                if todos_jugadores[0].col < grid_cols - 1:
                    if grid[todos_jugadores[0].row][todos_jugadores[0].col+1] in {0,1,2,3,4,5,500} and ((todos_jugadores[0].row,todos_jugadores[0].col+1) not in jugadores_posiciones):
                        todos_jugadores[0].col += 1
                else:
                    if grid[todos_jugadores[0].row][0] in {0,1,2,3,4} and ((todos_jugadores[0].row,0) not in jugadores_posiciones):
                        todos_jugadores[0].col = 0
            elif keys[pygame.K_UP]:
                todos_jugadores[0].orientation = "top"
                if todos_jugadores[0].row > 0:
                    if grid[todos_jugadores[0].row-1][todos_jugadores[0].col] in {0,1,2,3,4,5,500} and ((todos_jugadores[0].row-1,todos_jugadores[0].col) not in jugadores_posiciones):
                        todos_jugadores[0].row -= 1
                else:
                    if todos_jugadores[0].row > distancia_pursue or todos_jugadores[0].col > distancia_pursue:
                        if grid[grid_rows-1][todos_jugadores[0].col] in {0,1,2,3,4} and ((grid_rows-1,todos_jugadores[0].col) not in jugadores_posiciones):
                            todos_jugadores[0].row = grid_rows-1
            elif keys[pygame.K_DOWN]:
                todos_jugadores[0].orientation = "bottom"
                if todos_jugadores[0].row < grid_rows - 1:
                    if grid[todos_jugadores[0].row+1][todos_jugadores[0].col] in {0,1,2,3,4,5,500} and ((todos_jugadores[0].row+1,todos_jugadores[0].col) not in jugadores_posiciones):
                        todos_jugadores[0].row += 1
                else:
                    if grid[0][todos_jugadores[0].col] in {0,1,2,3,4}  and ((0,todos_jugadores[0].col) not in jugadores_posiciones):
                        todos_jugadores[0].row = 0
            jugadores_posiciones[0] = (todos_jugadores[0].row,todos_jugadores[0].col)
            last_update_time = current_time
        
        # Use a delay to control movement speed
        if players_amount > 1 and todos_jugadores[1].vidas>0 and current_time - last2_update_time > user_speed:
            if keys[pygame.K_a]:
                todos_jugadores[1].orientation = "left"
                if todos_jugadores[1].col > 0:
                    if grid[todos_jugadores[1].row][todos_jugadores[1].col-1] in {0,1,2,3,4,5,500} and ((todos_jugadores[1].row,todos_jugadores[1].col-1) not in jugadores_posiciones):
                        todos_jugadores[1].col -= 1
                else:
                    if todos_jugadores[1].row > distancia_pursue or todos_jugadores[1].col > distancia_pursue:
                        if grid[todos_jugadores[1].row][grid_cols-1] in {0,1,2,3,4} and ((todos_jugadores[1].row,grid_cols-1) not in jugadores_posiciones):
                            todos_jugadores[1].col = grid_cols-1
            elif keys[pygame.K_d]:
                todos_jugadores[1].orientation = "right"
                if todos_jugadores[1].col < grid_cols - 1:
                    if grid[todos_jugadores[1].row][todos_jugadores[1].col+1] in {0,1,2,3,4,5,500} and ((todos_jugadores[1].row,todos_jugadores[1].col+1) not in jugadores_posiciones):
                        todos_jugadores[1].col += 1
                else:
                    if grid[todos_jugadores[1].row][0] in {0,1,2,3,4} and ((todos_jugadores[1].row,0) not in jugadores_posiciones):
                        todos_jugadores[1].col = 0
            elif keys[pygame.K_w]:
                todos_jugadores[1].orientation = "top"
                if todos_jugadores[1].row > 0:
                    if grid[todos_jugadores[1].row-1][todos_jugadores[1].col] in {0,1,2,3,4,5,500} and ((todos_jugadores[1].row-1,todos_jugadores[1].col) not in jugadores_posiciones):
                        todos_jugadores[1].row -= 1
                else:
                    if todos_jugadores[1].row > distancia_pursue or todos_jugadores[1].col > distancia_pursue:
                        if grid[grid_rows-1][todos_jugadores[1].col] in {0,1,2,3,4} and ((grid_rows-1,todos_jugadores[1].col) not in jugadores_posiciones):
                            todos_jugadores[1].row = grid_rows-1
            elif keys[pygame.K_s]:
                todos_jugadores[1].orientation = "bottom"
                if todos_jugadores[1].row < grid_rows - 1:
                    if grid[todos_jugadores[1].row+1][todos_jugadores[1].col] in {0,1,2,3,4,5,500} and ((todos_jugadores[1].row+1,todos_jugadores[1].col) not in jugadores_posiciones):
                        todos_jugadores[1].row += 1
                else:
                    if grid[0][todos_jugadores[1].col] in {0,1,2,3,4}  and ((0,todos_jugadores[1].col) not in jugadores_posiciones):
                        todos_jugadores[1].row = 0
            jugadores_posiciones[1] = (todos_jugadores[1].row,todos_jugadores[1].col)
            last2_update_time = current_time
        
        # Use a delay to control movement speed
        if players_amount > 2 and todos_jugadores[2].vidas>0 and current_time - last3_update_time > user_speed:
            if keys[pygame.K_h]:
                todos_jugadores[2].orientation = "left"
                if todos_jugadores[2].col > 0:
                    if grid[todos_jugadores[2].row][todos_jugadores[2].col-1] in {0,1,2,3,4,5,500} and ((todos_jugadores[2].row,todos_jugadores[2].col-1) not in jugadores_posiciones):
                        todos_jugadores[2].col -= 1
                else:
                    if todos_jugadores[2].row > distancia_pursue or todos_jugadores[2].col > distancia_pursue:
                        if grid[todos_jugadores[2].row][grid_cols-1] in {0,1,2,3,4} and ((todos_jugadores[2].row,grid_cols-1) not in jugadores_posiciones):
                            todos_jugadores[2].col = grid_cols-1
            elif keys[pygame.K_k]:
                todos_jugadores[2].orientation = "right"
                if todos_jugadores[2].col < grid_cols - 1:
                    if grid[todos_jugadores[2].row][todos_jugadores[2].col+1] in {0,1,2,3,4,5,500} and ((todos_jugadores[2].row,todos_jugadores[2].col+1) not in jugadores_posiciones):
                        todos_jugadores[2].col += 1
                else:
                    if grid[todos_jugadores[2].row][0] in {0,1,2,3,4} and ((todos_jugadores[2].row,0) not in jugadores_posiciones):
                        todos_jugadores[2].col = 0
            elif keys[pygame.K_u]:
                todos_jugadores[2].orientation = "top"
                if todos_jugadores[2].row > 0:
                    if grid[todos_jugadores[2].row-1][todos_jugadores[2].col] in {0,1,2,3,4,5,500} and ((todos_jugadores[2].row-1,todos_jugadores[2].col) not in jugadores_posiciones):
                        todos_jugadores[2].row -= 1
                else:
                    if todos_jugadores[2].row > distancia_pursue or todos_jugadores[2].col > distancia_pursue:
                        if grid[grid_rows-1][todos_jugadores[2].col] in {0,1,2,3,4} and ((grid_rows-1,todos_jugadores[2].col) not in jugadores_posiciones):
                            todos_jugadores[2].row = grid_rows-1
            elif keys[pygame.K_j]:
                todos_jugadores[2].orientation = "bottom"
                if todos_jugadores[2].row < grid_rows - 1:
                    if grid[todos_jugadores[2].row+1][todos_jugadores[2].col] in {0,1,2,3,4,5,500} and ((todos_jugadores[2].row+1,todos_jugadores[2].col) not in jugadores_posiciones):
                        todos_jugadores[2].row += 1
                else:
                    if grid[0][todos_jugadores[2].col] in {0,1,2,3,4}  and ((0,todos_jugadores[2].col) not in jugadores_posiciones):
                        todos_jugadores[2].row = 0
            jugadores_posiciones[2] = (todos_jugadores[2].row,todos_jugadores[2].col)
            last3_update_time = current_time
        
        # Update game state
        for jugador in jugadores:
            # Map grid position to screen coordinates
            circle_x = jugador.col * grid_size + grid_size // 2
            circle_y = jugador.row * grid_size + grid_size // 2

            # Draw the circle
            draw_square(screen, circle_x, circle_y, circle_radius*1.8, jugador.orientation, mouth, jugador.color)
            #pygame.draw.circle(screen, (0, 0, 255), (circle_x, circle_y), circle_radius)

            if grid[jugador.row][jugador.col] == 1:
                grid[jugador.row][jugador.col] = 2
                totalPuntos -= 1
                jugador.puntos += 1
                if totalPuntos == 0:
                    nuevos_puntos = True
                    totalPuntos = len(libres)-len(items)-1
                    if special_item:
                        totalPuntos-=1
                    jugador.puntos += 10
                
            if grid[jugador.row][jugador.col] == 3:
                grid[jugador.row][jugador.col] = 2
                for item in items:
                    if item.col == jugador.col and item.row == jugador.row:
                        items.remove(item)
                items_posiciones.remove((jugador.row,jugador.col))
                jugador.puntos += 5
                jugador.puntos2 += 1
            
            if grid[jugador.row][jugador.col] == 4:
                grid[jugador.row][jugador.col] = 2
                special_item = False
                special_item_posicion = (-1,-1)
                special_time = True
                pygame.mixer.music.load("./assets/musicSpecial.mp3")
                pygame.mixer.music.play(-1)
                special_time_timer = curr_time
          
        if special_time and ((curr_time - special_time_timer) >= 5000):
            special_time = False
            pygame.mixer.music.load("./assets/musicGame.mp3")
            pygame.mixer.music.play(-1)
            
        # Draw grid lines (optional)
        #for i in range(1, grid_cols):
        #    pygame.draw.line(screen, (128, 128, 128), (i * grid_size, 0), (i * grid_size, height))
        #for j in range(1, grid_rows):
        #    pygame.draw.line(screen, (128, 128, 128), (0, j * grid_size), (width, j * grid_size))

        items_time_passed = curr_time - items_timer

        if items_time_passed >= 5000:
            item_pos = random.choice(libres)
            if item_pos != special_item_posicion and item_pos not in jugadores_posiciones and item_pos not in items_posiciones and grid[item_pos[0]][item_pos[1]] == 2:
                items.append(Item(item_pos[0],item_pos[1],(0,255,0)))
                items_posiciones.append((item_pos[0],item_pos[1]))
                grid[item_pos[0]][item_pos[1]] = 3
                if len(items) == 4:
                    items.pop(0)
                    grid[items_posiciones[0][0]][items_posiciones[0][1]] = 2
                    items_posiciones.pop(0)
            items_timer = curr_time  # Update the last update time
            
        special_item_time_passed = curr_time - special_item_timer

        if special_item_time_passed >= 10000:
            special_item_pos = random.choice(libres)
            if len(enemigos)>0 and special_item == False and special_item_pos not in jugadores_posiciones and special_item_pos not in items_posiciones and grid[special_item_pos[0]][special_item_pos[1]] == 2:
                special_item = True
                special_item_posicion = special_item_pos
                grid[special_item_pos[0]][special_item_pos[1]] = 4
            special_item_timer = curr_time  # Update the last update time

        # Draw Enemies
        for enemigo in enemigos:
            # Map grid position to screen coordinates
            enemy_x = enemigo.col * grid_size + grid_size // 2
            enemy_y = enemigo.row * grid_size + grid_size // 2
            #pygame.draw.circle(screen, (255, 0, 0), (enemy_x, enemy_y), circle_radius)
            drawEnemy(screen, (enemy_x, enemy_y), circle_radius*0.8, special_time)
            for jugador in jugadores:    
                if enemigo.col == jugador.col and enemigo.row == jugador.row:
                    if not special_time:
                        pygame.mixer.Channel(1).play(pygame.mixer.Sound("./assets/musicError.mp3"))
                        jugador.vidas -= 1
                        pygame.mixer.Channel(1).stop()
                        if jugador.vidas != 0:
                            jugador.col = 1
                            jugador.row = 1
                        else:
                            jugadores.remove(jugador)
                            for i, pos in enumerate(jugadores_posiciones):
                                if pos == (jugador.row, jugador.col):
                                    jugadores_posiciones[i] = (-1, -1)
                            #jugadores_posiciones.remove((jugador.row, jugador.col))
                            if len(jugadores) == 0:
                                paintFooter(screen, grid_size, grid_rows, grid_cols, len(todos_jugadores), todos_jugadores)
                                playing = False
                                resultsMenu(screen, width, height, len(todos_jugadores), todos_jugadores)
                    else:
                        pygame.mixer.Channel(2).play(pygame.mixer.Sound("./assets/musicGain.mp3"))
                        enemigos.remove(enemigo)
                        pygame.mixer.Channel(2).stop()
                        jugador.puntos += 20
                            
        if (curr_time - enemies_respawn_timer) > 40000:
            for i in range(0, enemies_amount - len(enemigos)):
                enemigos.append(Enemigo(grid_rows//2, grid_cols//2, (255,0,0)))
            enemies_respawn_timer = curr_time
        # Refresh the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(45)
    pygame.mixer.music.load("./assets/musicMenu.mp3")
    pygame.mixer.music.play(-1)

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)
    
def instru():
    SCREEN = pygame.display.set_mode((700, 640))
    pygame.display.set_caption("PAC-MANIA")
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")
        
        OPTIONS_IMG = pygame.image.load("assets/Intruction.png")        
        SCREEN.blit(OPTIONS_IMG, (60, 150))

        OPTIONS_TEXT = get_font(40).render("HOW TO PLAY", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(350, 120))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(60, 40), 
                            text_input="BACK", font=get_font(25), base_color="Black", hovering_color="Red")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def credit():
    SCREEN = pygame.display.set_mode((720, 620))
    pygame.display.set_caption("PAC-MANIA")
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("CREDITS", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(360, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)
        
        CRED_IMG = pygame.image.load("assets/credits.png")        
        SCREEN.blit(CRED_IMG, (140, 340))

        OPTIONS_BACK = Button(image=None, pos=(88, 50), 
                            text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Red")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    SCREEN = pygame.display.set_mode((720, 720))
    pygame.display.set_caption("PAC-MANIA")
    BG = pygame.image.load("assets/Background.png")
    while True:
        seed = random.randint(1, 1000)

        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(50).render("PAC-MANIA", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(360, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(360, 250), 
                            text_input="PLAY", font=get_font(25), base_color="#d7fcd4", hovering_color="Green")
        INSTRU_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(360, 400), 
                            text_input="HOW TO PLAY", font=get_font(25), base_color="#d7fcd4", hovering_color="Yellow")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(360, 550), 
                            text_input="QUIT", font=get_font(25), base_color="#d7fcd4", hovering_color="Red")
        CREDITS_BUTTON = Button(image=None, pos=(100, 700), 
                            text_input="CREDITS", font=get_font(25), base_color="#d7fcd4", hovering_color="Gray")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, INSTRU_BUTTON, QUIT_BUTTON, CREDITS_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    game_settings = setGame()
                    if game_settings[0]:
                        game(seed, game_settings[1], game_settings[2], game_settings[3])
                        SCREEN = pygame.display.set_mode((720, 720))
                if INSTRU_BUTTON.checkForInput(MENU_MOUSE_POS):
                    instru()
                if CREDITS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    credit()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        
pygame.init()
pygame.mixer.music.load("./assets/musicMenu.mp3")
pygame.mixer.music.play(-1)
main_menu()