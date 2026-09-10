<?php

namespace LinkCraftor\Runtime;

final class Configuration
{
    private const ALLOWED_ENVIRONMENTS = [
        'production',
        'staging',
        'development',
    ];

    private array $values;

    private function __construct( array $values )
    {
        $this->values = $values;
    }

    public static function load( string $config_file ): self
    {
        if ( ! is_readable( $config_file ) ) {
            throw new \RuntimeException( 'LinkCraftor configuration file is not readable.' );
        }

        $values = require $config_file;

        if ( ! is_array( $values ) ) {
            throw new \RuntimeException( 'LinkCraftor configuration must return an array.' );
        }

        $environment = defined( 'LINKCRAFTOR_ENVIRONMENT' )
            ? (string) LINKCRAFTOR_ENVIRONMENT
            : (string) ( $values['environment'] ?? 'production' );

        if ( ! in_array( $environment, self::ALLOWED_ENVIRONMENTS, true ) ) {
            throw new \RuntimeException( 'Invalid LinkCraftor environment.' );
        }

        $values['environment'] = $environment;

        if ( defined( 'LINKCRAFTOR_API_BASE_URL' ) ) {
            $values['api'][ $environment ] = (string) LINKCRAFTOR_API_BASE_URL;
        }

        return new self( $values );
    }

    public function environment(): string
    {
        return (string) $this->values['environment'];
    }

    public function apiBaseUrl(): ?string
    {
        $value = $this->values['api'][ $this->environment() ] ?? null;

        if ( null === $value || '' === $value ) {
            return null;
        }

        return rtrim( (string) $value, '/' );
    }

    public function httpTimeoutSeconds(): int
    {
        return max(
            1,
            (int) ( $this->values['http']['timeout_seconds'] ?? 20 )
        );
    }

    public function debugEnabled(): bool
    {
        return true === ( $this->values['features']['debug'] ?? false );
    }

    public function all(): array
    {
        return $this->values;
    }
}