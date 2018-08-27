<?php
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
$client = new Client('http://localhost:19000');
$result = $client->get_lastday();
echo json_encode($result);