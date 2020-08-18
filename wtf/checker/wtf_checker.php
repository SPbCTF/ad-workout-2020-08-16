#!/usr/bin/php
<?php
$SERVICE = "wtf";
$PORT = 2943;

require "_checker_common.php";

function info() {
    close("OK", "vulns: 1");
}

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

function check($ip) {
    $nonce = bin2hex(mcrypt_create_iv(16, MCRYPT_DEV_URANDOM));
    $request = "c|$nonce";
    $response = do_request($ip, $request);
    
    closeif($response != md5(file_get_contents("wtf_www_index_php") . $nonce), "MUMBLE", "Service binary integrity check failed");
    
    $testId = randstr(13, "LOHINUM");
    $testFlag = randstr(13, "LOHINUM");
    
    $request = "p|$testId|$testFlag";
    $response = do_request($ip, $request);
    
    closeif(!is_numeric($response), "MUMBLE", "Test data write failed", "Decrypted: $response");

    $request = "g|$testId";
    $response = do_request($ip, $request);
    
    closeif($response !== $testFlag, "MUMBLE", "Test data read failed", "Decrypted: $response");

    close("OK");
}

function put($ip, $flagId, $flag) {
    $request = "p|$flagId|$flag";
    $response = do_request($ip, $request);
    
    closeif(!is_numeric($response), "MUMBLE", "Bad response for PUT", "Decrypted: $response");

    close("OK");
}

function get($ip, $flagId, $flag) {
    $request = "g|$flagId";
    $response = do_request($ip, $request);
    
    closeif($response !== $flag, "CORRUPT", "Can't get correct flag", "Decrypted: $response");

    close("OK");
}

if ($argv[1] == "info") {
    info();
} elseif ($argv[1] == "check") {
    $HOST = $argv[2];
    check($argv[2]);
} elseif ($argv[1] == "put") {
    $HOST = $argv[2];
    put($argv[2], $argv[3], $argv[4]);
} elseif ($argv[1] == "get") {
    $HOST = $argv[2];
    get($argv[2], $argv[3], $argv[4]);
}
