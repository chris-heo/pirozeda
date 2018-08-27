<?php
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
//my windows machine seems to hate localhost.
//when using that hostname, it takes around 3 seconds to resolve it
//with 127.0.0.1 it just works. There's no place like 127.0.0.1

if(!isset($_GET["action"]) || !isset($_GET["datefrom"]) || !isset($_GET["dateto"]))
{
	exit();
}

$client = new Client('http://127.0.0.1:19000');

if($_GET["action"] == "chart")
{
	$result = $client->fslog_read(intval($_GET["datefrom"]), intval($_GET["dateto"]));
	echo json_encode($result);
}
