fn main() {
    let manifest_directory = std::path::PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    std::fs::create_dir_all(manifest_directory.join("resources").join("sidecar"))
        .expect("create sidecar resource staging directory");
    tauri_build::build()
}
