#!/usr/bin/env python3
"""
Snake Game - Cross-platform Console Version
Works in CI/headless environments without display
"""

import curses
import random
import sys
import os

# Stdscr will be set in main()
stdscr = None

# Game config
WIDTH = 40
HEIGHT = 20
SPEED = 100  # ms between moves

# Characters
SNAKE_HEAD = 'O'
SNAKE_BODY = 'o'
FOOD = '*'
WALL = '#'
EMPTY = ' '


def create_food(snake, height, width):
    """Place food avoiding snake body"""
    while True:
        fy = random.randint(1, height - 2)
        fx = random.randint(1, width - 2)
        if (fy, fx) not in snake:
            return (fy, fx)


def draw_border(win, height, width):
    """Draw border"""
    for x in range(width):
        win.addch(0, x, WALL)
        win.addch(height - 1, x, WALL)
    for y in range(height):
        win.addch(y, 0, WALL)
        win.addch(y, width - 1, WALL)


def main(stdscr):
    global stdscr
    stdscr = curses.initscr()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(SPEED)

    # Colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    # Initial state
    sh, sw = stdscr.getmaxyx()
    if sh < HEIGHT + 2 or sw < WIDTH + 2:
        stdscr.nodelay(False)
        stdscr.addstr(0, 0, f"Terminal too small ({sh}x{sw}), need {HEIGHT+2}x{WIDTH+2}")
        stdscr.getch()
        return

    # Create window for game area
    game_win = curses.newwin(HEIGHT + 2, WIDTH + 2, 0, 0)
    game_win.keypad(True)
    game_win.timeout(SPEED)

    # Init snake in center
    snake = [
        (HEIGHT // 2, WIDTH // 2 + 1),
        (HEIGHT // 2, WIDTH // 2),
        (HEIGHT // 2, WIDTH // 2 - 1),
    ]
    direction = curses.KEY_RIGHT

    food = create_food(snake, HEIGHT, WIDTH)
    score = 0
    high_score = load_high_score()

    # Title
    title_win = curses.newwin(3, WIDTH + 2, HEIGHT + 2, 0)
    title_win.addstr(1, 2, f"SNAKE  |  Score: {score}  |  Best: {high_score}  |  WASD/Arrows: Move  |  Q: Quit")
    title_win.timeout(0)

    running = True
    game_over = False

    while running:
        # Draw
        game_win.clear()
        draw_border(game_win, HEIGHT, WIDTH)

        # Draw food
        game_win.addch(food[0], food[1], FOOD, curses.color_pair(2))

        # Draw snake
        for i, (y, x) in enumerate(snake):
            ch = SNAKE_HEAD if i == 0 else SNAKE_BODY
            color = curses.color_pair(1)
            try:
                game_win.addch(y, x, ch, color)
            except curses.error:
                pass

        if game_over:
            msg = f" GAME OVER! Score: {score} "
            game_win.addstr(HEIGHT // 2, (WIDTH - len(msg)) // 2, msg, curses.color_pair(2))
            msg2 = " Press R to restart or Q to quit "
            game_win.addstr(HEIGHT // 2 + 1, (WIDTH - len(msg2)) // 2, msg2)

        title_win.clear()
        title_win.addstr(1, 2, f"SNAKE  |  Score: {score}  |  Best: {high_score}  |  WASD/Arrows: Move  |  Q: Quit")
        title_win.refresh()

        game_win.refresh()

        # Input
        try:
            key = game_win.getch()
        except curses.error:
            key = -1

        if key != -1:
            if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                # Can't reverse direction
                opposite = {
                    curses.KEY_UP: curses.KEY_DOWN,
                    curses.KEY_DOWN: curses.KEY_UP,
                    curses.KEY_LEFT: curses.KEY_RIGHT,
                    curses.KEY_RIGHT: curses.KEY_LEFT,
                }
                if direction != opposite.get(key):
                    direction = key
            elif key in [ord('w'), ord('W'), ord('s'), ord('S'), ord('a'), ord('A'), ord('d'), ord('D')]:
                new_dir = {
                    ord('w'): curses.KEY_UP, ord('W'): curses.KEY_UP,
                    ord('s'): curses.KEY_DOWN, ord('S'): curses.KEY_DOWN,
                    ord('a'): curses.KEY_LEFT, ord('A'): curses.KEY_LEFT,
                    ord('d'): curses.KEY_RIGHT, ord('D'): curses.KEY_RIGHT,
                }[key]
                opposite = {
                    curses.KEY_UP: curses.KEY_DOWN,
                    curses.KEY_DOWN: curses.KEY_UP,
                    curses.KEY_LEFT: curses.KEY_RIGHT,
                    curses.KEY_RIGHT: curses.KEY_LEFT,
                }
                if direction != opposite.get(new_dir):
                    direction = new_dir
            elif key in [ord('q'), ord('Q')]:
                running = False
                continue
            elif key in [ord('r'), ord('R')] and game_over:
                # Restart
                snake = [
                    (HEIGHT // 2, WIDTH // 2 + 1),
                    (HEIGHT // 2, WIDTH // 2),
                    (HEIGHT // 2, WIDTH // 2 - 1),
                ]
                direction = curses.KEY_RIGHT
                food = create_food(snake, HEIGHT, WIDTH)
                score = 0
                game_over = False
                continue

        if game_over:
            curses.napms(50)
            continue

        # Move snake
        head_y, head_x = snake[0]
        dir_map = {
            curses.KEY_UP: (-1, 0),
            curses.KEY_DOWN: (1, 0),
            curses.KEY_LEFT: (0, -1),
            curses.KEY_RIGHT: (0, 1),
        }
        dy, dx = dir_map.get(direction, (0, 1))
        new_head = (head_y + dy, head_x + dx)

        # Collision detection
        if (new_head[0] in [0, HEIGHT - 1] or
            new_head[1] in [0, WIDTH - 1] or
            new_head in snake):
            game_over = True
            if score > high_score:
                save_high_score(score)
                high_score = score
            continue

        snake.insert(0, new_head)

        # Eat food
        if new_head == food:
            score += 10
            food = create_food(snake, HEIGHT, WIDTH)
        else:
            snake.pop()

    curses.endwin()
    return score


def load_high_score():
    try:
        with open('snake_highscore.txt', 'r') as f:
            return int(f.read().strip())
    except:
        return 0


def save_high_score(score):
    try:
        with open('snake_highscore.txt', 'w') as f:
            f.write(str(score))
    except:
        pass


if __name__ == '__main__':
    # Handle terminal resize
    def resize_handler(sig, frame):
        pass  # We'll handle this in-game
    import signal
    signal.signal(signal.SIGWINCH, resize_handler)

    # Run with curses wrapper
    result = curses.wrapper(main)
    sys.exit(0 if result is None else result)
