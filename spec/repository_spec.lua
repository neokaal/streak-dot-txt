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

function tests.test_user_provided_data_integrity()
    local tmp_dir = "./.test_tmp/streak_lua_user_data_test_" .. os.time()
    repo.ensure_dir(tmp_dir)

    -- Copy user's specimen file to temporary directory
    local src_path = "spec/data/streak-business-current-affairs-&-company-updates.txt"
    local dest_path = tmp_dir .. "/streak-business-current-affairs-&-company-updates.txt"

    local src_file = io.open(src_path, "r")
    assert(src_file ~= nil, "Spec data file exists")
    local content = src_file:read("*a")
    src_file:close()

    local dest_file = io.open(dest_path, "w")
    dest_file:write(content)
    dest_file:close()

    -- Load the streak using load_streak
    local name_or_id = "Business Current Affairs & Company Updates"
    local streak = repo.load_streak(tmp_dir, name_or_id)
    assert(streak ~= nil, "Loaded user data streak successfully")
    assert(streak.id == "business-current-affairs-&-company-updates", "Retained correct custom slug ID")

    -- Let's verify that original timestamps are parsed correctly in raw_lines
    local found_ts = false
    for _, rl in ipairs(streak.raw_lines) do
        if rl.line == "2025-01-09T09:37:44.377302" then
            found_ts = true
        end
    end
    assert(found_ts, "Successfully loaded and kept raw line timestamps")

    -- Tick a new date: e.g. 2026-08-14
    repo.tick_streak(tmp_dir, name_or_id, "2026-08-14")

    -- Load the saved content from disk directly to verify formatting is preserved perfectly
    local updated_file = io.open(dest_path, "r")
    local updated_content = updated_file:read("*a")
    updated_file:close()

    -- Original timestamps must exist exactly as-is
    assert(updated_content:find("2025-01-09T09:37:44.377302", 1, true) ~= nil, "Original detailed timestamp 1 preserved on write")
    assert(updated_content:find("2025-01-10T16:44:14.656836", 1, true) ~= nil, "Original detailed timestamp 2 preserved on write")
    assert(updated_content:find("2026-08-14", 1, true) ~= nil, "New date added properly")

    -- Clean up test directory
    if package.config:sub(1,1) == "\\" then
        os.execute('rmdir /s /q "' .. tmp_dir:gsub("/", "\\") .. '" 2>nul')
    else
        os.execute('rm -rf "' .. tmp_dir .. '" 2>/dev/null')
    end
end

return tests
