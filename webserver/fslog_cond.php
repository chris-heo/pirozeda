<?php
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
//my windows machine seems to hate localhost.
//when using that hostname, it takes around 3 seconds to resolve it
//with 127.0.0.1 it just works. There's no place like 127.0.0.1

/*$df = 1525125600;
$dt = 1530395976;
$client = new Client('http://127.0.0.1:19000');
$result = $client->fslog_readcondensed($df, $dt, 2);
echo json_encode($result);
exit();*/

if(!isset($_GET["action"]) || !isset($_GET["datefrom"]) || !isset($_GET["dateto"]) || !isset($_GET["col"]))
{
	exit();
}

$client = new Client('http://127.0.0.1:19000');

if($_GET["action"] == "chart")
{
	$result = $client->fslog_readcondensed(intval($_GET["datefrom"]), intval($_GET["dateto"]), intval($_GET["col"]));
	echo json_encode($result);
}
