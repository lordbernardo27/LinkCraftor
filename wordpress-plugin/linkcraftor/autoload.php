<?php

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

spl_autoload_register(
    static function ( string $class ): void {
        $prefix = 'LinkCraftor\\';

        if ( strncmp( $class, $prefix, strlen( $prefix ) ) !== 0 ) {
            return;
        }

        $relative_class = substr( $class, strlen( $prefix ) );

        if ( $relative_class === '' ) {
            return;
        }

        $relative_path = str_replace( '\\', DIRECTORY_SEPARATOR, $relative_class ) . '.php';
        $file          = __DIR__ . DIRECTORY_SEPARATOR . 'src' . DIRECTORY_SEPARATOR . $relative_path;

        if ( is_readable( $file ) ) {
            require_once $file;
        }
    }
);
