<?php
include("config.php");
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
//my windows machine seems to hate localhost.
//when using that hostname, it takes around 3 seconds to resolve it
//with 127.0.0.1 it just works. There's no place like 127.0.0.1

$log->debug("fslog requested");

if(!isset($_GET["action"]) || !isset($_GET["datefrom"]) || !isset($_GET["dateto"]))
{
    $log->warning("required parameter not set");
    exit();
}

$client = new Client($pirozeda_host);

if($_GET["action"] == "chart")
{
    $result = $client->fslog_read(intval($_GET["datefrom"]), intval($_GET["dateto"]));
    echo json_encode($result);
    $log->debug("fslog chart returned");
}
else
{
    $log->warning("unknown action: " . $_GET["action"]);
}
