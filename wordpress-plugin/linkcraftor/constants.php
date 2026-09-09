<?php

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

if ( ! defined( 'LINKCRAFTOR_PLUGIN_DIR' ) ) {
    define( 'LINKCRAFTOR_PLUGIN_DIR', __DIR__ );
}

if ( ! defined( 'LINKCRAFTOR_SRC_DIR' ) ) {
    define( 'LINKCRAFTOR_SRC_DIR', LINKCRAFTOR_PLUGIN_DIR . DIRECTORY_SEPARATOR . 'src' );
}

if ( ! defined( 'LINKCRAFTOR_ASSETS_DIR' ) ) {
    define( 'LINKCRAFTOR_ASSETS_DIR', LINKCRAFTOR_PLUGIN_DIR . DIRECTORY_SEPARATOR . 'assets' );
}

if ( ! defined( 'LINKCRAFTOR_PLUGIN_SLUG' ) ) {
    define( 'LINKCRAFTOR_PLUGIN_SLUG', 'linkcraftor' );
}

if ( ! defined( 'LINKCRAFTOR_TEXT_DOMAIN' ) ) {
    define( 'LINKCRAFTOR_TEXT_DOMAIN', 'linkcraftor' );
}