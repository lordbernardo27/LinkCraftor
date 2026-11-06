<?php

declare(strict_types=1);

define(
    'ABSPATH',
    __DIR__ . '/'
);

$mock_http_mode = 'success';

class WP_Error
{
}

function is_wp_error(
    $value
): bool {
    return $value
        instanceof WP_Error;
}

function wp_json_encode(
    $value
) {
    return json_encode(
        $value
    );
}

function wp_remote_post(
    $url,
    $args = []
) {
    global $mock_http_mode;

    if (
        $mock_http_mode ===
        'transport_error'
    ) {
        return new WP_Error();
    }

    if (
        $mock_http_mode ===
        'http_500'
    ) {
        return [
            'response' => [
                'code' => 500,
            ],
            'body' => json_encode(
                [
                    'detail' =>
                        'internal server detail',
                ]
            ),
        ];
    }

    if (
        $mock_http_mode ===
        'invalid_json'
    ) {
        return [
            'response' => [
                'code' => 200,
            ],
            'body' =>
                'this-is-not-json',
        ];
    }

    if (
        $mock_http_mode ===
        'rejected'
    ) {
        return [
            'response' => [
                'code' => 200,
            ],
            'body' => json_encode(
                [
                    'ok' => false,
                ]
            ),
        ];
    }

    if (
        $mock_http_mode ===
        'bad_state'
    ) {
        return [
            'response' => [
                'code' => 200,
            ],
            'body' => json_encode(
                [
                    'ok' => true,
                    'status' =>
                        'connected',
                    'next_step' =>
                        'authorization',
                    'pairing_request_id' =>
                        'wppair_'
                        . str_repeat(
                            'a',
                            32
                        ),
                ]
            ),
        ];
    }

    if (
        $mock_http_mode ===
        'bad_pairing_id'
    ) {
        return [
            'response' => [
                'code' => 200,
            ],
            'body' => json_encode(
                [
                    'ok' => true,
                    'status' =>
                        'pending_authentication',
                    'next_step' =>
                        'authentication',
                    'pairing_request_id' =>
                        'bad-id',
                ]
            ),
        ];
    }

    return [
        'response' => [
            'code' => 200,
        ],
        'body' => json_encode(
            [
                'ok' => true,
                'status' =>
                    'pending_authentication',
                'next_step' =>
                    'authentication',
                'pairing_request_id' =>
                    'wppair_'
                    . str_repeat(
                        'a',
                        32
                    ),
                'security_boundary' => [
                    'authenticated' =>
                        false,
                    'authorized' =>
                        false,
                ],
            ]
        ),
    ];
}

function wp_remote_retrieve_response_code(
    $response
) {
    return $response['response']['code']
        ?? 0;
}

function wp_remote_retrieve_body(
    $response
) {
    return $response['body']
        ?? '';
}


require_once __DIR__
    . '/../src/Connection/PairingRequestBuilder.php';

require_once __DIR__
    . '/../src/Connection/PairingHttpClient.php';


use LinkCraftor\Connection\PairingRequestBuilder;
use LinkCraftor\Connection\PairingHttpClient;


function pass_check(
    string $name
): void {
    echo $name
        . ': PASS'
        . PHP_EOL;
}


function fail_check(
    string $name,
    string $detail = ''
): void {
    echo $name
        . ': FAIL';

    if (
        $detail !== ''
    ) {
        echo ' -> '
            . $detail;
    }

    echo PHP_EOL;

    exit(1);
}


function expect_error(
    string $name,
    array $result,
    string $expected
): void {
    if (
        ($result['ok'] ?? null)
            === false
        && ($result['error'] ?? '')
            === $expected
    ) {
        pass_check(
            $name
        );

        return;
    }

    fail_check(
        $name,
        json_encode(
            $result
        )
    );
}


echo
    '=== 2.2.7 WORDPRESS PAIRING REQUEST BUILDER ==='
    . PHP_EOL;


$snapshot = [
    'installation_id' =>
        '550e8400-e29b-41d4-a716-446655440000',

    'site_identity' => [
        'site_id' =>
            '123e4567-e89b-42d3-a456-426614174000',

        'home_url' =>
            'https://example.com',

        'site_url' =>
            'https://example.com/wp',

        'blog_id' =>
            1,
    ],

    'plugin_version' =>
        '1.0.0',

    'wordpress_version' =>
        '6.8.1',

    'php_version' =>
        '8.4.0',

    'protocol_version' =>
        '1.0',

    'lifecycle_status' =>
        'active',
];


$payload =
    PairingRequestBuilder::buildFromSnapshot(
        $snapshot
    );


$required_fields = [
    'installation_id',
    'site_id',
    'home_url',
    'site_url',
    'blog_id',
    'plugin_version',
    'wordpress_version',
    'php_version',
    'protocol_version',
    'lifecycle_status',
];


foreach (
    $required_fields
    as $field
) {
    if (
        array_key_exists(
            $field,
            $payload
        )
    ) {
        pass_check(
            'BUILDER_'
            . strtoupper(
                $field
            )
        );
    } else {
        fail_check(
            'BUILDER_'
            . strtoupper(
                $field
            )
        );
    }
}


foreach (
    [
        'workspace_id',
        'access_token',
        'refresh_token',
        'connection_id',
        'domain_id',
    ]
    as $forbidden
) {
    if (
        ! array_key_exists(
            $forbidden,
            $payload
        )
    ) {
        pass_check(
            'BUILDER_FORBIDS_'
            . strtoupper(
                $forbidden
            )
        );
    } else {
        fail_check(
            'BUILDER_FORBIDS_'
            . strtoupper(
                $forbidden
            )
        );
    }
}


$missing_snapshot =
    $snapshot;

unset(
    $missing_snapshot[
        'site_identity'
    ][
        'site_id'
    ]
);


try {
    PairingRequestBuilder::buildFromSnapshot(
        $missing_snapshot
    );

    fail_check(
        'BUILDER_MISSING_SITE_ID_REJECTED'
    );

} catch (
    RuntimeException $exception
) {
    pass_check(
        'BUILDER_MISSING_SITE_ID_REJECTED'
    );
}


echo
    '2.2.7_WORDPRESS_PAIRING_REQUEST_BUILDER: CERTIFIED'
    . PHP_EOL;


echo PHP_EOL;
echo
    '=== 2.2.8 WORDPRESS HTTP SUBMISSION BOUNDARY ==='
    . PHP_EOL;


$mock_http_mode =
    'success';


$success =
    PairingHttpClient::submit(
        'https://api.linkcraftor.com/api/wordpress/pairing/request',
        $payload
    );


if (
    ($success['ok'] ?? null)
        === true
    && ($success['status'] ?? '')
        === 'pending_authentication'
    && ($success['next_step'] ?? '')
        === 'authentication'
    && ($success['pairing_request_id'] ?? '')
        === (
            'wppair_'
            . str_repeat(
                'a',
                32
            )
        )
) {
    pass_check(
        'HTTP_SUCCESS_BOUNDARY'
    );
} else {
    fail_check(
        'HTTP_SUCCESS_BOUNDARY',
        json_encode(
            $success
        )
    );
}


if (
    ! array_key_exists(
        'workspace_id',
        $success
    )
) {
    pass_check(
        'HTTP_NO_WORKSPACE_BINDING'
    );
} else {
    fail_check(
        'HTTP_NO_WORKSPACE_BINDING'
    );
}


if (
    ! array_key_exists(
        'access_token',
        $success
    )
) {
    pass_check(
        'HTTP_NO_TOKEN_ISSUANCE'
    );
} else {
    fail_check(
        'HTTP_NO_TOKEN_ISSUANCE'
    );
}


echo
    '2.2.8_WORDPRESS_HTTP_SUBMISSION_BOUNDARY: CERTIFIED'
    . PHP_EOL;


echo PHP_EOL;
echo
    '=== 2.2.9 ERROR / FAILURE CONTRACT ==='
    . PHP_EOL;


expect_error(
    'EMPTY_ENDPOINT_REJECTED',
    PairingHttpClient::submit(
        '',
        $payload
    ),
    'invalid_endpoint'
);


$mock_http_mode =
    'transport_error';

expect_error(
    'TRANSPORT_ERROR_NORMALIZED',
    PairingHttpClient::submit(
        'https://api.linkcraftor.com/api/wordpress/pairing/request',
        $payload
    ),
    'transport_error'
);


$mock_http_mode =
    'http_500';

$server_failure =
    PairingHttpClient::submit(
        'https://api.linkcraftor.com/api/wordpress/pairing/request',
        $payload
    );

expect_error(
    'HTTP_500_NORMALIZED',
    $server_failure,
    'http_error'
);


if (
    strpos(
        json_encode(
            $server_failure
        ),
        'internal server detail'
    ) === false
) {
    pass_check(
        'INTERNAL_SERVER_DETAIL_NOT_EXPOSED'
    );
} else {
    fail_check(
        'INTERNAL_SERVER_DETAIL_NOT_EXPOSED'
    );
}


$mock_http_mode =
    'invalid_json';

expect_error(
    'INVALID_JSON_REJECTED',
    PairingHttpClient::submit(
        'https://api.linkcraftor.com/api/wordpress/pairing/request',
        $payload
    ),
    'invalid_json_response'
);


$mock_http_mode =
    'rejected';

expect_error(
    'PAIRING_REJECTION_NORMALIZED',
    PairingHttpClient::submit(
        'https://api.linkcraftor.com/api/wordpress/pairing/request',
        $payload
    ),
    'pairing_rejected'
);


$mock_http_mode =
    'bad_state';

expect_error(
    'UNEXPECTED_STATE_REJECTED',
    PairingHttpClient::submit(
        'https://api.linkcraftor.com/api/wordpress/pairing/request',
        $payload
    ),
    'invalid_pairing_state'
);


$mock_http_mode =
    'bad_pairing_id';

expect_error(
    'INVALID_PAIRING_ID_REJECTED',
    PairingHttpClient::submit(
        'https://api.linkcraftor.com/api/wordpress/pairing/request',
        $payload
    ),
    'invalid_pairing_request_id'
);


echo
    '2.2.9_WORDPRESS_ERROR_FAILURE_CONTRACT: CERTIFIED'
    . PHP_EOL;


echo PHP_EOL;
echo
    '=== COMBINED PHP RESULT ==='
    . PHP_EOL;

echo
    '2.2.7_TO_2.2.9: CERTIFIED'
    . PHP_EOL;