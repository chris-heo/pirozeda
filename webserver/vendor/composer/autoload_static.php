<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInitff36832adaf1effc9d40b6af259160e7
{
    public static $prefixesPsr0 = array (
        'J' => 
        array (
            'JsonRPC' => 
            array (
                0 => __DIR__ . '/..' . '/fguillot/json-rpc/src',
            ),
        ),
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->prefixesPsr0 = ComposerStaticInitff36832adaf1effc9d40b6af259160e7::$prefixesPsr0;

        }, null, ClassLoader::class);
    }
}