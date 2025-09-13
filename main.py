import pygame
import random
import heapq

# --- Your Maze Generation and Solving Logic (Untouched) ---

# Maze dimensions (odd numbers)
WIDTH, HEIGHT = 21, 21

# Initialize maze full of walls
maze = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Directions (dx, dy)
DIRS = [(-2, 0), (2, 0), (0, -2), (0, 2)]

# Recursive DFS Maze Generator
def generate_maze(x, y):
    maze[y][x] = " "  # mark passage
    directions = DIRS[:]
    random.shuffle(directions)

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 < nx < WIDTH-1 and 0 < ny < HEIGHT-1:
            if maze[ny][nx] == "#":  # unvisited
                maze[y + dy//2][x + dx//2] = " "  # carve wall
                generate_maze(nx, ny)

# A* Solver
def a_star_solver(maze_data, start, end):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, end), 0, start))
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, g_current, current = heapq.heappop(open_set)

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)
            if 0 <= nr < HEIGHT and 0 <= nc < WIDTH and maze_data[nr][nc] != '#':
                tentative_g = g_current + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
                    came_from[neighbor] = current
    return None

# --- New Pygame Visualization Code ---

# Constants for drawing
CELL_SIZE = 30
SCREEN_WIDTH = WIDTH * CELL_SIZE
SCREEN_HEIGHT = HEIGHT * CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

def draw_maze(screen, maze_data, path):
    """Draws the maze and the path onto the screen."""
    screen.fill(BLACK)
    for y, row in enumerate(maze_data):
        for x, char in enumerate(row):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = BLACK
            if char == ' ':
                color = WHITE
            elif char == 'S':
                color = GREEN
            elif char == 'E':
                color = RED
            
            pygame.draw.rect(screen, color, rect)

    # Draw the solved path on top
    if path:
        for r, c in path:
             if maze_data[r][c] not in ('S', 'E'):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, YELLOW, rect)


def main():
    """Main function to run the Pygame app."""
    # --- Generate and Solve the Maze First ---
    generate_maze(1, 1)

    # Mark start and end points
    start_pos = (1, 1)
    end_pos = (HEIGHT-2, WIDTH-2)
    maze[start_pos[0]][start_pos[1]] = "S"
    maze[end_pos[0]][end_pos[1]] = "E"
    
    # Solve the maze
    solved_path = a_star_solver(maze, start_pos, end_pos)

    # --- Initialize Pygame and Create Window ---
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Generator and A* Solver")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # --- Drawing ---
        draw_maze(screen, maze, solved_path)
        pygame.display.flip()

    pygame.quit()

# Run the main function when the script is executed
if __name__ == "__main__":
    main()