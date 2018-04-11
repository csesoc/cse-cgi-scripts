<?php

$user = $_GET["user"];
if (!preg_match("/^[a-z0-9]+$/", $user)) {
   die();
}

header("Content-Type: text/plain");
$arg = escapeshellarg("user.$user");
system("udb $arg");
?>
