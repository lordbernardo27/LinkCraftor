<?php

declare(strict_types=1);

define('ABSPATH', __DIR__ . '/');

$options = [];

$current_home_url = 'https://example.com/';
$current_site_url = 'https://example.com/';
$current_blog_id  = 1;

function get_option($name, $default = false) {
    global $options;

    return array_key_exists($name, $options)
        ? $options[$name]
        : $default;
}

function add_option($name, $value, $deprecated = '', $autoload = null) {
    global $options;

    if (array_key_exists($name, $options)) {
        return false;
    }

    $options[$name] = $value;

    return true;
}

function update_option($name, $value) {
    global $options;

    $options[$name] = $value;

    return true;
}

function home_url($path = '') {
    global $current_home_url;

    return $current_home_url;
}

function site_url($path = '') {
    global $current_site_url;

    return $current_site_url;
}

function get_current_blog_id() {
    global $current_blog_id;

    return $current_blog_id;
}

function wp_generate_uuid4() {
    $data = random_bytes(16);

    $data[6] = chr(
        (ord($data[6]) & 0x0f) | 0x40
    );

    $data[8] = chr(
        (ord($data[8]) & 0x3f) | 0x80
    );

    return vsprintf(
        '%s%s-%s-%s-%s-%s%s%s',
        str_split(bin2hex($data), 4)
    );
}

require_once __DIR__ . '/../src/Identity/SiteIdentity.php';

use LinkCraftor\Identity\SiteIdentity;

function pass($name): void {
    echo $name . ": PASS" . PHP_EOL;
}

function fail($name, $detail = ''): void {
    echo $name . ": FAIL";

    if ($detail !== '') {
        echo " - " . $detail;
    }

    echo PHP_EOL;

    exit(1);
}

function assert_true($condition, $name, $detail = ''): void {
    if ($condition) {
        pass($name);
        return;
    }

    fail($name, $detail);
}

function is_uuid4($value): bool {
    return is_string($value)
        && preg_match(
            '/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i',
            $value
        ) === 1;
}

echo "=== SITE IDENTITY BEHAVIOR TEST ===" . PHP_EOL;

$first = SiteIdentity::getOrCreate();

assert_true(
    isset($first['site_id']) && is_uuid4($first['site_id']),
    'SITE_ID_CREATE_UUID4'
);

$first_site_id = $first['site_id'];

assert_true(
    ($first['home_url'] ?? null) === 'https://example.com',
    'INITIAL_HOME_URL'
);

assert_true(
    ($first['site_url'] ?? null) === 'https://example.com',
    'INITIAL_SITE_URL'
);

assert_true(
    ($first['blog_id'] ?? null) === 1,
    'INITIAL_BLOG_ID'
);

$second = SiteIdentity::getOrCreate();

assert_true(
    ($second['site_id'] ?? null) === $first_site_id,
    'SITE_ID_PERSISTENCE_REPEAT_CALL'
);

$current_home_url = 'https://www.example.com/new-home/';
$current_site_url = 'https://www.example.com/wp/';
$current_blog_id  = 7;

$third = SiteIdentity::getOrCreate();

assert_true(
    ($third['site_id'] ?? null) === $first_site_id,
    'SITE_ID_PERSISTENCE_AFTER_METADATA_CHANGE'
);

assert_true(
    ($third['home_url'] ?? null) === 'https://www.example.com/new-home',
    'HOME_URL_REFRESH'
);

assert_true(
    ($third['site_url'] ?? null) === 'https://www.example.com/wp',
    'SITE_URL_REFRESH'
);

assert_true(
    ($third['blog_id'] ?? null) === 7,
    'BLOG_ID_REFRESH'
);

$stored = get_option(
    SiteIdentity::OPTION_NAME,
    null
);

assert_true(
    is_array($stored),
    'SITE_IDENTITY_PERSISTED'
);

assert_true(
    ($stored['site_id'] ?? null) === $first_site_id,
    'STORED_SITE_ID_UNCHANGED'
);

assert_true(
    is_uuid4($stored['site_id'] ?? null),
    'STORED_SITE_ID_UUID4_VALID'
);

$before_reactivation = $stored['site_id'];

$fourth = SiteIdentity::getOrCreate();

assert_true(
    ($fourth['site_id'] ?? null) === $before_reactivation,
    'SITE_ID_REACTIVATION_STYLE_REUSE'
);

echo PHP_EOL;
echo "=== FINAL CERTIFICATION ===" . PHP_EOL;
echo "SITE_IDENTITY_BEHAVIOR: CERTIFIED" . PHP_EOL;