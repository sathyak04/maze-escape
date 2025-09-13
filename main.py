import pygame
import random
import heapq
import asyncio  # Import the asyncio library

# --- Pygame Setup ---
# Constants are defined outside the main function
SCREEN_WIDTH, SCREEN_HEIGHT = 630, 630
CELL_SIZE = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WIDTH, HEIGHT = 21, 21
DIRS = [(-2, 0), (2, 0), (0, -2), (0, 2)]

# --- Maze Logic ---
# Maze is now a global variable to be accessed by functions
maze = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

def generate_maze(x, y):
    maze[y][x] = " "
    directions = DIRS[:]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 < nx < WIDTH - 1 and 0 < ny < HEIGHT - 1 and maze[ny][nx] == "#":
            maze[y + dy // 2][x + dx // 2] = " "
            generate_maze(nx, ny)

def a_star_solver(maze_layout, start, end):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    open_set = []
    heapq.heappush(open_set, (heuristic(start, end), 0, start))
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
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)
            if 0 <= nr < HEIGHT and 0 <= nc < WIDTH and maze_layout[nr][nc] != '#':
                tentative_g = g_current + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
                    came_from[neighbor] = current
    return None

def draw_maze(surface, solved_path):
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = WHITE
            if cell == "#":
                color = BLACK
            elif cell == "S":
                color = GREEN
            elif cell == "E":
                color = RED
            pygame.draw.rect(surface, color, rect)
    if solved_path:
        for r, c in solved_path:
            if maze[r][c] not in ["S", "E"]:
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, YELLOW, rect)

# Create an async main function that pygbag can run
async def main():
    print("Initializing Pygame...")
    pygame.init()
    
    print("Setting up Pygame screen...")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Escape")

    # --- Maze Generation and Solving ---
    print("Generating Maze...")
    generate_maze(1, 1)
    maze[1][1] = "S"
    maze[HEIGHT - 2][WIDTH - 2] = "E"
    
    print("Solving Maze with A*...")
    start_pos = (1, 1)
    end_pos = (HEIGHT - 2, WIDTH - 2)
    maze_for_solver = [row[:] for row in maze]
    a_star_path = a_star_solver(maze_for_solver, start_pos, end_pos)

    print("Starting main game loop...")
    # The main loop is now 'while True'
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return  # Exit the function to stop the game

        screen.fill(BLACK)
        draw_maze(screen, a_star_path)
        pygame.display.flip()

        # This is the crucial line: it gives control back to the browser
        await asyncio.sleep(0)

# This is the entry point for the script
if __name__ == "__main__":
    asyncio.run(main())