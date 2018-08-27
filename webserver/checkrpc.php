<?php

include("vendor/autoload.php");
use JsonRPC\Client;

try {
    $client = new Client('http://localhost:19000');
    print_r($client->info());
}
catch(Exception $ex)
{
    echo "<pre>";
    echo "no love :(";
    print_r($ex);
    echo "</pre>";
}
