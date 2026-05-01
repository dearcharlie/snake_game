import { invoke } from "@tauri-apps/api/core";

// === Types (mirror of Rust) ===
interface Position {
  x: number;
  y: number;
}

interface SnakeSegment {
  x: number;
  y: number;
}

type Direction = "Up" | "Down" | "Left" | "Right";

interface GameState {
  snake: SnakeSegment[];
  food: Position;
  direction: Direction;
  next_direction: Direction;
  score: number;
  high_score: number;
  game_over: boolean;
  grid_width: number;
  grid_height: number;
  speed: number;
}

// === Game Config ===
const CELL_SIZE = 20;
const GRID_W = 30;
const GRID_H = 20;
const CANVAS_W = GRID_W * CELL_SIZE;
const CANVAS_H = GRID_H * CELL_SIZE;

// === DOM Elements ===
const canvas = document.getElementById("game-canvas") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
const scoreEl = document.getElementById("score")!;
const highScoreEl = document.getElementById("high-score")!;
const statusEl = document.getElementById("status")!;
const overlay = document.getElementById("overlay")!;
const overlayTitle = document.getElementById("overlay-title")!;
const overlayScore = document.getElementById("overlay-score")!;

// Set actual canvas size
canvas.width = CANVAS_W;
canvas.height = CANVAS_H;

// === Game State ===
let gameState: GameState | null = null;
let started = false;
let paused = false;
let _animationId: number | null = null;
let lastTick = 0;
let tickInterval = 100; // ms

// === Colors ===
const COLORS = {
  bg: "#0f0f1a",
  grid: "#1a1a2e",
  snakeHead: "#00d9ff",
  snakeBody: "#0099cc",
  food: "#ff6b6b",
  wall: "#16213e",
  text: "#eee",
};

// === Drawing ===
function drawGrid() {
  ctx.fillStyle = COLORS.bg;
  ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);

  ctx.strokeStyle = COLORS.grid;
  ctx.lineWidth = 0.5;
  for (let x = 0; x <= GRID_W; x++) {
    ctx.beginPath();
    ctx.moveTo(x * CELL_SIZE, 0);
    ctx.lineTo(x * CELL_SIZE, CANVAS_H);
    ctx.stroke();
  }
  for (let y = 0; y <= GRID_H; y++) {
    ctx.beginPath();
    ctx.moveTo(0, y * CELL_SIZE);
    ctx.lineTo(CANVAS_W, y * CELL_SIZE);
    ctx.stroke();
  }
}

function drawBorder() {
  ctx.fillStyle = COLORS.wall;
  // Top
  ctx.fillRect(0, 0, CANVAS_W, CELL_SIZE);
  // Bottom
  ctx.fillRect(0, CANVAS_H - CELL_SIZE, CANVAS_W, CELL_SIZE);
  // Left
  ctx.fillRect(0, 0, CELL_SIZE, CANVAS_H);
  // Right
  ctx.fillRect(CANVAS_W - CELL_SIZE, 0, CELL_SIZE, CANVAS_H);
}

function drawSnake(snake: SnakeSegment[]) {
  snake.forEach((seg, i) => {
    const isHead = i === 0;
    ctx.fillStyle = isHead ? COLORS.snakeHead : COLORS.snakeBody;
    const padding = 1;
    ctx.fillRect(
      seg.x * CELL_SIZE + padding,
      seg.y * CELL_SIZE + padding,
      CELL_SIZE - padding * 2,
      CELL_SIZE - padding * 2
    );
    // Rounded corners
    ctx.beginPath();
    const r = 4;
    const x = seg.x * CELL_SIZE + padding;
    const y = seg.y * CELL_SIZE + padding;
    const w = CELL_SIZE - padding * 2;
    const h = CELL_SIZE - padding * 2;
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.arcTo(x + w, y, x + w, y + r, r);
    ctx.lineTo(x + w, y + h - r);
    ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
    ctx.lineTo(x + r, y + h);
    ctx.arcTo(x, y + h, x, y + h - r, r);
    ctx.lineTo(x, y + r);
    ctx.arcTo(x, y, x + r, y, r);
    ctx.fill();
  });
}

function drawFood(food: Position) {
  ctx.fillStyle = COLORS.food;
  const padding = 2;
  ctx.beginPath();
  const cx = food.x * CELL_SIZE + CELL_SIZE / 2;
  const cy = food.y * CELL_SIZE + CELL_SIZE / 2;
  const r = CELL_SIZE / 2 - padding;
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fill();
}

function render(state: GameState) {
  drawGrid();
  drawBorder();
  drawFood(state.food);
  drawSnake(state.snake);
}

function updateUI(state: GameState) {
  scoreEl.textContent = state.score.toString();
  highScoreEl.textContent = state.high_score.toString();

  if (state.game_over) {
    statusEl.textContent = "Game Over!";
    overlayTitle.textContent = "GAME OVER";
    overlayScore.textContent = `Score: ${state.score}`;
    overlay.classList.remove("hidden");
  } else if (!started) {
    statusEl.textContent = "Press SPACE to start";
    overlayTitle.textContent = "SNAKE GAME";
    overlayScore.textContent = "";
    overlay.classList.remove("hidden");
  } else if (paused) {
    statusEl.textContent = "Paused";
    overlayTitle.textContent = "PAUSED";
    overlayScore.textContent = `Score: ${state.score}`;
    overlay.classList.remove("hidden");
  } else {
    statusEl.textContent = "Playing...";
    overlay.classList.add("hidden");
  }
}

// === Game Loop ===
async function tick() {
  if (!started || paused || !gameState) return;

  try {
    const newState = await invoke<GameState>("tick");
    gameState = newState;
    render(newState);
    updateUI(newState);

    if (newState.game_over) {
      started = false;
    }
  } catch (e) {
    console.error("tick error:", e);
  }
}

function gameLoop(timestamp: number) {
  if (!started || paused) {
    _animationId = requestAnimationFrame(gameLoop);
    return;
  }

  if (timestamp - lastTick >= tickInterval) {
    lastTick = timestamp;
    tick();
  }

  _animationId = requestAnimationFrame(gameLoop);
}

// === Controls ===
async function handleKey(e: KeyboardEvent) {
  if (e.repeat) return;

  const key = e.key.toLowerCase();

  // Start / Pause
  if (key === " " || key === "enter") {
    e.preventDefault();
    if (!started || gameState?.game_over) {
      await startGame();
    } else {
      paused = !paused;
      if (!paused) {
        statusEl.textContent = "Playing...";
        overlay.classList.add("hidden");
      } else {
        statusEl.textContent = "Paused";
        overlayTitle.textContent = "PAUSED";
        overlay.classList.remove("hidden");
      }
    }
    return;
  }

  // Restart
  if (key === "r") {
    await startGame();
    return;
  }

  // Direction
  if (!gameState || gameState.game_over || paused) return;

  const dirMap: Record<string, Direction> = {
    arrowup: "Up",
    arrowdown: "Down",
    arrowleft: "Left",
    arrowright: "Right",
    w: "Up",
    s: "Down",
    a: "Left",
    d: "Right",
  };

  const dir = dirMap[key];
  if (dir) {
    e.preventDefault();
    try {
      await invoke("set_direction", { direction: dir.toLowerCase() });
    } catch (err) {
      console.error("set_direction error:", err);
    }
  }
}

async function startGame() {
  try {
    overlay.classList.add("hidden");
    started = true;
    paused = false;
    gameState = await invoke<GameState>("start_game");
    tickInterval = gameState.speed;
    render(gameState);
    updateUI(gameState);
    lastTick = performance.now();
  } catch (e) {
    console.error("start_game error:", e);
  }
}

// === Init ===
async function init() {
  // Get initial state
  try {
    gameState = await invoke<GameState>("get_game_state");
    render(gameState);
    updateUI(gameState);
  } catch (e) {
    console.error("init error:", e);
    drawGrid();
    drawBorder();
  }

  // Listen for key events
  window.addEventListener("keydown", handleKey);

  // Start render loop
  _animationId = requestAnimationFrame(gameLoop);
}

init();
