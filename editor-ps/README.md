# editor-ps

 - Author: Alexander Menshchikov ([n0str](https://github.com/n0str))
 - Language: **Python**
 - Ideas: Path traversal in consul; Base64 collisions
 - Bugs: Unsanitized variables pass to the consul request; Check an ownership of article by base64, but used resource by its decoded value 

## Vulns

1. `Tag` in `/search` request goes unsanitized 
   
   [Query to /search](sploits/sploit.py)

2. You can add article with another base64 article id, which would be decoded to the other's `article_id` used by `/getComments` action

   [Query to /getComments](sploits/sploit.py)


