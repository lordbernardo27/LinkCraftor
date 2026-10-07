<?php

namespace LinkCraftor\Runtime;

final class UninstallPolicy
{
    public const PROTECTED_OPTIONS = [
        'linkcraftor_installation_id',
        'linkcraftor_site_identity',
        'linkcraftor_site_mapping',
        'linkcraftor_post_mappings',
        'linkcraftor_connection_registry',
        'linkcraftor_phrase_preparation_state',
    ];

    private const DISPOSABLE_OPTIONS = [
        Lifecycle::STATE_OPTION,
        'linkcraftor_runtime_notice',
        'linkcraftor_activation_error',
    ];

    public static function run(): void
    {
        foreach ( self::DISPOSABLE_OPTIONS as $option ) {
            if ( function_exists( 'delete_option' ) ) {
                delete_option( $option );
            }
        }
    }

    public static function protectedOptions(): array
    {
        return self::PROTECTED_OPTIONS;
    }
}