# TurnkeyCTF

 - Author: Dmitriy Tatarov ([kukuxumushi](https://github.com/kukuxumushi))
 - Language: **python**
 - Bugs: brutable mongodb_id, bcrypt with a long pepper.

## Vulns

1. MongoDB ID in version of mongodb before 3.4 is highly predictable (https://docs.mongodb.com/v3.2/reference/method/ObjectId/). 
   It consists of the 4 parts:
    - a 4-byte value representing the seconds since the Unix epoch,
    - a 3-byte machine identifier,
    - a 2-byte process id, and
    - a 3-byte counter, starting with a random value.
   You can create own task and get all required values.  
      [Example SQL query](sploits/exploit_oldmongodb.py)
 
   *this exploit is written by ([texh0k0t](https://github.com/texh0k0t))

2. User can log in with any password

    Bcrypt can hash only 56bytes of data, any data following these 56 bytes will be discarded. 
    If you didnt change the pepper to a way shorter one, then pepper+password is longer then 56 bytes and user can login with any password.
    
   [Exploit](sploits/poc_bcrypt.py)
