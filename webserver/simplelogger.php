<?php

class Logger
{
    const CRITICAL = 50;
    const FATAL = self::CRITICAL;
    const ERROR = 40;
    const WARNING = 30;
    const INFO = 20;
    const DEBUG = 10;
    const NOTSET = 0;

    private $filename = null;
    private $filemode = null;
    private $filehandle = null;
    public $formatstring = "{time}\t{levelname}\t{filename}:{funcname}:{line}\t{message}";
    public $formattime = "Y-m-d H:i:s.v";
    public $loglevel = self::WARNING;
    private $_errorlevels = array();
    

    public function __construct($filename, $loglevel=self::WARNING, $mode="a")
    {
        $this->filename = $filename;
        $this->loglevel = $loglevel;
        $this->filemode = $mode;

        $this->_errorlevels = [
            self::CRITICAL => "CRITICAL",
            self::FATAL => "FATAL",
            self::ERROR => "ERROR",
            self::WARNING => "WARNING",
            self::INFO => "INFO",
            self::DEBUG => "DEBUG",
            self::NOTSET => "NOTSET",
        ];
    }

    public function __destruct()
    {
        if($this->filehandle == null)
            return;
        fclose($this->filehandle);
    }

    private function openlog()
    {
        if($this->filehandle != null || $this->filename == null || $this->filename == "")
            return false;
        
        $this->filehandle = fopen($this->filename, $this->filemode);
        return true;
    }



    public function error($message)
    {
        $this->log(self::ERROR, $message, true);
    }

    public function warning($message)
    {
        $this->log(self::WARNING, $message, true);
    }

    public function info($message)
    {
        $this->log(self::INFO, $message, true);
    }

    public function debug($message)
    {
        $this->log(self::DEBUG, $message, true);
    }

    public function log($level, $message, $secondstage=false)
    {
        if($level < $this->loglevel || $this->loglevel == self::NOTSET)
        {
            return;
        }

        

        $trace_offset = 0;
        if($secondstage == true)
            $trace_offset++;
        $trackback = debug_backtrace();
        $file = $trackback[$trace_offset + 0]["file"];
        $line = $trackback[$trace_offset + 0]["line"];
        $func = "__module__";
        if(count($trackback) > ($trace_offset + 1))
        {
            $func = $trackback[$trace_offset + 1]["function"];
        }

        $this->log_raw($level, $file, $line, $func, $message);
    }

    public function log_raw($level, $file, $line, $func, $message)
    {
        if($level < $this->loglevel || $this->loglevel == self::NOTSET)
        {
            return;
        }

        if($this->openlog() == false)
        {
            return;
        }


        $levelname = "UNKNOWN";
        if(array_key_exists($level, $this->_errorlevels))
        {
            $levelname = $this->_errorlevels[$level];
        }

        $time = (new DateTime())->format($this->formattime);

        fwrite($this->filehandle, strtr($this->formatstring . "\n", [
            "{time}" => $time,
            "{level}" => $level,
            "{levelname}" => $levelname,
            "{filename}" => $file,
            "{funcname}" => $func,
            "{line}" => $line,
            "{message}" => $message,
        ]));
    }


}