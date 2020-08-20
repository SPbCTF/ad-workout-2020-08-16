local username = KEYS[1]
local name = KEYS[2]
local info = KEYS[3]

-- we don't need transaction
-- Redis when execute Lua script use STW
local exists = redis.pcall('HGET', 'teams:name', name)
if not exists then
    -- get the current timestamp to seed random
    local time = redis.pcall('TIME')
    math.randomseed(time[1])
    local rnd = math.random()
    local join_token = redis.sha1hex(rnd)

    redis.pcall('HSET', 'teams:name', name, name)
    redis.pcall('HSET', 'teams:join_token', name, join_token)
    redis.pcall('HSET', 'teams:info', name, info)

    redis.pcall('HSET', 'participants', username, name)
    return { ok = join_token }
else
    return { err = "Team already exists" }
end
