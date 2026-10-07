<?php

namespace LinkCraftor\Identity;

use LinkCraftor\Runtime\Lifecycle;

final class IdentitySnapshot
{
    public static function build(): array
    {
        global $wp_version;

        $lifecycle = function_exists( 'get_option' )
            ? get_option(
                Lifecycle::STATE_OPTION,
                []
            )
            : [];

        if ( ! is_array( $lifecycle ) ) {
            $lifecycle = [];
        }

        return [
            'installation_id'   => InstallationIdentity::getOrCreate(),
            'site_identity'     => SiteIdentity::getOrCreate(),
            'plugin_version'    => LINKCRAFTOR_VERSION,
            'wordpress_version' => isset( $wp_version )
                ? (string) $wp_version
                : '',
            'php_version'       => PHP_VERSION,
            'minimum_php'       => LINKCRAFTOR_MIN_PHP_VERSION,
            'minimum_wordpress' => LINKCRAFTOR_MIN_WP_VERSION,
            'protocol_version'  => LINKCRAFTOR_PROTOCOL_VERSION,
            'lifecycle_status'  => isset( $lifecycle['status'] )
                ? (string) $lifecycle['status']
                : 'unknown',
        ];
    }
}