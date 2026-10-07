<?php

namespace LinkCraftor\Identity;

final class SiteIdentity
{
    public const OPTION_NAME = 'linkcraftor_site_identity';

    public static function getOrCreate(): array
    {
        $current = self::buildCurrent();

        if ( ! function_exists( 'get_option' ) ) {
            return $current;
        }

        $stored = get_option(
            self::OPTION_NAME,
            null
        );

        if ( is_array( $stored ) ) {
            $merged = array_merge(
                $stored,
                $current
            );

            if ( function_exists( 'update_option' ) ) {
                update_option(
                    self::OPTION_NAME,
                    $merged
                );
            }

            return $merged;
        }

        if ( function_exists( 'add_option' ) ) {
            add_option(
                self::OPTION_NAME,
                $current,
                '',
                false
            );
        }

        return $current;
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

    private static function normalizeUrl( string $url ): string
    {
        return rtrim(
            trim( $url ),
            '/'
        );
    }
}