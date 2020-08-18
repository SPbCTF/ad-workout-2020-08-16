<?php
// protocol: g|id
//           p|id|flag
//           c|nonce

// p|1231-1231-1231|1234567890123456789012345678901=

// $_SERVER['SCRIPT_FILENAME'] == "/var/www/index.php"
// $_SERVER['GATEWAY_INTERFACE'] == "CGI/1.1"
// $_SERVER['SERVER_PROTOCOL'] == "HTTP/0.9"
// $_SERVER['REQUEST_URI'] == ""
// $_SERVER['REQUEST_METHOD'] == "qwe"

// bad chars: 00 09 0a 0b 0c 0d 20

// decrypt with: SCRIPT_FILENAME, GATEWAY_INTERFACE, REQUEST_URI, SERVER_PROTOCOL, hash(crc32b, __FILE__)
// iv: part of $_SERVER['REQUEST_METHOD'] 

// 1. SQL injection
// 2. SELECT INTO OUTFILE /var/www/tmp/ (0777 dir)  <- doesnt work, screwed up :(
// 3. RCE via crypto
// 4. Obvious backdoor with crc32 forging 0xDEADdbDB into mysql_query

// backdoor: if (self is not 0666 /*hell*/ or tmp is not 0777 /*heaven*/ or exists tmp/.htaccess or not exists tmp/.htdenied or crc32(tmp/.htdenied) != 0xDEADdbDB) and crc32(query) == 0xDEADdbDB

// encryption: $key = md5($_SERVER['SCRIPT_FILENAME'] . $_SERVER['GATEWAY_INTERFACE'] . $_SERVER['REQUEST_URI'] . $_SERVER['SERVER_PROTOCOL'] . hash('crc32b', __FILE__, true/*==FFFFFFFF*/), true)
// $key = "\xf9\x85\xcb\xd6\xbb\xf9\x21\x39\x62\x28\xaa\x9b\xb4\x4a\xd4\x99";
// $iv = "\x94\xae\xc3\x7f\xf4\x92\xfe\x82\x29\x07\x2c\x12\x90\xa4\x87\x61";


$m = $_SERVER['REQUEST_METHOD'];
if ((strlen($m) % 16) != 0 || strlen($m) < 48) {
    header("HTTP/1.1 400 Bad Request");
    exit('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>400 Bad Request</title>
</head><body>
<h1>Bad Request</h1>
<p>Your browser sent a request that this server could not understand.<br />
</p>
<hr>
<address>Apache/2.2.22 (Ubuntu) Server at 172.17.0.2 Port 80</address>
</body></html>
');
}

mysql_connect("localhost", "root", "");
mysql_query('CREATE DATABASE IF NOT EXISTS `db`');
mysql_select_db("db");
mysql_query('
    CREATE TABLE IF NOT EXISTS `storage` (
      `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `time` int NOT NULL,
      `key` varchar(16) NOT NULL,
      `data` varchar(32) NOT NULL
    );
');

$k = substr($m, 0, 32);
$i = substr($m, 32, 16);
$e = substr($m, 48);
$d = mcrypt_decrypt("loki97", $k, $e, "cbc", $i);
$d = rtrim($d, "\x00");

list ($m, $y, $d) = explode('|', $d, 3);

$r = '';
if ($m == 'g') {
    $r = mysql_query("SELECT * FROM `storage` WHERE `key` = \"$y\"");
    $r = mysql_fetch_assoc($r);
    $r = $r['data'];
} elseif ($m == 'p') {
    mysql_query("INSERT INTO `storage` (`time`, `key`, `data`) VALUES (" . time() . ", \"$y\", \"$d\")");
    $r = mysql_insert_id();
} elseif ($m == 'c') {
    $r = md5(file_get_contents(__FILE__) . $y);
} else {
    $r = '?';
}

$i = mcrypt_create_iv(16, MCRYPT_DEV_URANDOM);
$r = mcrypt_encrypt("loki97", $k, $r, "cbc", $i);

echo $i, $r;
exit;
