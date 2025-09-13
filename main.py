import pygame
import random
import heapq
import asyncio  # Import the asyncio library

# --- Pygame Setup ---
SCREEN_WIDTH, SCREEN_HEIGHT = 630, 630
CELL_SIZE = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WIDTH, HEIGHT = 21, 21
DIRS = [(-2, 0), (2, 0), (0, -2), (0, 2)]

# --- Maze Logic ---
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

# --- Player Sprite ---
class Player(pygame.sprite.Sprite):
    def __init__(self, row, col):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.row, self.col = row, col
        self.update_position()

    def update_position(self):
        self.rect.topleft = (self.col * CELL_SIZE + 2, self.row * CELL_SIZE + 2)

    def move(self, dr, dc):
        new_row, new_col = self.row + dr, self.col + dc
        if 0 <= new_row < HEIGHT and 0 <= new_col < WIDTH:
            if maze[new_row][new_col] != "#":  # not a wall
                self.row, self.col = new_row, new_col
                self.update_position()

# --- Async Main Loop ---
async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Escape")

    # Maze generation
    generate_maze(1, 1)
    maze[1][1] = "S"
    maze[HEIGHT - 2][WIDTH - 2] = "E"

    # Solve for path (optional visualization)
    start_pos = (1, 1)
    end_pos = (HEIGHT - 2, WIDTH - 2)
    maze_for_solver = [row[:] for row in maze]
    a_star_path = a_star_solver(maze_for_solver, start_pos, end_pos)

    # Create player
    player = Player(1, 1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(-1, 0)
                elif event.key == pygame.K_DOWN:
                    player.move(1, 0)
                elif event.key == pygame.K_LEFT:
                    player.move(0, -1)
                elif event.key == pygame.K_RIGHT:
                    player.move(0, 1)

        screen.fill(BLACK)
        draw_maze(screen, a_star_path)
        screen.blit(player.image, player.rect)
        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())