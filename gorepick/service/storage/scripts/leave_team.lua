local username = KEYS[1]

-- we don't need transaction
-- Redis when execute Lua script use STW
local joined = redis.pcall('HGET', 'participants', username)
if not joined then
    return { err = "Already leaved" }
end

redis.pcall('HDEL', 'participants', username)
return { ok = "OK" }
