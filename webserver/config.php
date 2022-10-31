<?php

include("simplelogger.php");

$pirozeda_host = "http://127.0.0.1:19000";
// leave file name empty or rise log level to disable logging
$log_file = "php_backend.log";
$log_level = Logger::ERROR;



$log = new Logger($log_file, $log_level);

if($log_level >= Logger::ERROR)
{
    function merh(int $errno, string $errstr, string $errfile, int $errline, array $errcontext)
    {
        global $log;
        $log->log_raw(Logger::ERROR, $errfile, $errline, "?", "Unhandled error: " . $errstr);
    }

    set_error_handler("merh", E_ALL);

    function mexh(Throwable $exception)
    {
        global $log;
        $log->log_raw(Logger::ERROR, $exception->getFile(), $exception->getLine(), "?", "Unhandled exception: " . $exception->getMessage());
    }

    set_exception_handler('mexh');
}
