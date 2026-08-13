-- streak_lua/json.lua
-- Minimal, robust JSON encoder/decoder for Lua 5.4

local json = {}

local function escape_str(s)
    local escape_map = {
        ['"'] = '\\"',
        ['\\'] = '\\\\',
        ['\b'] = '\\b',
        ['\f'] = '\\f',
        ['\n'] = '\\n',
        ['\r'] = '\\r',
        ['\t'] = '\\t',
    }
    return s:gsub('["\\\b\f\n\r\t]', escape_map)
end

function json.encode(val)
    local t = type(val)
    if t == "nil" then
        return "null"
    elseif t == "boolean" or t == "number" then
        return tostring(val)
    elseif t == "string" then
        return '"' .. escape_str(val) .. '"'
    elseif t == "table" then
        -- Check if it is an array
        local is_array = false
        local n = #val
        if n > 0 then
            is_array = true
        else
            -- Empty table default to object or array if explicit
            if val._is_array then is_array = true end
        end

        if is_array then
            local parts = {}
            for i = 1, n do
                table.insert(parts, json.encode(val[i]))
            end
            return "[" .. table.concat(parts, ",") .. "]"
        else
            local parts = {}
            for k, v in pairs(val) do
                if type(k) == "string" and k:sub(1, 1) ~= "_" then
                    table.insert(parts, json.encode(k) .. ":" .. json.encode(v))
                end
            end
            table.sort(parts)
            return "{" .. table.concat(parts, ",") .. "}"
        end
    else
        error("Cannot json-encode type: " .. t)
    end
end

-- Parser implementation
local function skip_whitespace(str, pos)
    return str:match("^%s*()", pos)
end

local parse_value -- forward declaration

local function parse_object(str, pos)
    local obj = {}
    pos = pos + 1 -- skip '{'
    pos = skip_whitespace(str, pos)
    if str:sub(pos, pos) == "}" then
        return obj, pos + 1
    end

    while pos <= #str do
        local key
        key, pos = parse_value(str, pos)
        if type(key) ~= "string" then
            error("Expected string key in JSON object at pos " .. tostring(pos))
        end
        pos = skip_whitespace(str, pos)
        if str:sub(pos, pos) ~= ":" then
            error("Expected ':' after key in JSON object at pos " .. tostring(pos))
        end
        pos = skip_whitespace(str, pos + 1)
        local val
        val, pos = parse_value(str, pos)
        obj[key] = val
        pos = skip_whitespace(str, pos)
        local c = str:sub(pos, pos)
        if c == "}" then
            return obj, pos + 1
        elseif c == "," then
            pos = skip_whitespace(str, pos + 1)
        else
            error("Expected ',' or '}' in JSON object at pos " .. tostring(pos))
        end
    end
    error("Unterminated JSON object")
end

local function parse_array(str, pos)
    local arr = {}
    pos = pos + 1 -- skip '['
    pos = skip_whitespace(str, pos)
    if str:sub(pos, pos) == "]" then
        return arr, pos + 1
    end

    while pos <= #str do
        local val
        val, pos = parse_value(str, pos)
        table.insert(arr, val)
        pos = skip_whitespace(str, pos)
        local c = str:sub(pos, pos)
        if c == "]" then
            return arr, pos + 1
        elseif c == "," then
            pos = skip_whitespace(str, pos + 1)
        else
            error("Expected ',' or ']' in JSON array at pos " .. tostring(pos))
        end
    end
    error("Unterminated JSON array")
end

local function parse_string(str, pos)
    local finish = pos + 1
    while finish <= #str do
        local c = str:sub(finish, finish)
        if c == '"' then
            local s = str:sub(pos + 1, finish - 1)
            s = s:gsub("\\n", "\n"):gsub("\\r", "\r"):gsub("\\t", "\t"):gsub('\\"', '"'):gsub("\\\\", "\\")
            return s, finish + 1
        elseif c == "\\" then
            finish = finish + 2
        else
            finish = finish + 1
        end
    end
    error("Unterminated string in JSON")
end

local function parse_number(str, pos)
    local num_str = str:match("^-?%d+%.?%d*[eE]?[+-]?%d*", pos)
    local num = tonumber(num_str)
    if not num then error("Invalid number in JSON at pos " .. pos) end
    return num, pos + #num_str
end

parse_value = function(str, pos)
    pos = skip_whitespace(str, pos)
    local c = str:sub(pos, pos)
    if c == "{" then
        return parse_object(str, pos)
    elseif c == "[" then
        return parse_array(str, pos)
    elseif c == '"' then
        return parse_string(str, pos)
    elseif c == "t" and str:sub(pos, pos + 3) == "true" then
        return true, pos + 4
    elseif c == "f" and str:sub(pos, pos + 4) == "false" then
        return false, pos + 5
    elseif c == "n" and str:sub(pos, pos + 3) == "null" then
        return nil, pos + 4
    elseif c == "-" or c:match("%d") then
        return parse_number(str, pos)
    else
        error("Unexpected character in JSON at pos " .. pos .. ": '" .. c .. "'")
    end
end

function json.decode(str)
    if not str or str == "" then return nil end
    local val, _ = parse_value(str, 1)
    return val
end

return json
