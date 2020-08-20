local username = KEYS[1]

local team = redis.pcall('HGET', 'participants', username)
if not team then
    return { username }
end

local team_info = redis.pcall('HGET', 'teams:info', team)
local team_token = redis.pcall('HGET', 'teams:join_token', team)
return { username, team, team_info, team_token }
