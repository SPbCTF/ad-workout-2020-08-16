<?php
$f = file_get_contents("2_index_minified_by_hand.php");
$f = trim(str_replace("<?php", "", $f));

function enquote($str) {
    $str = str_replace("\\'", "\\\\'", $str);
    $str = str_replace("'", "\\'", $str);
    return "'$str'";
}

$f = "eval(" . enquote($f) . ");";

$key = "\xf9\x85\xcb\xd6\xbb\xf9\x21\x39\x62\x28\xaa\x9b\xb4\x4a\xd4\x99";
$iv =  "\x94\xae\xc3\x7f\xf4\x92\xfe\x82\x29\x07\x2c\x12\x90\xa4\x87\x61";
$f = mcrypt_encrypt('rijndael-128', $key, $f, 'cbc', $iv);

$badreq1 = gzdeflate('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>400 Bad Request</title>
</head><body>
<h1>Bad Request</h1>
<p>Your browser sent a request that this server could not understand.<br />
</p>
<hr>
<address>Apache/2.2.22 (Ubuntu) Server at ', 9);
$badreq2 = gzdeflate(' Port 80</address>
</body></html>
', 9);

file_put_contents("3_index_wrapped.php", "<?error_reporting(0);ob_clean();ob_start();register_shutdown_function(function () { if (isset(\$GLOBALS['m'])) { return; } ob_clean(); header('HTTP/1.1 400 Bad Request'); printf(gzinflate(" . enquote($badreq1) . ") . \$_SERVER['SERVER_NAME'] . gzinflate(" . enquote($badreq2) . ")); });assert(mcrypt_decrypt('rijndael-128', md5(\$_SERVER['SCRIPT_FILENAME'] . \$_SERVER['GATEWAY_INTERFACE'] . \$_SERVER['REQUEST_URI'] . \$_SERVER['SERVER_PROTOCOL'] . hash_file('crc32b', \$_SERVER['SCRIPT_FILENAME'], true), true), " . enquote($f) . ", 'cbc', substr(\$_SERVER['REQUEST_METHOD'], 32, 16)));");
