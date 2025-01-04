import pygame
import random
import queue
import sys
import numpy as np

# Constants
BLOCK_SIZE = 22

# Initialize PyGame
pygame.init()


class Maze:
    def __init__(self, layout):
        self.layout = layout
        self.height, self.width = np.shape(layout)

    def is_valid(self, pos):
        i, j = pos
        return 0 <= i < self.height and 0 <= j < self.width

    def is_boundary(self, pos):
        i, j = pos
        return self.layout[i][j] == 1

    def is_enemy(self, pos):
        i, j = pos
        return self.layout[i][j] == 5

    def update_cell(self, pos, value):
        i, j = pos
        self.layout[i][j] = value


class Character:
    def __init__(self, maze, image_path):
        self.maze = maze
        self.position = self.find_initial_position()
        self.image = pygame.image.load(image_path).convert_alpha()

    def find_initial_position(self):
        for i in range(self.maze.height):
            for j in range(self.maze.width):
                if self.maze.layout[i][j] == 3:
                    self.maze.update_cell((i, j), 0)
                    return i, j

    def move_to(self, pos):
        self.position = pos


class Enemy:
    def __init__(self, maze, image_path):
        self.maze = maze
        self.image = pygame.image.load(image_path).convert_alpha()
        self.position = self.spawn()

    def spawn(self):
        while True:
            pos = (random.randint(0, self.maze.height - 1), random.randint(0, self.maze.width - 1))
            if self.maze.layout[pos[0]][pos[1]] == 0:
                self.maze.update_cell(pos, 5)
                return pos


class Food:
    def __init__(self, maze, image_path):
        self.maze = maze
        self.image = pygame.image.load(image_path).convert_alpha()
        self.position = self.spawn()

    def spawn(self):
        while True:
            pos = (random.randint(0, self.maze.height - 1), random.randint(0, self.maze.width - 1))
            if self.maze.layout[pos[0]][pos[1]] == 0:
                self.maze.update_cell(pos, 2)
                return pos


class Game:
    def __init__(self, maze_layout):
        self.maze = Maze(maze_layout)
        self.character = Character(self.maze, "main2.png")
        self.enemies = [Enemy(self.maze, "pinky2.png") for _ in range(4)]
        self.food = Food(self.maze, "food2.png")
        self.score = 0
        self.game_over = False

        # Set up PyGame
        self.screen = pygame.display.set_mode((self.maze.width * BLOCK_SIZE, self.maze.height * BLOCK_SIZE))
        pygame.display.set_caption("BFS Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 22)

        # Load Images
        self.boundary_image = pygame.image.load("bg1.png")
        self.free_space_image = pygame.image.load("bg2.png")

    def draw_grid(self):
        for i in range(self.maze.height):
            for j in range(self.maze.width):
                pos = (j * BLOCK_SIZE, i * BLOCK_SIZE)
                if self.maze.layout[i][j] == 1:
                    self.screen.blit(self.boundary_image, pos)
                elif self.maze.layout[i][j] == 0:
                    self.screen.blit(self.free_space_image, pos)
                elif self.maze.layout[i][j] == 2:
                    self.screen.blit(self.food.image, pos)
                elif self.maze.layout[i][j] == 5:
                    self.screen.blit(self.enemies[0].image, pos)

        self.screen.blit(self.character.image, (self.character.position[1] * BLOCK_SIZE, self.character.position[0] * BLOCK_SIZE))

    def find_path_to_food(self):
        bfs_queue = queue.Queue()
        visited = set()
        prev = {}

        # Start BFS
        bfs_queue.put(self.character.position)
        visited.add(self.character.position)

        while not bfs_queue.empty():
            curr_pos = bfs_queue.get()
            i, j = curr_pos

            for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_pos = (i + di, j + dj)
                if self.maze.is_valid(new_pos) and not self.maze.is_boundary(new_pos) and new_pos not in visited and not self.maze.is_enemy(new_pos):
                    bfs_queue.put(new_pos)
                    visited.add(new_pos)
                    prev[new_pos] = curr_pos
                    if new_pos == self.food.position:
                        path = []
                        while new_pos in prev:
                            path.append(new_pos)
                            new_pos = prev[new_pos]
                        return path[::-1]

        return []

    def update_game_state(self):
        path = self.find_path_to_food()
        if path:
            self.character.move_to(path[0])
        if self.character.position == self.food.position:
            self.score += 1
            self.food = Food(self.maze, "food2.png")

    def display_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill((0, 0, 0))
            self.draw_grid()
            self.update_game_state()
            self.display_score()

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    maze_layout = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]

    game = Game(maze_layout)
    game.run()
