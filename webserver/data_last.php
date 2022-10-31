<?php
include("config.php");
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
//my windows machine seems to hate localhost.
//when using that hostname, it takes around 3 seconds to resolve it
//with 127.0.0.1 it just works. There's no place like 127.0.0.1
$log->debug("data_last requested");

$client = new Client($pirozeda_host);
$result = $client->ramlog_getlast();
echo json_encode($result);

$log->debug("data_last returned");
