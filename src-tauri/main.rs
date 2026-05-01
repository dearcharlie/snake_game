#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use snake_game_lib::GameManager;

fn main() {
    let _ = env_logger::try_init();
    log::info!("Starting Snake Game...");

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .manage(GameManager::new())
        .invoke_handler(tauri::generate_handler![
            snake_game_lib::start_game,
            snake_game_lib::get_game_state,
            snake_game_lib::set_direction,
            snake_game_lib::tick,
            snake_game_lib::reset_game,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
