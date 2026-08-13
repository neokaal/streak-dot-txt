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

return tests
