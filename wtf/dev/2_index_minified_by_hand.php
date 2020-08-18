<?php
$m=$_SERVER['REQUEST_METHOD'];if((strlen($m)%16)!=0||strlen($m)<48){header("HTTP/1.1 400 Bad Request");exit('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>400 Bad Request</title>
</head><body>
<h1>Bad Request</h1>
<p>Your browser sent a request that this server could not understand.<br />
</p>
<hr>
<address>Apache/2.2.22 (Ubuntu) Server at ' . $_SERVER['SERVER_NAME'] . ' Port 80</address>
</body></html>
');}mysql_connect("localhost","root","");mysql_query('CREATE DATABASE IF NOT EXISTS`db`');mysql_select_db("db");mysql_query('CREATE TABLE IF NOT EXISTS`storage`(`id`int NOT NULL AUTO_INCREMENT PRIMARY KEY,`time`int NOT NULL,`key`varchar(16)NOT NULL,`data`varchar(32)NOT NULL);');$k=substr($m,0,32);$i=substr($m,32,16);$e=substr($m,48);$d=mcrypt_decrypt("loki97",$k,$e,"cbc",$i);$d=rtrim($d,"\0");list($m,$y,$d)=explode('|',$d,3);$r='';if($m=='g'){$r=mysql_query("SELECT*FROM`storage`WHERE`key`=\"$y\"");$r=mysql_fetch_assoc($r);$r=$r['data'];}elseif($m=='p'){mysql_query("INSERT INTO`storage`(`time`,`key`,`data`)VALUES(".time().",\"$y\",\"$d\")");$r=mysql_insert_id();}elseif($m=='c')$r=md5(file_get_contents($_SERVER['SCRIPT_FILENAME']).$y);else$r='?';$i=mcrypt_create_iv(16,MCRYPT_DEV_URANDOM);$r=mcrypt_encrypt("loki97",$k,$r,"cbc",$i);echo$i,$r;exit;