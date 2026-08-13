-- streak_lua/repository.lua
-- File repository layer with atomic write safety and directory scanning in modern Lua 5.4

local json = require("streak_lua.json")
local core = require("streak_lua.core")

local repo = {}

-- Get default streaks directory (~/streaks)
function repo.get_default_dir()
    local env_dir = os.getenv("STREAKS_DIR")
    if env_dir and env_dir ~= "" then
        return env_dir
    end
    local home = os.getenv("HOME") or os.getenv("USERPROFILE") or "."
    return home .. "/streaks"
end

-- Ensure directory exists
function repo.ensure_dir(dir)
    dir = dir or repo.get_default_dir()
    if os.name == "nt" or package.config:sub(1,1) == "\\" then
        local win_dir = dir:gsub("/", "\\")
        os.execute('mkdir "' .. win_dir .. '" 2>nul')
    else
        os.execute('mkdir -p "' .. dir .. '" 2>/dev/null')
    end
end

-- Read file contents
function repo.read_file(path)
    local f, err = io.open(path, "r")
    if not f then return nil, err end
    local content = f:read("*a")
    f:close()
    return content
end

-- Write file atomically (.tmp -> rename)
function repo.write_file_atomic(path, content)
    local tmp_path = path .. ".tmp." .. os.time()
    local f, err = io.open(tmp_path, "w")
    if not f then return false, err end
    f:write(content)
    f:close()

    local ok, ren_err = os.rename(tmp_path, path)
    if not ok then
        -- On Windows C runtime, rename fails if target file already exists
        os.remove(path)
        ok, ren_err = os.rename(tmp_path, path)
    end
    if not ok then
        -- Fallback: try copy/remove if cross-device rename fails
        local rf = io.open(tmp_path, "r")
        if rf then
            local data = rf:read("*a")
            rf:close()
            local wf = io.open(path, "w")
            if wf then
                wf:write(data)
                wf:close()
                os.remove(tmp_path)
                return true
            end
        end
        return false, ren_err
    end
    return true
end

-- Extract streak ID from filename (e.g. "streak-habit.txt" -> "habit")
function repo.id_from_filename(filename)
    if not filename:match("%.txt$") or filename:match("^%.") then
        return nil
    end
    local id = filename:match("^streak%-(.+)%.txt$")
    if id then return id end
    return filename:match("^(.+)%.txt$")
end

-- Load streaks-config.json
function repo.load_config(dir)
    dir = dir or repo.get_default_dir()
    local config_path = dir .. "/streaks-config.json"
    local content = repo.read_file(config_path)
    if not content then
        return { version = 1, order = {}, panel_order = {} }
    end
    local ok, parsed = pcall(json.decode, content)
    if ok and type(parsed) == "table" then
        if not parsed.order and not parsed.panel_order then
            parsed.order = {}
            parsed.panel_order = {}
        elseif not parsed.order then
            parsed.order = parsed.panel_order or {}
        elseif not parsed.panel_order then
            parsed.panel_order = parsed.order or {}
        end
        return parsed
    end
    return { version = 1, order = {}, panel_order = {} }
end

-- Save streaks-config.json preserving existing keys
function repo.save_config(dir, config)
    dir = dir or repo.get_default_dir()
    repo.ensure_dir(dir)
    local config_path = dir .. "/streaks-config.json"
    local encoded = json.encode(config)
    return repo.write_file_atomic(config_path, encoded)
end

-- List directory files safely in pure Lua
function repo.list_directory_files(dir)
    local search_dir = dir
    if not search_dir:match("[/\\]$") then
        search_dir = search_dir .. "/"
    end

    local files = {}
    local p
    if os.name == "nt" or package.config:sub(1,1) == "\\" then
        local win_dir = search_dir:gsub("/", "\\")
        p = io.popen('dir /b "' .. win_dir .. '" 2>nul')
    else
        p = io.popen('ls -1 "' .. search_dir .. '" 2>/dev/null')
    end

    if p then
        for line in p:lines() do
            line = line:gsub("[\r\n]", "")
            if line ~= "" then
                table.insert(files, line)
            end
        end
        p:close()
    end
    return files
end

-- List all streak files in directory
function repo.list_streaks(dir)
    dir = dir or repo.get_default_dir()
    repo.ensure_dir(dir)

    local streaks = {}
    local config = repo.load_config(dir)

    local files = repo.list_directory_files(dir)
    for _, filename in ipairs(files) do
        if filename:match("%.txt$") and not filename:match("^%.") then
            local id = repo.id_from_filename(filename)
            if id then
                local content = repo.read_file(dir .. "/" .. filename)
                if content then
                    local streak = core.parse_streak(content, id)
                    streak.filename = filename
                    table.insert(streaks, streak)
                end
            end
        end
    end

    -- Align config.order and config.panel_order
    local available_ids = {}
    for _, s in ipairs(streaks) do
        available_ids[s.id] = true
    end

    local order_list = config.order or config.panel_order or {}
    local ordered = {}
    local seen = {}
    for _, id in ipairs(order_list) do
        if available_ids[id] and not seen[id] then
            seen[id] = true
            table.insert(ordered, id)
        end
    end

    -- Sort unlisted streaks alphabetically
    local unlisted = {}
    for _, s in ipairs(streaks) do
        if not seen[s.id] then
            table.insert(unlisted, s.id)
        end
    end
    table.sort(unlisted)
    for _, id in ipairs(unlisted) do
        table.insert(ordered, id)
    end

    config.order = ordered
    config.panel_order = ordered

    local order_map = {}
    for idx, id in ipairs(ordered) do
        order_map[id] = idx
    end

    table.sort(streaks, function(a, b)
        local oa = order_map[a.id] or 999999
        local ob = order_map[b.id] or 999999
        if oa ~= ob then
            return oa < ob
        else
            return a.id < b.id
        end
    end)

    return streaks, config
end

-- Load a single streak by ID or name
function repo.load_streak(dir, id_or_name)
    dir = dir or repo.get_default_dir()
    repo.ensure_dir(dir)
    local slug = core.slugify(id_or_name)

    -- Check direct filename
    local path = dir .. "/streak-" .. slug .. ".txt"
    local content = repo.read_file(path)
    if content then
        return core.parse_streak(content, slug)
    end

    -- Check legacy filename
    path = dir .. "/" .. id_or_name .. ".txt"
    content = repo.read_file(path)
    if content then
        return core.parse_streak(content, slug)
    end

    -- Scan directory for display name or ID match
    local streaks = repo.list_streaks(dir)
    for _, s in ipairs(streaks) do
        if s.id == slug or s.name:lower() == id_or_name:lower() then
            return s
        end
    end

    return nil
end

-- Save streak
function repo.save_streak(dir, streak)
    dir = dir or repo.get_default_dir()
    repo.ensure_dir(dir)
    local filename = "streak-" .. streak.id .. ".txt"
    local path = dir .. "/" .. filename
    local content = core.format_streak(streak)
    return repo.write_file_atomic(path, content)
end

-- Tick or untick a streak for a given date (default today)
function repo.tick_streak(dir, id_or_name, date_str)
    date_str = date_str or core.format_date()
    local streak = repo.load_streak(dir, id_or_name)

    if not streak then
        -- Create new streak if it doesn't exist
        local slug = core.slugify(id_or_name)
        streak = {
            id = slug,
            name = id_or_name,
            tick = "Daily",
            dates = {},
            date_set = {},
        }
    end

    -- Toggle or append date
    if streak.date_set[date_str] then
        -- Untick (remove date)
        streak.date_set[date_str] = nil
        local new_dates = {}
        for _, d in ipairs(streak.dates) do
            if d ~= date_str then
                table.insert(new_dates, d)
            end
        end
        streak.dates = new_dates
    else
        -- Tick (add date)
        streak.date_set[date_str] = true
        table.insert(streak.dates, date_str)
        table.sort(streak.dates)
    end

    repo.save_streak(dir, streak)
    -- Do NOT mutate config order when ticking - controls must remain in fixed positions
    return streak
end

-- Archive a streak (move to archive/ directory)
function repo.archive_streak(dir, id_or_name)
    dir = dir or repo.get_default_dir()
    local streak = repo.load_streak(dir, id_or_name)
    if not streak then return false, "Streak not found" end

    local archive_dir = dir .. "/archive"
    repo.ensure_dir(archive_dir)

    local src_path = dir .. "/streak-" .. streak.id .. ".txt"
    local dest_path = archive_dir .. "/streak-" .. streak.id .. ".txt"

    -- Ensure unique destination filename if archive already exists
    if repo.read_file(dest_path) then
        dest_path = archive_dir .. "/streak-" .. streak.id .. "-" .. os.time() .. ".txt"
    end

    local ok, err = os.rename(src_path, dest_path)
    if not ok then
        os.remove(dest_path)
        ok, err = os.rename(src_path, dest_path)
    end
    if not ok then
        -- Fallback copy and delete
        local content = repo.read_file(src_path)
        if content then
            repo.write_file_atomic(dest_path, content)
            os.remove(src_path)
            ok = true
        end
    end

    -- Remove from order & panel_order if present
    local config = repo.load_config(dir)
    local order_list = config.order or config.panel_order or {}
    local new_order = {}
    for _, id in ipairs(order_list) do
        if id ~= streak.id then
            table.insert(new_order, id)
        end
    end
    config.order = new_order
    config.panel_order = new_order
    repo.save_config(dir, config)

    return ok, err
end

return repo
