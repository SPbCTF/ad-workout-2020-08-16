local username = KEYS[1]
local user_token = KEYS[2]

local token = redis.pcall('HGET', 'users', username)
if not token then
    return { err = "User not found" }
end

if token == user_token then
    return { ok = "OK" }
else
    return { err = "Access denied. Invalid token" }
end
