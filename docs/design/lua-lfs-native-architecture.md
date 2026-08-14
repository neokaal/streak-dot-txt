# Pure Lua & Native LuaFileSystem (LFS) Architecture

## Overview

To maintain maximum application speed, zero UI thread freezing, and prevent command-prompt subshell windows (`cmd.exe`) from flashing open on Windows, Streak.txt uses a native **LuaFileSystem (`lfs`)** module built directly from source.

All streak logic remains 100% pure Lua in `streak_lua/`. The Tauri Rust desktop wrapper remains ultra-thin, exposing `lfs` via static compilation and standard C preloading (`package.preload["lfs"]`).

---

## Architecture Diagram

```text
                        ┌────────────────────────────────────────┐
                        │              C Source                  │
                        │  Lua 5.4 Source + LuaFileSystem (lfs.c)│
                        └───────────────────┬────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
         [ Tauri / Rust Build ]                           [ Local .luaenv Build ]
 ┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
 │ build.rs compiles lfs.c via `cc`     │        │ Makefile/Luarocks builds Lua & lfs   │
 │ Statically linked into binary        │        │ into .luaenv for CLI & Busted tests  │
 └──────────────────┬───────────────────┘        └──────────────────┬───────────────────┘
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            ▼
                        ┌────────────────────────────────────────┐
                        │        Pure Lua Business Logic         │
                        │    local lfs = require("lfs")          │
                        └────────────────────────────────────────┘
```

---

## Key Principles & Design Goals

1. **Pure Lua Business Logic**:
   - `streak_lua/repository.lua` requires `lfs` strictly (`local lfs = require("lfs")`).
   - If `lfs` is not present, Lua throws an explicit, immediate error rather than falling back to slow subshell commands (`io.popen` / `os.execute`).

2. **Zero Subshell / Command Window Spawns**:
   - Directory traversal (`lfs.dir`) and directory creation (`lfs.mkdir`) use direct OS filesystem syscalls.
   - Eliminates process creation overhead (50-200ms) on Windows/macOS/Linux, making streak ticking sub-millisecond and preventing console pop-ups.

3. **Static C Preloading in Tauri (`main.rs`)**:
   - In Tauri desktop builds, `lfs.c` is compiled statically by Rust's `cc` crate during `build.rs`.
   - `main.rs` registers `luaopen_lfs` in Lua's `package.preload["lfs"]`.
   - Eliminates external dynamic library dependencies (`lfs.dll`, `lfs.so`, `lfs.dylib`), Windows DLL symbol lookup issues (`lua54.dll`), and file-locking bugs.

4. **Hermetic Local Environment (`.luaenv`)**:
   - Supported identically across macOS, Linux, and Windows.
   - `.luaenv` is built via `luarocks` / `hererocks` from source.
   - CLI execution and test runners (`busted`, `spec/test_runner.lua`) run against `.luaenv`.

---

## Implementation Details

### 1. `streak_lua/repository.lua`

Strict requirement without subshell fallbacks:

```lua
local json = require("streak_lua.json")
local core = require("streak_lua.core")
local lfs = require("lfs") -- Fails immediately if lfs is unavailable

local repo = {}

-- Ensure directory exists recursively
function repo.ensure_dir(dir)
    dir = dir or repo.get_default_dir()
    local path = ""
    for part in dir:gmatch("[^/^\\]+") do
        path = path == "" and part or (path .. "/" .. part)
        if not lfs.attributes(path, "mode") then
            lfs.mkdir(path)
        end
    end
end

-- List directory files safely using LFS
function repo.list_directory_files(dir)
    repo.ensure_dir(dir)
    local files = {}
    for file in lfs.dir(dir) do
        if file ~= "." and file ~= ".." then
            table.insert(files, file)
        end
    end
    return files
end
```

### 2. Desktop Shell (`desktop/src-tauri/`)

- **`build.rs`**: Compiles `vendor/luafilesystem/src/lfs.c` into the static binary using `cc`.
- **`src/main.rs`**:
  ```rust
  extern "C" {
      fn luaopen_lfs(L: *mut mlua::lua_State) -> std::os::raw::c_int;
  }

  fn init_lua() -> Result<Lua, Box<dyn std::error::Error>> {
      let lua = Lua::new();

      // Preload static lfs module
      unsafe {
          let lfs_func = lua.create_c_function(|state| {
              Ok(luaopen_lfs(state.as_ptr()))
          })?;
          let package: mlua::Table = lua.globals().get("package")?;
          let preload: mlua::Table = package.get("preload")?;
          preload.set("lfs", lfs_func)?;
      }

      // Load embedded pure Lua scripts...
      Ok(lua)
  }
  ```

### 3. macOS and Local `.luaenv` Setup

The `.luaenv` folder in the project root holds the local developer environment on macOS, Linux, and Windows:

```bash
# Install LuaFileSystem into .luaenv from source
.luaenv/bin/luarocks --tree .luaenv install luafilesystem
```

Tests run seamlessly across platforms using:
```bash
make test-lua
```
