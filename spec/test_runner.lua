-- spec/test_runner.lua
-- Runner for Lua unit test suites

package.path = ";./?.lua;./?/init.lua;" .. package.path

local core_tests = require("spec.streak_core_spec")
local repo_tests = require("spec.repository_spec")

local total, passed, failed = 0, 0, 0

local function run_suite(name, suite)
    print("Running suite: " .. name)
    for test_name, fn in pairs(suite) do
        total = total + 1
        local ok, err = pcall(fn)
        if ok then
            passed = passed + 1
            print("  ✓ " .. test_name)
        else
            failed = failed + 1
            print("  ✗ " .. test_name .. " -> " .. tostring(err))
        end
    end
end

run_suite("streak_core_spec", core_tests)
run_suite("repository_spec", repo_tests)

print(string.format("\nTest Summary: %d total, %d passed, %d failed", total, passed, failed))

if failed > 0 then
    os.exit(1)
end
