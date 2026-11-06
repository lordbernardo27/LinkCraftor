<?php

namespace LinkCraftor\Connection;

use LinkCraftor\Identity\IdentitySnapshot;

final class PairingRequestBuilder
{
    public static function build(): array
    {
        return self::buildFromSnapshot(
            IdentitySnapshot::build()
        );
    }

    public static function buildFromSnapshot(
        array $snapshot
    ): array {
        $site_identity = isset(
            $snapshot['site_identity']
        ) && is_array(
            $snapshot['site_identity']
        )
            ? $snapshot['site_identity']
            : [];

        return [
            'installation_id' => self::requiredString(
                $snapshot,
                'installation_id'
            ),

            'site_id' => self::requiredString(
                $site_identity,
                'site_id'
            ),

            'home_url' => self::requiredString(
                $site_identity,
                'home_url'
            ),

            'site_url' => self::requiredString(
                $site_identity,
                'site_url'
            ),

            'blog_id' => self::requiredPositiveInt(
                $site_identity,
                'blog_id'
            ),

            'plugin_version' => self::requiredString(
                $snapshot,
                'plugin_version'
            ),

            'wordpress_version' => self::requiredString(
                $snapshot,
                'wordpress_version'
            ),

            'php_version' => self::requiredString(
                $snapshot,
                'php_version'
            ),

            'protocol_version' => self::requiredString(
                $snapshot,
                'protocol_version'
            ),

            'lifecycle_status' => self::requiredString(
                $snapshot,
                'lifecycle_status'
            ),
        ];
    }

    private static function requiredString(
        array $source,
        string $key
    ): string {
        $value = isset(
            $source[$key]
        )
            ? trim(
                (string) $source[$key]
            )
            : '';

        if ( $value === '' ) {
            throw new \RuntimeException(
                'Missing required pairing field: '
                . $key
            );
        }

        return $value;
    }

    private static function requiredPositiveInt(
        array $source,
        string $key
    ): int {
        $value = $source[$key] ?? null;

        if (
            ! is_int( $value )
            || $value < 1
        ) {
            throw new \RuntimeException(
                'Invalid required pairing field: '
                . $key
            );
        }

        return $value;
    }
}