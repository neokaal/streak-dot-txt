#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[cfg(not(debug_assertions))]
fn start_local_server(_app: &tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command;

    let executable = std::env::current_exe()?;
    let sidecar = executable
        .parent()
        .ok_or("unable to find the Streak.txt application directory")?
        .join("streak-server");
    Command::new(sidecar)
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
