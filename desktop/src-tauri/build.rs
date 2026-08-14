fn main() {
    let manifest_directory = std::path::PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    std::fs::create_dir_all(manifest_directory.join("resources").join("sidecar"))
        .expect("create sidecar resource staging directory");

    let root_build_dir = manifest_directory
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("build");

    let lfs_src_dir = root_build_dir.join("luafilesystem-1_9_0").join("src");
    let lua_src_dir = root_build_dir.join("lua-5.4.8").join("src");

    let mut build = cc::Build::new();
    build.file(lfs_src_dir.join("lfs.c"));
    build.include(&lfs_src_dir);
    if lua_src_dir.exists() {
        build.include(&lua_src_dir);
    }

    build.warnings(false);
    build.compile("lfs");

    tauri_build::build();
}
