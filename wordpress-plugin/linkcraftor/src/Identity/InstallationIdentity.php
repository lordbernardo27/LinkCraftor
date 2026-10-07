<?php

namespace LinkCraftor\Identity;

final class InstallationIdentity
{
    public const OPTION_NAME = 'linkcraftor_installation_id';

    public static function getOrCreate(): string
    {
        $existing = self::get();

        if ( $existing !== null ) {
            return $existing;
        }

        $id = self::generate();

        if ( function_exists( 'add_option' ) ) {
            add_option(
                self::OPTION_NAME,
                $id,
                '',
                false
            );
        }

        $stored = self::get();

        return $stored ?? $id;
    }

    public static function get(): ?string
    {
        if ( ! function_exists( 'get_option' ) ) {
            return null;
        }

        $value = get_option(
            self::OPTION_NAME,
            null
        );

        if ( ! is_string( $value ) || $value === '' ) {
            return null;
        }

        return $value;
    }

    private static function generate(): string
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
            str_split( bin2hex( $data ), 4 )
        );
    }
}