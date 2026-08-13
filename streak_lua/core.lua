-- streak_lua/core.lua
-- Core parsing, slugification, date handling, and streak statistics in modern Lua 5.4

local json = require("streak_lua.json")

local core = {}

-- Utility: trim string
function core.trim(s)
    return s and s:match("^%s*(.-)%s*$") or ""
end

-- Generate a clean slug for streak ID from display name
function core.slugify(name)
    local slug = name:lower()
    slug = slug:gsub("[^a-z0-9%-]", "-")
    slug = slug:gsub("%-+", "-")
    slug = slug:gsub("^%-", ""):gsub("%-$", "")
    if slug == "" then
        slug = "streak"
    end
    return slug
end

-- Format YYYY-MM-DD date string
function core.format_date(time_sec)
    time_sec = time_sec or os.time()
    return os.date("!%Y-%m-%d", time_sec)
end

-- Parse streak file content
function core.parse_streak(content, id)
    local name = id
    local tick = "Daily"
    local dates = {}
    local date_set = {}

    local fm_content = content:match("^%-%-%-\r?\n(.-)\r?\n%-%-%-")
    if fm_content then
        for line in fm_content:gmatch("[^\r\n]+") do
            local k, v = line:match("^([^:]+):%s*(.*)$")
            if k and v then
                k = core.trim(k):lower()
                v = core.trim(v)
                if k == "name" and v ~= "" then
                    name = v
                elseif k == "tick" and v ~= "" then
                    tick = v
                end
            end
        end
    end

    -- Extract dates after frontmatter (or whole file if no frontmatter)
    local body = content
    if fm_content then
        local _, finish = content:find("^%-%-%-\r?\n(.-)\r?\n%-%-%-")
        if finish then
            body = content:sub(finish + 1)
        end
    end

    for line in body:gmatch("[^\r\n]+") do
        local trimmed = core.trim(line)
        local y, m, d = trimmed:match("^(%d%d%d%d)%-(%d%d)%-(%d%d)")
        if y and m and d then
            local date_str = string.format("%04d-%02d-%02d", tonumber(y), tonumber(m), tonumber(d))
            if not date_set[date_str] then
                date_set[date_str] = true
                table.insert(dates, date_str)
            end
        end
    end

    table.sort(dates)

    return {
        id = id,
        name = name,
        tick = tick,
        dates = dates,
        date_set = date_set,
    }
end

-- Format streak table back to plain text file format
function core.format_streak(streak)
    local lines = {
        "---",
        "name: " .. (streak.name or streak.id),
        "tick: " .. (streak.tick or "Daily"),
        "---",
    }
    table.sort(streak.dates)
    for _, d in ipairs(streak.dates) do
        table.insert(lines, d)
    end
    return table.concat(lines, "\n") .. "\n"
end

-- Convert YYYY-MM-DD to absolute Gregorian day number (timezone independent)
function core.date_to_day(date_str)
    if not date_str then return nil end
    local y, m, d = date_str:match("^(%d%d%d%d)%-(%d%d)%-(%d%d)")
    if not y then return nil end
    y, m, d = tonumber(y), tonumber(m), tonumber(d)
    local a = math.floor((14 - m) / 12)
    local y1 = y + 4800 - a
    local m1 = m + 12 * a - 3
    return d + math.floor((153 * m1 + 2) / 5) + 365 * y1 + math.floor(y1 / 4) - math.floor(y1 / 100) + math.floor(y1 / 400) - 32045
end

-- Calculate statistics for a streak given today's date
function core.calculate_stats(streak, today_str)
    today_str = today_str or core.format_date()
    local today_day = core.date_to_day(today_str)

    local dates = streak.dates or {}
    local total_ticks = #dates
    local ticked_today = streak.date_set and (streak.date_set[today_str] == true)

    if total_ticks == 0 then
        return {
            id = streak.id,
            name = streak.name,
            tick = streak.tick or "Daily",
            current_streak = 0,
            longest_streak = 0,
            ticked_today = false,
            total_ticks = 0,
            completion_rate = 0.0,
            last_ticked = nil,
        }
    end

    local last_ticked = dates[#dates]

    -- Extract sorted unique day numbers
    local day_set = {}
    local days = {}
    for _, d in ipairs(dates) do
        local dn = core.date_to_day(d)
        if dn and not day_set[dn] then
            day_set[dn] = true
            table.insert(days, dn)
        end
    end
    table.sort(days)

    -- Calculate longest streak and current streak
    local longest = 0
    local current_run = 0
    local last_day = nil

    for _, dn in ipairs(days) do
        if last_day == nil or dn == last_day + 1 then
            current_run = current_run + 1
        else
            current_run = 1
        end
        if current_run > longest then
            longest = current_run
        end
        last_day = dn
    end

    -- Current active streak as of today
    local current_streak = 0
    if #days > 0 and today_day then
        local most_recent_day = days[#days]
        if most_recent_day == today_day or most_recent_day == (today_day - 1) then
            current_streak = 1
            local idx = #days
            while idx > 1 do
                if days[idx] == days[idx - 1] + 1 then
                    current_streak = current_streak + 1
                    idx = idx - 1
                else
                    break
                end
            end
        end
    end

    -- Completion rate calculation
    local first_day = days[1]
    local days_span = math.max(1, (today_day and (today_day - first_day + 1) or 1))
    local completion_rate = math.min(1.0, #days / days_span)

    return {
        id = streak.id,
        name = streak.name,
        tick = streak.tick or "Daily",
        current_streak = current_streak,
        longest_streak = longest,
        ticked_today = ticked_today,
        total_ticks = total_ticks,
        completion_rate = math.floor(completion_rate * 1000 + 0.5) / 1000,
        last_ticked = last_ticked,
    }
end

return core
