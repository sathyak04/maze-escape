import pygame
import random
import heapq
import asyncio
import time

# --- Pygame Setup ---
pygame.mixer.pre_init(44100, -16, 2, 512) # Pre-initialize mixer for better performance
pygame.init() # Moved init here to use fonts globally
SCREEN_WIDTH, SCREEN_HEIGHT = 630, 710  # Maze (630) + 2 Buttons (80)
CELL_SIZE = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WIDTH, HEIGHT = 21, 21
DIRS = [(-2, 0), (2, 0), (0, -2), (0, 2)]

# --- Fonts ---
# Using a fallback font in case pixel.ttf is not found
try:
    FONT = pygame.font.Font("pixel.ttf", 20)
    TITLE_FONT = pygame.font.Font("pixel.ttf", 32)
    SCORE_FONT = pygame.font.Font("pixel.ttf", 25)
except FileNotFoundError:
    FONT = pygame.font.Font(None, 24)
    TITLE_FONT = pygame.font.Font(None, 36)
    SCORE_FONT = pygame.font.Font(None, 28)


# --- Score ---
score = 0

# --- Sprites ---
# Using placeholders in case images are not found
try:
    PLAYER_IMAGE_PATH = "mushroom.png"
    FINISH_IMAGE_PATH = "star.png"
    player_sprite_image = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
    finish_sprite = pygame.image.load(FINISH_IMAGE_PATH).convert_alpha()
except FileNotFoundError:
    # Create simple colored surfaces as fallbacks
    player_sprite_image = pygame.Surface((CELL_SIZE-4, CELL_SIZE-4))
    player_sprite_image.fill(GREEN)
    finish_sprite = pygame.Surface((CELL_SIZE-4, CELL_SIZE-4))
    finish_sprite.fill((255, 0, 0)) # Red

# --- Sounds ---
class DummySound:
    def play(self): pass

# NOTE: Pygame works best with .wav or .ogg files.
try:
    WIN_SOUND_PATH = "win.wav"  # Sound for reaching the star
    win_sound = pygame.mixer.Sound(WIN_SOUND_PATH)
except (pygame.error, FileNotFoundError):
    win_sound = DummySound()

try:
    MOVE_SOUND_PATH = "move.wav" # Sound for player movement
    move_sound = pygame.mixer.Sound(MOVE_SOUND_PATH)
except (pygame.error, FileNotFoundError):
    move_sound = DummySound()


finish_sprite = pygame.transform.scale(finish_sprite, (CELL_SIZE-4, CELL_SIZE-4))

# --- Maze Logic ---
maze = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

def generate_maze(x, y):
    stack = [(x, y)]
    maze[y][x] = " "

    while stack:
        cx, cy = stack[-1]
        directions = DIRS[:]
        random.shuffle(directions)

        carved = False
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 < nx < WIDTH - 1 and 0 < ny < HEIGHT - 1 and maze[ny][nx] == "#":
                maze[cy + dy // 2][cx + dx // 2] = " "
                maze[ny][nx] = " "
                stack.append((nx, ny))
                carved = True
                break
        if not carved:
            stack.pop()

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
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = current[0]+dr, current[1]+dc
            neighbor = (nr, nc)
            if 0 <= nr < HEIGHT and 0 <= nc < WIDTH and maze_layout[nr][nc] != '#':
                tentative_g = g_current + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
                    came_from[neighbor] = current
    return None

def draw_maze(surface, solved_path, show_solution):
    """
    Rewritten to correctly handle coloring the solution path, including the end cell.
    """
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Determine the background color first
            if show_solution and solved_path and (r, c) in solved_path:
                # If the solution is active and this cell is on the path, it's yellow.
                pygame.draw.rect(surface, YELLOW, rect)
            elif cell == "#":
                pygame.draw.rect(surface, BLACK, rect)
            else:
                # Otherwise, it's a regular white floor tile.
                pygame.draw.rect(surface, WHITE, rect)

            # Draw the star sprite on top of the background (yellow or white)
            if cell == "E":
                surface.blit(finish_sprite, (c * CELL_SIZE + 2, r * CELL_SIZE + 2))

def draw_button(surface, text, rect, active=True):
    color = WHITE if active else (120,120,120)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)
    label = FONT.render(text, True, BLACK)
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)

# --- Separate Title and Score Functions ---
def draw_title(surface):
    # Title: "THE MUSH" (white) + "ROOMS" (red)
    part1 = TITLE_FONT.render("THE MUSH", True, WHITE)
    part2 = TITLE_FONT.render("ROOMS", True, (255, 0, 0))  # red
    y_pos = SCREEN_HEIGHT - 100
    surface.blit(part1, (50, y_pos))
    surface.blit(part2, (50 + part1.get_width(), y_pos))

def draw_score(surface):
    y_pos = SCREEN_HEIGHT - 100
    score_text = SCORE_FONT.render(f"SCORE: {score}", True, RED)
    surface.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 100, y_pos - 610))
    instruction_text = SCORE_FONT.render("USE ARROW OR WASD KEYS TO MOVE", True, WHITE)
    surface.blit(instruction_text, (score_text.get_rect().right + 215, y_pos + 5))

# --- Player ---
class Player(pygame.sprite.Sprite):
    def __init__(self, row, col):
        super().__init__()
        self.image = pygame.transform.scale(player_sprite_image, (CELL_SIZE-4, CELL_SIZE-4))
        self.rect = self.image.get_rect()
        self.row, self.col = int(row), int(col)
        self.x = self.col*CELL_SIZE + 2
        self.y = self.row*CELL_SIZE + 2
        self.target_x = self.x
        self.target_y = self.y
        self.speed = 6
        self.moving = False
        self.rect.topleft = (int(self.x), int(self.y))

    def update(self):
        if self.x < self.target_x:
            self.x = min(self.x + self.speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - self.speed, self.target_x)
        if self.y < self.target_y:
            self.y = min(self.y + self.speed, self.target_y)
        elif self.y > self.target_y:
            self.y = max(self.y - self.speed, self.target_y)
        self.rect.topleft = (int(self.x), int(self.y))
        if self.x == self.target_x and self.y == self.target_y:
            self.moving = False
            self.row = (self.y - 2)//CELL_SIZE
            self.col = (self.x - 2)//CELL_SIZE

    def move(self, dr, dc):
        if self.moving:
            return
        new_row = self.row + dr
        new_col = self.col + dc
        if 0 <= new_row < HEIGHT and 0 <= new_col < WIDTH and maze[new_row][new_col] != "#":
            # Play move sound on successful move
            move_sound.play()
            self.row = new_row
            self.col = new_col
            self.target_x = self.col*CELL_SIZE + 2
            self.target_y = self.row*CELL_SIZE + 2
            self.moving = True

# --- Reset ---
def reset_game():
    global maze
    for r in range(HEIGHT):
        for c in range(WIDTH):
            maze[r][c] = "#"
    generate_maze(1,1)

    # Get all open cells
    open_cells = [(r, c) for r in range(HEIGHT) for c in range(WIDTH) if maze[r][c] == " "]

    # Pick player start
    start = random.choice(open_cells)
    # Pick finish, far enough from start
    finish = random.choice([cell for cell in open_cells if abs(cell[0]-start[0])+abs(cell[1]-start[1]) > 6])
    maze[finish[0]][finish[1]] = "E"

    player = Player(start[0], start[1])
    # Path does not need to be calculated here anymore, it's done on-demand
    return player, finish  # return finish position as well

# --- Main Loop ---
async def main():
    global score
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("The MushROOMS")

    reset_button = pygame.Rect(100, SCREEN_HEIGHT - 55, 180, 30)
    solution_button = pygame.Rect(330, SCREEN_HEIGHT - 55, 180, 30)

    player, finish_pos = reset_game()
    a_star_path = None # Path is now calculated when needed
    show_solution = False
    solution_timer = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    player.move(-1,0)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    player.move(1,0)
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    player.move(0,-1)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    player.move(0,1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button.collidepoint(event.pos):
                    player, finish_pos = reset_game()
                    show_solution = False
                    a_star_path = None
                elif solution_button.collidepoint(event.pos):
                    # MODIFICATION: Calculate path from player's current position
                    a_star_path = a_star_solver(maze, (player.row, player.col), finish_pos)
                    show_solution = True
                    solution_timer = time.time()

        # Hide solution after 1s
        if show_solution and time.time() - solution_timer >= 1:
            show_solution = False

        # Win condition
        if (player.row, player.col) == finish_pos:
            score += 1
            win_sound.play() # Play the sound when the player wins
            player, finish_pos = reset_game()
            show_solution = False
            a_star_path = None

        # Update sliding
        player.update()

        # Draw
        screen.fill(BLACK)
        draw_maze(screen, a_star_path, show_solution)
        screen.blit(player.image, player.rect)
        draw_title(screen)
        draw_score(screen)
        draw_button(screen, "RESET MAZE", reset_button)
        draw_button(screen, "SHOW SOLUTION", solution_button)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())

