<?php
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
$client = new Client('http://127.0.0.1:19000');
/*
$action = isset($_GET["a"]) ? $_GET["a"] : null;
$args

if($action == null)
{
    exit();
}
else
{
    switch($a)
    {
        case "display_getcurrent":
    }
}

*/

$result = $client->display_getcurrent(null);
echo json_encode($result);