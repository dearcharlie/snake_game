#!/usr/bin/env python3
"""
贪吃蛇游戏 - Cross-platform Snake Game
Author: Hermes User
"""

import pygame
import random
import sys
import os

# 配置
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
FPS = 10
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT + 60  # 60 for score bar

# 颜色
BG_COLOR = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
SNAKE_HEAD_COLOR = (0, 200, 0)
SNAKE_BODY_COLOR = (0, 150, 0)
FOOD_COLOR = (255, 80, 80)
TEXT_COLOR = (255, 255, 255)
SCORE_BG_COLOR = (40, 40, 40)

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = RIGHT
        self.grow = False

    @property
    def head(self):
        return self.body[0]

    def move(self):
        head_x, head_y = self.head
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            return False

        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)

        if self.grow:
            self.grow = False
        else:
            self.body.pop()

        return True

    def check_food(self, food_pos):
        return self.head == food_pos


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.respawn([])

    def respawn(self, snake_body):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_body:
                self.position = pos
                break


class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('贪吃蛇 - Snake Game')
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.high_score = self.load_high_score()
        self.reset()

    def load_high_score(self):
        try:
            with open('snake_highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            try:
                with open('snake_highscore.txt', 'w') as f:
                    f.write(str(score))
            except:
                pass

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.game_over = False
        self.paused = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.snake.direction != DOWN:
                            self.snake.direction = UP
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.snake.direction != UP:
                            self.snake.direction = DOWN
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.snake.direction != RIGHT:
                            self.snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.snake.direction != LEFT:
                            self.snake.direction = RIGHT
                    elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused

        return True

    def update(self):
        if self.game_over or self.paused:
            return

        if not self.snake.move():
            self.game_over = True
            self.save_high_score(self.score)
            return

        if self.snake.check_food(self.food.position):
            self.snake.grow = True
            self.food.respawn(self.snake.body)
            self.score += 10

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 60), (x, WINDOW_HEIGHT))
        for y in range(60, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def draw_score_bar(self):
        pygame.draw.rect(self.screen, SCORE_BG_COLOR, (0, 0, WINDOW_WIDTH, 60))
        pygame.draw.line(self.screen, GRID_COLOR, (0, 58), (WINDOW_WIDTH, 58), 2)

        score_text = self.font.render(f'Score: {self.score}', True, TEXT_COLOR)
        high_text = self.font.render(f'Best: {self.high_score}', True, (200, 200, 100))
        hint_text = self.font.render('P:Pause W/S/A/D:Move', True, (150, 150, 150))

        self.screen.blit(score_text, (20, 18))
        self.screen.blit(high_text, (200, 18))
        self.screen.blit(hint_text, (420, 18))

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake.body):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            pygame.draw.rect(
                self.screen, color,
                (x * CELL_SIZE + 1, y * CELL_SIZE + 61, CELL_SIZE - 2, CELL_SIZE - 2),
                border_radius=4
            )

    def draw_food(self):
        x, y = self.food.position
        pygame.draw.rect(
            self.screen, FOOD_COLOR,
            (x * CELL_SIZE + 2, y * CELL_SIZE + 62, CELL_SIZE - 4, CELL_SIZE - 4),
            border_radius=4
        )

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.big_font.render('GAME OVER', True, (255, 100, 100))
        score_text = self.font.render(f'Score: {self.score}', True, TEXT_COLOR)
        restart_text = self.font.render('Press ENTER to restart', True, (150, 150, 150))
        esc_text = self.font.render('Press ESC to quit', True, (150, 150, 150))

        self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 280))
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 340))
        self.screen.blit(esc_text, (WINDOW_WIDTH // 2 - esc_text.get_width() // 2, 380))

    def draw_paused(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        paused_text = self.big_font.render('PAUSED', True, (255, 255, 100))
        hint_text = self.font.render('Press P to continue', True, (150, 150, 150))

        self.screen.blit(paused_text, (WINDOW_WIDTH // 2 - paused_text.get_width() // 2, 250))
        self.screen.blit(hint_text, (WINDOW_WIDTH // 2 - hint_text.get_width() // 2, 330))

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_grid()
        self.draw_score_bar()
        self.draw_food()
        self.draw_snake()

        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_paused()

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        return 0


def main():
    # Windows 下隐藏控制台
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    game = SnakeGame()
    return game.run()


if __name__ == '__main__':
    sys.exit(main())
