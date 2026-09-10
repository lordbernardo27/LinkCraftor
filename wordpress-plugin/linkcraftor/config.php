<?php

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

return [
    'environment' => 'production',

    'api' => [
        'production' => null,
        'staging'    => null,
        'development'=> null,
    ],

    'http' => [
        'timeout_seconds' => 20,
    ],

    'features' => [
        'debug' => false,
    ],
];