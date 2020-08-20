local username = KEYS[1]
local password = KEYS[2]

-- we don't need transaction
-- Redis when execute Lua script use STW
local exists = redis.pcall('HGET', 'users', username)
if exists then
    return { err = "User already exists" }
end

local token = redis.sha1hex(password)
redis.pcall('HSET', 'users', username, token)
return { ok = token }
