<?php

namespace LinkCraftor\Connection;

final class PairingHttpClient
{
    private const TIMEOUT_SECONDS = 15;

    public static function submit(
        string $endpoint,
        array $payload
    ): array {
        $endpoint = trim(
            $endpoint
        );

        if ( $endpoint === '' ) {
            return self::failure(
                'invalid_endpoint',
                'Pairing endpoint is not configured.'
            );
        }

        if (
            ! function_exists(
                'wp_remote_post'
            )
        ) {
            return self::failure(
                'http_transport_unavailable',
                'WordPress HTTP transport is unavailable.'
            );
        }

        $encoded = function_exists(
            'wp_json_encode'
        )
            ? wp_json_encode(
                $payload
            )
            : json_encode(
                $payload
            );

        if (
            ! is_string( $encoded )
            || $encoded === ''
        ) {
            return self::failure(
                'request_encoding_failed',
                'Pairing request could not be encoded.'
            );
        }

        $response = wp_remote_post(
            $endpoint,
            [
                'timeout' => self::TIMEOUT_SECONDS,
                'redirection' => 0,
                'headers' => [
                    'Accept' => 'application/json',
                    'Content-Type' => 'application/json',
                ],
                'body' => $encoded,
                'data_format' => 'body',
            ]
        );

        if (
            function_exists(
                'is_wp_error'
            )
            && is_wp_error(
                $response
            )
        ) {
            return self::failure(
                'transport_error',
                'Unable to reach LinkCraftor.'
            );
        }

        if (
            ! is_array(
                $response
            )
        ) {
            return self::failure(
                'invalid_transport_response',
                'LinkCraftor returned an invalid transport response.'
            );
        }

        $status_code = function_exists(
            'wp_remote_retrieve_response_code'
        )
            ? (int) wp_remote_retrieve_response_code(
                $response
            )
            : self::fallbackStatusCode(
                $response
            );

        $body = function_exists(
            'wp_remote_retrieve_body'
        )
            ? (string) wp_remote_retrieve_body(
                $response
            )
            : self::fallbackBody(
                $response
            );

        if (
            $status_code < 200
            || $status_code >= 300
        ) {
            return self::failure(
                'http_error',
                'LinkCraftor rejected the pairing request.',
                $status_code
            );
        }

        $decoded = json_decode(
            $body,
            true
        );

        if (
            ! is_array(
                $decoded
            )
        ) {
            return self::failure(
                'invalid_json_response',
                'LinkCraftor returned an invalid JSON response.',
                $status_code
            );
        }

        if (
            ($decoded['ok'] ?? null)
            !== true
        ) {
            return self::failure(
                'pairing_rejected',
                'LinkCraftor did not accept the pairing request.',
                $status_code
            );
        }

        if (
            ($decoded['status'] ?? '')
            !== 'pending_authentication'
        ) {
            return self::failure(
                'invalid_pairing_state',
                'LinkCraftor returned an unexpected pairing state.',
                $status_code
            );
        }

        if (
            ($decoded['next_step'] ?? '')
            !== 'authentication'
        ) {
            return self::failure(
                'invalid_pairing_next_step',
                'LinkCraftor returned an unexpected next step.',
                $status_code
            );
        }

        $pairing_request_id = isset(
            $decoded['pairing_request_id']
        )
            ? trim(
                (string) $decoded['pairing_request_id']
            )
            : '';

        if (
            ! preg_match(
                '/^wppair_[0-9a-f]{32}$/',
                $pairing_request_id
            )
        ) {
            return self::failure(
                'invalid_pairing_request_id',
                'LinkCraftor returned an invalid pairing request identifier.',
                $status_code
            );
        }

        return [
            'ok' => true,
            'status' => 'pending_authentication',
            'next_step' => 'authentication',
            'pairing_request_id' => $pairing_request_id,
            'http_status' => $status_code,
            'response' => $decoded,
        ];
    }

    private static function failure(
        string $code,
        string $message,
        int $http_status = 0
    ): array {
        return [
            'ok' => false,
            'error' => $code,
            'message' => $message,
            'http_status' => $http_status,
        ];
    }

    private static function fallbackStatusCode(
        array $response
    ): int {
        return isset(
            $response['response']['code']
        )
            ? (int) $response['response']['code']
            : 0;
    }

    private static function fallbackBody(
        array $response
    ): string {
        return isset(
            $response['body']
        )
            ? (string) $response['body']
            : '';
    }
}