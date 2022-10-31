<?php
include("config.php");
include("vendor/autoload.php");
use JsonRPC\Client;
header("Content-Type: application/json");
//my windows machine seems to hate localhost.
//when using that hostname, it takes around 3 seconds to resolve it
//with 127.0.0.1 it just works. There's no place like 127.0.0.1
$client = new Client($pirozeda_host);

$log->debug("filetrace requested");

if(!isset($_GET["action"]))
{
    $log->warning("required parameter not set");
    exit();
} 

$action = $_GET["action"];
if($action == "start")
{
    $log->debug("start requested");

    if(isset($_GET["duration"]))
    {
        $duration = intval($_GET["duration"]);
        $log->debug("duration: " . $duration);
        $result = $client->trace_start($duration);
    }
}
else if($action == "stop")
{
    $log->debug("stop requested");
    $result = $client->trace_stop();
}
echo json_encode($result);

$log->debug("filetrace returned");
