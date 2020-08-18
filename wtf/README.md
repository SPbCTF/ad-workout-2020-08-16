# wtf

 - Author: Vlad Roskov ([v0s](https://github.com/v0s))
 - Language: **PHP**
 - Idea: Apache in old versions allows requests consisting of a single word, triggering `/index.php` and treating the word as `REQUEST_METHOD`
 - Bugs: backdoor triggered via CRC32 forcing, SQL injection, RCE via IV manipulation

## Vulns

1. Obvious backdoor in the plaintext part. Trigger by constructing an SQL query and forcing its CRC32 to `0xDEADdbDB` using e.g. [crchack](https://github.com/resilar/crchack)
   
   [Example SQL query](sploits/1_sql_query_crc.txt)

2. Simple SQL injection inside get/put API methods

   [Exploit](sploits/2_sqli_client.php)

3. RCE via IV manipulation

   [Exploit](sploits/3_iv_pwn.php) 

## Development stages

[Here](dev/)
