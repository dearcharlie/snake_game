#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use snake_game_lib::{GameManager, GameState, Direction};
use std::sync::Mutex;

struct AppState(Mutex<GameManager>);

#[tauri::command]
fn start_game(state: tauri::State<'_, AppState>) -> GameState {
    state.0.lock().unwrap().restart();
    state.0.lock().unwrap().get_state()
}

#[tauri::command]
fn get_game_state(state: tauri::State<'_, AppState>) -> GameState {
    state.0.lock().unwrap().get_state()
}

#[tauri::command]
fn set_direction(state: tauri::State<'_, AppState>, direction: String) {
    let dir = match direction.as_str() {
        "up" => Direction::Up,
        "down" => Direction::Down,
        "left" => Direction::Left,
        "right" => Direction::Right,
        _ => return,
    };
    state.0.lock().unwrap().set_direction(dir);
}

#[tauri::command]
fn tick_game(state: tauri::State<'_, AppState>) -> GameState {
    state.0.lock().unwrap().tick()
}

#[tauri::command]
fn restart_game(state: tauri::State<'_, AppState>) -> GameState {
    state.0.lock().unwrap().restart();
    state.0.lock().unwrap().get_state()
}

fn main() {
    log::info!("Starting Snake Game...");

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .manage(AppState(Mutex::new(GameManager::new())))
        .invoke_handler(tauri::generate_handler![
            start_game,
            get_game_state,
            set_direction,
            tick_game,
            restart_game,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
