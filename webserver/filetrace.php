<?php
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
//my windows machine seems to hate localhost.
//when using that hostname, it takes around 3 seconds to resolve it
//with 127.0.0.1 it just works. There's no place like 127.0.0.1
$client = new Client('http://127.0.0.1:19000');

if(!isset($_GET["action"])) exit();
$action = $_GET["action"];
if($action == "start")
{
    if(isset($_GET["duration"]))
    {
        $duration = intval($_GET["duration"]);
        $result = $client->trace_start($duration);
    }
}
else if($action == "stop")
{
    $result = $client->trace_stop();
}
echo json_encode($result);