import random
import heapq

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
def a_star_solver(maze, start, end):
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
            if 0 <= nr < HEIGHT and 0 <= nc < WIDTH and maze[nr][nc] != '#':
                tentative_g = g_current + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
                    came_from[neighbor] = current
    return None

# Generate maze starting at (1,1)
generate_maze(1, 1)

# Mark start and end points
maze[1][1] = "S"
maze[HEIGHT-2][WIDTH-2] = "E"

# Print column numbers
print("   " + "".join(f"{i%10}" for i in range(WIDTH)))

# Print maze with row numbers
for idx, row in enumerate(maze):
    print(f"{idx%10:2} " + "".join(row))

# Solve maze with A*
a_star_path = a_star_solver(maze, (1,1), (HEIGHT-2, WIDTH-2))

# Optional: mark A* path in maze
if a_star_path:
    for r, c in a_star_path:
        if maze[r][c] == " ":
            maze[r][c] = "."
    print("\nMaze with A* path (dots):")
    print("   " + "".join(f"{i%10}" for i in range(WIDTH)))
    for idx, row in enumerate(maze):
        print(f"{idx%10:2} " + "".join(row))