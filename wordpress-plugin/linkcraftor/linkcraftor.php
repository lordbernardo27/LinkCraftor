<?php
/**
 * Plugin Name: LinkCraftor
 * Description: Official LinkCraftor integration for WordPress.
 * Version: 0.1.0
 * Requires at least: 6.0
 * Requires PHP: 8.1
 * Author: LinkCraftor
 * Text Domain: linkcraftor
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

if ( ! defined( 'LINKCRAFTOR_PLUGIN_FILE' ) ) {
    define( 'LINKCRAFTOR_PLUGIN_FILE', __FILE__ );
}

require_once __DIR__ . '/constants.php';
require_once __DIR__ . '/autoload.php';