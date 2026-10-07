<?php

if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
    exit;
}

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

if ( ! defined( 'LINKCRAFTOR_PLUGIN_FILE' ) ) {
    define(
        'LINKCRAFTOR_PLUGIN_FILE',
        __DIR__ . DIRECTORY_SEPARATOR . 'linkcraftor.php'
    );
}

require_once __DIR__ . '/constants.php';
require_once __DIR__ . '/autoload.php';

\LinkCraftor\Runtime\UninstallPolicy::run();