#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[cfg(not(debug_assertions))]
use std::{
    fs::{self, OpenOptions},
    io::{Read, Write},
    net::{SocketAddr, TcpListener, TcpStream},
    process::{Command, Stdio},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};
#[cfg(any(not(debug_assertions), test))]
use std::{
    process::Child,
    sync::{Arc, Mutex},
};
#[cfg(not(debug_assertions))]
use tauri::Manager;

#[cfg(any(not(debug_assertions), test))]
#[derive(Clone, Default)]
struct SidecarState {
    child: Arc<Mutex<Option<Child>>>,
}

#[cfg(any(not(debug_assertions), test))]
impl SidecarState {
    fn stop(&self) -> bool {
        if let Some(mut child) = self.child.lock().expect("sidecar lock poisoned").take() {
            let _ = child.kill();
            let _ = child.wait();
            true
        } else {
            false
        }
    }
}

#[cfg(not(debug_assertions))]
fn available_port() -> std::io::Result<u16> {
    let listener = TcpListener::bind(("127.0.0.1", 0))?;
    Ok(listener.local_addr()?.port())
}

#[cfg(not(debug_assertions))]
fn instance_token() -> String {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    format!("{:x}-{:x}", std::process::id(), timestamp)
}

fn response_is_ready(response: &str, token: &str) -> bool {
    response.starts_with("HTTP/1.1 200") && response.ends_with(token)
}

#[cfg(not(debug_assertions))]
fn sidecar_is_ready(port: u16, token: &str) -> bool {
    let address = SocketAddr::from(([127, 0, 0, 1], port));
    let Ok(mut stream) = TcpStream::connect_timeout(&address, Duration::from_millis(200)) else {
        return false;
    };
    let _ = stream.set_read_timeout(Some(Duration::from_millis(500)));
    let request = format!(
        "GET /desktop-health?token={token} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n\r\n"
    );
    if stream.write_all(request.as_bytes()).is_err() {
        return false;
    }
    let mut response = String::new();
    stream.read_to_string(&mut response).is_ok() && response_is_ready(&response, token)
}

#[cfg(not(debug_assertions))]
fn show_startup_error(app: &tauri::AppHandle, message: &str) {
    if let Some(window) = app.get_webview_window("main") {
        let script = format!("window.__streakStartupFailed({message:?})");
        let _ = window.eval(&script);
    }
}

#[cfg(not(debug_assertions))]
fn start_local_server(
    app: &tauri::App,
    state: SidecarState,
) -> Result<(), Box<dyn std::error::Error>> {
    let executable = std::env::current_exe()?;
    let sidecar = executable
        .parent()
        .ok_or("unable to find the Streak.txt application directory")?
        .join("streak-server");

    let log_directory = app.path().app_log_dir()?;
    fs::create_dir_all(&log_directory)?;
    let log_path = log_directory.join("sidecar.log");
    let stdout = OpenOptions::new()
        .create(true)
        .truncate(true)
        .write(true)
        .open(&log_path)?;
    let stderr = stdout.try_clone()?;

    let port = available_port()?;
    let token = instance_token();
    let child = Command::new(sidecar)
        .env("STREAK_PORT", port.to_string())
        .env("STREAK_INSTANCE_TOKEN", &token)
        .stdout(Stdio::from(stdout))
        .stderr(Stdio::from(stderr))
        .spawn()?;
    *state.child.lock().expect("sidecar lock poisoned") = Some(child);

    let app_handle = app.handle().clone();
    thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(60);
        while Instant::now() < deadline {
            let exited = state
                .child
                .lock()
                .expect("sidecar lock poisoned")
                .as_mut()
                .and_then(|child| child.try_wait().ok())
                .flatten()
                .is_some();
            if exited {
                show_startup_error(
                    &app_handle,
                    &format!(
                        "Streak.txt could not start its local server.\n\nDetails: {}",
                        log_path.display()
                    ),
                );
                return;
            }
            if sidecar_is_ready(port, &token) {
                if let Some(window) = app_handle.get_webview_window("main") {
                    let url = format!("http://127.0.0.1:{port}/");
                    if let Ok(url) = tauri::Url::parse(&url) {
                        let _ = window.navigate(url);
                    }
                }
                return;
            }
            thread::sleep(Duration::from_millis(200));
        }
        show_startup_error(
            &app_handle,
            &format!(
                "Streak.txt timed out while starting its local server.\n\nDetails: {}",
                log_path.display()
            ),
        );
    });
    Ok(())
}

fn main() {
    let app = tauri::Builder::default()
        .setup(|_app| {
            #[cfg(not(debug_assertions))]
            {
                let state = SidecarState::default();
                _app.manage(state.clone());
                if let Err(error) = start_local_server(_app, state) {
                    let app_handle = _app.handle().clone();
                    let message =
                        format!("Streak.txt could not start its local server.\n\n{error}");
                    thread::spawn(move || {
                        thread::sleep(Duration::from_millis(500));
                        show_startup_error(&app_handle, &message);
                    });
                }
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building Streak.txt");

    app.run(|_app_handle, _event| {
        #[cfg(not(debug_assertions))]
        if let tauri::RunEvent::Exit = _event {
            _app_handle.state::<SidecarState>().stop();
        }
    });
}

#[cfg(test)]
mod tests {
    use super::{response_is_ready, SidecarState};
    use std::process::{Command, Stdio};

    #[test]
    fn readiness_requires_both_success_and_the_expected_instance() {
        assert!(response_is_ready(
            "HTTP/1.1 200 OK\r\ncontent-type: text/plain\r\n\r\nabc-123",
            "abc-123"
        ));
        assert!(!response_is_ready(
            "HTTP/1.1 200 OK\r\ncontent-type: text/plain\r\n\r\nother",
            "abc-123"
        ));
        assert!(!response_is_ready(
            "HTTP/1.1 404 Not Found\r\n\r\nabc-123",
            "abc-123"
        ));
    }

    #[test]
    fn stopping_the_sidecar_terminates_and_reaps_the_child() {
        #[cfg(unix)]
        let child = Command::new("sleep")
            .arg("30")
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn test child");

        #[cfg(windows)]
        let child = Command::new("ping")
            .args(["-n", "30", "127.0.0.1"])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn test child");

        let state = SidecarState::default();
        *state.child.lock().expect("sidecar lock poisoned") = Some(child);
        assert!(state.stop());
        assert!(state.child.lock().expect("sidecar lock poisoned").is_none());
        assert!(!state.stop());
    }
}
