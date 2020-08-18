<?php
function generate_trash($len) {
    if ($len == 0) {
        $len = mt_rand(100, 2000);
    }
    $res = "";
    while (strlen($res) < $len) {
        $chunk = random_bytes($len);
        $res .= $chunk;
        $res = str_replace('<'.'?', '', $res);
    }
    $res = substr($res, 0, $len);
    return $res;
}

function generate_statement($len) {
    if ($len == 0) {
        $len = mt_rand(100, 2000);
    }
    $forbiddenChars = implode(range("\x00", "\x2F")) . implode(range("\x3A", "\x40")) . implode(range("\x5B", "\x60")) . implode(range("\x7B", "\x7F"));
    $res = "";
    while (strlen($res) < $len) {
        $chunk = random_bytes($len);
        $chunk = str_replace(str_split($forbiddenChars), '', $chunk);
        while ($res == "" && $chunk != "" && is_numeric($chunk[0])) {
            $chunk = substr($chunk, 1);
        }
        $res .= $chunk;
    }
    $res = substr($res, 0, $len);
    return $res;
}

function generate_comment($len) {
    if ($len == 0) {
        $len = mt_rand(100, 2000);
    }
    $forbiddenChars = "\r\n";
    $res = "#";
    while (strlen($res) < $len) {
        $chunk = random_bytes($len);
        $chunk = str_replace(str_split($forbiddenChars), '', $chunk);
        $res .= $chunk;
        $res = str_replace('?'.'>', '', $res);
    }
    $res = substr($res, 0, $len);
    $res .= mt_rand(0, 1) ? "\n" : "\r";
    return $res;
}

function generate_ident($id, $len) {
    static $varList = [];

    if (isset($varList[$id])) {
        return $varList[$id];
    }
    
    if ($len == 0) {
        $len = mt_rand(100, 2000);
    }
    $res = generate_statement($len);
    $varList[$id] = $res;
    return $res;
}

$f = file_get_contents("4_index_wrapped_placeholders.php");

$f = preg_replace_callback('#\{TRASH:(\d+)\}#s', function ($m) { return generate_trash($m[1]); }, $f);
$f = preg_replace_callback('#\{STATEMENT:(\d+)\}#s', function ($m) { return generate_statement($m[1]); }, $f);
$f = preg_replace_callback('#\{IDENT(\w+):(\d+)\}#s', function ($m) { return generate_ident($m[1], $m[2]); }, $f);
$f = preg_replace_callback('#\{COMMENT:(\d+)\}#s', function ($m) { return generate_comment($m[1]); }, $f);
$f = preg_replace_callback('#\{INVERT:([^}]+)\}#s', function ($m) { return ~ $m[1]; }, $f);

file_put_contents("5_index_trashed.php", $f);
