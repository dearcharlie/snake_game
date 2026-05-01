use rand::Rng;
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    pub x: i32,
    pub y: i32,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum Direction {
    Up,
    Down,
    Left,
    Right,
}

fn are_opposite(a: Direction, b: Direction) -> bool {
    matches!(
        (a, b),
        (Direction::Up, Direction::Down)
            | (Direction::Down, Direction::Up)
            | (Direction::Left, Direction::Right)
            | (Direction::Right, Direction::Left)
    )
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnakeSegment {
    pub x: i32,
    pub y: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameState {
    pub snake: Vec<SnakeSegment>,
    pub food: Position,
    pub direction: Direction,
    pub next_direction: Direction,
    pub score: i32,
    pub high_score: i32,
    pub game_over: bool,
    pub grid_width: i32,
    pub grid_height: i32,
    pub speed: u32,
}

impl Default for GameState {
    fn default() -> Self {
        Self {
            snake: vec![],
            food: Position { x: 0, y: 0 },
            direction: Direction::Right,
            next_direction: Direction::Right,
            score: 0,
            high_score: 0,
            game_over: false,
            grid_width: 30,
            grid_height: 20,
            speed: 100,
        }
    }
}

pub struct GameManager {
    state: Mutex<GameState>,
}

impl GameManager {
    pub fn new() -> Self {
        let manager = Self {
            state: Mutex::new(GameState::default()),
        };
        manager.do_reset();
        manager
    }

    fn do_reset(&self) {
        let mut state = self.state.lock().unwrap();
        let grid_width = state.grid_width;
        let grid_height = state.grid_height;
        let high_score = state.high_score;
        let speed = state.speed;

        let start_x = grid_width / 2;
        let start_y = grid_height / 2;

        let snake = vec![
            SnakeSegment { x: start_x, y: start_y },
            SnakeSegment { x: start_x - 1, y: start_y },
            SnakeSegment { x: start_x - 2, y: start_y },
        ];

        let food = Self::random_food_internal(&snake, grid_width, grid_height);

        *state = GameState {
            snake,
            food,
            direction: Direction::Right,
            next_direction: Direction::Right,
            score: 0,
            high_score,
            game_over: false,
            grid_width,
            grid_height,
            speed,
        };
    }

    fn random_food_internal(snake: &[SnakeSegment], grid_width: i32, grid_height: i32) -> Position {
        let mut rng = rand::thread_rng();
        loop {
            let x = rng.gen_range(1..grid_width - 1);
            let y = rng.gen_range(1..grid_height - 1);
            if !snake.iter().any(|s| s.x == x && s.y == y) {
                return Position { x, y };
            }
        }
    }

    pub fn set_direction(&self, dir: Direction) {
        let mut state = self.state.lock().unwrap();
        if !state.game_over && !are_opposite(dir, state.direction) {
            state.next_direction = dir;
        }
    }

    pub fn tick(&self) -> GameState {
        let mut state = self.state.lock().unwrap();

        if state.game_over {
            return state.clone();
        }

        state.direction = state.next_direction;

        let head = &state.snake[0];
        let (dx, dy) = match state.direction {
            Direction::Up => (0, -1),
            Direction::Down => (0, 1),
            Direction::Left => (-1, 0),
            Direction::Right => (1, 0),
        };

        let new_head = SnakeSegment {
            x: head.x + dx,
            y: head.y + dy,
        };

        if new_head.x <= 0
            || new_head.x >= state.grid_width - 1
            || new_head.y <= 0
            || new_head.y >= state.grid_height - 1
        {
            state.game_over = true;
            if state.score > state.high_score {
                state.high_score = state.score;
            }
            return state.clone();
        }

        if state.snake.iter().any(|s| s.x == new_head.x && s.y == new_head.y) {
            state.game_over = true;
            if state.score > state.high_score {
                state.high_score = state.score;
            }
            return state.clone();
        }

        let eating = new_head.x == state.food.x && new_head.y == state.food.y;

        let mut new_snake = vec![new_head.clone()];
        new_snake.extend_from_slice(&state.snake[..]);

        if eating {
            state.score += 10;
            state.food = Self::random_food_internal(&new_snake, state.grid_width, state.grid_height);
        } else {
            new_snake.pop();
        }

        state.snake = new_snake;
        state.clone()
    }

    pub fn get_state(&self) -> GameState {
        self.state.lock().unwrap().clone()
    }

    pub fn restart(&self) {
        self.do_reset();
    }
}
