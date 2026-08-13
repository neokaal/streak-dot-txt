#!/usr/bin/env lua
-- streak.lua
-- Command-line interface for Streak.txt written in Lua 5.4

package.path = ";./?.lua;./?/init.lua;" .. package.path

local core = require("streak_lua.core")
local repo = require("streak_lua.repository")

local function print_usage()
    print([[
Streak.txt - Local-first habit tracker

Usage:
  lua streak.lua list [--dir PATH]
  lua streak.lua new --name "NAME" [--dir PATH]
  lua streak.lua tick --name "NAME" [--date YYYY-MM-DD] [--dir PATH]
  lua streak.lua view --name "NAME" [--dir PATH]
  lua streak.lua archive --name "NAME" [--dir PATH]
]])
end

local function parse_args(args)
    local opts = { command = args[1], dir = nil, name = nil, date = nil }
    local idx = 2
    while idx <= #args do
        local arg = args[idx]
        if arg == "--dir" and idx < #args then
            opts.dir = args[idx + 1]
            idx = idx + 2
        elseif arg == "--name" and idx < #args then
            opts.name = args[idx + 1]
            idx = idx + 2
        elseif arg == "--date" and idx < #args then
            opts.date = args[idx + 1]
            idx = idx + 2
        else
            idx = idx + 1
        end
    end
    return opts
end

local function main()
    local opts = parse_args(arg)
    local dir = opts.dir or repo.get_default_dir()

    if not opts.command or opts.command == "help" or opts.command == "-h" then
        print_usage()
        return
    end

    if opts.command == "list" then
        local streaks, _ = repo.list_streaks(dir)
        print(string.format("%-20s %-20s %-12s %-10s", "ID", "NAME", "CURRENT", "TOTAL"))
        print(string.rep("-", 65))
        for _, s in ipairs(streaks) do
            local stats = core.calculate_stats(s)
            print(string.format("%-20s %-20s %-12d %-10d", s.id, s.name, stats.current_streak, stats.total_ticks))
        end

    elseif opts.command == "new" then
        if not opts.name then
            print("Error: --name is required for new")
            os.exit(1)
        end
        local slug = core.slugify(opts.name)
        local streak = { id = slug, name = opts.name, tick = "Daily", dates = {}, date_set = {} }
        repo.save_streak(dir, streak)
        print("Created streak: " .. opts.name .. " (" .. slug .. ")")

    elseif opts.command == "tick" then
        if not opts.name then
            print("Error: --name is required for tick")
            os.exit(1)
        end
        local date_str = opts.date or core.format_date()
        local streak = repo.tick_streak(dir, opts.name, date_str)
        local stats = core.calculate_stats(streak, date_str)
        print(string.format("Ticked '%s' for %s. Current streak: %d", streak.name, date_str, stats.current_streak))

    elseif opts.command == "view" then
        if not opts.name then
            print("Error: --name is required for view")
            os.exit(1)
        end
        local streak = repo.load_streak(dir, opts.name)
        if not streak then
            print("Streak not found: " .. opts.name)
            os.exit(1)
        end
        local stats = core.calculate_stats(streak)
        print("Name: " .. streak.name .. " (" .. streak.id .. ")")
        print("Current Streak: " .. stats.current_streak .. " days")
        print("Longest Streak: " .. stats.longest_streak .. " days")
        print("Total Ticks:    " .. stats.total_ticks)
        print("Last Ticked:    " .. (stats.last_ticked or "Never"))

    elseif opts.command == "archive" then
        if not opts.name then
            print("Error: --name is required for archive")
            os.exit(1)
        end
        local ok, err = repo.archive_streak(dir, opts.name)
        if ok then
            print("Archived streak: " .. opts.name)
        else
            print("Failed to archive: " .. tostring(err))
            os.exit(1)
        end
    else
        print("Unknown command: " .. opts.command)
        print_usage()
        os.exit(1)
    end
end

main()
