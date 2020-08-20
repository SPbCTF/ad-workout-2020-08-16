# GoRePiCk

 - Author: Roman Opyakin ([Sinketsu](https://github.com/Sinketsu))
 - Language: **Go**
 
## Description

According to legend it is a backend GRPC API for registering users and teams to play CTF.

- Protobuf + GRPC
- Redis + lua scripts

## Deploy

```bash
docker-compose up -d --build
```

## Vulns

1. Bad validation on `authorization` header. 

   In [auth.go](service/api/auth.go) we have:
   ```go
   auth := authHeader[0]
   idx := strings.LastIndex(auth, ":")
   token := auth[idx+1:]
   login := auth[:idx]
   ```
   
   But in [server.go](service/api/server.go) we have:
   ```go 
   func (s *Server) GetUsername(ctx context.Context) string {
   	...
   	auth := authHeader[0]
   	authData := strings.Split(auth, ":")
   
   	return authData[0]
   }
   ```
   
   So, we can register user with name like `flagUser:<somestring>` and get flags as user `flagUser`
   
   [Exploit](sploits/registerUser.go)
   
2. Predictable join token.

   In [create_team.lua](service/storage/scripts/create_team.lua) we have:
   ```lua
   local time = redis.pcall('TIME')
   math.randomseed(time[1])
   local rnd = math.random()
   local join_token = redis.sha1hex(rnd)
   ```
   
   Random generator seeds by current time. According to [this](https://redis.io/commands/time), `TIME` function in redis returns array `[<unix time in seconds>, <microseconds>]`. So, if we now the timestamp of team creation we can generate the same join token. Timestamp of creation we have from `/Events` stream in API.
   
   [Exploit](sploits/teamInvite.go)
   
