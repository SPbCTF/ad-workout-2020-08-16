local username = KEYS[1]
local team = KEYS[2]
local token = KEYS[3]

-- we don't need transaction
-- Redis when execute Lua script use STW
local exists = redis.pcall('HGET', 'teams:name', team)
if not exists then
    return { err = "Team not found" }
end

local join_token = redis.pcall('HGET', 'teams:join_token', team)
if token ~= join_token then
    return { err = "Access denied. Invalid join token" }
end

local user_team = redis.pcall('HGET', 'participants', username)
if user_team == team then
    return { err = "Already joined" }
end

redis.pcall("HSET", 'participants', username, team)
return { ok = "OK" }

