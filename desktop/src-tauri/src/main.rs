#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use mlua::Lua;
use std::sync::Mutex;
use tauri::State;

struct AppState {
    lua: Mutex<Lua>,
}

// Embedded Lua code
const LUA_JSON: &str = include_str!("../../../streak_lua/json.lua");
const LUA_CORE: &str = include_str!("../../../streak_lua/core.lua");
const LUA_REPO: &str = include_str!("../../../streak_lua/repository.lua");

extern "C" {
    fn luaopen_lfs(L: *mut std::ffi::c_void) -> std::os::raw::c_int;
}

fn init_lua() -> Result<Lua, Box<dyn std::error::Error>> {
    let lua = Lua::new();

    // Register statically linked lfs C module into package.preload["lfs"]
    unsafe {
        let lfs_fn: mlua::ffi::lua_CFunction = std::mem::transmute(luaopen_lfs as *const ());
        let lfs_c_func = lua.create_c_function(lfs_fn)?;
        let package: mlua::Table = lua.globals().get("package")?;
        let preload: mlua::Table = package.get("preload")?;
        preload.set("lfs", lfs_c_func)?;
    }

    // Register embedded modules in package.loaded
    lua.load(format!(
        r#"
        package.loaded["streak_lua.json"] = (function()
            {}
        end)()
        package.loaded["streak_lua.core"] = (function()
            {}
        end)()
        package.loaded["streak_lua.repository"] = (function()
            {}
        end)()

        _G.json = package.loaded["streak_lua.json"]
        _G.core = package.loaded["streak_lua.core"]
        _G.repo = package.loaded["streak_lua.repository"]
        "#,
        LUA_JSON, LUA_CORE, LUA_REPO
    ))
    .exec()?;

    Ok(lua)
}

#[tauri::command]
fn list_streaks(state: State<AppState>) -> Result<String, String> {
    let lua = state.lua.lock().map_err(|e| e.to_string())?;
    let script = r#"
        local dir = repo.get_default_dir()
        local streaks, config = repo.list_streaks(dir)
        local result = {}
        for _, s in ipairs(streaks) do
            local stats = core.calculate_stats(s)
            table.insert(result, stats)
        end
        return json.encode({ streaks = result, panel_order = config.panel_order or {} })
    "#;
    let json_res: String = lua.load(script).eval().map_err(|e| e.to_string())?;
    Ok(json_res)
}

#[tauri::command]
fn tick_streak(id: String, state: State<AppState>) -> Result<String, String> {
    let lua = state.lua.lock().map_err(|e| e.to_string())?;
    let script = format!(
        r#"
        local dir = repo.get_default_dir()
        local streak = repo.tick_streak(dir, {:?})
        local stats = core.calculate_stats(streak)
        return json.encode(stats)
    "#,
        id
    );
    let json_res: String = lua.load(&script).eval().map_err(|e| e.to_string())?;
    Ok(json_res)
}

#[tauri::command]
fn create_streak(name: String, state: State<AppState>) -> Result<String, String> {
    let lua = state.lua.lock().map_err(|e| e.to_string())?;
    let script = format!(
        r#"
        local dir = repo.get_default_dir()
        local slug = core.slugify({:?})
        local streak = {{ id = slug, name = {:?}, tick = "Daily", dates = {{}}, date_set = {{}} }}
        repo.save_streak(dir, streak)
        local stats = core.calculate_stats(streak)
        return json.encode(stats)
    "#,
        name, name
    );
    let json_res: String = lua.load(&script).eval().map_err(|e| e.to_string())?;
    Ok(json_res)
}

#[tauri::command]
fn archive_streak(id: String, state: State<AppState>) -> Result<bool, String> {
    let lua = state.lua.lock().map_err(|e| e.to_string())?;
    let script = format!(
        r#"
        local dir = repo.get_default_dir()
        local ok, err = repo.archive_streak(dir, {:?})
        return ok
    "#,
        id
    );
    let ok: bool = lua.load(&script).eval().map_err(|e| e.to_string())?;
    Ok(ok)
}

fn main() {
    let lua = init_lua().expect("Failed to initialize Lua VM");
    let state = AppState {
        lua: Mutex::new(lua),
    };

    tauri::Builder::default()
        .manage(state)
        .invoke_handler(tauri::generate_handler![
            list_streaks,
            tick_streak,
            create_streak,
            archive_streak
        ])
        .run(tauri::generate_context!())
        .expect("error while running Streak.txt application");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_embedded_lua_initialization() {
        let lua = init_lua().expect("init_lua should succeed");
        let eval_res: String = lua
            .load("return core.slugify('Morning Walk')")
            .eval()
            .expect("eval slugify");
        assert_eq!(eval_res, "morning-walk");
    }

    #[test]
    fn test_lfs_integration() {
        let lua = init_lua().expect("init_lua should succeed");
        let lfs_version: String = lua
            .load("local lfs = require('lfs'); return lfs._VERSION")
            .eval()
            .expect("eval lfs._VERSION");
        assert!(lfs_version.contains("LuaFileSystem"));
    }
}
