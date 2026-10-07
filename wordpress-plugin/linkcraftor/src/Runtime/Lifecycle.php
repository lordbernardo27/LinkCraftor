<?php

namespace LinkCraftor\Runtime;

final class Lifecycle
{
    public const STATE_OPTION = 'linkcraftor_lifecycle_state';

    public const UNINSTALL_POLICY_OPTION = 'linkcraftor_uninstall_policy';

    public const UNINSTALL_POLICY_PRESERVE_MAPPINGS = 'preserve_mappings';

    private const SCHEDULED_HOOKS = [
        'linkcraftor_runtime_tick',
        'linkcraftor_sync_tick',
        'linkcraftor_automation_tick',
    ];

    public static function register(): void
    {
        if ( function_exists( 'register_activation_hook' ) ) {
            register_activation_hook(
                LINKCRAFTOR_PLUGIN_FILE,
                [ self::class, 'activate' ]
            );
        }

        if ( function_exists( 'register_deactivation_hook' ) ) {
            register_deactivation_hook(
                LINKCRAFTOR_PLUGIN_FILE,
                [ self::class, 'deactivate' ]
            );
        }
    }

    public static function activate(): void
    {
        global $wp_version;

        $errors = self::environmentErrors(
            isset( $wp_version ) ? (string) $wp_version : '',
            PHP_VERSION
        );

        if ( $errors !== [] ) {
            $message = implode( ' ', $errors );

            if ( function_exists( 'wp_die' ) ) {
                wp_die(
                    esc_html( $message ),
                    esc_html__( 'LinkCraftor activation failed', 'linkcraftor' )
                );
            }

            throw new \RuntimeException( $message );
        }

        $existing = function_exists( 'get_option' )
            ? get_option( self::STATE_OPTION, [] )
            : [];

        if ( ! is_array( $existing ) ) {
            $existing = [];
        }

        $timestamp = self::timestamp();

        $state = [
            'status'             => 'active',
            'plugin_version'     => LINKCRAFTOR_VERSION,
            'protocol_version'   => LINKCRAFTOR_PROTOCOL_VERSION,
            'first_activated_at' => $existing['first_activated_at'] ?? $timestamp,
            'activated_at'       => $timestamp,
            'deactivated_at'     => null,
        ];

        self::writeOption(
            self::STATE_OPTION,
            $state
        );

        \LinkCraftor\Identity\InstallationIdentity::getOrCreate();
        \LinkCraftor\Identity\SiteIdentity::getOrCreate();

        if (
            function_exists( 'get_option' )
            && false === get_option( self::UNINSTALL_POLICY_OPTION, false )
        ) {
            self::addOption(
                self::UNINSTALL_POLICY_OPTION,
                self::UNINSTALL_POLICY_PRESERVE_MAPPINGS
            );
        }
    }

    public static function deactivate(): void
    {
        foreach ( self::SCHEDULED_HOOKS as $hook ) {
            if ( function_exists( 'wp_clear_scheduled_hook' ) ) {
                wp_clear_scheduled_hook( $hook );
            }
        }

        $existing = function_exists( 'get_option' )
            ? get_option( self::STATE_OPTION, [] )
            : [];

        if ( ! is_array( $existing ) ) {
            $existing = [];
        }

        $existing['status']         = 'inactive';
        $existing['deactivated_at'] = self::timestamp();

        self::writeOption(
            self::STATE_OPTION,
            $existing
        );
    }

    public static function environmentErrors(
        string $wordpress_version,
        string $php_version
    ): array {
        $errors = [];

        if (
            $wordpress_version === ''
            || version_compare(
                $wordpress_version,
                LINKCRAFTOR_MIN_WP_VERSION,
                '<'
            )
        ) {
            $errors[] = sprintf(
                'LinkCraftor requires WordPress %s or later.',
                LINKCRAFTOR_MIN_WP_VERSION
            );
        }

        if (
            version_compare(
                $php_version,
                LINKCRAFTOR_MIN_PHP_VERSION,
                '<'
            )
        ) {
            $errors[] = sprintf(
                'LinkCraftor requires PHP %s or later.',
                LINKCRAFTOR_MIN_PHP_VERSION
            );
        }

        return $errors;
    }

    private static function writeOption(
        string $name,
        mixed $value
    ): void {
        if ( ! function_exists( 'get_option' ) ) {
            return;
        }

        if ( false === get_option( $name, false ) ) {
            self::addOption( $name, $value );

            return;
        }

        if ( function_exists( 'update_option' ) ) {
            update_option( $name, $value );
        }
    }

    private static function addOption(
        string $name,
        mixed $value
    ): void {
        if ( function_exists( 'add_option' ) ) {
            add_option(
                $name,
                $value,
                '',
                false
            );
        }
    }

    private static function timestamp(): string
    {
        if ( function_exists( 'current_time' ) ) {
            return (string) current_time( 'mysql', true );
        }

        return gmdate( 'Y-m-d H:i:s' );
    }
}