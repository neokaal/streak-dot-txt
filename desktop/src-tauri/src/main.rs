#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

#[cfg(not(debug_assertions))]
fn start_local_server(app: &tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command;

    let sidecar = app.path().resource_dir()?.join("streak-server");
    let data_dir = app.path().home_dir()?.join("streaks");
    Command::new(sidecar)
        .env("STREAKS_DIR", data_dir)
        .env("STREAK_PORT", "8000")
        .spawn()?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            #[cfg(not(debug_assertions))]
            start_local_server(app)?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running Streak.txt");
}
