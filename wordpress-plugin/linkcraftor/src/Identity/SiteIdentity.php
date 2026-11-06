<?php

namespace LinkCraftor\Identity;

final class SiteIdentity
{
    public const OPTION_NAME = 'linkcraftor_site_identity';

    public static function getOrCreate(): array
    {
        $stored = self::get();

        $site_id = (
            is_array( $stored )
            && isset( $stored['site_id'] )
            && self::isValidUuid4( (string) $stored['site_id'] )
        )
            ? (string) $stored['site_id']
            : self::generateSiteId();

        $current = self::buildCurrent();

        $identity = array_merge(
            is_array( $stored ) ? $stored : [],
            $current,
            [
                'site_id' => $site_id,
            ]
        );

        if ( ! function_exists( 'get_option' ) ) {
            return $identity;
        }

        if ( is_array( $stored ) ) {
            if ( function_exists( 'update_option' ) ) {
                update_option(
                    self::OPTION_NAME,
                    $identity
                );
            }

            return $identity;
        }

        if ( function_exists( 'add_option' ) ) {
            add_option(
                self::OPTION_NAME,
                $identity,
                '',
                false
            );
        }

        $persisted = self::get();

        return is_array( $persisted )
            ? $persisted
            : $identity;
    }

    public static function get(): ?array
    {
        if ( ! function_exists( 'get_option' ) ) {
            return null;
        }

        $value = get_option(
            self::OPTION_NAME,
            null
        );

        return is_array( $value )
            ? $value
            : null;
    }

    private static function buildCurrent(): array
    {
        $home_url = function_exists( 'home_url' )
            ? (string) home_url( '/' )
            : '';

        $site_url = function_exists( 'site_url' )
            ? (string) site_url( '/' )
            : $home_url;

        $blog_id = function_exists( 'get_current_blog_id' )
            ? (int) get_current_blog_id()
            : 0;

        return [
            'home_url' => self::normalizeUrl( $home_url ),
            'site_url' => self::normalizeUrl( $site_url ),
            'blog_id'  => $blog_id,
        ];
    }

    private static function generateSiteId(): string
    {
        if ( function_exists( 'wp_generate_uuid4' ) ) {
            return (string) wp_generate_uuid4();
        }

        $data = random_bytes( 16 );

        $data[6] = chr(
            ( ord( $data[6] ) & 0x0f ) | 0x40
        );

        $data[8] = chr(
            ( ord( $data[8] ) & 0x3f ) | 0x80
        );

        return vsprintf(
            '%s%s-%s-%s-%s-%s%s%s',
            str_split(
                bin2hex( $data ),
                4
            )
        );
    }

    private static function isValidUuid4( string $value ): bool
    {
        return preg_match(
            '/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i',
            trim( $value )
        ) === 1;
    }

    private static function normalizeUrl( string $url ): string
    {
        return rtrim(
            trim( $url ),
            '/'
        );
    }
}