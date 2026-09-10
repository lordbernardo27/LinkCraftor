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

if ( ! defined( 'LINKCRAFTOR_CONFIG_FILE' ) ) {
    define( 'LINKCRAFTOR_CONFIG_FILE', LINKCRAFTOR_PLUGIN_DIR . DIRECTORY_SEPARATOR . 'config.php' );
}

if ( ! defined( 'LINKCRAFTOR_PLUGIN_SLUG' ) ) {
    define( 'LINKCRAFTOR_PLUGIN_SLUG', 'linkcraftor' );
}

if ( ! defined( 'LINKCRAFTOR_TEXT_DOMAIN' ) ) {
    define( 'LINKCRAFTOR_TEXT_DOMAIN', 'linkcraftor' );
}

if ( ! defined( 'LINKCRAFTOR_VERSION' ) ) {
    define( 'LINKCRAFTOR_VERSION', '0.1.0' );
}

if ( ! defined( 'LINKCRAFTOR_MIN_WP_VERSION' ) ) {
    define( 'LINKCRAFTOR_MIN_WP_VERSION', '6.9' );
}

if ( ! defined( 'LINKCRAFTOR_MIN_PHP_VERSION' ) ) {
    define( 'LINKCRAFTOR_MIN_PHP_VERSION', '8.3' );
}

if ( ! defined( 'LINKCRAFTOR_PROTOCOL_VERSION' ) ) {
    define( 'LINKCRAFTOR_PROTOCOL_VERSION', '1.0' );
}