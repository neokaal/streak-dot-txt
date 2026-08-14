-- spec/streak_core_spec.lua
-- Unit tests for core Lua module

local core = require("streak_lua.core")
local json = require("streak_lua.json")

local tests = {}

function tests.test_slugify()
    assert(core.slugify("Morning Walk") == "morning-walk", "slugify basic")
    assert(core.slugify("  Daily Run #1! ") == "daily-run-1", "slugify special chars")
    assert(core.slugify("!!!") == "streak", "slugify fallback")
end

function tests.test_parse_and_format()
    local raw = "---\nname: Exercise\ntick: Daily\n---\n2026-08-10\n2026-08-11\n"
    local streak = core.parse_streak(raw, "exercise")

    assert(streak.id == "exercise", "parsed id")
    assert(streak.name == "Exercise", "parsed name")
    assert(streak.tick == "Daily", "parsed tick")
    assert(#streak.dates == 2, "parsed 2 dates")
    assert(streak.dates[1] == "2026-08-10", "first date")
    assert(streak.dates[2] == "2026-08-11", "second date")

    local formatted = core.format_streak(streak)
    assert(formatted:find("name: Exercise", 1, true), "formatted contains name")
    assert(formatted:find("2026-08-10", 1, true), "formatted contains date 1")
    assert(formatted:find("2026-08-11", 1, true), "formatted contains date 2")
end

function tests.test_stats_calculation()
    local raw = "---\nname: Read\ntick: Daily\n---\n2026-08-10\n2026-08-11\n2026-08-12\n"
    local streak = core.parse_streak(raw, "read")

    local stats = core.calculate_stats(streak, "2026-08-12")
    assert(stats.current_streak == 3, "current streak 3")
    assert(stats.longest_streak == 3, "longest streak 3")
    assert(stats.ticked_today == true, "ticked today true")
    assert(stats.total_ticks == 3, "total ticks 3")

    local stats_gap = core.calculate_stats(streak, "2026-08-14")
    assert(stats_gap.current_streak == 0, "current streak 0 after gap")
    assert(stats_gap.longest_streak == 3, "longest streak remains 3")
    assert(stats_gap.ticked_today == false, "ticked today false")
end

function tests.test_json_encoder()
    local obj = { name = "test", count = 5, active = true, items = { "a", "b" } }
    local encoded = json.encode(obj)
    local decoded = json.decode(encoded)

    assert(decoded.name == "test", "json string")
    assert(decoded.count == 5, "json number")
    assert(decoded.active == true, "json bool")
    assert(#decoded.items == 2, "json array length")
    assert(decoded.items[1] == "a", "json array item")
end

function tests.test_timestamp_preservation()
    -- Sample raw streak content matching user format with timestamps
    local raw = "---\nname: Business Updates\ntick: Daily\n---\n2025-01-07\n2025-01-09T09:37:44.377302\n2025-01-10T16:44:14.656836\n"
    local streak = core.parse_streak(raw, "business-updates")

    assert(#streak.dates == 3, "parsed 3 dates")
    assert(streak.date_set["2025-01-07"] == true, "has date 1")
    assert(streak.date_set["2025-01-09"] == true, "has date 2")
    assert(streak.date_set["2025-01-10"] == true, "has date 3")

    -- Format back without changes and ensure original formatting is preserved 100%
    local formatted = core.format_streak(streak)
    assert(formatted:find("2025-01-09T09:37:44.377302", 1, true) ~= nil, "timestamp preserved")
    assert(formatted:find("2025-01-10T16:44:14.656836", 1, true) ~= nil, "timestamp preserved")
    assert(formatted:find("2025-01-07", 1, true) ~= nil, "simple date preserved")

    -- Now tick a new date "2025-01-11"
    -- Since we aren't calling tick_streak directly in this core test, let's update model state like repo.tick_streak does
    local target_date = "2025-01-11"
    streak.date_set[target_date] = true
    table.insert(streak.dates, target_date)
    table.insert(streak.raw_lines, { date = target_date, line = target_date })

    local formatted_ticked = core.format_streak(streak)
    assert(formatted_ticked:find("2025-01-09T09:37:44.377302", 1, true) ~= nil, "timestamp preserved after tick")
    assert(formatted_ticked:find("2025-01-10T16:44:14.656836", 1, true) ~= nil, "timestamp preserved after tick")
    assert(formatted_ticked:find("2025-01-11", 1, true) ~= nil, "new tick line added")
end

return tests
