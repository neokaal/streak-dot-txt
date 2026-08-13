-- spec/repository_spec.lua
-- Unit tests for repository module in isolated temporary directory

local core = require("streak_lua.core")
local repo = require("streak_lua.repository")

local tests = {}

function tests.test_repository_crud()
    local tmp_dir = "./.test_tmp/streak_lua_test_" .. os.time()
    repo.ensure_dir(tmp_dir)

    -- Test tick/create
    local s1 = repo.tick_streak(tmp_dir, "Morning Walk", "2026-08-10")
    assert(s1.id == "morning-walk", "repo tick created slug id")
    assert(#s1.dates == 1, "repo tick date added")

    -- Test load
    local loaded, load_err = repo.load_streak(tmp_dir, "morning-walk")
    if not loaded then
        print("DEBUG: load failed, dir contents:")
        local cmd = (package.config:sub(1,1) == "\\") and ('dir "' .. tmp_dir:gsub("/", "\\") .. '"') or ('ls -la "' .. tmp_dir .. '"')
        local p = io.popen(cmd)
        if p then print(p:read("*a")); p:close() end
    end
    assert(loaded ~= nil, "loaded streak found: " .. tostring(load_err))
    assert(loaded.name == "Morning Walk", "loaded name matches")

    -- Test config saving & order
    local streaks, config = repo.list_streaks(tmp_dir)
    assert(#streaks == 1, "list_streaks count 1")
    assert(#config.panel_order == 1, "config panel_order length 1")
    assert(config.panel_order[1] == "morning-walk", "panel order match")

    -- Test untick (toggle)
    repo.tick_streak(tmp_dir, "Morning Walk", "2026-08-10")
    local unticked = repo.load_streak(tmp_dir, "morning-walk")
    assert(#unticked.dates == 0, "unticked date removed")

    -- Test archive
    local ok, err = repo.archive_streak(tmp_dir, "morning-walk")
    assert(ok == true, "archive succeeded")
    local archived_load = repo.load_streak(tmp_dir, "morning-walk")
    assert(archived_load == nil, "archived streak no longer in main list")

    -- Clean up test directory
    if package.config:sub(1,1) == "\\" then
        os.execute('rmdir /s /q "' .. tmp_dir:gsub("/", "\\") .. '" 2>nul')
    else
        os.execute('rm -rf "' .. tmp_dir .. '" 2>/dev/null')
    end
end

return tests
